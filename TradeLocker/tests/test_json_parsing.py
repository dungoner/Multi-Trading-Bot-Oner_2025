"""
Unit tests for TradeLocker MTF_ONER Bot - JSON Parsing
Tests: CSDL JSON parsing, validation, error handling
Run: pytest test_json_parsing.py -v
"""

import pytest
import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class CSDLLoveRow:
    """CSDL Row data structure"""
    max_loss: float = 0.0
    timestamp: int = 0
    signal: int = 0
    pricediff: float = 0.0
    timediff: int = 0
    news: int = 0


class TestCSDLJSONParsing:
    """Test CSDL JSON parsing logic"""

    def parse_csdl_json(self, json_content: str) -> tuple:
        """
        Helper: Parse CSDL JSON array

        Returns:
            (success: bool, rows: List[CSDLLoveRow])
        """
        try:
            data = json.loads(json_content)

            if not isinstance(data, list):
                return (False, [])

            rows = []
            for i in range(min(7, len(data))):
                row_data = data[i]

                row = CSDLLoveRow()
                row.max_loss = row_data.get('max_loss', 0.0)
                row.timestamp = row_data.get('timestamp', 0)
                row.signal = row_data.get('signal', 0)
                row.pricediff = row_data.get('pricediff', 0.0)
                row.timediff = row_data.get('timediff', 0)
                row.news = row_data.get('news', 0)

                rows.append(row)

            return (len(rows) >= 1, rows)

        except json.JSONDecodeError:
            return (False, [])
        except Exception:
            return (False, [])

    def test_valid_json_all_7_rows(self):
        """Test parsing valid JSON with all 7 timeframes"""
        valid_json = """[
            {"max_loss": 1000.0, "timestamp": 1699876543, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 15},
            {"max_loss": 950.0, "timestamp": 1699876544, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -20},
            {"max_loss": 900.0, "timestamp": 1699876545, "signal": 0, "pricediff": 0.0, "timediff": 0, "news": 0},
            {"max_loss": 850.0, "timestamp": 1699876546, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 30},
            {"max_loss": 800.0, "timestamp": 1699876547, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -5},
            {"max_loss": 750.0, "timestamp": 1699876548, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 10},
            {"max_loss": 700.0, "timestamp": 1699876549, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -70}
        ]"""

        success, rows = self.parse_csdl_json(valid_json)

        assert success is True, "Parsing should succeed"
        assert len(rows) == 7, "Should parse all 7 rows"

        # Verify M1 (index 0)
        assert abs(rows[0].max_loss - 1000.0) < 0.01, "M1 MaxLoss"
        assert rows[0].timestamp == 1699876543, "M1 Timestamp"
        assert rows[0].signal == 1, "M1 Signal"
        assert rows[0].news == 15, "M1 News"

        # Verify M5 (index 1)
        assert rows[1].signal == -1, "M5 Signal"
        assert rows[1].news == -20, "M5 News"

        # Verify D1 (index 6)
        assert abs(rows[6].max_loss - 700.0) < 0.01, "D1 MaxLoss"
        assert rows[6].news == -70, "D1 News"

    def test_invalid_json_syntax(self):
        """Test handling of invalid JSON syntax"""
        invalid_json = "{this is not valid json}"

        success, rows = self.parse_csdl_json(invalid_json)

        assert success is False, "Should fail for invalid JSON"
        assert len(rows) == 0, "Should return empty list"

    def test_json_not_array(self):
        """Test handling of non-array JSON"""
        not_array = '{"max_loss": 1000.0}'

        success, rows = self.parse_csdl_json(not_array)

        assert success is False, "Should fail for non-array JSON"

    def test_empty_array(self):
        """Test handling of empty array"""
        empty = "[]"

        success, rows = self.parse_csdl_json(empty)

        assert success is False, "Should fail for empty array"
        assert len(rows) == 0, "Should return empty list"

    def test_partial_rows_less_than_7(self):
        """Test parsing with less than 7 rows"""
        partial_json = """[
            {"max_loss": 1000.0, "timestamp": 1699876543, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 15},
            {"max_loss": 950.0, "timestamp": 1699876544, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -20},
            {"max_loss": 900.0, "timestamp": 1699876545, "signal": 0, "pricediff": 0.0, "timediff": 0, "news": 0}
        ]"""

        success, rows = self.parse_csdl_json(partial_json)

        assert success is True, "Should succeed with < 7 rows"
        assert len(rows) == 3, "Should parse 3 rows"
        assert abs(rows[0].max_loss - 1000.0) < 0.01, "First row correct"
        assert abs(rows[2].max_loss - 900.0) < 0.01, "Third row correct"

    def test_missing_fields_use_defaults(self):
        """Test that missing fields use default values"""
        missing_fields = """[
            {"signal": 1, "news": 15},
            {"max_loss": 950.0},
            {"timestamp": 1699876545, "signal": -1},
            {"max_loss": 850.0, "timestamp": 1699876546, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 30},
            {"max_loss": 800.0, "timestamp": 1699876547, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -5},
            {"max_loss": 750.0, "timestamp": 1699876548, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 10},
            {"max_loss": 700.0, "timestamp": 1699876549, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -70}
        ]"""

        success, rows = self.parse_csdl_json(missing_fields)

        assert success is True, "Should handle missing fields"

        # Row 0: missing max_loss and timestamp
        assert rows[0].max_loss == 0.0, "Default MaxLoss = 0.0"
        assert rows[0].timestamp == 0, "Default Timestamp = 0"
        assert rows[0].signal == 1, "Signal present"
        assert rows[0].news == 15, "News present"

        # Row 1: missing most fields
        assert abs(rows[1].max_loss - 950.0) < 0.01, "MaxLoss present"
        assert rows[1].signal == 0, "Default Signal = 0"
        assert rows[1].news == 0, "Default News = 0"

    def test_more_than_7_rows_only_parse_7(self):
        """Test that only first 7 rows are parsed when > 7 exist"""
        many_rows = """[
            {"max_loss": 1000.0, "timestamp": 1699876543, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 15},
            {"max_loss": 950.0, "timestamp": 1699876544, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -20},
            {"max_loss": 900.0, "timestamp": 1699876545, "signal": 0, "pricediff": 0.0, "timediff": 0, "news": 0},
            {"max_loss": 850.0, "timestamp": 1699876546, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 30},
            {"max_loss": 800.0, "timestamp": 1699876547, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -5},
            {"max_loss": 750.0, "timestamp": 1699876548, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 10},
            {"max_loss": 700.0, "timestamp": 1699876549, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -70},
            {"max_loss": 650.0, "timestamp": 1699876550, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 5},
            {"max_loss": 600.0, "timestamp": 1699876551, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -10}
        ]"""

        success, rows = self.parse_csdl_json(many_rows)

        assert success is True, "Should succeed"
        assert len(rows) == 7, "Should only parse first 7 rows"
        assert abs(rows[6].max_loss - 700.0) < 0.01, "7th row is index 6"

    @pytest.mark.parametrize("test_signal,test_news,expected_signal,expected_news", [
        (1, 15, 1, 15),
        (-1, -20, -1, -20),
        (0, 0, 0, 0),
    ])
    def test_signal_and_news_values(self, test_signal, test_news, expected_signal, expected_news):
        """Test various signal and news values"""
        test_json = f"""[
            {{"max_loss": 1000.0, "timestamp": 1699876543, "signal": {test_signal}, "pricediff": 0.0, "timediff": 0, "news": {test_news}}},
            {{"max_loss": 950.0, "timestamp": 1699876544, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -20}},
            {{"max_loss": 900.0, "timestamp": 1699876545, "signal": 0, "pricediff": 0.0, "timediff": 0, "news": 0}},
            {{"max_loss": 850.0, "timestamp": 1699876546, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 30}},
            {{"max_loss": 800.0, "timestamp": 1699876547, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -5}},
            {{"max_loss": 750.0, "timestamp": 1699876548, "signal": 1, "pricediff": 0.0, "timediff": 0, "news": 10}},
            {{"max_loss": 700.0, "timestamp": 1699876549, "signal": -1, "pricediff": 0.0, "timediff": 0, "news": -70}}
        ]"""

        success, rows = self.parse_csdl_json(test_json)

        assert success is True, "Parsing should succeed"
        assert rows[0].signal == expected_signal, f"Signal mismatch"
        assert rows[0].news == expected_news, f"News mismatch"


if __name__ == "__main__":
    # Run tests with: python test_json_parsing.py
    pytest.main([__file__, "-v", "--tb=short"])
