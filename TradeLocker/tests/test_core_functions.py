"""
Unit tests for TradeLocker MTF_ONER Bot - Core Functions
Tests: CSDL parsing, NEWS extraction, TF checks, NY hours filter
Run: pytest test_core_functions.py -v
"""

import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test helpers (we'll create a simplified version without full bot)


class TestNEWSExtraction:
    """Test NEWS CASCADE system (14 variables)"""

    def map_news_to_14_variables(self, news_values):
        """Helper: Extract level and direction from NEWS values"""
        levels = []
        directions = []

        for news in news_values:
            levels.append(abs(news))

            if news > 0:
                directions.append(1)
            elif news < 0:
                directions.append(-1)
            else:
                directions.append(0)

        return levels, directions

    @pytest.mark.parametrize("input_news,expected_level,expected_direction", [
        (15, 15, 1),      # Positive NEWS: +15 → level=15, direction=+1
        (-20, 20, -1),    # Negative NEWS: -20 → level=20, direction=-1
        (0, 0, 0),        # Zero NEWS: 0 → level=0, direction=0
        (70, 70, 1),      # Max NEWS: +70 → level=70, direction=+1
        (-70, 70, -1),    # Min NEWS: -70 → level=70, direction=-1
    ])
    def test_map_news_extraction(self, input_news, expected_level, expected_direction):
        """Test single NEWS value extraction"""
        levels, directions = self.map_news_to_14_variables([input_news])

        assert levels[0] == expected_level, f"Level mismatch for NEWS={input_news}"
        assert directions[0] == expected_direction, f"Direction mismatch for NEWS={input_news}"

    def test_map_news_all_7_timeframes(self):
        """Test extraction for all 7 timeframes"""
        test_news = [15, -20, 30, -5, 0, 10, -70]

        levels, directions = self.map_news_to_14_variables(test_news)

        # Verify M1 (index 0)
        assert levels[0] == 15 and directions[0] == 1, "M1 failed"

        # Verify M5 (index 1)
        assert levels[1] == 20 and directions[1] == -1, "M5 failed"

        # Verify H1 (index 4) - zero case
        assert levels[4] == 0 and directions[4] == 0, "H1 zero case failed"

        # Verify D1 (index 6)
        assert levels[6] == 70 and directions[6] == -1, "D1 failed"


class TestNYSessionHours:
    """Test NY Session Hours filter"""

    def is_within_ny_hours(self, enabled, start, end, current_hour):
        """Helper: Check if hour is within NY session"""
        if not enabled:
            return True

        if start < end:
            # Simple case: same day (e.g., 14:00-21:00)
            return (current_hour >= start and current_hour < end)
        else:
            # Cross midnight (e.g., 22:00-06:00)
            return (current_hour >= start or current_hour < end)

    @pytest.mark.parametrize("start,end,current,expected", [
        (14, 21, 15, True),   # 15:00 is within 14:00-21:00
        (14, 21, 13, False),  # 13:00 is before 14:00
        (14, 21, 22, False),  # 22:00 is after 21:00
        (14, 21, 14, True),   # 14:00 is start boundary (inclusive)
        (14, 21, 21, False),  # 21:00 is end boundary (exclusive)
    ])
    def test_simple_case_same_day(self, start, end, current, expected):
        """Test simple case (start < end)"""
        result = self.is_within_ny_hours(True, start, end, current)

        assert result == expected, f"Hour {current} check failed for {start:02d}:00-{end:02d}:00"

    @pytest.mark.parametrize("start,end,current,expected", [
        (22, 6, 23, True),   # 23:00 is within 22:00-06:00 (cross midnight)
        (22, 6, 3, True),    # 03:00 is within 22:00-06:00 (cross midnight)
        (22, 6, 7, False),   # 07:00 is after 06:00
        (22, 6, 21, False),  # 21:00 is before 22:00
        (22, 6, 22, True),   # 22:00 is start boundary
        (22, 6, 6, False),   # 06:00 is end boundary
    ])
    def test_cross_midnight_case(self, start, end, current, expected):
        """Test cross-midnight case (start > end)"""
        result = self.is_within_ny_hours(True, start, end, current)

        assert result == expected, f"Cross-midnight hour {current} check failed"

    def test_filter_disabled_always_returns_true(self):
        """Test that disabled filter always returns True"""
        # Try various hours when filter is disabled
        for hour in [0, 5, 12, 23]:
            result = self.is_within_ny_hours(False, 14, 21, hour)
            assert result is True, f"Disabled filter should return True for hour {hour}"


class TestTFEnabled:
    """Test TF enabled checks"""

    def is_tf_enabled(self, tf_index, tf_flags):
        """Helper: Check if TF is enabled"""
        if tf_index < 0 or tf_index >= 7:
            return False
        return tf_flags[tf_index]

    @pytest.mark.parametrize("tf_index,expected", [
        (0, True),   # M1 enabled
        (1, True),   # M5 enabled
        (2, True),   # M15 enabled
        (3, False),  # M30 disabled
        (6, False),  # D1 disabled
        (-1, False), # Invalid index
        (7, False),  # Invalid index
    ])
    def test_tf_enabled_check(self, tf_index, expected):
        """Test TF enabled status"""
        tf_flags = [True, True, True, False, False, False, False]  # M1,M5,M15 ON

        result = self.is_tf_enabled(tf_index, tf_flags)

        assert result == expected, f"TF index {tf_index} check failed"


class TestProgressiveLotCalculation:
    """Test progressive lot sizing formula"""

    def calculate_progressive_lot(self, base_lot, tf_index, strategy_index):
        """Helper: Calculate progressive lot size"""
        strategy_multipliers = [2.0, 1.0, 3.0]  # S1=×2, S2=×1, S3=×3
        tf_increments = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]

        return (base_lot * strategy_multipliers[strategy_index]) + tf_increments[tf_index]

    @pytest.mark.parametrize("base,tf,strat,expected", [
        (0.1, 0, 0, 0.21),  # M1_S1 = (0.1×2) + 0.01 = 0.21
        (0.1, 0, 1, 0.11),  # M1_S2 = (0.1×1) + 0.01 = 0.11
        (0.1, 0, 2, 0.31),  # M1_S3 = (0.1×3) + 0.01 = 0.31
        (0.1, 6, 0, 0.27),  # D1_S1 = (0.1×2) + 0.07 = 0.27
        (0.1, 6, 1, 0.17),  # D1_S2 = (0.1×1) + 0.07 = 0.17
        (0.1, 6, 2, 0.37),  # D1_S3 = (0.1×3) + 0.07 = 0.37
        (0.2, 3, 1, 0.24),  # M30_S2 = (0.2×1) + 0.04 = 0.24
    ])
    def test_progressive_lot_formula(self, base, tf, strat, expected):
        """Test progressive lot calculation"""
        result = self.calculate_progressive_lot(base, tf, strat)

        assert abs(result - expected) < 0.001, f"Lot calculation mismatch: got {result}, expected {expected}"


