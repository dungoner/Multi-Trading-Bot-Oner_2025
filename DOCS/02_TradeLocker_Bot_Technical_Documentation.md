# TRADELOCKER PYTHON BOT - TECHNICAL DOCUMENTATION
# TÀI LIỆU KỸ THUẬT BOT TRADELOCKER PYTHON

```
═══════════════════════════════════════════════════════════
    TRADELOCKER MTF ONER V1 - MULTI-TIMEFRAME TRADING BOT
    BOT GIAO DỊCH ĐA KHUNG THỜI GIAN CHO TRADELOCKER
═══════════════════════════════════════════════════════════

Version: TL_V1
File: TradeLocker_MTF_ONER.py
Lines: 2,148 lines of Python code
Converted From: MT5 EA V2 (2,995 lines MQL5)
Logic: 100% identical to MT5 EA - FULL FEATURE PARITY

Platform: TradeLocker (Web-based trading platform)
Language: Python 3.8+
Dependencies: tradelocker, requests, dataclasses

Author: Multi-Trading-Bot-Oner Team
Documentation: Claude (Anthropic AI)
Date: 2025-11-07

═══════════════════════════════════════════════════════════
```

---

## MỤC LỤC | TABLE OF CONTENTS

**PHẦN I: TỔNG QUAN HỆ THỐNG**
1. [Tổng Quan Hệ Thống](#1-tổng-quan-hệ-thống)
2. [Kiến Trúc & Integration](#2-kiến-trúc--integration)
3. [Cấu Hình & Input Parameters](#3-cấu-hình--input-parameters)

**PHẦN II: CẤU TRÚC DỮ LIỆU**
4. [Data Structures (Classes)](#4-data-structures-classes)
5. [CSDL File Format](#5-csdl-file-format)
6. [API Integration](#6-api-integration)

**PHẦN III: CORE LOGIC**
7. [Main Loop & Timer](#7-main-loop--timer)
8. [Signal Processing](#8-signal-processing)
9. [Position Management](#9-position-management)

**PHẦN IV: STRATEGIES**
10. [Strategy S1: HOME (Binary)](#10-strategy-s1-home-binary)
11. [Strategy S2: TREND (Follow D1)](#11-strategy-s2-trend-follow-d1)
12. [Strategy S3: NEWS (High Compact)](#12-strategy-s3-news-high-compact)

**PHẦN V: RISK MANAGEMENT**
13. [Stoploss Mechanisms (Layer1 & Layer2)](#13-stoploss-mechanisms-layer1--layer2)
14. [Take Profit & Close Logic](#14-take-profit--close-logic)
15. [Error Handling & Recovery](#15-error-handling--recovery)

**PHẦN VI: ADVANCED TOPICS**
16. [HTTP API Integration](#16-http-api-integration)
17. [Lot Size Conversion (MT5 vs TradeLocker)](#17-lot-size-conversion-mt5-vs-tradelocker)
18. [Real-world Examples](#18-real-world-examples)

**PHẦN VII: DEPLOYMENT**
19. [Installation & Setup](#19-installation--setup)
20. [Troubleshooting](#20-troubleshooting)
21. [Performance & Monitoring](#21-performance--monitoring)

**PHẦN VIII: APPENDIX**
22. [FAQ](#22-faq)
23. [Credits & Acknowledgments](#23-credits--acknowledgments)
24. [Conclusion](#24-conclusion)

---

═══════════════════════════════════════════════════════════
 1. TỔNG QUAN HỆ THỐNG
═══════════════════════════════════════════════════════════

## 1.1 Vai Trò & Mục Đích

**TradeLocker Python Bot** là một **Expert Advisor (EA) tự động giao dịch** được viết bằng Python, chạy trên nền tảng **TradeLocker** (web-based trading platform).

### Vai Trò Trong Hệ Thống

```
┌──────────────────────────────────────────────────────┐
│         WALLSTREET BOT (MT4/MT5 Indicator)           │
│   Detect crossovers → Set GlobalVariables            │
└──────────────────┬───────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────┐
│              SPY BOT (MT4/MT5 Indicator)             │
│   Read GlobalVariables → Detect CASCADE              │
│   → Write CSDL1.json (10 columns × 7 TF)             │
└──────────────────┬───────────────────────────────────┘
                   ↓
      ┌────────────┴────────────┬────────────────────┐
      ↓                         ↓                    ↓
┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ EA MT4       │  │ EA MT5           │  │ TRADELOCKER BOT      │
│ (MQL4)       │  │ (MQL5)           │  │ (PYTHON) ← YOU ARE HERE
├──────────────┤  ├──────────────────┤  ├──────────────────────┤
│ Read CSDL1   │  │ Read CSDL1       │  │ Read CSDL1 via:      │
│ Open/Close   │  │ Open/Close       │  │ - Local file OR      │
│ MT4 platform │  │ MT5 platform     │  │ - HTTP API           │
│              │  │                  │  │ Open/Close via:      │
│              │  │                  │  │ - TradeLocker API    │
└──────────────┘  └──────────────────┘  └──────────────────────┘
                                         - Web-based platform
                                         - No MT4/MT5 needed!
```

### Tại Sao Cần TradeLocker Bot?

**Vấn đề:**
- MT4/MT5 chỉ chạy trên Windows (hoặc Wine trên Linux)
- Cần VPS để chạy 24/7
- License restrictions (một số brokers không hỗ trợ EA)
- Desktop app phải mở liên tục

**Giải pháp: TradeLocker Bot**
```
✅ Cross-platform: Chạy trên Linux/Windows/Mac
✅ Cloud-based: TradeLocker là web platform, không cần desktop
✅ API-driven: Giao dịch qua HTTP API (REST)
✅ Flexible deployment: Chạy trên bất kỳ server nào có Python
✅ Same logic: 100% giống MT5 EA (converted code)
```

### Mục Đích Chính

1. **Clone MT5 EA logic sang TradeLocker platform**
   - Giữ nguyên 100% trading logic
   - Cùng 3 strategies (S1, S2, S3)
   - Cùng 7 timeframes (M1-D1)
   - Cùng risk management (Layer1, Layer2)

2. **Read CSDL data từ SPY Bot**
   - Đọc CSDL1.json (local file hoặc HTTP API)
   - Parse 10 columns × 7 TF
   - Extract signals, news, max_loss

3. **Execute trades trên TradeLocker**
   - API calls qua `tradelocker` library
   - Open/Close positions
   - Manage SL/TP
   - Monitor account balance

4. **Tự động hoàn toàn (24/7)**
   - Chạy trong background (systemd service hoặc screen)
   - Auto-reconnect khi mất kết nối
   - Error recovery
   - Health monitoring

---

## 1.2 Sơ Đồ Luồng Tổng Quát

### HIGH-LEVEL FLOW

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: INITIALIZATION                                 │
├─────────────────────────────────────────────────────────┤
│ 1. Load config.json                                     │
│ 2. Connect to TradeLocker API                           │
│ 3. Get account info (ID, balance, leverage)             │
│ 4. Detect symbol (XAUUSD, EURUSD, etc.)                 │
│ 5. Initialize data structures (EASymbolData)            │
│ 6. Calculate magic numbers (21 = 7 TF × 3 strategies)   │
│ 7. Pre-calculate lot sizes (21 values)                  │
│ 8. Restore open positions from TradeLocker              │
│ 9. Start timer thread (1 second interval)               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: MAIN LOOP (OnTimer every 1 second)            │
├─────────────────────────────────────────────────────────┤
│ CYCLE 1: Read CSDL Data                                 │
│   - HTTP API request: GET /api/csdl/XAUUSD.json         │
│   - Or read local file: CSDL/XAUUSD.json                │
│   - Parse JSON: 7 rows × 10 columns                     │
│   - Extract: signal, price_diff, news, max_loss         │
│                                                          │
│ CYCLE 2: Process Signals (7 TF loop)                    │
│   FOR each timeframe (M1, M5, M15, M30, H1, H4, D1):    │
│     - Check TF enabled (config.TF_M1, TF_M5, ...)       │
│     - Detect new signal (compare with old)              │
│     - Check signal conditions (NEWS filter, etc.)       │
│     - Execute strategies:                               │
│       * S1: HOME (Binary with NEWS filter)              │
│       * S2: TREND (Follow D1 direction)                 │
│       * S3: NEWS (High cascade only)                    │
│                                                          │
│ CYCLE 3: Manage Positions (21 orders)                   │
│   FOR each position (7 TF × 3 strategies):              │
│     - Check stoploss (Layer1: CSDL max_loss)            │
│     - Check stoploss (Layer2: margin-based)             │
│     - Check close conditions (M1 cross, own TF, TP)     │
│     - Close if needed via TradeLocker API               │
│                                                          │
│ CYCLE 4: Health Check & Monitoring                      │
│   - Check connection alive                              │
│   - Log statistics (total orders, PnL, etc.)            │
│   - Handle errors & reconnect if needed                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: SHUTDOWN (on SIGINT/SIGTERM)                  │
├─────────────────────────────────────────────────────────┤
│ 1. Stop timer thread gracefully                         │
│ 2. Close all open positions (if configured)             │
│ 3. Disconnect from TradeLocker API                      │
│ 4. Save state (optional)                                │
│ 5. Log final summary                                    │
│ 6. Exit                                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 1.3 Output & Effects

Bot KHÔNG ghi file output, chỉ **THỰC HIỆN LỆNH GIAO DỊCH** trên TradeLocker:

### Hành Động Của Bot

```
┌────────────────────────────────────────────────┐
│ ACTION 1: OPEN POSITION                        │
├────────────────────────────────────────────────┤
│ API Call: POST /v1/trade/orders                │
│ Request: {                                     │
│   "instrument_id": 123,                        │
│   "side": "buy",                               │
│   "qty": 1000,                                 │
│   "type": "market",                            │
│   "stopLoss": 2648.50,                         │
│   "takeProfit": null                           │
│ }                                              │
│                                                │
│ Response: {                                    │
│   "orderId": "abc123",                         │
│   "status": "filled",                          │
│   "fillPrice": 2650.00                         │
│ }                                              │
│                                                │
│ Effect:                                        │
│ → Position opened on TradeLocker account       │
│ → Margin deducted                              │
│ → Position visible in web UI                   │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ ACTION 2: CLOSE POSITION                       │
├────────────────────────────────────────────────┤
│ API Call: DELETE /v1/trade/positions/{id}      │
│                                                │
│ Effect:                                        │
│ → Position closed on TradeLocker               │
│ → PnL realized                                 │
│ → Balance updated                              │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ ACTION 3: MODIFY STOPLOSS/TAKEPROFIT           │
├────────────────────────────────────────────────┤
│ API Call: PATCH /v1/trade/positions/{id}       │
│ Request: {                                     │
│   "stopLoss": 2649.00,                         │
│   "takeProfit": 2655.00                        │
│ }                                              │
│                                                │
│ Effect:                                        │
│ → SL/TP updated on existing position           │
└────────────────────────────────────────────────┘
```

### Log Output (Console & File)

```
2024-01-16 10:00:01 [INFO] [INIT] TradeLocker Bot Starting...
2024-01-16 10:00:02 [INFO] [INIT] Connecting to TradeLocker (DEMO)...
2024-01-16 10:00:03 [INFO] [INIT] Connected! Account ID: 12345
2024-01-16 10:00:03 [INFO] [INIT] Balance: $10,000.00 | Leverage: 1:100
2024-01-16 10:00:03 [INFO] [INIT] Symbol: XAUUSD | Instrument ID: 456
2024-01-16 10:00:03 [INFO] [INIT] Magic numbers generated: 21 strategies
2024-01-16 10:00:04 [INFO] [INIT] Restored 3 open positions
2024-01-16 10:00:04 [INFO] [INIT] Bot initialized successfully ✓
2024-01-16 10:00:04 [INFO] [TIMER] Starting main loop (1s interval)...
2024-01-16 10:00:05 [INFO] [CSDL] Reading via HTTP: http://api.example.com/XAUUSD.json
2024-01-16 10:00:05 [INFO] [CSDL] Parsed: 7 TF, Signal M5=BUY, NEWS=+30
2024-01-16 10:00:06 [INFO] [S1] M5 BUY signal detected (NEWS=+30 >= 20)
2024-01-16 10:00:06 [INFO] [S1] Opening BUY position: Lot=0.1, SL=2648.50
2024-01-16 10:00:07 [INFO] [TL_API] Order placed: ID=abc123, Fill=2650.00
2024-01-16 10:00:07 [INFO] [S1] Position opened ✓ Ticket=abc123
...
2024-01-16 10:05:30 [INFO] [CLOSE] M5_S1 position closed: PnL=+$45.50
2024-01-16 10:05:30 [INFO] [STATS] Total trades: 15 | Win: 12 | Loss: 3 | Win rate: 80%
```

---

═══════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════
 2. KIẾN TRÚC & INTEGRATION
═══════════════════════════════════════════════════════════

## 2.1 Architecture Overview

**TradeLocker Bot** là một **hybrid architecture** kết hợp:
- **Event-driven**: Timer triggers mỗi 1 giây
- **API-based**: Giao tiếp với TradeLocker qua REST API
- **Data-driven**: Đọc CSDL signals từ SPY Bot
- **State-machine**: Quản lý positions với flags

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│              TRADELOCKER PYTHON BOT                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. CONFIG MODULE (config.json)                   │  │
│  │    - Load user settings                          │  │
│  │    - Validate parameters                         │  │
│  │    - 30+ input params                            │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 2. DATA STRUCTURES (dataclasses)                 │  │
│  │    - CSDLLoveRow: 6 columns × 7 TF              │  │
│  │    - EASymbolData: 116 variables                 │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 3. TRADELOCKER API CLIENT (TLAPI)                │  │
│  │    - Connection management                       │  │
│  │    - Instrument lookup                           │  │
│  │    - Order placement                             │  │
│  │    - Position management                         │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 4. CSDL READER (File or HTTP)                    │  │
│  │    - Read CSDL1.json (local or remote)           │  │
│  │    - Parse JSON (7 rows × 10 cols)               │  │
│  │    - Extract signals, news, max_loss             │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 5. SIGNAL PROCESSOR                              │  │
│  │    - Detect new signals (compare old vs new)     │  │
│  │    - Check conditions (NEWS filter, direction)   │  │
│  │    - Trigger strategies (S1, S2, S3)             │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 6. STRATEGY EXECUTOR                             │  │
│  │    - S1: HOME (Binary with NEWS)                 │  │
│  │    - S2: TREND (Follow D1)                       │  │
│  │    - S3: NEWS (High cascade)                     │  │
│  │    - Calculate lot size, SL, TP                  │  │
│  │    - Open positions via API                      │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 7. POSITION MANAGER                              │  │
│  │    - Track 21 positions (7 TF × 3 strategies)    │  │
│  │    - Check stoploss (Layer1, Layer2)             │  │
│  │    - Check close conditions (M1, own TF, TP)     │  │
│  │    - Close via API                               │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 8. MAIN TIMER LOOP (1 second interval)           │  │
│  │    - Read CSDL → Process → Execute → Manage      │  │
│  │    - Health check                                │  │
│  │    - Error recovery                              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
             ↓                              ↓
┌─────────────────────┐         ┌──────────────────────┐
│ TRADELOCKER SERVER  │         │ CSDL DATA SOURCE     │
│ (API endpoints)     │         │ (SPY Bot output)     │
│ - Orders            │         │ - Local file         │
│ - Positions         │         │ - HTTP API           │
│ - Account info      │         │ - JSON format        │
└─────────────────────┘         └──────────────────────┘
```

---

## 2.2 Integration With Other Bots

### Data Flow Chain

```
STEP 1: WallStreet Bot (MT4/MT5 Indicator)
├─ Detect MA crossovers on 7 TF
├─ Set GlobalVariables:
│   XAUUSD_M1_SignalType1 = 1 (BUY)
│   XAUUSD_M1_LastSignalTime = 1705401600
│   XAUUSD_M5_SignalType1 = 1 (BUY)
│   ...
└─ Output: GlobalVariables (in-memory MT4/MT5)

STEP 2: SPY Bot (MT4/MT5 Indicator)
├─ Read GlobalVariables from WallStreet
├─ Detect CASCADE patterns (L1-L7)
├─ Calculate NEWS scores (±10 to ±70)
├─ Write CSDL1.json:
│   [
│     [1, 2650.0, 0, 1705401600, 2.5, 120, 30, 1, 0, -4.2],  // M1
│     [1, 2649.5, 1705401600, 1705401300, 0, 0, 30, 0, 0, -4.2],  // M5
│     ...
│   ]
└─ Output: CSDL1.json file (local or uploaded to HTTP server)

STEP 3: TradeLocker Bot (Python) ← WE ARE HERE
├─ Read CSDL1.json:
│   Option A: Local file (same VPS as MT4/MT5)
│   Option B: HTTP API (remote server)
│
├─ Parse JSON → Extract data:
│   Row 0 (M1): signal=1, news=30, max_loss=-4.2
│   Row 1 (M5): signal=1, news=30, max_loss=-4.2
│   ...
│
├─ Process signals:
│   M5 signal: BUY, NEWS=30 >= MinNewsLevelS1(2) ✓
│   → Trigger S1 strategy
│
├─ Execute trade:
│   API call: POST /v1/trade/orders
│   {
│     "instrument_id": 456,
│     "side": "buy",
│     "qty": 1000,  // Converted from lot 0.1
│     "type": "market",
│     "stopLoss": 2648.50
│   }
│
└─ Output: Position opened on TradeLocker account
```

### Timeline Example

```
10:00:00.100  WallStreet detect M5 cross → GlobalVariable
10:00:01.500  SPY Bot read GlobalVariable → Process
10:00:01.600  SPY Bot write CSDL1.json
              File: [1, 2649.5, ..., 30, ...]

10:00:02.000  TradeLocker Bot OnTimer() tick
10:00:02.100  Read CSDL1.json (HTTP or file)
10:00:02.200  Parse JSON → signal=1, news=30
10:00:02.300  Check S1 conditions:
              - TF_M5 enabled? YES ✓
              - Signal new? YES (old=0, new=1) ✓
              - NEWS >= 2? YES (30 >= 2) ✓
              - Direction match? YES ✓
              → OPEN BUY

10:00:02.400  Calculate lot size:
              - FixedLotSize = 0.1 lot (MT5 style)
              - Convert to TradeLocker qty:
                qty = 0.1 × 100 × 2650 = 26,500
              - Round: 26,500 → 26,500

10:00:02.500  API call: POST /v1/trade/orders
10:00:02.700  Response: orderId = "abc123"
10:00:02.800  Save position:
              - position_flags[1][0] = 1  // M5, S1
              - position_tickets[1][0] = "abc123"

10:00:02.900  Log: "[S1] M5 BUY opened ✓ Ticket=abc123"

Total latency: 0.8 seconds (from WallStreet cross to position opened)
```

---

## 2.3 Key Differences vs MT5 EA

### Similarities (100% Logic Parity)

| Feature | MT5 EA | TradeLocker Bot | Status |
|---------|--------|-----------------|--------|
| 7 Timeframes | M1-D1 | M1-D1 | ✅ Same |
| 3 Strategies | S1, S2, S3 | S1, S2, S3 | ✅ Same |
| 21 Orders | 7×3 | 7×3 | ✅ Same |
| NEWS Filter | MinNewsLevel | MinNewsLevel | ✅ Same |
| Close Modes | M1 / Own TF | M1 / Own TF | ✅ Same |
| Stoploss | Layer1, Layer2 | Layer1, Layer2 | ✅ Same |
| Take Profit | Fixed USD / None | Fixed USD / None | ✅ Same |
| CSDL Format | 10 columns | 10 columns | ✅ Same |
| Magic Numbers | 100001-100021 | 100001-100021 | ✅ Same |
| Signal Logic | signal != 0 && time > old | signal != 0 && time > old | ✅ Same |

### Differences (Platform Specific)

| Feature | MT5 EA | TradeLocker Bot | Reason |
|---------|--------|-----------------|--------|
| **Language** | MQL5 | Python 3 | Platform requirement |
| **API** | MT5 Terminal API | TradeLocker REST API | Different platforms |
| **Lot Size Unit** | 1.0 = 100 oz (XAUUSD) | qty = units | Different convention |
| **Position ID** | Ticket (ulong) | orderId (string UUID) | API difference |
| **File I/O** | FileOpen/FileClose | open()/read() | Language difference |
| **Timer** | OnTimer() callback | threading.Timer | Language difference |
| **Connection** | Always connected | HTTP requests | Stateless API |
| **CSDL Source** | Local file only | Local OR HTTP API | Flexible |
| **Deployment** | Windows desktop | Linux server | Cross-platform |
| **Dependencies** | MT5 Terminal | Python + tradelocker lib | Different stack |

### Lot Size Conversion (CRITICAL!)

```
MT5 EA lot calculation:
- 1.0 lot = 100 oz (for XAUUSD)
- 0.1 lot = 10 oz
- Margin = lot × contract_size × price / leverage
- Example: 0.1 lot @ 2650 = 10 × 2650 / 100 = $265 margin

TradeLocker qty calculation:
- qty = number of UNITS
- For XAUUSD: 1 unit = 1 troy ounce
- qty = 1000 means 1000 oz = 10 lots (MT5 style)
- Margin = qty × price / leverage
- Example: 1000 qty @ 2650 = 1000 × 2650 / 100 = $26,500 margin

Conversion formula (implemented in bot):
qty = MT5_lot × 100 × price

Example:
- MT5 lot = 0.1
- Price = 2650
- qty = 0.1 × 100 × 2650 = 26,500

WHY multiply by price?
- TradeLocker qty is VALUE-based, not LOT-based
- 0.1 lot @ 2650 = $265 position value
- But qty needs to be in UNITS (oz)
- So: 0.1 lot = 10 oz, but API expects VALUE
- Hence: qty = lot × 100 × price
```

**⚠️ CRITICAL NOTE:**

Nếu conversion sai → Lot size sai → Margin sai → Account blown!

Bot đã implement đúng công thức theo test results từ TradeLocker API.

---


═══════════════════════════════════════════════════════════
 3. CẤU HÌNH & INPUT PARAMETERS
═══════════════════════════════════════════════════════════

## 3.1 Config File Structure

Bot đọc cấu hình từ file `config.json` thay vì hardcode trong code.

**File Location:**
```
TradeLocker/
├─ TradeLocker_MTF_ONER.py
├─ config.json  ← Configuration file
├─ requirements.txt
└─ README.md
```

**config.json Format:**

```json
{
  "TF_M1": false,
  "TF_M5": true,
  "TF_M15": true,
  "TF_M30": true,
  "TF_H1": true,
  "TF_H4": true,
  "TF_D1": false,

  "S1_HOME": true,
  "S2_TREND": true,
  "S3_NEWS": true,

  "S1_CloseByM1": true,
  "S2_CloseByM1": false,

  "FixedLotSize": 0.1,
  "MaxLoss_Fallback": -1000.0,

  "CSDL_Source": "HTTP_API",
  "HTTP_Server_IP": "dungalading.duckdns.org",
  "HTTP_API_Key": "",
  "EnableSymbolNormalization": false,

  "S1_UseNewsFilter": true,
  "MinNewsLevelS1": 2,
  "S1_RequireNewsDirection": true,

  "S2_TrendMode": 0,

  "MinNewsLevelS3": 20,
  "EnableBonusNews": true,
  "BonusOrderCount": 1,
  "MinNewsLevelBonus": 2,
  "BonusLotMultiplier": 1.2,

  "StoplossMode": 1,
  "Layer2_Divisor": 5.0,

  "TakeProfitMode": 1,
  "FixedTPUSD": 100.0,

  "TL_Environment": "demo",
  "TL_Username": "your_username",
  "TL_Password": "your_password",
  "TL_Server": "https://demo.tradelocker.com",

  "Symbol": "XAUUSD",

  "DebugMode": false,
  "EnableDashboard": false,
  "TimerIntervalSeconds": 1,

  "EnableTrailingStop": false,
  "TrailingStopUSD": 0.0,
  "TrailingStepUSD": 0.0
}
```

---

## 3.2 Parameter Categories

Tất cả 30+ parameters được chia thành 6 nhóm:

### A. CORE SETTINGS (14 params)

#### A.1 Timeframe Toggles (7 params)

```python
TF_M1: bool = False   # M1 Signal (usually disabled, too noisy)
TF_M5: bool = True    # M5 (recommended for most strategies)
TF_M15: bool = True   # M15
TF_M30: bool = True   # M30
TF_H1: bool = True    # H1
TF_H4: bool = True    # H4
TF_D1: bool = False   # D1 (usually disabled, too slow)
```

**Purpose:** Cho phép bật/tắt từng timeframe riêng biệt.

**Examples:**

```
Scenario 1: Conservative (only major TF)
TF_M1=False, TF_M5=True, TF_M15=False, TF_M30=True, TF_H1=True, TF_H4=True, TF_D1=True
→ 4 TF enabled: M5, M30, H1, H4, D1
→ Max 12 orders (4 TF × 3 strategies)

Scenario 2: Aggressive (all TF except M1)
TF_M1=False, TF_M5=True, TF_M15=True, TF_M30=True, TF_H1=True, TF_H4=True, TF_D1=True
→ 6 TF enabled: M5-D1
→ Max 18 orders (6 TF × 3 strategies)

Scenario 3: Scalping (fast TF only)
TF_M1=True, TF_M5=True, TF_M15=True, TF_M30=False, TF_H1=False, TF_H4=False, TF_D1=False
→ 3 TF enabled: M1, M5, M15
→ Max 9 orders (3 TF × 3 strategies)
```

#### A.2 Strategy Toggles (3 params)

```python
S1_HOME: bool = True    # S1: Binary (most common)
S2_TREND: bool = True   # S2: Trend following
S3_NEWS: bool = True    # S3: NEWS-based (high cascade only)
```

**Purpose:** Bật/tắt từng strategy riêng biệt.

**Combination Examples:**

```
Scenario 1: S1 only (safest)
S1_HOME=True, S2_TREND=False, S3_NEWS=False
→ 1 strategy × 7 TF = max 7 orders
→ Low risk, stable

Scenario 2: S1 + S3 (balanced)
S1_HOME=True, S2_TREND=False, S3_NEWS=True
→ 2 strategies × 7 TF = max 14 orders
→ Medium risk, S3 for high opportunities

Scenario 3: All strategies (aggressive)
S1_HOME=True, S2_TREND=True, S3_NEWS=True
→ 3 strategies × 7 TF = max 21 orders
→ High risk, max profit potential
```

#### A.3 Close Mode Configuration (2 params)

```python
S1_CloseByM1: bool = True    # S1: Close by M1 (fast exit)
S2_CloseByM1: bool = False   # S2: Close by own TF (slow exit)
```

**Purpose:** Quyết định signal nào được dùng để đóng lệnh.

**Logic:**

```
CloseByM1 = True:
├─ Close when M1 signal reverses
├─ Example: M5 BUY opened, M1 SELL appears → Close M5 BUY
├─ Faster exit (M1 is quickest TF)
└─ Suitable for: S1 (fast in-out), S3 (news-based)

CloseByM1 = False:
├─ Close when OWN TF signal reverses
├─ Example: M5 BUY opened, M5 SELL appears → Close M5 BUY
├─ Slower exit (wait for own TF to reverse)
└─ Suitable for: S2 (trend following, hold longer)
```

**Examples:**

```
M5 BUY opened @ 10:00 by S1 strategy
S1_CloseByM1 = True

Timeline:
10:00:00  M5 BUY opened (S1)
10:01:30  M1 SELL signal appears
10:01:31  Bot checks: S1_CloseByM1=True → Close M5 BUY
10:01:32  API call: Close position
Result: Position held for 1.5 minutes

═══════════════════════════════════════════════════════════

M5 BUY opened @ 10:00 by S2 strategy
S2_CloseByM1 = False

Timeline:
10:00:00  M5 BUY opened (S2)
10:01:30  M1 SELL signal appears
10:01:31  Bot checks: S2_CloseByM1=False → IGNORE M1, wait for M5
10:05:00  M5 SELL signal appears
10:05:01  Bot checks: Own TF reversed → Close M5 BUY
10:05:02  API call: Close position
Result: Position held for 5 minutes (longer)
```

#### A.4 Risk Management (2 params)

```python
FixedLotSize: float = 0.1
MaxLoss_Fallback: float = -1000.0
```

**FixedLotSize:**
- Lot size cố định cho TẤT CẢ lệnh
- Unit: MT5 lot style (0.1 = 10 oz for XAUUSD)
- Will be converted to TradeLocker qty
- Range: 0.01 - 10.0 (recommend 0.01 - 1.0)

**MaxLoss_Fallback:**
- Max loss fallback nếu CSDL fail
- Unit: USD
- Used when CSDL max_loss = 0 (invalid)
- Example: -1000 means stoploss at -$1000 loss

**Examples:**

```
Account balance: $10,000
FixedLotSize: 0.1
XAUUSD price: 2650

Lot calculation:
- MT5 lot: 0.1
- TradeLocker qty: 0.1 × 100 × 2650 = 26,500
- Margin (1:100): 26,500 / 100 = $265
- Position value: $265

Risk per trade:
- If stoploss: -$10 USD (example from CSDL)
- Risk %: 10 / 10,000 = 0.1% per trade ✓ Safe

If 21 orders all opened:
- Total margin: 265 × 21 = $5,565
- Margin usage: 5,565 / 10,000 = 55.65%
- Still safe (< 80% margin limit)
```

#### A.5 Data Source (1 param)

```python
CSDL_Source: str = "HTTP_API"
```

**Options:**
- `"FOLDER_1"`: Local file from CSDL/ folder
- `"FOLDER_2"`: Alternative local folder
- `"FOLDER_3"`: Third local folder option
- `"HTTP_API"`: Remote HTTP server (RECOMMENDED)

**Why HTTP_API is better:**

```
Local File:
├─ Bot và MT4/MT5 phải cùng VPS
├─ File I/O overhead
├─ File lock conflicts possible
└─ Limited scalability

HTTP API:
├─ Bot có thể ở server khác
├─ Cached responses (faster)
├─ No file lock issues
├─ Easy to scale (multiple bots → 1 API server)
└─ RECOMMENDED ✓
```

#### A.6 HTTP API Settings (3 params)

```python
HTTP_Server_IP: str = "dungalading.duckdns.org"
HTTP_API_Key: str = ""
EnableSymbolNormalization: bool = False
```

**HTTP_Server_IP:**
- Domain hoặc IP của HTTP server
- Example: `"api.example.com"` hoặc `"192.168.1.100"`
- Bot sẽ call: `http://{server}/api/csdl/XAUUSD.json`

**HTTP_API_Key:**
- API key for authentication (optional)
- Nếu empty: no authentication
- Nếu có value: gửi trong header `X-API-Key`

**EnableSymbolNormalization:**
- `True`: Normalize symbol name (XAUUSD → XAU/USD)
- `False`: Use raw symbol name
- Usually `False` for TradeLocker

**HTTP Request Example:**

```python
# With API key
GET http://dungalading.duckdns.org/api/csdl/XAUUSD.json
Headers:
  X-API-Key: your_secret_key_here
  
Response:
{
  "symbol": "XAUUSD",
  "data": [
    [1, 2650.0, 0, 1705401600, 2.5, 120, 30, 1, 0, -4.2],
    [1, 2649.5, 1705401600, 1705401300, 0, 0, 30, 0, 0, -4.2],
    ...
  ]
}
```

---

### B. STRATEGY CONFIG (8 params)

#### B.1 S1 NEWS Filter (3 params)

```python
S1_UseNewsFilter: bool = True
MinNewsLevelS1: int = 2
S1_RequireNewsDirection: bool = True
```

**S1_UseNewsFilter:**
- `True`: S1 check NEWS score trước khi open
- `False`: S1 open ngay khi có signal (ignore NEWS)
- RECOMMEND: `True` (safer)

**MinNewsLevelS1:**
- Min NEWS score cần thiết
- Range: 2-70 (higher = stricter)
- Common values:
  - `2`: Very loose (L2 cascade = ±20 score)
  - `5`: Moderate (L5 cascade = ±50 score)
  - `7`: Strict (L7 cascade = ±70 score)

**S1_RequireNewsDirection:**
- `True`: NEWS direction phải match signal direction
- `False`: Chỉ cần NEWS score đủ, không cần match direction
- Example:
  - Signal: BUY (+1)
  - NEWS: +30 (BUY cascade)
  - RequireDirection=True: ✓ PASS (match)
  - Signal: BUY (+1)
  - NEWS: -30 (SELL cascade)
  - RequireDirection=True: ✗ FAIL (not match)
  - RequireDirection=False: ✓ PASS (score đủ, ignore direction)

**Decision Tree:**

```
S1 Strategy signal processing:

1. Check TF enabled?
   ├─ NO → Skip
   └─ YES → Continue

2. Check S1_HOME enabled?
   ├─ NO → Skip S1
   └─ YES → Continue

3. Check signal new?
   ├─ NO → Skip (already processed)
   └─ YES → Continue

4. Check S1_UseNewsFilter?
   ├─ NO → OPEN position (skip NEWS check)
   └─ YES → Continue to NEWS check

5. Check NEWS >= MinNewsLevelS1?
   ├─ NO → Skip (NEWS too low)
   └─ YES → Continue

6. Check S1_RequireNewsDirection?
   ├─ NO → OPEN position
   └─ YES → Continue to direction check

7. Check NEWS direction == signal direction?
   ├─ NO → Skip (direction mismatch)
   └─ YES → OPEN position ✓
```

**Examples:**

```
Example 1: Loose filter
S1_UseNewsFilter = True
MinNewsLevelS1 = 2
S1_RequireNewsDirection = False

M5 signal: BUY (+1)
M5 NEWS: +20 (L2 cascade)

Check:
├─ UseNewsFilter? YES → Check NEWS
├─ NEWS=20 >= MinLevel=2? YES (20 >= 2 means 20/10=2, L2) ✓
├─ RequireDirection? NO → Skip direction check
└─ RESULT: OPEN BUY ✓

Example 2: Strict filter
S1_UseNewsFilter = True
MinNewsLevelS1 = 5
S1_RequireNewsDirection = True

M5 signal: BUY (+1)
M5 NEWS: +20 (L2 cascade)

Check:
├─ UseNewsFilter? YES → Check NEWS
├─ NEWS=20 >= MinLevel=5? NO (20/10=2 < 5) ✗
└─ RESULT: SKIP (NEWS too low)

Example 3: Direction mismatch
S1_UseNewsFilter = True
MinNewsLevelS1 = 2
S1_RequireNewsDirection = True

M5 signal: BUY (+1)
M5 NEWS: -30 (L3 SELL cascade)

Check:
├─ UseNewsFilter? YES → Check NEWS
├─ NEWS=-30, abs=30 >= MinLevel=2? YES (30/10=3 >= 2) ✓
├─ RequireDirection? YES → Check direction
├─ Signal=+1 (BUY), NEWS=-30 (SELL) → Mismatch ✗
└─ RESULT: SKIP (direction mismatch)
```

#### B.2 S2 TREND Mode (1 param)

```python
S2_TrendMode: int = 0
```

**Options:**
- `0`: S2_FOLLOW_D1 (auto follow D1 signal)
- `1`: S2_FORCE_BUY (always BUY regardless D1)
- `-1`: S2_FORCE_SELL (always SELL regardless D1)

**Purpose:** S2 strategy theo trend của D1, hoặc force 1 direction.

**Logic:**

```
S2_TrendMode = 0 (FOLLOW_D1):
├─ Read D1 signal from CSDL
├─ If D1 = +1 (BUY): S2 chỉ mở BUY trên các TF
├─ If D1 = -1 (SELL): S2 chỉ mở SELL trên các TF
└─ If D1 = 0 (NONE): S2 không mở lệnh nào

S2_TrendMode = 1 (FORCE_BUY):
├─ Ignore D1 signal
├─ S2 LUÔN mở BUY khi có signal
└─ Use case: Bullish bias, long-only strategy

S2_TrendMode = -1 (FORCE_SELL):
├─ Ignore D1 signal
├─ S2 LUÔN mở SELL khi có signal
└─ Use case: Bearish bias, short-only strategy
```

**Examples:**

```
Example 1: Follow D1 (normal)
S2_TrendMode = 0
D1 signal: BUY (+1)

M5 signal: BUY (+1)
→ S2 check: D1=BUY, M5=BUY → Match ✓ → OPEN M5 BUY

M15 signal: SELL (-1)
→ S2 check: D1=BUY, M15=SELL → Not match ✗ → SKIP

═══════════════════════════════════════════════════════════

Example 2: Force BUY (bullish bias)
S2_TrendMode = 1
D1 signal: SELL (-1)

M5 signal: BUY (+1)
→ S2 check: Force BUY mode → OPEN M5 BUY ✓

M15 signal: SELL (-1)
→ S2 check: Force BUY mode, but M15=SELL → SKIP ✗
  (chỉ mở BUY, không mở SELL)

═══════════════════════════════════════════════════════════

Example 3: Force SELL (bearish bias)
S2_TrendMode = -1
D1 signal: BUY (+1)

M5 signal: SELL (-1)
→ S2 check: Force SELL mode → OPEN M5 SELL ✓

M15 signal: BUY (+1)
→ S2 check: Force SELL mode, but M15=BUY → SKIP ✗
  (chỉ mở SELL, không mở BUY)
```

#### B.3 S3 NEWS Configuration (5 params)

```python
MinNewsLevelS3: int = 20
EnableBonusNews: bool = True
BonusOrderCount: int = 1
MinNewsLevelBonus: int = 2
BonusLotMultiplier: float = 1.2
```

**MinNewsLevelS3:**
- Min NEWS score cho S3 strategy
- Range: 2-70
- Common: 20 (L2 cascade minimum)
- S3 chỉ trade khi có CASCADE mạnh

**EnableBonusNews:**
- `True`: Enable bonus orders khi NEWS cao
- `False`: Disable bonus (chỉ mở 1 order mỗi TF)

**BonusOrderCount:**
- Số lượng bonus orders mỗi TF
- Range: 1-5
- Example: `3` means 3 bonus orders per TF (total 4 orders: 1 main + 3 bonus)

**MinNewsLevelBonus:**
- Min NEWS score để trigger bonus
- Usually lower than MinNewsLevelS3
- Example: MinNewsLevelS3=20, MinNewsLevelBonus=2
  - NEWS=30: Trigger S3 + Bonus
  - NEWS=20: Trigger S3 only (no bonus)
  - NEWS=10: Skip S3 (too low)

**BonusLotMultiplier:**
- Lot size multiplier cho bonus orders
- Range: 1.0-10.0
- Example: Main lot=0.1, Multiplier=1.2 → Bonus lot=0.12

**Bonus Logic:**

```
S3 Strategy processing:

1. Check NEWS >= MinNewsLevelS3?
   ├─ NO → Skip S3
   └─ YES → Open main S3 order

2. Check EnableBonusNews?
   ├─ NO → Done (only main order)
   └─ YES → Continue bonus check

3. Check NEWS >= MinNewsLevelBonus?
   ├─ NO → Done (only main order)
   └─ YES → Open bonus orders

4. Open BonusOrderCount bonus orders:
   - Lot size: FixedLotSize × BonusLotMultiplier
   - Same direction as main order
   - Same SL/TP
```

**Examples:**

```
Example 1: S3 with bonus
MinNewsLevelS3 = 20
EnableBonusNews = True
BonusOrderCount = 2
MinNewsLevelBonus = 2
BonusLotMultiplier = 1.5
FixedLotSize = 0.1

M5 signal: BUY (+1)
M5 NEWS: +50 (L5 cascade)

Processing:
├─ NEWS=50 >= MinNewsLevelS3=20? YES ✓
├─ Open main S3 order: Lot=0.1
├─ EnableBonusNews? YES
├─ NEWS=50 >= MinNewsLevelBonus=2? YES ✓
├─ Open bonus orders:
│   Bonus 1: Lot=0.1×1.5=0.15
│   Bonus 2: Lot=0.1×1.5=0.15
└─ Total: 3 orders (1 main + 2 bonus)

Total lot: 0.1 + 0.15 + 0.15 = 0.4 lot
Total margin: 0.4 × 100 × 2650 / 100 = $1,060

═══════════════════════════════════════════════════════════

Example 2: S3 without bonus (NEWS too low)
MinNewsLevelS3 = 20
EnableBonusNews = True
MinNewsLevelBonus = 5
FixedLotSize = 0.1

M5 signal: BUY (+1)
M5 NEWS: +30 (L3 cascade)

Processing:
├─ NEWS=30 >= MinNewsLevelS3=20? YES ✓
├─ Open main S3 order: Lot=0.1
├─ EnableBonusNews? YES
├─ NEWS=30 >= MinNewsLevelBonus=5? NO (30/10=3 < 5) ✗
└─ Total: 1 order (only main, no bonus)

Total lot: 0.1 lot
```

---

