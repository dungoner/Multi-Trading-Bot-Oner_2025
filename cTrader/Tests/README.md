# cTrader MTF_ONER_cBot - Unit Tests

## Overview

This directory contains comprehensive unit tests for the cTrader MTF_ONER_cBot trading bot (C# NUnit). Tests validate core functions, CSDL JSON parsing, and the new optimizations added.

## Test Files

### 1. `CoreFunctionsTests.cs`
Tests core trading logic functions:

- **NEWS CASCADE Tests**: NEWS extraction to 14 variables (7 levels + 7 directions)
- **NY Session Hours Filter Tests**: Simple and cross-midnight hour checks
- **TF Enabled Check Tests**: Timeframe toggle validation
- **Progressive Lot Calculation Tests**: Lot sizing formula validation
- **Signal Change Detection Tests**: Signal change logic validation
- **Layer1 Threshold Calculation Tests**: Stoploss threshold calculation

### 2. `JSONParsingTests.cs`
Tests CSDL JSON parsing and validation:

- Valid JSON with all 7 timeframes
- Invalid JSON syntax handling
- Non-array JSON handling
- Empty array handling
- Less than 7 rows (partial data)
- Missing fields with default values

## Test Data

Mock CSDL JSON files in `TestData/`:

- `valid_7_rows.json`: Complete valid data for all 7 timeframes
- `partial_2_rows.json`: Only 2 timeframes (M1, M5)
- `missing_fields.json`: Rows with missing fields (tests default value handling)
- `empty_array.json`: Empty JSON array (should fail parsing)

## Requirements

### NUnit Framework
The tests use NUnit 3.x framework. Required packages:

```xml
<PackageReference Include="NUnit" Version="3.13.3" />
<PackageReference Include="NUnit3TestAdapter" Version="4.3.1" />
<PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.4.1" />
<PackageReference Include="Newtonsoft.Json" Version="13.0.2" />
<PackageReference Include="Moq" Version="4.18.4" />
```

### cAlgo API
Tests reference the cAlgo.API from cTrader platform.

## Running Tests

### Visual Studio:
1. Open the solution in Visual Studio
2. Build the solution (Ctrl+Shift+B)
3. Open Test Explorer (Test → Test Explorer)
4. Click "Run All" to execute all tests

### Visual Studio Code:
1. Install C# extension
2. Install .NET Core Test Explorer extension
3. Open Test Explorer panel
4. Click "Run All Tests"

### Command Line (dotnet CLI):
```bash
cd /home/user/Multi-Trading-Bot-Oner_2025/cTrader/Tests
dotnet test --verbosity normal
```

### Run specific test file:
```bash
dotnet test --filter FullyQualifiedName~CoreFunctionsTests
dotnet test --filter FullyQualifiedName~JSONParsingTests
```

### Run specific test:
```bash
dotnet test --filter FullyQualifiedName~MapNewsTo14Variables_ShouldExtractLevelAndDirection
```

## Expected Output

Successful test run should show:

```
Test run for cAlgo.Tests.dll (.NET 6.0)
Microsoft (R) Test Execution Command Line Tool
Copyright (c) Microsoft Corporation.  All rights reserved.

Starting test execution, please wait...
A total of 1 test files matched the specified pattern.

Passed!  - Failed:     0, Passed:    25, Skipped:     0, Total:    25
```

## Test Coverage

### Core Functions (CoreFunctionsTests.cs):
✅ NEWS CASCADE extraction (14 variables)
✅ NY Session Hours filter (10+ test cases)
✅ Timeframe enabled checks (5 test cases)
✅ Progressive lot calculation (6+ test cases)
✅ Signal change detection (5 test cases)
✅ Layer1 threshold calculation (3 test cases)

### JSON Parsing (JSONParsingTests.cs):
✅ Valid JSON parsing (all 7 rows)
✅ Invalid JSON syntax handling
✅ Non-array JSON handling
✅ Empty array handling
✅ Partial rows handling (< 7)
✅ Missing fields with defaults

**Total Test Cases**: ~25 tests covering all critical functions

## New Optimizations Tested

These tests validate the 3 new optimizations added:

1. **S2 NEWS Filter** (Optional, Default OFF)
   - Validates NEWS level threshold checks (MinNewsLevelS2)
   - Validates NEWS direction matching logic (S2_RequireNewsDirection)

2. **NY Session Hours Filter** (Only S1/S2, Not S3/Bonus)
   - Tests simple same-day hours (e.g., 14:00-21:00)
   - Tests cross-midnight hours (e.g., 22:00-06:00)
   - Tests filter disabled behavior (EnableNYHoursFilter = false)

3. **Multi-Symbol Safety**
   - Tests use instance-level data structures (EASymbolData class)
   - Ensures no static variable conflicts (moved PrintFailed to instance)

## Integration with Bot

The test helper methods mirror the actual bot logic in:
- `cTrader/Robots/MTF_ONER_V2/MTF_ONER_cBot.cs`

Tests are isolated and don't require:
- Live cTrader API connection
- Real market data
- Broker account
- Running cTrader platform

## Test Attributes Used

### NUnit Attributes:
- `[TestFixture]`: Marks a class as containing tests
- `[Test]`: Marks a method as a test case
- `[TestCase]`: Provides inline data for parameterized tests
- `[SetUp]`: Runs before each test method

### Example:
```csharp
[Test]
[TestCase(15, 15, 1, Description = "Positive NEWS: +15 → level=15, direction=+1")]
[TestCase(-20, 20, -1, Description = "Negative NEWS: -20 → level=20, direction=-1")]
public void MapNewsTo14Variables_ShouldExtractLevelAndDirection(int inputNews, int expectedLevel, int expectedDirection)
{
    // Test implementation
}
```

## Troubleshooting

### Build Errors
If you see build errors:
1. Ensure cAlgo.API is referenced correctly
2. Check that Newtonsoft.Json is installed
3. Verify .NET target framework matches your setup

### Test Discovery Issues
If tests don't appear in Test Explorer:
1. Rebuild the solution
2. Restart Visual Studio/VS Code
3. Check that NUnit3TestAdapter is installed

### Reference Errors
If you see missing references:
```bash
dotnet restore
```

### cAlgo.API Not Found
The tests require the cAlgo.API from cTrader. Ensure:
1. cTrader is installed
2. cAlgo.API.dll is referenced in the project
3. Or mock the required interfaces with Moq

## Mock Objects

For tests that require cTrader Robot API objects:
```csharp
using Moq;

// Mock Symbol
var mockSymbol = new Mock<Symbol>();
mockSymbol.Setup(s => s.Bid).Returns(1.1234);

// Mock Server
var mockServer = new Mock<Server>();
mockServer.Setup(s => s.Time).Returns(DateTime.Now);
```

## Contributing

When adding new tests:
1. Follow NUnit naming conventions
2. Use descriptive test names (e.g., `MethodName_Scenario_ExpectedBehavior`)
3. Use `[TestCase]` for testing multiple inputs
4. Add XML documentation comments

### Example:
```csharp
/// <summary>
/// Test that MapNewsTo14Variables correctly extracts level and direction
/// </summary>
[Test]
[TestCase(15, 15, 1)]
public void MapNewsTo14Variables_PositiveNews_ExtractsCorrectly(int input, int level, int direction)
{
    // Arrange, Act, Assert
}
```

## License

Tests are part of the MTF_ONER_cBot project.