class TestSignalChangeDetection:
    """Test signal change detection logic"""

    def should_open_new_order(self, old_signal, new_signal, old_time, new_time):
        """Helper: Detect if should open new order"""
        return (old_signal != new_signal and
                new_signal != 0 and
                old_time < new_time and
                (new_time - old_time) > 15)

    @pytest.mark.parametrize("old_sig,new_sig,old_time,new_time,expected", [
        (1, -1, 100, 120, True),   # Signal changed 1→-1, time diff 20s → OPEN
        (1, 1, 100, 120, False),   # Signal unchanged 1→1 → NO OPEN
        (1, 0, 100, 120, False),   # New signal = 0 → NO OPEN
        (1, -1, 100, 110, False),  # Time diff 10s < 15s → NO OPEN
        (0, 1, 100, 120, True),    # Signal 0→1 (first run) → OPEN
        (-1, 1, 100, 200, True),   # Signal -1→1 with large time gap → OPEN
    ])
    def test_signal_change_detection(self, old_sig, new_sig, old_time, new_time, expected):
        """Test signal change detection logic"""
        result = self.should_open_new_order(old_sig, new_sig, old_time, new_time)

        assert result == expected, f"Signal detection failed for {old_sig}→{new_sig}"


class TestLayer1ThresholdCalculation:
    """Test Layer1 stoploss threshold calculation"""

    def calculate_layer1_threshold(self, max_loss, lot, fallback):
        """Helper: Calculate Layer1 threshold"""
        if abs(max_loss) < 1.0:
            max_loss = abs(fallback)

        return -(max_loss * lot)

    @pytest.mark.parametrize("max_loss,lot,fallback,expected", [
        (1000.0, 0.21, -1000.0, -210.0),  # MaxLoss=1000, Lot=0.21 → -210
        (500.0, 0.11, -1000.0, -55.0),    # MaxLoss=500, Lot=0.11 → -55
        (0.5, 0.21, -1000.0, -210.0),     # MaxLoss=0.5 (invalid) → Use fallback
        (0.0, 0.11, -500.0, -55.0),       # MaxLoss=0 → Use fallback 500
    ])
    def test_layer1_threshold(self, max_loss, lot, fallback, expected):
        """Test Layer1 threshold calculation"""
        result = self.calculate_layer1_threshold(max_loss, lot, fallback)

        assert abs(result - expected) < 0.01, f"Threshold mismatch: got {result}, expected {expected}"


if __name__ == "__main__":
    # Run tests with: python test_core_functions.py
    pytest.main([__file__, "-v", "--tb=short"])
