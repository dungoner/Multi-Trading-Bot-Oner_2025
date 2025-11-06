# MTF_ONER_V2 cTrader Conversion

## Overview

This directory contains the **cTrader/C# conversion** of the MT5 Multi-Timeframe Trading Bot (MTF_ONER_V2). The conversion is based on the MT5 EA located in `MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5`.

**Conversion Status**: Phase A1 - Core Infrastructure ✅ COMPLETED

---

## Project Structure

```
cTrader/
├── README.md                    # This file
└── Robots/
    └── MTF_ONER_V2/
        └── MTF_ONER_cBot.cs    # Main cBot file (Phase A1 complete)
```

---

## Phase A1 - Core Infrastructure ✅ COMPLETED

### What Was Implemented

#### 1. **Data Structures (C# Classes)**
   - `CSDLRow` - Single row of signal data (6 fields)
   - `EASymbolData` - All EA state for current symbol (116+ fields)

   **MT5 → cTrader Conversions**:
   ```mql5
   // MT5 (MQL5)
   struct CSDLLoveRow {
       double max_loss;
       long timestamp;
       int signal;
       // ...
   };
   ```

   ```csharp
   // cTrader (C#)
   public class CSDLRow {
       public double MaxLoss { get; set; }
       public long Timestamp { get; set; }
       public int Signal { get; set; }
       // ...
   }
   ```

#### 2. **Enumerations**
   - `CSDLSourceEnum` - CSDL data source (File or HTTP)
   - `S2TrendMode` - Trend mode (Follow D1 / Force BUY/SELL)
   - `StoplossMode` - Stoploss strategy (None / Layer1 / Layer2)

#### 3. **Parameters (30+ inputs)**
   - All MT5 input parameters converted to cBot Parameters with attributes
   - Organized into 4 groups: Core Settings, Strategy Config, Risk Protection, Auxiliary

   **Example**:
   ```csharp
   [Parameter("TF_M5", DefaultValue = true, Group = "A. CORE SETTINGS")]
   public bool TF_M5 { get; set; }

   [Parameter("StoplossMode", DefaultValue = StoplossMode.LAYER1_MAXLOSS, Group = "C. RISK PROTECTION")]
   public StoplossMode StoplossMode { get; set; }
   ```

