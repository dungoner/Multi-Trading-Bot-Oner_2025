# TradeLocker MTF_ONER Bot - Unit Tests

## Overview

This directory contains comprehensive unit tests for the TradeLocker MTF_ONER trading bot. Tests validate core functions, CSDL JSON parsing, and the new optimizations added.

## Test Files

### 1. `test_core_functions.py`
Tests core trading logic functions:

- **TestNEWSExtraction**: NEWS CASCADE system (14 variables: 7 levels + 7 directions)
- **TestNYSessionHours**: NY Session Hours filter (simple and cross-midnight cases)
- **TestTFEnabled**: Timeframe enabled/disabled checks
- **TestProgressiveLotCalculation**: Progressive lot sizing formula
- **TestSignalChangeDetection**: Signal change detection logic
- **TestLayer1ThresholdCalculation**: Layer1 stoploss threshold calculation

### 2. `test_json_parsing.py`
Tests CSDL JSON parsing and validation:

- Valid JSON with all 7 timeframes
- Invalid JSON syntax handling
- Non-array JSON handling
- Empty array handling
- Partial rows (< 7 timeframes)
- Missing fields with default values
- More than 7 rows (should only parse first 7)

## Test Data

Mock CSDL JSON files in `test_data/`:

- `valid_7_rows.json`: Complete valid data for all 7 timeframes
- `partial_3_rows.json`: Only 3 timeframes (M1, M5, M15)
- `missing_fields.json`: Rows with missing fields (tests default value handling)
- `empty_array.json`: Empty JSON array (should fail parsing)

## Requirements

Install test dependencies:

```bash
pip install pytest
```

The tests use Python's built-in modules (`json`, `dataclasses`, `typing`, `datetime`) - no additional dependencies required.

## Running Tests

### Run all tests with verbose output:
```bash
cd /home/user/Multi-Trading-Bot-Oner_2025/TradeLocker/tests
pytest -v
```

### Run specific test file:
```bash
pytest test_core_functions.py -v
pytest test_json_parsing.py -v
```

### Run specific test class:
```bash
pytest test_core_functions.py::TestNEWSExtraction -v
pytest test_json_parsing.py::TestCSDLJSONParsing -v
```

### Run specific test method:
```bash
pytest test_core_functions.py::TestNEWSExtraction::test_map_news_all_7_timeframes -v
```

### Run with short traceback:
```bash
pytest -v --tb=short
```

### Run directly with Python:
```bash
python test_core_functions.py
python test_json_parsing.py
```

## Expected Output

Successful test run should show:

```
========================= test session starts =========================
collected 30 items

test_core_functions.py::TestNEWSExtraction::test_map_news_extraction[15-15-1] PASSED [ 3%]
test_core_functions.py::TestNEWSExtraction::test_map_news_extraction[-20-20--1] PASSED [ 6%]
test_core_functions.py::TestNEWSExtraction::test_map_news_extraction[0-0-0] PASSED [ 10%]
...
test_json_parsing.py::TestCSDLJSONParsing::test_valid_json_all_7_rows PASSED [ 93%]
test_json_parsing.py::TestCSDLJSONParsing::test_invalid_json_syntax PASSED [ 96%]
test_json_parsing.py::TestCSDLJSONParsing::test_empty_array PASSED [100%]

========================= 30 passed in 0.15s ==========================
```

## Test Coverage

### Core Functions (test_core_functions.py):
✅ NEWS CASCADE extraction (14 variables)
✅ NY Session Hours filter (14+ test cases)
✅ Timeframe enabled checks (7 test cases)
✅ Progressive lot calculation (7+ test cases)
✅ Signal change detection (6 test cases)
✅ Layer1 threshold calculation (4 test cases)

### JSON Parsing (test_json_parsing.py):
✅ Valid JSON parsing (all 7 rows)
✅ Invalid JSON syntax handling
✅ Non-array JSON handling
✅ Empty array handling
✅ Partial rows handling (< 7)
✅ Missing fields with defaults
✅ More than 7 rows (parse only first 7)
✅ Parameterized signal/news value testing

**Total Test Cases**: ~30 tests covering all critical functions

## New Optimizations Tested

These tests validate the 3 new optimizations added:

1. **S2 NEWS Filter** (Optional, Default OFF)
   - Validates NEWS level threshold checks
   - Validates NEWS direction matching logic

2. **NY Session Hours Filter** (Only S1/S2, Not S3/Bonus)
   - Tests simple same-day hours (e.g., 14:00-21:00)
   - Tests cross-midnight hours (e.g., 22:00-06:00)
   - Tests filter disabled behavior

3. **Multi-Symbol Safety**
   - Tests use instance-level data structures (EASymbolData dataclass)
   - Ensures no static/global variable conflicts

## Integration with Bot

The test helper functions mirror the actual bot logic in:
- `TradeLocker/TradeLocker_MTF_ONER.py`

Tests are isolated and don't require:
- Live TradeLocker API connection
- Real market data
- Broker account

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'pytest'`:
```bash
pip install pytest
```

### Test Discovery Issues
Ensure you're in the correct directory:
```bash
cd /home/user/Multi-Trading-Bot-Oner_2025/TradeLocker/tests
```

### Test Failures
If tests fail:
1. Check Python version (requires Python 3.7+)
2. Verify test data files exist in `test_data/`
3. Review traceback for specific assertion failures

## Contributing

When adding new tests:
1. Follow existing test structure (class-based organization)
2. Use descriptive test names (e.g., `test_map_news_extraction`)
3. Use `@pytest.mark.parametrize` for testing multiple inputs
4. Add docstrings explaining what the test validates

## License

Tests are part of the MTF_ONER Bot project.