#### 4. **Bot Lifecycle Methods**
   - `OnStart()` - Initialization (replaces MT5's OnInit)
   - `OnTick()` - Main trading logic (replaces MT5's OnTick)
   - `OnStop()` - Cleanup (replaces MT5's OnDeinit)

#### 5. **Initialization System**
   - `InitializeSymbolInfo()` - Symbol name normalization and CSDL path setup
   - `InitializeHttpClient()` - HTTP client setup for API calls
   - `InitializeLabels()` - Position labels (replaces MT5 magic numbers)
   - `InitializeLotSizes()` - Pre-calculate lot sizes for all TF×Strategy combinations
   - `InitializeStoplossThresholds()` - Setup Layer1 thresholds
   - `InitializePositionFlags()` - Initialize position tracking

#### 6. **File Reader (System.IO)**
   - `ReadCSDLFromFile()` - Read local JSON files using System.IO
   - `ParseCSDLJSON()` - Parse JSON array (7 rows) using Newtonsoft.Json

   **Supports all 3 folder sources**:
   - `FOLDER_1` - DataAutoOner (Botspy)
   - `FOLDER_2` - DataAutoOner2 (_Default_Ea)
   - `FOLDER_3` - DataAutoOner3 (_Sync/_Ea)

#### 7. **HTTP API Client (HttpClient)**
   - `ReadCSDLFromAPI()` - Fetch CSDL via HTTP GET request
   - `ReadCSDL()` - Smart routing (HTTP or File with retry logic)

   **Features**:
   - Headers: User-Agent, Host, X-API-Key
   - Timeout: 500ms
   - Retry logic: 2 attempts with 100ms delay
   - URL format: `http://server/api/csdl/{symbol}_LIVE.json`

#### 8. **Utility Methods**
   - `NormalizeSymbolName()` - Remove broker suffixes (LTCUSDC→LTCUSD, XAUUSD.xyz→XAUUSD)
   - `IsTFEnabled()` - Check if timeframe is enabled
   - `SignalToString()` - Convert signal integer to readable string
   - `DebugPrint()` - Debug logging (controlled by DebugMode parameter)

---

## Key Differences: MT5 vs cTrader

### 1. **Position Identification**

| MT5 | cTrader |
|-----|---------|
| Magic Number (integer) | Label (string) |
| `int magic = 101051` | `string label = "LTCUSD_M5_S1"` |

**Reason**: cTrader's Position class uses string labels for easier human-readable identification.

### 2. **Volume Units**

| MT5 | cTrader |
|-----|---------|
| Lots (0.01 = 1,000 units) | Units (10,000 units) |
| `double volume = 0.1` | `double volume = 10000` |

**Conversion**: `units = lots × 100,000`

### 3. **File Access**

| MT5 | cTrader |
|-----|---------|
| `FileOpen()`, `FileReadString()` | `File.ReadAllText()` |
| MQL5 file functions | System.IO namespace |

### 4. **HTTP Requests**

| MT5 | cTrader |
|-----|---------|
| `WebRequest()` function | `HttpClient` class |
| 7-parameter function | Object-oriented API |

### 5. **JSON Parsing**

| MT5 | cTrader |
|-----|---------|
| Manual string parsing | Newtonsoft.Json library |
| `StringFind()`, `StringSubstr()` | `JsonConvert.DeserializeObject()` |

---

## JSON Data Format

The CSDL data is stored as a JSON array with 7 objects (one per timeframe):

```json
[
  {
    "max_loss": 10.0,
    "timestamp": 1234567890,
    "signal": 1,
    "pricediff": 0.0,
    "timediff": 0,
    "news": 15
  },
  // ... 6 more rows for M5, M15, M30, H1, H4, D1
]
```

**Fields**:
- `max_loss` - Maximum loss per 1 lot (used for Layer1 stoploss)
- `timestamp` - Unix timestamp
- `signal` - Trading signal (1=BUY, -1=SELL, 0=NONE)
- `pricediff` - Price difference (unused)
- `timediff` - Time difference (unused)
- `news` - News level (CASCADE ±11-16, used for S1/S3 filters)

---

## Next Steps - Phase A2: Order Management

The next phase will implement the core trading operations:

### Planned Implementations:

1. **OrderSendSafe()**
   - Open orders with retry logic (Error 134/131 → retry with 0.01 lot)
   - Use `ExecuteMarketOrder()` with label tracking
   - Handle volume normalization (lots → units)

2. **CloseOrderSafely()**
   - Close positions with retry logic (Error 146/138 → retry 1x)
   - Use `ClosePosition()` method
   - Smart error handling (no EA stop on errors)

3. **Position Tracking**
   - Use `Positions` collection (replaces OrdersTotal/OrderSelect)
   - Filter by label (replaces magic number filtering)
   - Update `_eaData.PositionFlags[tf, strategy]`

4. **Magic Number → Label Mapping**
   - MT5: `magic = 101051` (M5, S1, Symbol hash)
   - cTrader: `label = "LTCUSD_M5_S1"`

---

## How to Use (Phase A1)

### Prerequisites

1. **cTrader Platform**: Download and install cTrader
2. **Newtonsoft.Json**: Already included in cTrader
3. **FullAccess Rights**: Required for file I/O and HTTP requests

### Installation

1. Open cTrader
2. Go to **Automate** → **cBots**
3. Click **+** → **Import cBot**
4. Select `MTF_ONER_cBot.cs`
5. Compile (should compile without errors)

### Configuration

**For File-Based CSDL**:
- Set `CSDL_Source` to `FOLDER_1`, `FOLDER_2`, or `FOLDER_3`
- Ensure CSDL files exist in MetaTrader common files folder
- Path: `C:\Users\{user}\AppData\Roaming\MetaQuotes\Terminal\Common\Files\DataAutoOner2\`

**For HTTP API CSDL**:
- Set `CSDL_Source` to `HTTP_API`
- Set `HTTP_Server_IP` to your server domain/IP
- Set `HTTP_API_Key` if authentication required
- Ensure server is running and accessible

### Testing Phase A1

Since order management is not yet implemented, you can test:

1. **Initialization**: Check log for successful initialization messages
2. **File Reading**: Enable `DebugMode=true` to see file read attempts
3. **HTTP API**: Check network requests in debug log
4. **Symbol Normalization**: Verify symbol name conversion

**Expected Log Output**:
```
=== MTF_ONER_V2 cBot Starting ===
[INIT] Symbol: LTCUSDC → Normalized: LTCUSD
[INIT] CSDL: C:\...\DataAutoOner2
[INIT] Position labels initialized (7 TF × 3 Strategies = 21 labels)
[INIT] Lot sizes initialized (Fixed: 0.1 lots)
[INIT] Enabled: 5 TF × 3 Strategies = 15 potential orders
=== MTF_ONER_V2 cBot Started Successfully ===
```

---

## Conversion Progress

| Phase | Status | Description |
|-------|--------|-------------|
| **A1** | ✅ **COMPLETED** | Core Infrastructure (data structures, file I/O, HTTP API) |
| **A2** | 🔄 PENDING | Order Management (OrderSendSafe, CloseOrderSafely) |
| **A3** | 🔄 PENDING | Strategy Logic (S1, S2, S3, signal detection) |
| **A4** | 🔄 PENDING | Risk Management (stoploss, takeprofit) |
| **A5** | 🔄 PENDING | Testing & Optimization |

---

## Known Limitations (Phase A1)

1. **No Trading Logic**: OnTick() is empty (will be implemented in Phase A2-A4)
2. **No Position Management**: Cannot open/close positions yet
3. **No Signal Detection**: No logic to detect signal changes
4. **No Strategy Execution**: S1, S2, S3 strategies not implemented

These are **expected** - Phase A1 only focuses on infrastructure.

---

## File Size Comparison

| File | Language | Lines of Code | Status |
|------|----------|---------------|--------|
| MT5 EA | MQL5 | ~3,000 lines | ✅ Production |
| cTrader cBot | C# | ~800 lines | ✅ Phase A1 Complete |

**Note**: Final cBot will be ~1,500-2,000 lines after all phases complete.

---

## Support & Documentation

- **MT5 Source**: `MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5`
- **cTrader Docs**: https://ctrader.com/api
- **Newtonsoft.Json**: https://www.newtonsoft.com/json/help/html/Introduction.htm

---

## Credits

**Original MT5 EA**: _MT5_EAs_MTF ONER_V2
**Conversion**: Claude (Anthropic) + User
**Platform**: cTrader (Spotware Systems)
**Version**: cTrader_V1 (Phase A1)
**Date**: 2025-11-06
