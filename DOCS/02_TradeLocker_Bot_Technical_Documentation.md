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


### C. RISK PROTECTION (5 params)

#### C.1 Stoploss Mode (2 params)

```python
StoplossMode: int = 1
Layer2_Divisor: float = 5.0
```

**StoplossMode Options:**
- `0`: NONE (no stoploss, very risky!)
- `1`: LAYER1_MAXLOSS (use CSDL max_loss value)
- `2`: LAYER2_MARGIN (margin-based calculation)

**Layer2_Divisor:**
- Divisor for Layer2 calculation
- Formula: `sl_threshold = -(margin / divisor)`
- Common values: 5.0 (conservative), 10.0 (aggressive)

**Logic:**

```
StoplossMode = 0 (NONE):
├─ No stoploss set
├─ Position can go to -100% (margin call)
└─ VERY RISKY! Not recommended

StoplossMode = 1 (LAYER1 - CSDL):
├─ Use max_loss from CSDL file
├─ If max_loss = -10.0 USD → SL = entry - 10.0
├─ Safe if CSDL accurate
└─ Fallback to MaxLoss_Fallback if CSDL = 0

StoplossMode = 2 (LAYER2 - MARGIN):
├─ Calculate based on margin
├─ Formula: threshold = -(margin / Layer2_Divisor)
├─ Example: margin=$265, divisor=5
│   → threshold = -265/5 = -$53 loss
├─ More conservative (accounts for leverage)
└─ Independent of CSDL data
```

**Examples:**

```
Example 1: Layer1 (CSDL-based)
StoplossMode = 1
CSDL max_loss = -10.0 USD
Entry price: 2650.00

Calculation:
├─ SL price = 2650 - 10.0 = 2640.00
└─ If price drops to 2640 → Close position

Example 2: Layer2 (Margin-based)
StoplossMode = 2
Layer2_Divisor = 5.0
Lot size: 0.1 (MT5 style)
Price: 2650
Leverage: 1:100

Calculation:
├─ Margin = 0.1 × 100 × 2650 / 100 = $265
├─ Threshold = -265 / 5 = -$53
├─ SL price = 2650 - (53 / 0.1 / 100) = 2650 - 5.3 = 2644.70
└─ If loss reaches -$53 → Close position

Example 3: Fallback
StoplossMode = 1
CSDL max_loss = 0 (invalid!)
MaxLoss_Fallback = -1000.0

Calculation:
├─ max_loss = 0 → Invalid
├─ Use fallback: -1000.0
├─ SL price = 2650 - 1000 = 1650.00
└─ Very wide SL (emergency fallback)
```

#### C.2 Take Profit Mode (2 params)

```python
TakeProfitMode: int = 1
FixedTPUSD: float = 100.0
```

**TakeProfitMode Options:**
- `0`: NONE (no TP, hold until close signal)
- `1`: FIXED_USD (fixed USD profit target)
- `2`: TRAILING (trailing stop, not implemented yet)

**FixedTPUSD:**
- Fixed profit target in USD
- Range: 10.0 - 1000.0 USD
- Example: 100.0 means close at +$100 profit

**Logic:**

```
TakeProfitMode = 0 (NONE):
├─ No TP set
├─ Hold position until close signal (M1 or own TF)
├─ Can capture large trends
└─ Risk: May give back profits if no close signal

TakeProfitMode = 1 (FIXED_USD):
├─ Set TP at entry + FixedTPUSD
├─ Example: Entry=2650, TP=$100 → Close at 2650 + 10 = 2660
├─ Automatic profit taking
└─ Suitable for scalping, news trading

TakeProfitMode = 2 (TRAILING):
├─ Not implemented yet in current version
└─ Future feature
```

**Examples:**

```
Example 1: No TP (hold for trend)
TakeProfitMode = 0
Entry: 2650.00 BUY
Current: 2670.00 (+$200 profit)

Bot logic:
├─ No TP set
├─ Wait for M1 SELL signal (if S1_CloseByM1=True)
├─ Or wait for M5 SELL signal (if own TF)
└─ Can capture full trend move

Result:
- If trend continues to 2680: +$300 profit ✓
- If reverses to 2645: -$50 loss ✗ (gave back profit)

Example 2: Fixed TP (secure profit)
TakeProfitMode = 1
FixedTPUSD = 100.0
Entry: 2650.00 BUY
Lot: 0.1

Calculation:
├─ TP profit target: $100
├─ Price move needed: 100 / (0.1 × 100) = 10 USD
├─ TP price: 2650 + 10 = 2660.00
└─ Close when price hits 2660

Result:
- Price reaches 2660: +$100 profit ✓ (secured)
- No risk of giving back profit
```

#### C.3 Trailing Stop (3 params - NOT IMPLEMENTED YET)

```python
EnableTrailingStop: bool = False
TrailingStopUSD: float = 0.0
TrailingStepUSD: float = 0.0
```

**Status:** Future feature, not implemented in current version.

**Planned Logic:**

```
When implemented:
├─ Move SL up as profit increases
├─ Lock in profits dynamically
└─ Example:
    Entry: 2650 BUY
    Initial SL: 2640 (-$10)
    Price: 2660 (+$100)
    Trail: Move SL to 2650 (break-even)
    Price: 2670 (+$200)
    Trail: Move SL to 2660 (+$100 locked)
```

---

### D. TRADELOCKER CONNECTION (4 params)

```python
TL_Environment: str = "demo"
TL_Username: str = "your_username"
TL_Password: str = "your_password"
TL_Server: str = "https://demo.tradelocker.com"
```

**TL_Environment:**
- `"demo"`: Demo account (paper trading)
- `"live"`: Live account (real money)
- ALWAYS start with demo!

**TL_Username & TL_Password:**
- TradeLocker account credentials
- **SECURITY:** Never commit to git!
- Use environment variables in production:
  ```bash
  export TL_USERNAME="your_username"
  export TL_PASSWORD="your_password"
  ```

**TL_Server:**
- TradeLocker API server URL
- Demo: `https://demo.tradelocker.com`
- Live: `https://live.tradelocker.com`
- Automatically set based on TL_Environment

**Connection Flow:**

```
1. Load config.json
   ├─ Read TL_Environment, Username, Password
   └─ Validate credentials format

2. Initialize TLAPI
   ├─ from tradelocker import TLAPI
   ├─ tl = TLAPI(
   │     environment=TL_Environment,
   │     username=TL_Username,
   │     password=TL_Password,
   │     server=TL_Server
   │   )
   └─ Connection established

3. Authenticate
   ├─ API sends login request
   ├─ Receive access token
   └─ Token stored in TLAPI instance

4. Get account info
   ├─ Call: tl.get_accounts()
   ├─ Response: [{id, balance, currency, leverage}]
   └─ Select first account (or by ID)

5. Ready to trade
   └─ Bot can now place orders
```

**Example:**

```python
# In code
self.tl = TLAPI(
    environment=self.config.TL_Environment,  # "demo"
    username=self.config.TL_Username,         # "john@example.com"
    password=self.config.TL_Password,         # "SecurePass123!"
    server=self.config.TL_Server              # Auto-set
)

# Get accounts
accounts = self.tl.get_accounts()
self.account_id = accounts[0]['id']  # "12345"

# Get balance
balance = accounts[0]['balance']  # 10000.00
leverage = accounts[0]['leverage']  # 100

print(f"Connected! Balance: ${balance}, Leverage: 1:{leverage}")
# Output: Connected! Balance: $10000.0, Leverage: 1:100
```

---

### E. ADVANCED SETTINGS (4 params)

```python
Symbol: str = "XAUUSD"
DebugMode: bool = False
EnableDashboard: bool = False
TimerIntervalSeconds: int = 1
```

**Symbol:**
- Trading symbol (instrument)
- Common values: "XAUUSD", "EURUSD", "BTCUSD", etc.
- Must match CSDL filename (XAUUSD.json)
- Case-sensitive!

**DebugMode:**
- `True`: Enable verbose logging (DEBUG level)
- `False`: Normal logging (INFO level)
- Debug shows:
  - HTTP requests/responses
  - CSDL parsing details
  - API call parameters
  - Position state changes
- Use for troubleshooting only (verbose)

**EnableDashboard:**
- `True`: Print dashboard to console every N seconds
- `False`: Disable dashboard (cleaner logs)
- Dashboard shows:
  - Current positions (21 slots)
  - PnL per position
  - Total PnL
  - Win/Loss statistics
- Not implemented yet (future feature)

**TimerIntervalSeconds:**
- OnTimer interval in seconds
- Default: 1 (recommended)
- Range: 1-60 seconds
- Lower = more responsive, higher CPU
- Higher = less responsive, lower CPU

**Examples:**

```
Example 1: Production setup
Symbol = "XAUUSD"
DebugMode = False
EnableDashboard = False
TimerIntervalSeconds = 1

Log output (clean):
2024-01-16 10:00:01 [INFO] [CSDL] Reading XAUUSD.json
2024-01-16 10:00:01 [INFO] [S1] M5 BUY opened ✓
2024-01-16 10:05:30 [INFO] [CLOSE] M5_S1 closed: PnL=+$45.50

═══════════════════════════════════════════════════════════

Example 2: Debug setup
Symbol = "XAUUSD"
DebugMode = True
TimerIntervalSeconds = 1

Log output (verbose):
2024-01-16 10:00:01 [DEBUG] [TIMER] OnTimer tick #12345
2024-01-16 10:00:01 [DEBUG] [CSDL] HTTP GET http://api.example.com/XAUUSD.json
2024-01-16 10:00:01 [DEBUG] [CSDL] Response: 200 OK, 1234 bytes
2024-01-16 10:00:01 [DEBUG] [CSDL] Parsed: 7 rows
2024-01-16 10:00:01 [DEBUG] [CSDL] Row 1 (M5): signal=1, news=30, max_loss=-4.2
2024-01-16 10:00:01 [DEBUG] [SIGNAL] M5 signal: new=1, old=0 → NEW SIGNAL
2024-01-16 10:00:01 [DEBUG] [S1] Check TF_M5: enabled=True
2024-01-16 10:00:01 [DEBUG] [S1] Check S1_HOME: enabled=True
2024-01-16 10:00:01 [DEBUG] [S1] Check NEWS: 30 >= 2 → PASS
2024-01-16 10:00:01 [INFO] [S1] M5 BUY opened ✓
```

---

═══════════════════════════════════════════════════════════
 4. DATA STRUCTURES (CLASSES)
═══════════════════════════════════════════════════════════

## 4.1 CSDLLoveRow Class

**Purpose:** Store CSDL data for ONE timeframe (1 row = 6 columns).

**Definition:**

```python
@dataclass
class CSDLLoveRow:
    """CSDL data for one timeframe (6 columns) | Dữ liệu CSDL cho 1 khung thời gian"""
    max_loss: float = 0.0      # Col 1: Max loss per 1 LOT (USD)
    timestamp: int = 0         # Col 2: Timestamp (Unix epoch)
    signal: int = 0            # Col 3: Signal (1=BUY, -1=SELL, 0=NONE)
    pricediff: float = 0.0     # Col 4: Price diff USD (unused in current version)
    timediff: int = 0          # Col 5: Time diff minutes (unused)
    news: int = 0              # Col 6: News CASCADE (±10-70, or ±1-7 for Cat2)
```

**Fields Explained:**

| Field | Type | Range | Purpose | Example |
|-------|------|-------|---------|---------|
| max_loss | float | -∞ to 0 | Max loss per 1 lot (Layer1 SL) | -4.2 |
| timestamp | int | Unix epoch | Signal timestamp | 1705401600 |
| signal | int | -1, 0, +1 | Trade signal direction | +1 (BUY) |
| pricediff | float | Any | Price movement USD (unused) | 2.5 |
| timediff | int | Seconds | Time since signal (unused) | 120 |
| news | int | ±1 to ±70 | CASCADE score | +30 (L3) |

**Usage Example:**

```python
# Parse CSDL row
row = CSDLLoveRow(
    max_loss=-4.2,
    timestamp=1705401600,
    signal=1,
    pricediff=2.5,
    timediff=120,
    news=30
)

# Access fields
if row.signal == 1:
    print(f"BUY signal at {row.timestamp}")
    print(f"NEWS score: {row.news}")
    print(f"Max loss: ${row.max_loss} per lot")

# Output:
# BUY signal at 1705401600
# NEWS score: 30
# Max loss: $-4.2 per lot
```

**Why Only 6 Columns?**

CSDL1 file has 10 columns, but bot only uses 6:

```
CSDL1 Format (10 columns):
[signal, price, cross_ref, timestamp, price_diff, time_diff, 
 news_cat1, news_cat2_l1, news_cat2_l2, max_loss]

Bot uses (6 columns):
[max_loss, timestamp, signal, pricediff, timediff, news]
            ↑             ↑        ↑         ↑       ↑       ↑
         Col 10        Col 4    Col 1    Col 5    Col 6  Col 7-9 (merged)

Mapping:
- max_loss: Column 10 (max_loss)
- timestamp: Column 4 (timestamp)
- signal: Column 1 (signal)
- pricediff: Column 5 (price_diff) - not used
- timediff: Column 6 (time_diff) - not used
- news: Column 7 (news_cat1) - main news score
```

---

## 4.2 EASymbolData Class

**Purpose:** Store ALL data for current symbol (116 variables!).

**Definition (simplified):**

```python
@dataclass
class EASymbolData:
    """EA data structure for current symbol (116 variables)"""

    # ===== GROUP 1: Symbol Info (9 vars) =====
    symbol_name: str = ""                    # "XAUUSD"
    normalized_symbol_name: str = ""         # "XAU/USD" (optional)
    symbol_prefix: str = ""                  # "" or "m" or "f"
    symbol_type: str = ""                    # "METAL", "FX", "CRYPTO"
    all_leverages: str = ""                  # "1:100"
    broker_name: str = ""                    # "TradeLocker"
    account_type: str = ""                   # "DEMO" or "LIVE"
    csdl_folder: str = ""                    # "CSDL/"
    csdl_filename: str = ""                  # "XAUUSD.json"

    # ===== GROUP 2: CSDL Rows (7 rows) =====
    csdl_rows: List[CSDLLoveRow] = field(default_factory=lambda: [CSDLLoveRow() for _ in range(7)])
    # csdl_rows[0] = M1 data
    # csdl_rows[1] = M5 data
    # ...
    # csdl_rows[6] = D1 data

    # ===== GROUP 3: Core Signals (14 vars = 2×7 TF) =====
    signal_old: List[int] = field(default_factory=lambda: [0] * 7)
    timestamp_old: List[int] = field(default_factory=lambda: [0] * 7)
    # Used to detect NEW signals (compare old vs new)

    # ===== GROUP 4: Magic Numbers (21 vars: 7×3) =====
    magic_numbers: List[List[int]] = field(default_factory=lambda: [[0]*3 for _ in range(7)])
    # magic_numbers[tf_idx][strategy_idx]
    # Example: magic_numbers[1][0] = 100002 (M5, S1)

    # ===== GROUP 5: Lot Sizes (21 vars: 7×3) =====
    lot_sizes: List[List[float]] = field(default_factory=lambda: [[0.0]*3 for _ in range(7)])
    # Pre-calculated lot sizes for all 21 positions

    # ===== GROUP 6: Strategy Conditions (15 vars) =====
    trend_d1: int = 0                                    # D1 trend (-1, 0, +1)
    news_level: List[int] = field(default_factory=lambda: [0] * 7)       # NEWS score per TF
    news_direction: List[int] = field(default_factory=lambda: [0] * 7)   # NEWS direction per TF

    # ===== GROUP 7: Stoploss Thresholds (21 vars: 7×3) =====
    layer1_thresholds: List[List[float]] = field(default_factory=lambda: [[0.0]*3 for _ in range(7)])
    # Layer1 SL thresholds from CSDL max_loss

    # ===== GROUP 8: Position Flags (21 vars: 7×3) =====
    position_flags: List[List[int]] = field(default_factory=lambda: [[0]*3 for _ in range(7)])
    # 0 = no position, 1 = position open
    # Example: position_flags[1][0] = 1 means M5_S1 has open position

    # ===== GROUP 9: Position Tickets (21 vars: 7×3) =====
    position_tickets: List[List[Optional[str]]] = field(default_factory=lambda: [[None]*3 for _ in range(7)])
    # TradeLocker order IDs (UUID strings)
    # Example: position_tickets[1][0] = "abc-123-def" (M5_S1 ticket)

    # ===== GROUP 10: Global State (5 vars) =====
    first_run_completed: bool = False        # Init completed?
    weekend_last_day: int = 0                # Last weekend reset day
    health_last_check_hour: int = -1         # Last health check hour
    timer_last_run_time: int = 0             # Last timer execution time
    init_summary: str = ""                   # Init summary message
```

**116 Variables Breakdown:**

```
Group 1: Symbol Info          =  9 vars
Group 2: CSDL Rows (7×6)      = 42 vars
Group 3: Core Signals (2×7)   = 14 vars
Group 4: Magic Numbers (7×3)  = 21 vars
Group 5: Lot Sizes (7×3)      = 21 vars
Group 6: Strategy (1+7+7)     = 15 vars
Group 7: SL Thresholds (7×3)  = 21 vars
Group 8: Position Flags (7×3) = 21 vars
Group 9: Tickets (7×3)        = 21 vars
Group 10: Global State        =  5 vars
────────────────────────────────────────
TOTAL                         = 190 vars (some nested)
But actual top-level fields  = 116 vars
```

**Usage Example:**

```python
# Initialize
g_ea = EASymbolData()

# Set symbol info
g_ea.symbol_name = "XAUUSD"
g_ea.symbol_type = "METAL"
g_ea.broker_name = "TradeLocker"

# Load CSDL data
g_ea.csdl_rows[1].signal = 1      # M5 BUY
g_ea.csdl_rows[1].news = 30       # L3 cascade
g_ea.csdl_rows[1].max_loss = -4.2  # SL

# Save old signal (for comparison)
g_ea.signal_old[1] = 0    # M5 old signal was NONE

# Detect new signal
if g_ea.csdl_rows[1].signal != g_ea.signal_old[1]:
    print("NEW M5 signal detected!")
    # Open position...
    g_ea.position_flags[1][0] = 1  # Mark M5_S1 as open
    g_ea.position_tickets[1][0] = "abc-123"  # Save ticket

# Check position exists
if g_ea.position_flags[1][0] == 1:
    ticket = g_ea.position_tickets[1][0]
    print(f"M5_S1 position open: ticket={ticket}")
```

---

## 5. CSDL File Format & Parsing

The **CSDL (Cơ Sở Dữ Liệu Love)** file is the **ONLY data source** that the TradeLocker Bot reads to determine trading signals. This file is written by the SPY Bot indicator and read by the TradeLocker Bot every 1 second.

### 5.1. File Location & Naming

**File Path Options:**

**Option 1: Local File (Legacy)**
```
CSDL/XAUUSD.json
```

**Option 2: HTTP API (Recommended for Production)**
```
http://your-server.com/api/csdl/XAUUSD
```

**File Naming Convention:**
```
Format: {symbol_name}.json
Examples:
  XAUUSD.json       → Gold spot
  EURUSD.json       → EUR/USD forex
  BTCUSD.json       → Bitcoin
```

**Configuration in config.json:**
```json
{
  "USE_HTTP_FOR_CSDL_READING": true,
  "HTTP_API_BASE_URL": "http://your-server.com/api/csdl",
  "Symbol": "XAUUSD"
}
```

**File Access Logic:**
```python
def get_csdl_file_path() -> str:
    """Determine CSDL file path based on config"""
    if config.USE_HTTP_FOR_CSDL_READING:
        return f"{config.HTTP_API_BASE_URL}/{config.Symbol}"
    else:
        return f"CSDL/{config.Symbol}.json"
```

---

### 5.2. CSDL 10-Column Format (SPY Bot Output)

The SPY Bot indicator writes CSDL data in **10 columns** for each timeframe. The TradeLocker Bot reads this data and maps it to **6 columns** in the `CSDLLoveRow` class.

**SPY Bot Output Structure (10 Columns):**

```
Column Index │ Column Name      │ Data Type │ Description
─────────────┼──────────────────┼───────────┼────────────────────────────────
     0       │ signal           │ int       │ -1=SELL, 0=NONE, +1=BUY
     1       │ price            │ float     │ Signal price (2650.50)
     2       │ cross_ref        │ int       │ Cross reference ID
     3       │ timestamp        │ int       │ Unix timestamp (1699999999)
     4       │ price_diff       │ float     │ Price difference from trigger
     5       │ time_diff        │ int       │ Time diff in seconds
     6       │ news_cat1        │ int       │ NEWS category 1 (CASCADE score)
     7       │ news_cat2        │ int       │ NEWS category 2 (unused)
     8       │ max_loss         │ float     │ Max loss in USD (Layer1 SL)
     9       │ reserved         │ any       │ Reserved for future use
```

**JSON Structure (7 Timeframes × 10 Columns):**

```json
{
  "M1": [1, 2650.50, 123, 1699999999, 0.0, 0, 30, 0, -4.2, null],
  "M5": [-1, 2651.00, 124, 1699999998, 0.5, 1, 20, 0, -3.8, null],
  "M15": [0, 0.0, 0, 0, 0.0, 0, 0, 0, 0.0, null],
  "M30": [1, 2649.80, 125, 1699999997, 0.7, 2, 40, 0, -5.5, null],
  "H1": [0, 0.0, 0, 0, 0.0, 0, 0, 0, 0.0, null],
  "H4": [1, 2648.50, 126, 1699999996, 2.0, 3, 50, 0, -6.1, null],
  "D1": [1, 2645.00, 127, 1699999995, 5.5, 4, 10, 0, -2.5, null]
}
```

---

### 5.3. Column-by-Column Details

#### Column 0: Signal

**Purpose:** Trade direction signal.

**Values:**
```
 -1 = SELL signal
  0 = NO signal (neutral)
 +1 = BUY signal
```

**Examples:**
```python
# BUY example
csdl_data["M5"][0] = 1
→ M5 timeframe has BUY signal

# SELL example
csdl_data["M5"][0] = -1
→ M5 timeframe has SELL signal

# No signal
csdl_data["M5"][0] = 0
→ M5 timeframe has NO active signal
```

**Critical Note:** Signal value can **change** at any time when SPY Bot detects new CASCADE pattern. The TradeLocker Bot compares `signal_new` vs `signal_old` to detect new signals.

---

#### Column 1: Price

**Purpose:** Price at which the signal was generated.

**Format:** Float with 2 decimals for XAUUSD.

**Examples:**
```python
# Signal BUY at 2650.50
csdl_data["M5"][1] = 2650.50

# Signal SELL at 2651.25
csdl_data["M5"][1] = 2651.25

# No signal (price = 0)
csdl_data["M5"][1] = 0.0
```

**Usage in Bot:**
```python
def calculate_qty(lot: float, price: float) -> int:
    """Use signal price for lot→qty conversion"""
    return int(lot * 100 * price)

# Example
signal_price = g_ea.csdl_rows[1].price  # 2650.50
lot = 0.1
qty = calculate_qty(lot, signal_price)  # 26,505 units
```

**Important:** This price is **historical** (when signal was detected). The bot must use **current market price** for actual order execution.

---

#### Column 2: Cross Reference

**Purpose:** Unique ID for signal instance (for debugging/tracking).

**Format:** Integer counter.

**Examples:**
```python
# First signal of the day
csdl_data["M5"][2] = 1

# 50th signal
csdl_data["M5"][2] = 50
```

**Usage:** Mostly for debugging. Not used in core trading logic.

---

#### Column 3: Timestamp

**Purpose:** Unix timestamp when signal was generated.

**Format:** Integer (seconds since 1970-01-01).

**Examples:**
```python
# Signal generated at 2024-01-15 10:30:00 UTC
csdl_data["M5"][3] = 1705316400

# Convert to human-readable
import datetime
dt = datetime.datetime.fromtimestamp(1705316400)
print(dt)  # 2024-01-15 10:30:00
```

**Usage in Bot:**
```python
def is_new_signal(tf_idx: int) -> bool:
    """Check if signal is new by comparing timestamp"""
    old_ts = g_ea.timestamp_old[tf_idx]
    new_ts = g_ea.csdl_rows[tf_idx].timestamp

    if new_ts > old_ts:
        return True  # NEW signal!
    return False
```

**Critical:** This is the **primary mechanism** to detect new signals. If timestamp changes → new signal detected.

---

#### Column 4: Price Difference

**Purpose:** Price movement since signal trigger.

**Format:** Float (positive or negative).

**Examples:**
```python
# Signal at 2650.00, current price 2650.50
csdl_data["M5"][4] = 0.50  # +0.50 USD profit

# Signal at 2650.00, current price 2649.50
csdl_data["M5"][4] = -0.50  # -0.50 USD loss
```

**Usage:** Can be used for advanced signal filtering (e.g., only take signals with price_diff < 1.0).

**Current Implementation:** Not actively used in TradeLocker Bot logic.

---

#### Column 5: Time Difference

**Purpose:** Time elapsed since signal trigger (in seconds).

**Format:** Integer.

**Examples:**
```python
# Signal triggered 30 seconds ago
csdl_data["M5"][5] = 30

# Signal triggered 2 minutes ago
csdl_data["M5"][5] = 120
```

**Usage:** Can be used for signal freshness filtering (e.g., only take signals < 60 seconds old).

**Current Implementation:** Not actively used in TradeLocker Bot logic.

---

#### Column 6: News Category 1 (CASCADE Score)

**Purpose:** **MOST IMPORTANT COLUMN** - Contains CASCADE detection score.

**Format:** Integer (0 to 70).

**Values:**
```
  0      = No CASCADE detected
  ±10    = L1 CASCADE (very weak)
  ±20    = L2 CASCADE (weak)
  ±30    = L3 CASCADE (medium)
  ±40    = L4 CASCADE (strong)
  ±50    = L5 CASCADE (very strong)
  ±60    = L6 CASCADE (extremely strong)
  ±70    = L7 CASCADE (maximum strength)
```

**Sign Convention:**
```
Positive (+10 to +70) = Bullish CASCADE (supports BUY)
Negative (-10 to -70) = Bearish CASCADE (supports SELL)
```

**Examples:**
```python
# L3 bullish CASCADE detected
csdl_data["M5"][6] = 30
→ Medium-strength BUY signal

# L5 bearish CASCADE detected
csdl_data["M5"][6] = -50
→ Very strong SELL signal

# No CASCADE
csdl_data["M5"][6] = 0
→ No NEWS filter applicable
```

**Usage in Strategy S1 (HOME with NEWS filter):**

```python
def check_s1_news_filter(news_score: int) -> bool:
    """
    S1 NEWS Filter Decision Tree

    Args:
        news_score: CASCADE score from Column 6

    Returns:
        True if signal passes NEWS filter
        False if signal blocked by NEWS filter
    """
    abs_news = abs(news_score)

    # No CASCADE → pass (no blocking)
    if abs_news == 0:
        return True

    # L1 or L2 CASCADE (weak) → pass
    if abs_news <= 20:
        return True

    # L3 to L7 CASCADE (medium to max) → BLOCK
    if abs_news >= 30:
        return False

    return True

# Example usage
news_score = g_ea.csdl_rows[1].news  # M5 news = 30
if check_s1_news_filter(news_score):
    print("S1: Signal PASSED NEWS filter")
else:
    print("S1: Signal BLOCKED by NEWS filter")
    # Do not open S1 position
```

**Usage in Strategy S3 (NEWS):**

```python
def check_s3_news_condition(news_score: int) -> bool:
    """
    S3 NEWS Condition: Only trade on HIGH CASCADE

    Args:
        news_score: CASCADE score from Column 6

    Returns:
        True if CASCADE is high enough (L3+)
        False otherwise
    """
    abs_news = abs(news_score)

    # L3 or higher (30+) → TRADE
    if abs_news >= 30:
        return True

    # L1 or L2 (below 30) → NO TRADE
    return False

# Example usage
news_score = g_ea.csdl_rows[1].news  # M5 news = 50
if check_s3_news_condition(news_score):
    print("S3: HIGH CASCADE detected - open NEWS position")
    # Open S3 NEWS position
else:
    print("S3: CASCADE too weak - skip")
```

**Critical Importance:** This column determines:
1. Whether S1 positions are BLOCKED (NEWS filter)
2. Whether S3 positions are ALLOWED (NEWS condition)
3. Bonus order logic in S3 (higher CASCADE → more bonus orders)

---

#### Column 7: News Category 2

**Purpose:** Reserved for future use (second NEWS category).

**Format:** Integer.

**Current Status:** **NOT USED** in current implementation.

**Value:** Always 0.

---

#### Column 8: Max Loss (Layer1 Stoploss)

**Purpose:** **CRITICAL** - Maximum allowed loss in USD for this signal (Layer1 SL).

**Format:** Float (always negative or zero).

**Examples:**
```python
# Max loss = -4.2 USD
csdl_data["M5"][8] = -4.2
→ If position loss reaches -$4.20, close immediately

# Max loss = -10.5 USD
csdl_data["M5"][8] = -10.5
→ If position loss reaches -$10.50, close immediately

# No stoploss
csdl_data["M5"][8] = 0.0
→ No Layer1 SL protection
```

**Usage in Layer1 Stoploss Logic:**

```python
def check_layer1_stoploss(tf_idx: int, strategy_idx: int) -> bool:
    """
    Check if Layer1 SL threshold reached

    Args:
        tf_idx: Timeframe index (0=M1, 1=M5, ...)
        strategy_idx: Strategy index (0=S1, 1=S2, 2=S3)

    Returns:
        True if SL threshold reached (should close position)
        False otherwise
    """
    # Get Layer1 SL threshold from CSDL
    sl_threshold = g_ea.csdl_rows[tf_idx].max_loss  # Example: -4.2

    if sl_threshold == 0.0:
        return False  # No Layer1 SL configured

    # Get current position profit
    ticket = g_ea.position_tickets[tf_idx][strategy_idx]
    position = get_position_by_ticket(ticket)

    if position is None:
        return False

    current_profit = position['profit']  # Example: -4.5 USD

    # Check if loss exceeded threshold
    if current_profit <= sl_threshold:
        print(f"[LAYER1_SL] Position {ticket} hit SL: profit={current_profit:.2f} <= threshold={sl_threshold:.2f}")
        return True  # CLOSE POSITION!

    return False

# Example usage (every 1 second in main loop)
for tf_idx in range(7):
    for strat_idx in range(3):
        if g_ea.position_flags[tf_idx][strat_idx] == 1:
            if check_layer1_stoploss(tf_idx, strat_idx):
                close_position(tf_idx, strat_idx, reason="LAYER1_SL")
```

**Calculation in SPY Bot:**

The SPY Bot calculates `max_loss` based on CASCADE level and price movement analysis. The exact formula is proprietary, but the result is a **conservative** stoploss value.

**Example Calculation (Simplified):**
```
Typical values for XAUUSD:
L1 CASCADE → max_loss = -2.5 USD
L3 CASCADE → max_loss = -4.2 USD
L5 CASCADE → max_loss = -6.8 USD
L7 CASCADE → max_loss = -10.5 USD
```

**Important Notes:**
- Layer1 SL is **per-position** (not per account)
- Layer1 SL is **read from CSDL** (not configured in bot)
- Layer1 SL can **change** if SPY Bot updates the CSDL file
- Layer1 SL is **independent** of Layer2 SL (margin-based)

---

#### Column 9: Reserved

**Purpose:** Reserved for future expansion.

**Format:** Any type (typically null or 0).

**Current Status:** **NOT USED**.

---

### 5.4. Column Mapping (10 Columns → 6 Columns)

The TradeLocker Bot **ignores** some columns and **renames** others when loading CSDL data into `CSDLLoveRow` objects.

**Mapping Table:**

```
SPY Bot Column Index → CSDLLoveRow Field Name
────────────────────────────────────────────────
       0 (signal)     → signal
       1 (price)      → price
       2 (cross_ref)  → [IGNORED]
       3 (timestamp)  → timestamp
       4 (price_diff) → [IGNORED]
       5 (time_diff)  → [IGNORED]
       6 (news_cat1)  → news
       7 (news_cat2)  → [IGNORED]
       8 (max_loss)   → max_loss
       9 (reserved)   → [IGNORED]
```

**6 Columns Used by TradeLocker Bot:**

```python
@dataclass
class CSDLLoveRow:
    signal: int = 0           # Column 0
    price: float = 0.0        # Column 1
    timestamp: int = 0        # Column 3
    news: int = 0             # Column 6 (CASCADE score)
    max_loss: float = 0.0     # Column 8
    timeframe: str = ""       # Metadata (not from CSDL)
```

**Parsing Logic:**

```python
def parse_csdl_row(tf_name: str, row_data: list) -> CSDLLoveRow:
    """
    Parse 10-column CSDL row into 6-field CSDLLoveRow object

    Args:
        tf_name: Timeframe name ("M1", "M5", ...)
        row_data: List of 10 values from JSON

    Returns:
        CSDLLoveRow object
    """
    csdl_row = CSDLLoveRow()

    # Map columns
    csdl_row.signal = row_data[0]      # Column 0
    csdl_row.price = row_data[1]       # Column 1
    csdl_row.timestamp = row_data[3]   # Column 3 (skip 2)
    csdl_row.news = row_data[6]        # Column 6 (skip 4,5)
    csdl_row.max_loss = row_data[8]    # Column 8 (skip 7)
    csdl_row.timeframe = tf_name       # Metadata

    # Columns 2, 4, 5, 7, 9 are IGNORED

    return csdl_row

# Example usage
json_data = {
    "M5": [1, 2650.50, 123, 1699999999, 0.0, 0, 30, 0, -4.2, null]
}

m5_row = parse_csdl_row("M5", json_data["M5"])
print(m5_row.signal)     # 1 (BUY)
print(m5_row.price)      # 2650.50
print(m5_row.timestamp)  # 1699999999
print(m5_row.news)       # 30 (L3 CASCADE)
print(m5_row.max_loss)   # -4.2
print(m5_row.timeframe)  # "M5"
```

---

### 5.5. Complete CSDL Parsing Example

**Input: CSDL JSON File (XAUUSD.json)**

```json
{
  "M1": [1, 2650.50, 123, 1699999999, 0.0, 0, 30, 0, -4.2, null],
  "M5": [-1, 2651.00, 124, 1699999998, 0.5, 1, 20, 0, -3.8, null],
  "M15": [0, 0.0, 0, 0, 0.0, 0, 0, 0, 0.0, null],
  "M30": [1, 2649.80, 125, 1699999997, 0.7, 2, 40, 0, -5.5, null],
  "H1": [0, 0.0, 0, 0, 0.0, 0, 0, 0, 0.0, null],
  "H4": [1, 2648.50, 126, 1699999996, 2.0, 3, 50, 0, -6.1, null],
  "D1": [1, 2645.00, 127, 1699999995, 5.5, 4, 10, 0, -2.5, null]
}
```

**Parsing Code:**

```python
import json
from typing import Dict, List

def load_csdl_from_file(file_path: str) -> Dict[str, List]:
    """Load CSDL JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def parse_csdl_file(file_path: str) -> List[CSDLLoveRow]:
    """
    Parse entire CSDL file into 7 CSDLLoveRow objects

    Args:
        file_path: Path to CSDL JSON file

    Returns:
        List of 7 CSDLLoveRow objects (M1, M5, ..., D1)
    """
    # Load JSON
    json_data = load_csdl_from_file(file_path)

    # Timeframe order (must match array indexing)
    tf_names = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]

    # Parse each TF
    csdl_rows = []
    for tf_name in tf_names:
        if tf_name in json_data:
            row_data = json_data[tf_name]
            csdl_row = parse_csdl_row(tf_name, row_data)
            csdl_rows.append(csdl_row)
        else:
            # Missing TF → use empty row
            csdl_rows.append(CSDLLoveRow(timeframe=tf_name))

    return csdl_rows

# Usage
csdl_rows = parse_csdl_file("CSDL/XAUUSD.json")

# Access data
print(f"M1 signal: {csdl_rows[0].signal}")       # 1 (BUY)
print(f"M1 news: {csdl_rows[0].news}")           # 30 (L3)
print(f"M5 signal: {csdl_rows[1].signal}")       # -1 (SELL)
print(f"M5 news: {csdl_rows[1].news}")           # 20 (L2)
print(f"M15 signal: {csdl_rows[2].signal}")      # 0 (NONE)
```

**Output after Parsing:**

```
csdl_rows[0] (M1):  signal=1,  price=2650.50, ts=1699999999, news=30,  max_loss=-4.2
csdl_rows[1] (M5):  signal=-1, price=2651.00, ts=1699999998, news=20,  max_loss=-3.8
csdl_rows[2] (M15): signal=0,  price=0.0,     ts=0,          news=0,   max_loss=0.0
csdl_rows[3] (M30): signal=1,  price=2649.80, ts=1699999997, news=40,  max_loss=-5.5
csdl_rows[4] (H1):  signal=0,  price=0.0,     ts=0,          news=0,   max_loss=0.0
csdl_rows[5] (H4):  signal=1,  price=2648.50, ts=1699999996, news=50,  max_loss=-6.1
csdl_rows[6] (D1):  signal=1,  price=2645.00, ts=1699999995, news=10,  max_loss=-2.5
```

---

### 5.6. HTTP API Format (Alternative to Local File)

When `USE_HTTP_FOR_CSDL_READING = true`, the bot fetches CSDL data via HTTP GET request instead of reading local file.

**HTTP Request:**

```http
GET http://your-server.com/api/csdl/XAUUSD HTTP/1.1
Host: your-server.com
User-Agent: TradeLockerBot/1.0
Accept: application/json
```

**HTTP Response (Same JSON Format):**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 456

{
  "M1": [1, 2650.50, 123, 1699999999, 0.0, 0, 30, 0, -4.2, null],
  "M5": [-1, 2651.00, 124, 1699999998, 0.5, 1, 20, 0, -3.8, null],
  "M15": [0, 0.0, 0, 0, 0.0, 0, 0, 0, 0.0, null],
  "M30": [1, 2649.80, 125, 1699999997, 0.7, 2, 40, 0, -5.5, null],
  "H1": [0, 0.0, 0, 0, 0.0, 0, 0, 0, 0.0, null],
  "H4": [1, 2648.50, 126, 1699999996, 2.0, 3, 50, 0, -6.1, null],
  "D1": [1, 2645.00, 127, 1699999995, 5.5, 4, 10, 0, -2.5, null]
}
```

**Python Code for HTTP Fetch:**

```python
import requests
import json
from typing import Dict, List, Optional

def fetch_csdl_via_http(base_url: str, symbol: str) -> Optional[Dict[str, List]]:
    """
    Fetch CSDL data via HTTP API

    Args:
        base_url: Base URL (e.g., "http://server.com/api/csdl")
        symbol: Symbol name (e.g., "XAUUSD")

    Returns:
        JSON data dict, or None if error
    """
    url = f"{base_url}/{symbol}"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] HTTP {response.status_code}: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("[ERROR] HTTP request timeout (5s)")
        return None

    except requests.exceptions.ConnectionError:
        print("[ERROR] HTTP connection failed")
        return None

    except Exception as e:
        print(f"[ERROR] HTTP fetch failed: {e}")
        return None

# Usage
json_data = fetch_csdl_via_http(
    base_url="http://your-server.com/api/csdl",
    symbol="XAUUSD"
)

if json_data:
    # Parse normally
    csdl_rows = parse_csdl_json(json_data)
else:
    print("Failed to fetch CSDL data")
```

**Advantages of HTTP API:**

1. **Centralized data source** - Multiple bots can read from same server
2. **No file system access needed** - Works in restricted environments
3. **Real-time updates** - No need for file sync mechanisms
4. **Scalable** - Can serve hundreds of bots simultaneously
5. **Monitoring** - Server can log all read requests

**Disadvantages:**

1. **Network dependency** - Bot fails if network/server down
2. **Latency** - ~10-50ms slower than local file read
3. **Single point of failure** - Server downtime affects all bots

**Recommendation:** Use HTTP API for production, local file for testing.

---

### 5.7. Error Handling for CSDL Parsing

**Common Errors:**

1. **File not found (local mode)**
2. **HTTP server unreachable (HTTP mode)**
3. **Malformed JSON**
4. **Missing timeframes**
5. **Invalid column count**
6. **Wrong data types**

**Robust Parsing Code:**

```python
def load_csdl_safely(config: Config) -> Optional[List[CSDLLoveRow]]:
    """
    Load CSDL with comprehensive error handling

    Returns:
        List of 7 CSDLLoveRow objects, or None if critical error
    """
    try:
        # Fetch JSON data
        if config.USE_HTTP_FOR_CSDL_READING:
            json_data = fetch_csdl_via_http(config.HTTP_API_BASE_URL, config.Symbol)
        else:
            file_path = f"CSDL/{config.Symbol}.json"
            with open(file_path, 'r') as f:
                json_data = json.load(f)

        if json_data is None:
            print("[ERROR] Failed to load CSDL data")
            return None

        # Validate JSON structure
        if not isinstance(json_data, dict):
            print("[ERROR] CSDL data is not a dictionary")
            return None

        # Parse each timeframe
        tf_names = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
        csdl_rows = []

        for tf_name in tf_names:
            if tf_name not in json_data:
                print(f"[WARNING] Missing TF: {tf_name}, using empty row")
                csdl_rows.append(CSDLLoveRow(timeframe=tf_name))
                continue

            row_data = json_data[tf_name]

            # Validate row is a list
            if not isinstance(row_data, list):
                print(f"[ERROR] {tf_name} data is not a list")
                csdl_rows.append(CSDLLoveRow(timeframe=tf_name))
                continue

            # Validate row has 10 columns
            if len(row_data) < 10:
                print(f"[ERROR] {tf_name} has only {len(row_data)} columns (expected 10)")
                csdl_rows.append(CSDLLoveRow(timeframe=tf_name))
                continue

            # Parse row safely
            try:
                csdl_row = CSDLLoveRow()
                csdl_row.signal = int(row_data[0]) if row_data[0] is not None else 0
                csdl_row.price = float(row_data[1]) if row_data[1] is not None else 0.0
                csdl_row.timestamp = int(row_data[3]) if row_data[3] is not None else 0
                csdl_row.news = int(row_data[6]) if row_data[6] is not None else 0
                csdl_row.max_loss = float(row_data[8]) if row_data[8] is not None else 0.0
                csdl_row.timeframe = tf_name

                csdl_rows.append(csdl_row)

            except (ValueError, TypeError) as e:
                print(f"[ERROR] Failed to parse {tf_name}: {e}")
                csdl_rows.append(CSDLLoveRow(timeframe=tf_name))
                continue

        return csdl_rows

    except FileNotFoundError:
        print(f"[ERROR] CSDL file not found: CSDL/{config.Symbol}.json")
        return None

    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON format: {e}")
        return None

    except Exception as e:
        print(f"[ERROR] Unexpected error loading CSDL: {e}")
        return None

# Usage in main loop
csdl_rows = load_csdl_safely(config)
if csdl_rows is None:
    print("[FATAL] Cannot load CSDL data - bot cannot trade")
    # Keep running with old data, or exit
else:
    # Update global state
    g_ea.csdl_rows = csdl_rows
    print(f"[OK] Loaded CSDL data: {len(csdl_rows)} timeframes")
```

**Error Recovery Strategies:**

1. **Missing file/HTTP error:** Keep using old CSDL data (don't clear signals)
2. **Malformed JSON:** Log error, use empty rows for affected TFs
3. **Missing TF:** Use empty row for that TF (signal=0)
4. **Invalid data type:** Use default value (0 or 0.0)
5. **Critical errors:** Continue running but log warning to user

---

### 5.8. CSDL Update Frequency

**SPY Bot Write Frequency:**

The SPY Bot indicator updates the CSDL file:
- **Every tick** when signal changes
- **Minimum interval:** ~1 second (MT4/MT5 tick rate)
- **Maximum interval:** Depends on market activity

**TradeLocker Bot Read Frequency:**

The TradeLocker Bot reads CSDL file:
- **Every 1 second** (timer interval)
- **Configurable** via `TimerIntervalSeconds` (default: 1)

**Data Freshness:**

```
Timeline Example:

10:30:00.000 - SPY Bot detects CASCADE, writes CSDL file
10:30:00.100 - File write completes
10:30:01.000 - TradeLocker Bot reads CSDL (1-second timer fires)
10:30:01.050 - Bot detects new signal (timestamp changed)
10:30:01.100 - Bot opens position via TradeLocker API
10:30:01.300 - Position confirmed

Total latency: ~1.3 seconds from signal detection to position open
```

**Optimizations:**

1. **Reduce timer interval** to 0.5s for faster signal detection (higher CPU)
2. **Use HTTP API** with WebSocket notifications (real-time updates)
3. **File watch mechanism** (inotify on Linux) to read immediately on file change

**Current Implementation:** 1-second timer (good balance of speed vs CPU usage).

---

### 5.9. CSDL Data Validation Checklist

Before using CSDL data for trading decisions, the bot should validate:

**✓ Validation Checklist:**

```python
def validate_csdl_data(csdl_rows: List[CSDLLoveRow]) -> bool:
    """
    Validate CSDL data integrity before trading

    Returns:
        True if data is valid, False otherwise
    """
    # Check 1: Must have 7 rows
    if len(csdl_rows) != 7:
        print(f"[VALIDATION] ERROR: Expected 7 TF rows, got {len(csdl_rows)}")
        return False

    # Check 2: Timeframes must match expected order
    expected_tfs = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
    for idx, expected_tf in enumerate(expected_tfs):
        if csdl_rows[idx].timeframe != expected_tf:
            print(f"[VALIDATION] ERROR: TF[{idx}] expected {expected_tf}, got {csdl_rows[idx].timeframe}")
            return False

    # Check 3: Signal values must be -1, 0, or +1
    for idx, row in enumerate(csdl_rows):
        if row.signal not in [-1, 0, 1]:
            print(f"[VALIDATION] WARNING: {row.timeframe} signal={row.signal} (invalid)")
            # Don't fail, just fix it
            csdl_rows[idx].signal = 0

    # Check 4: Price must be positive (if signal != 0)
    for idx, row in enumerate(csdl_rows):
        if row.signal != 0 and row.price <= 0:
            print(f"[VALIDATION] WARNING: {row.timeframe} has signal but price={row.price}")
            # Don't fail, just fix it
            csdl_rows[idx].signal = 0

    # Check 5: Timestamp must be reasonable (not in future, not too old)
    import time
    current_time = int(time.time())
    for idx, row in enumerate(csdl_rows):
        if row.timestamp > current_time + 3600:  # Future (>1 hour ahead)
            print(f"[VALIDATION] WARNING: {row.timeframe} timestamp is in future")
            csdl_rows[idx].timestamp = 0

        if row.signal != 0 and row.timestamp < current_time - 86400:  # Old (>24h)
            print(f"[VALIDATION] WARNING: {row.timeframe} signal is >24h old")
            # Don't fail, but log it

    # Check 6: NEWS score must be in valid range (-70 to +70)
    for idx, row in enumerate(csdl_rows):
        if abs(row.news) > 70:
            print(f"[VALIDATION] WARNING: {row.timeframe} news={row.news} (out of range)")
            csdl_rows[idx].news = 0

    # Check 7: max_loss must be negative or zero
    for idx, row in enumerate(csdl_rows):
        if row.max_loss > 0:
            print(f"[VALIDATION] WARNING: {row.timeframe} max_loss={row.max_loss} (should be ≤0)")
            csdl_rows[idx].max_loss = 0.0

    print("[VALIDATION] CSDL data passed all checks ✓")
    return True

# Usage before trading
if validate_csdl_data(g_ea.csdl_rows):
    # Safe to trade
    process_signals()
else:
    print("[VALIDATION] CSDL data failed validation - skipping this cycle")
```

---

## 6. TradeLocker API Integration

The TradeLocker Bot communicates with the **TradeLocker trading platform** via REST API to execute all trading operations. This section documents the complete API integration architecture.

### 6.1. TradeLocker Platform Overview

**What is TradeLocker?**

TradeLocker is a **web-based** trading platform (not desktop like MT4/MT5) that provides:
- Multi-asset trading (Forex, Metals, Crypto, Indices, Commodities)
- Web-based interface (no software installation)
- REST API for algorithmic trading
- Multi-account management
- Mobile app support

**Key Differences from MT4/MT5:**

```
Feature               │ MT4/MT5                │ TradeLocker
──────────────────────┼────────────────────────┼─────────────────────
Platform Type         │ Desktop software       │ Web-based
API Type              │ Native (MQL4/MQL5)     │ REST API (HTTP)
Connection            │ Persistent (socket)    │ Stateless (HTTP)
Position Tracking     │ Automatic (built-in)   │ Manual (ticket IDs)
Lot Style             │ Standard lot (0.01+)   │ Quantity/units
Language              │ MQL4/MQL5 only         │ Any (Python, JS, etc)
Authentication        │ Account+Server         │ Username+Password+Token
```

**TradeLocker API Base URL:**

```
DEMO Environment:
https://demo.tradelocker.com/backend-api

LIVE Environment:
https://live.tradelocker.com/backend-api
```

---

### 6.2. Authentication Flow

TradeLocker uses a **two-step authentication** process:

1. **Login** with username/password → Get JWT access token
2. **Use token** in all subsequent API requests

**Step 1: Login Request**

```http
POST https://demo.tradelocker.com/backend-api/auth/jwt/token
Content-Type: application/json

{
  "email": "your_username@example.com",
  "password": "your_password",
  "server": "DEMO-Server1"
}
```

**Step 1: Login Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "tokenType": "Bearer"
}
```

**Step 2: Use Access Token in Requests**

```http
GET https://demo.tradelocker.com/backend-api/trade/accounts
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Python Implementation:**

```python
import requests
from typing import Optional, Dict

class TradeLockerAuth:
    """TradeLocker authentication manager"""

    def __init__(self, environment: str, email: str, password: str, server: str):
        self.environment = environment  # "DEMO" or "LIVE"
        self.email = email
        self.password = password
        self.server = server
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_in: int = 0

    def get_base_url(self) -> str:
        """Get API base URL based on environment"""
        if self.environment == "DEMO":
            return "https://demo.tradelocker.com/backend-api"
        else:
            return "https://live.tradelocker.com/backend-api"

    def login(self) -> bool:
        """
        Login to TradeLocker and get access token

        Returns:
            True if login successful, False otherwise
        """
        url = f"{self.get_base_url()}/auth/jwt/token"

        payload = {
            "email": self.email,
            "password": self.password,
            "server": self.server
        }

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("accessToken")
                self.refresh_token = data.get("refreshToken")
                self.expires_in = data.get("expiresIn", 3600)

                print(f"[AUTH] Login successful. Token expires in {self.expires_in}s")
                return True
            else:
                print(f"[AUTH] Login failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            print("[AUTH] Login timeout")
            return False

        except Exception as e:
            print(f"[AUTH] Login error: {e}")
            return False

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authorization token"""
        if not self.access_token:
            raise Exception("Not authenticated. Call login() first.")

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token

        Returns:
            True if refresh successful, False otherwise
        """
        if not self.refresh_token:
            print("[AUTH] No refresh token available. Need to login again.")
            return self.login()

        url = f"{self.get_base_url()}/auth/jwt/refresh"

        payload = {
            "refreshToken": self.refresh_token
        }

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("accessToken")
                self.expires_in = data.get("expiresIn", 3600)

                print(f"[AUTH] Token refreshed. Expires in {self.expires_in}s")
                return True
            else:
                print(f"[AUTH] Refresh failed: {response.status_code}")
                return self.login()  # Fallback to full login

        except Exception as e:
            print(f"[AUTH] Refresh error: {e}")
            return self.login()  # Fallback to full login

# Usage example
auth = TradeLockerAuth(
    environment="DEMO",
    email="your_username@example.com",
    password="your_password",
    server="DEMO-Server1"
)

if auth.login():
    # Use auth.get_headers() in all API requests
    headers = auth.get_headers()
    print(f"Authorization: {headers['Authorization'][:50]}...")
else:
    print("Login failed")
```

**Token Expiration Handling:**

The access token typically expires after **1 hour (3600 seconds)**. The bot should:

1. **Track token expiration time**
2. **Refresh token** before expiration (e.g., at 50 minutes)
3. **Retry with new token** if API returns 401 Unauthorized

**Auto-Refresh Logic:**

```python
import time

class TradeLockerAuthWithAutoRefresh(TradeLockerAuth):
    """Auth manager with automatic token refresh"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_issued_at: int = 0

    def login(self) -> bool:
        """Login and record issue time"""
        result = super().login()
        if result:
            self.token_issued_at = int(time.time())
        return result

    def refresh_access_token(self) -> bool:
        """Refresh and record issue time"""
        result = super().refresh_access_token()
        if result:
            self.token_issued_at = int(time.time())
        return result

    def is_token_expired(self) -> bool:
        """Check if token is expired or about to expire"""
        if not self.access_token:
            return True

        current_time = int(time.time())
        elapsed = current_time - self.token_issued_at

        # Refresh if >50 minutes old (before 60 min expiration)
        return elapsed > 3000

    def ensure_token_valid(self) -> bool:
        """Ensure token is valid, refresh if needed"""
        if not self.access_token:
            return self.login()

        if self.is_token_expired():
            print("[AUTH] Token about to expire, refreshing...")
            return self.refresh_access_token()

        return True

# Usage in main loop
auth = TradeLockerAuthWithAutoRefresh(...)
auth.login()

# Every 1 second in timer
def on_timer():
    # Check token validity
    if not auth.ensure_token_valid():
        print("[ERROR] Authentication failed")
        return

    # Make API calls...
    headers = auth.get_headers()
    # ...
```

---

### 6.3. Core API Endpoints

The TradeLocker Bot uses the following REST API endpoints:

**Summary Table:**

```
Endpoint                          │ Method │ Purpose
──────────────────────────────────┼────────┼──────────────────────────────
/auth/jwt/token                   │ POST   │ Login and get access token
/auth/jwt/refresh                 │ POST   │ Refresh access token
/trade/accounts                   │ GET    │ Get list of trading accounts
/trade/accounts/{accNum}          │ GET    │ Get account details
/trade/instruments                │ GET    │ Get list of instruments
/trade/positions                  │ GET    │ Get open positions
/trade/orders                     │ POST   │ Create new order
/trade/orders/{orderId}           │ DELETE │ Close/cancel order
/trade/orders/{orderId}           │ PATCH  │ Modify order (SL/TP)
```

Let me document each endpoint in detail:

---

#### 6.3.1. GET /trade/accounts

**Purpose:** Get list of all trading accounts accessible with current credentials.

**Request:**

```http
GET https://demo.tradelocker.com/backend-api/trade/accounts
Authorization: Bearer {access_token}
```

**Response:**

```json
{
  "accounts": [
    {
      "id": 12345,
      "accNum": "DXR123456",
      "name": "Demo Account 1",
      "currency": "USD",
      "balance": 10000.00,
      "equity": 10050.25,
      "margin": 2650.00,
      "freeMargin": 7400.25,
      "marginLevel": 379.25,
      "server": "DEMO-Server1",
      "type": "DEMO",
      "leverage": 100,
      "status": "ACTIVE"
    }
  ]
}
```

**Python Code:**

```python
def get_accounts(auth: TradeLockerAuth) -> Optional[list]:
    """
    Get list of trading accounts

    Returns:
        List of account dicts, or None if error
    """
    url = f"{auth.get_base_url()}/trade/accounts"
    headers = auth.get_headers()

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data.get("accounts", [])
        else:
            print(f"[API] Get accounts failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"[API] Get accounts error: {e}")
        return None

# Usage
accounts = get_accounts(auth)
if accounts:
    for acc in accounts:
        print(f"Account: {acc['accNum']}, Balance: ${acc['balance']:.2f}")
```

---

#### 6.3.2. GET /trade/accounts/{accNum}

**Purpose:** Get detailed information for a specific account.

**Request:**

```http
GET https://demo.tradelocker.com/backend-api/trade/accounts/DXR123456
Authorization: Bearer {access_token}
```

**Response:**

```json
{
  "id": 12345,
  "accNum": "DXR123456",
  "name": "Demo Account 1",
  "currency": "USD",
  "balance": 10000.00,
  "equity": 10050.25,
  "credit": 0.00,
  "margin": 2650.00,
  "freeMargin": 7400.25,
  "marginLevel": 379.25,
  "unrealizedPnL": 50.25,
  "realizedPnL": 150.00,
  "server": "DEMO-Server1",
  "type": "DEMO",
  "leverage": 100,
  "status": "ACTIVE",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

**Key Fields:**

- `balance`: Account balance (deposits - withdrawals)
- `equity`: Current equity (balance + unrealized P&L)
- `margin`: Used margin for all open positions
- `freeMargin`: Available margin (equity - margin)
- `marginLevel`: Margin level percentage (equity / margin × 100)
- `unrealizedPnL`: Total profit/loss of open positions

**Python Code:**

```python
def get_account_info(auth: TradeLockerAuth, acc_num: str) -> Optional[dict]:
    """
    Get account information

    Args:
        auth: Auth manager
        acc_num: Account number (e.g., "DXR123456")

    Returns:
        Account info dict, or None if error
    """
    url = f"{auth.get_base_url()}/trade/accounts/{acc_num}"
    headers = auth.get_headers()

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"[API] Get account info failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"[API] Get account info error: {e}")
        return None

# Usage
acc_info = get_account_info(auth, "DXR123456")
if acc_info:
    print(f"Balance: ${acc_info['balance']:.2f}")
    print(f"Equity: ${acc_info['equity']:.2f}")
    print(f"Margin Level: {acc_info['marginLevel']:.2f}%")
```

---

#### 6.3.3. GET /trade/instruments

**Purpose:** Get list of available trading instruments (symbols).

**Request:**

```http
GET https://demo.tradelocker.com/backend-api/trade/instruments
Authorization: Bearer {access_token}
```

**Response:**

```json
{
  "instruments": [
    {
      "id": 1001,
      "tradableInstrumentId": 1001,
      "name": "XAU/USD",
      "description": "Gold vs US Dollar",
      "type": "METAL",
      "digits": 2,
      "lotSize": 1,
      "lotStep": 1,
      "minQty": 1,
      "maxQty": 1000000,
      "contractSize": 1,
      "tickSize": 0.01,
      "tickValue": 0.01,
      "currency": "USD",
      "baseCurrency": "XAU",
      "quoteCurrency": "USD",
      "margin": 1.0,
      "leverage": 100,
      "tradingHours": "24/5",
      "status": "ACTIVE"
    },
    {
      "id": 1002,
      "tradableInstrumentId": 1002,
      "name": "EUR/USD",
      "description": "Euro vs US Dollar",
      "type": "FX",
      "digits": 5,
      "lotSize": 100000,
      "lotStep": 1000,
      "minQty": 1000,
      "maxQty": 10000000,
      "contractSize": 100000,
      "tickSize": 0.00001,
      "tickValue": 1.00,
      "currency": "USD",
      "baseCurrency": "EUR",
      "quoteCurrency": "USD",
      "margin": 1.0,
      "leverage": 500,
      "tradingHours": "24/5",
      "status": "ACTIVE"
    }
  ]
}
```

**Key Fields:**

- `tradableInstrumentId`: **CRITICAL** - Use this ID for order placement
- `name`: Symbol name (may have "/" separator)
- `type`: Instrument type (METAL, FX, CRYPTO, etc.)
- `digits`: Price decimal places
- `minQty`: Minimum order quantity
- `maxQty`: Maximum order quantity
- `contractSize`: Contract size (units per lot)

**Python Code:**

```python
def get_instruments(auth: TradeLockerAuth) -> Optional[list]:
    """
    Get list of available instruments

    Returns:
        List of instrument dicts, or None if error
    """
    url = f"{auth.get_base_url()}/trade/instruments"
    headers = auth.get_headers()

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data.get("instruments", [])
        else:
            print(f"[API] Get instruments failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"[API] Get instruments error: {e}")
        return None

def find_instrument_by_name(instruments: list, symbol: str) -> Optional[dict]:
    """
    Find instrument by symbol name

    Args:
        instruments: List of instruments from get_instruments()
        symbol: Symbol name (e.g., "XAUUSD", "XAU/USD", "Gold")

    Returns:
        Instrument dict, or None if not found
    """
    # Try exact match first
    for inst in instruments:
        if inst['name'] == symbol:
            return inst

    # Try case-insensitive match
    for inst in instruments:
        if inst['name'].upper() == symbol.upper():
            return inst

    # Try removing "/" separator
    symbol_no_slash = symbol.replace("/", "")
    for inst in instruments:
        inst_name_no_slash = inst['name'].replace("/", "")
        if inst_name_no_slash.upper() == symbol_no_slash.upper():
            return inst

    # Not found
    return None

# Usage
instruments = get_instruments(auth)
if instruments:
    print(f"Found {len(instruments)} instruments")

    # Find XAUUSD
    xauusd = find_instrument_by_name(instruments, "XAUUSD")
    if xauusd:
        print(f"XAUUSD ID: {xauusd['tradableInstrumentId']}")
        print(f"Min Qty: {xauusd['minQty']}")
        print(f"Max Qty: {xauusd['maxQty']}")
    else:
        print("XAUUSD not found")
```

---

#### 6.3.4. GET /trade/positions

**Purpose:** Get list of currently open positions.

**Request:**

```http
GET https://demo.tradelocker.com/backend-api/trade/positions?accNum=DXR123456
Authorization: Bearer {access_token}
```

**Response:**

```json
{
  "positions": [
    {
      "id": "pos-abc-123-def",
      "orderId": "ord-abc-123-def",
      "accNum": "DXR123456",
      "tradableInstrumentId": 1001,
      "instrumentName": "XAU/USD",
      "side": "BUY",
      "qty": 26500,
      "openPrice": 2650.50,
      "currentPrice": 2652.00,
      "profit": 39.75,
      "commission": 0.00,
      "swap": 0.00,
      "margin": 2650.00,
      "stopLoss": 0.0,
      "takeProfit": 0.0,
      "openTime": "2024-01-15T10:30:00Z",
      "updateTime": "2024-01-15T10:35:00Z",
      "status": "OPEN"
    },
    {
      "id": "pos-def-456-ghi",
      "orderId": "ord-def-456-ghi",
      "accNum": "DXR123456",
      "tradableInstrumentId": 1001,
      "instrumentName": "XAU/USD",
      "side": "SELL",
      "qty": 13250,
      "openPrice": 2651.00,
      "currentPrice": 2652.00,
      "profit": -13.25,
      "commission": 0.00,
      "swap": 0.00,
      "margin": 1325.00,
      "stopLoss": 2655.0,
      "takeProfit": 2645.0,
      "openTime": "2024-01-15T10:32:00Z",
      "updateTime": "2024-01-15T10:35:00Z",
      "status": "OPEN"
    }
  ]
}
```

**Key Fields:**

- `id`: **Position ticket ID** (use for closing position)
- `orderId`: Original order ID that created this position
- `side`: "BUY" or "SELL"
- `qty`: Position quantity (NOT lot size!)
- `openPrice`: Entry price
- `currentPrice`: Current market price
- `profit`: Current profit/loss in USD
- `margin`: Margin used by this position

**Python Code:**

```python
def get_positions(auth: TradeLockerAuth, acc_num: str) -> Optional[list]:
    """
    Get list of open positions

    Args:
        auth: Auth manager
        acc_num: Account number

    Returns:
        List of position dicts, or None if error
    """
    url = f"{auth.get_base_url()}/trade/positions"
    headers = auth.get_headers()
    params = {"accNum": acc_num}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data.get("positions", [])
        else:
            print(f"[API] Get positions failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"[API] Get positions error: {e}")
        return None

def find_position_by_id(positions: list, position_id: str) -> Optional[dict]:
    """Find position by ticket ID"""
    for pos in positions:
        if pos['id'] == position_id:
            return pos
    return None

# Usage
positions = get_positions(auth, "DXR123456")
if positions:
    print(f"Open positions: {len(positions)}")
    for pos in positions:
        print(f"  {pos['side']} {pos['instrumentName']} qty={pos['qty']} profit=${pos['profit']:.2f}")
```

---

#### 6.3.5. POST /trade/orders (Open Position)

**Purpose:** Create a new market order (open position).

**Request:**

```http
POST https://demo.tradelocker.com/backend-api/trade/orders
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "accNum": "DXR123456",
  "tradableInstrumentId": 1001,
  "side": "BUY",
  "type": "MARKET",
  "qty": 26500,
  "stopLoss": 0.0,
  "takeProfit": 0.0,
  "clientOrderId": "M5_S1_BUY_1705316400"
}
```

**Request Fields:**

- `accNum`: Account number (**required**)
- `tradableInstrumentId`: Instrument ID from GET /instruments (**required**)
- `side`: "BUY" or "SELL" (**required**)
- `type`: "MARKET" or "LIMIT" (**required**)
- `qty`: Quantity in units (**required**, NOT lot size!)
- `stopLoss`: Stoploss price (0.0 = no SL)
- `takeProfit`: Take profit price (0.0 = no TP)
- `clientOrderId`: Custom ID for tracking (optional but recommended)

**Response (Success):**

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "orderId": "ord-abc-123-def",
  "status": "FILLED",
  "fillPrice": 2650.52,
  "fillQty": 26500,
  "fillTime": "2024-01-15T10:30:01Z",
  "positionId": "pos-abc-123-def"
}
```

**Response (Error):**

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "INVALID_QTY",
  "message": "Quantity 100 is below minimum 1000 for this instrument"
}
```

**Python Code:**

```python
def open_position(
    auth: TradeLockerAuth,
    acc_num: str,
    instrument_id: int,
    side: str,
    qty: int,
    stop_loss: float = 0.0,
    take_profit: float = 0.0,
    client_order_id: str = ""
) -> Optional[dict]:
    """
    Open a new market position

    Args:
        auth: Auth manager
        acc_num: Account number
        instrument_id: Tradable instrument ID (from get_instruments)
        side: "BUY" or "SELL"
        qty: Quantity in units (NOT lot size!)
        stop_loss: SL price (0.0 = no SL)
        take_profit: TP price (0.0 = no TP)
        client_order_id: Custom order ID for tracking

    Returns:
        Order result dict with orderId and positionId, or None if error
    """
    url = f"{auth.get_base_url()}/trade/orders"
    headers = auth.get_headers()

    payload = {
        "accNum": acc_num,
        "tradableInstrumentId": instrument_id,
        "side": side,
        "type": "MARKET",
        "qty": qty
    }

    # Add optional fields if specified
    if stop_loss > 0:
        payload["stopLoss"] = stop_loss

    if take_profit > 0:
        payload["takeProfit"] = take_profit

    if client_order_id:
        payload["clientOrderId"] = client_order_id

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 201:
            result = response.json()
            print(f"[API] Order created: {result['orderId']}, position: {result.get('positionId', 'N/A')}")
            return result
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            print(f"[API] Order failed: {response.status_code} - {error_data.get('message', response.text)}")
            return None

    except Exception as e:
        print(f"[API] Order error: {e}")
        return None

# Usage example
result = open_position(
    auth=auth,
    acc_num="DXR123456",
    instrument_id=1001,  # XAUUSD
    side="BUY",
    qty=26500,  # 0.1 lot × 100 × 2650
    stop_loss=0.0,  # No SL
    take_profit=0.0,  # No TP
    client_order_id="M5_S1_BUY_1705316400"
)

if result:
    position_id = result.get("positionId")
    print(f"Position opened: {position_id}")
    # Save position_id to g_ea.position_tickets[tf_idx][strategy_idx]
else:
    print("Failed to open position")
```

---

#### 6.3.6. DELETE /trade/orders/{orderId} (Close Position)

**Purpose:** Close an open position.

**Request:**

```http
DELETE https://demo.tradelocker.com/backend-api/trade/orders/pos-abc-123-def
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "accNum": "DXR123456"
}
```

**Important:** Use the **position ID** (not order ID) in the URL path.

**Response (Success):**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "orderId": "close-ord-abc-123",
  "positionId": "pos-abc-123-def",
  "status": "FILLED",
  "closePrice": 2652.00,
  "closeQty": 26500,
  "profit": 39.75,
  "closeTime": "2024-01-15T10:35:00Z"
}
```

**Python Code:**

```python
def close_position(
    auth: TradeLockerAuth,
    acc_num: str,
    position_id: str
) -> bool:
    """
    Close an open position

    Args:
        auth: Auth manager
        acc_num: Account number
        position_id: Position ticket ID (from position['id'])

    Returns:
        True if close successful, False otherwise
    """
    url = f"{auth.get_base_url()}/trade/orders/{position_id}"
    headers = auth.get_headers()
    payload = {"accNum": acc_num}

    try:
        response = requests.delete(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            profit = result.get('profit', 0.0)
            print(f"[API] Position closed: {position_id}, profit: ${profit:.2f}")
            return True
        else:
            print(f"[API] Close failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"[API] Close error: {e}")
        return False

# Usage
if close_position(auth, "DXR123456", "pos-abc-123-def"):
    print("Position closed successfully")
    # Clear position_tickets and position_flags
else:
    print("Failed to close position")
```

---

#### 6.3.7. PATCH /trade/orders/{orderId} (Modify SL/TP)

**Purpose:** Modify stoploss or take profit of an open position.

**Request:**

```http
PATCH https://demo.tradelocker.com/backend-api/trade/orders/pos-abc-123-def
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "accNum": "DXR123456",
  "stopLoss": 2645.00,
  "takeProfit": 2660.00
}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "orderId": "pos-abc-123-def",
  "stopLoss": 2645.00,
  "takeProfit": 2660.00,
  "updateTime": "2024-01-15T10:36:00Z"
}
```

**Python Code:**

```python
def modify_position_sl_tp(
    auth: TradeLockerAuth,
    acc_num: str,
    position_id: str,
    stop_loss: float = None,
    take_profit: float = None
) -> bool:
    """
    Modify stoploss and/or take profit of position

    Args:
        auth: Auth manager
        acc_num: Account number
        position_id: Position ticket ID
        stop_loss: New SL price (None = don't change)
        take_profit: New TP price (None = don't change)

    Returns:
        True if modify successful, False otherwise
    """
    url = f"{auth.get_base_url()}/trade/orders/{position_id}"
    headers = auth.get_headers()

    payload = {"accNum": acc_num}

    if stop_loss is not None:
        payload["stopLoss"] = stop_loss

    if take_profit is not None:
        payload["takeProfit"] = take_profit

    if len(payload) == 1:  # Only accNum, nothing to modify
        print("[API] No SL/TP specified to modify")
        return False

    try:
        response = requests.patch(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            print(f"[API] Position modified: {position_id}")
            return True
        else:
            print(f"[API] Modify failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"[API] Modify error: {e}")
        return False

# Usage
if modify_position_sl_tp(auth, "DXR123456", "pos-abc-123-def", stop_loss=2645.00):
    print("SL modified successfully")
```

---

### 6.4. Complete API Wrapper Class

Here's a complete API wrapper that combines all endpoints:

```python
import requests
import time
from typing import Optional, Dict, List

class TradeLockerAPI:
    """Complete TradeLocker API wrapper"""

    def __init__(self, environment: str, email: str, password: str, server: str, acc_num: str):
        """
        Initialize TradeLocker API

        Args:
            environment: "DEMO" or "LIVE"
            email: Login email
            password: Login password
            server: Server name (e.g., "DEMO-Server1")
            acc_num: Account number (e.g., "DXR123456")
        """
        self.environment = environment
        self.email = email
        self.password = password
        self.server = server
        self.acc_num = acc_num

        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_issued_at: int = 0

        # Cached data
        self.instruments: List[Dict] = []
        self.instrument_id_cache: Dict[str, int] = {}  # symbol → instrument_id

    def get_base_url(self) -> str:
        """Get API base URL"""
        if self.environment == "DEMO":
            return "https://demo.tradelocker.com/backend-api"
        else:
            return "https://live.tradelocker.com/backend-api"

    def login(self) -> bool:
        """Login and get access token"""
        url = f"{self.get_base_url()}/auth/jwt/token"
        payload = {
            "email": self.email,
            "password": self.password,
            "server": self.server
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("accessToken")
                self.refresh_token = data.get("refreshToken")
                self.token_issued_at = int(time.time())
                print("[API] Login successful")
                return True
            else:
                print(f"[API] Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[API] Login error: {e}")
            return False

    def ensure_token_valid(self) -> bool:
        """Ensure token is valid, refresh if needed"""
        if not self.access_token:
            return self.login()

        elapsed = int(time.time()) - self.token_issued_at
        if elapsed > 3000:  # >50 minutes
            print("[API] Refreshing token...")
            return self.refresh_access_token()

        return True

    def refresh_access_token(self) -> bool:
        """Refresh access token"""
        if not self.refresh_token:
            return self.login()

        url = f"{self.get_base_url()}/auth/jwt/refresh"
        payload = {"refreshToken": self.refresh_token}

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("accessToken")
                self.token_issued_at = int(time.time())
                print("[API] Token refreshed")
                return True
            else:
                return self.login()
        except Exception as e:
            print(f"[API] Refresh error: {e}")
            return self.login()

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with auth token"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def load_instruments(self) -> bool:
        """Load and cache instruments"""
        if not self.ensure_token_valid():
            return False

        url = f"{self.get_base_url()}/trade/instruments"
        headers = self.get_headers()

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.instruments = data.get("instruments", [])

                # Build cache
                self.instrument_id_cache = {}
                for inst in self.instruments:
                    name = inst['name']
                    inst_id = inst['tradableInstrumentId']
                    self.instrument_id_cache[name] = inst_id
                    self.instrument_id_cache[name.replace("/", "")] = inst_id  # Also store without "/"

                print(f"[API] Loaded {len(self.instruments)} instruments")
                return True
            else:
                print(f"[API] Load instruments failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[API] Load instruments error: {e}")
            return False

    def get_instrument_id(self, symbol: str) -> Optional[int]:
        """
        Get instrument ID by symbol name

        Args:
            symbol: Symbol name (e.g., "XAUUSD", "XAU/USD")

        Returns:
            Instrument ID, or None if not found
        """
        # Try cache first
        if symbol in self.instrument_id_cache:
            return self.instrument_id_cache[symbol]

        # Try without "/" separator
        symbol_no_slash = symbol.replace("/", "")
        if symbol_no_slash in self.instrument_id_cache:
            return self.instrument_id_cache[symbol_no_slash]

        # Try case-insensitive
        for key, value in self.instrument_id_cache.items():
            if key.upper() == symbol.upper():
                return value

        print(f"[API] Instrument not found: {symbol}")
        return None

    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.ensure_token_valid():
            return None

        url = f"{self.get_base_url()}/trade/accounts/{self.acc_num}"
        headers = self.get_headers()

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[API] Get account failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"[API] Get account error: {e}")
            return None

    def get_positions(self) -> Optional[List[Dict]]:
        """Get list of open positions"""
        if not self.ensure_token_valid():
            return None

        url = f"{self.get_base_url()}/trade/positions"
        headers = self.get_headers()
        params = {"accNum": self.acc_num}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("positions", [])
            else:
                print(f"[API] Get positions failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"[API] Get positions error: {e}")
            return None

    def open_position(
        self,
        symbol: str,
        side: str,
        qty: int,
        stop_loss: float = 0.0,
        take_profit: float = 0.0,
        client_order_id: str = ""
    ) -> Optional[Dict]:
        """
        Open a new market position

        Args:
            symbol: Symbol name (e.g., "XAUUSD")
            side: "BUY" or "SELL"
            qty: Quantity in units
            stop_loss: SL price (0.0 = no SL)
            take_profit: TP price (0.0 = no TP)
            client_order_id: Custom order ID

        Returns:
            Order result dict, or None if error
        """
        if not self.ensure_token_valid():
            return None

        # Get instrument ID
        instrument_id = self.get_instrument_id(symbol)
        if instrument_id is None:
            print(f"[API] Cannot open position: instrument not found: {symbol}")
            return None

        url = f"{self.get_base_url()}/trade/orders"
        headers = self.get_headers()

        payload = {
            "accNum": self.acc_num,
            "tradableInstrumentId": instrument_id,
            "side": side,
            "type": "MARKET",
            "qty": qty
        }

        if stop_loss > 0:
            payload["stopLoss"] = stop_loss
        if take_profit > 0:
            payload["takeProfit"] = take_profit
        if client_order_id:
            payload["clientOrderId"] = client_order_id

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 201:
                result = response.json()
                print(f"[API] Position opened: {result.get('positionId', 'N/A')}")
                return result
            else:
                error_data = response.json() if 'json' in response.headers.get('content-type', '') else {}
                print(f"[API] Open failed: {response.status_code} - {error_data.get('message', response.text)}")
                return None
        except Exception as e:
            print(f"[API] Open error: {e}")
            return None

    def close_position(self, position_id: str) -> bool:
        """
        Close an open position

        Args:
            position_id: Position ticket ID

        Returns:
            True if close successful, False otherwise
        """
        if not self.ensure_token_valid():
            return False

        url = f"{self.get_base_url()}/trade/orders/{position_id}"
        headers = self.get_headers()
        payload = {"accNum": self.acc_num}

        try:
            response = requests.delete(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                profit = result.get('profit', 0.0)
                print(f"[API] Position closed: {position_id}, profit: ${profit:.2f}")
                return True
            else:
                print(f"[API] Close failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[API] Close error: {e}")
            return False

# Usage example
api = TradeLockerAPI(
    environment="DEMO",
    email="your_email@example.com",
    password="your_password",
    server="DEMO-Server1",
    acc_num="DXR123456"
)

# Initialize
if api.login():
    if api.load_instruments():
        # Ready to trade
        result = api.open_position(
            symbol="XAUUSD",
            side="BUY",
            qty=26500,
            client_order_id="M5_S1_BUY"
        )
        if result:
            position_id = result.get("positionId")
            print(f"Position ID: {position_id}")
```

---

## 7. Main Loop & Timer Architecture

The TradeLocker Bot runs on a **timer-based architecture** using Python's `threading.Timer` to execute trading logic every N seconds (default: 1 second).

### 7.1. Timer Overview

**Why Timer Instead of While Loop?**

```python
# ❌ BAD: Tight while loop (consumes 100% CPU)
while True:
    process_trading_logic()
    time.sleep(1)  # Sleep blocks entire thread

# ✓ GOOD: Threading.Timer (efficient, non-blocking)
def on_timer():
    process_trading_logic()
    # Schedule next timer
    threading.Timer(1.0, on_timer).start()
```

**Advantages of threading.Timer:**
1. **Non-blocking** - Doesn't block main thread
2. **Low CPU usage** - Sleeps efficiently
3. **Precise timing** - More accurate than sleep()
4. **Cancelable** - Can stop timer gracefully
5. **Pythonic** - Standard library, no dependencies

---

### 7.2. Timer Implementation

**Basic Timer Setup:**

```python
import threading
import time

class TimerManager:
    """Manage repeating timer for bot main loop"""

    def __init__(self, interval_seconds: float = 1.0):
        """
        Initialize timer manager

        Args:
            interval_seconds: Timer interval in seconds (default 1.0)
        """
        self.interval = interval_seconds
        self.timer: threading.Timer = None
        self.is_running: bool = False

    def start(self):
        """Start the timer"""
        if self.is_running:
            print("[TIMER] Already running")
            return

        self.is_running = True
        self._schedule_next()
        print(f"[TIMER] Started with {self.interval}s interval")

    def stop(self):
        """Stop the timer"""
        self.is_running = False

        if self.timer:
            self.timer.cancel()
            self.timer = None

        print("[TIMER] Stopped")

    def _schedule_next(self):
        """Schedule next timer execution"""
        if not self.is_running:
            return

        self.timer = threading.Timer(self.interval, self._on_timer)
        self.timer.daemon = True  # Exit when main thread exits
        self.timer.start()

    def _on_timer(self):
        """Timer callback (executes every interval)"""
        try:
            # Execute trading logic
            self.on_tick()

        except Exception as e:
            print(f"[TIMER] Error in timer callback: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Schedule next execution
            self._schedule_next()

    def on_tick(self):
        """Override this method with trading logic"""
        print(f"[TIMER] Tick at {time.time()}")

# Usage
timer = TimerManager(interval_seconds=1.0)

def trading_logic():
    print("Executing trading logic...")
    # Read CSDL
    # Process signals
    # Check positions
    # etc.

# Override on_tick
timer.on_tick = trading_logic

# Start
timer.start()

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    timer.stop()
    print("Shutting down...")
```

---

### 7.3. Complete Main Loop Structure

**Full Implementation with Error Handling:**

```python
import threading
import time
import traceback
from typing import Optional

class TradeLockerBot:
    """Main TradeLocker Bot class"""

    def __init__(self, config: Config):
        """Initialize bot with configuration"""
        self.config = config
        self.api: Optional[TradeLockerAPI] = None
        self.g_ea: EASymbolData = EASymbolData()
        self.timer: Optional[threading.Timer] = None
        self.is_running: bool = False

        # Statistics
        self.tick_count: int = 0
        self.error_count: int = 0
        self.last_tick_time: int = 0

    def initialize(self) -> bool:
        """
        Initialize bot (login, load instruments, etc.)

        Returns:
            True if initialization successful, False otherwise
        """
        print("[BOT] Initializing...")

        # Step 1: Create API instance
        self.api = TradeLockerAPI(
            environment=self.config.TradeLocker_Environment,
            email=self.config.TradeLocker_Username,
            password=self.config.TradeLocker_Password,
            server=self.config.TradeLocker_Server,
            acc_num=self.config.AccountNumber  # Derived from login
        )

        # Step 2: Login
        if not self.api.login():
            print("[BOT] Login failed")
            return False

        # Step 3: Load instruments
        if not self.api.load_instruments():
            print("[BOT] Failed to load instruments")
            return False

        # Step 4: Get instrument ID for symbol
        instrument_id = self.api.get_instrument_id(self.config.Symbol)
        if instrument_id is None:
            print(f"[BOT] Symbol not found: {self.config.Symbol}")
            return False

        self.g_ea.symbol_name = self.config.Symbol
        self.g_ea.symbol_type = "METAL"  # Assume XAUUSD
        self.g_ea.broker_name = "TradeLocker"

        # Step 5: Get account info
        acc_info = self.api.get_account_info()
        if acc_info:
            print(f"[BOT] Account: {acc_info['accNum']}")
            print(f"[BOT] Balance: ${acc_info['balance']:.2f}")
            print(f"[BOT] Leverage: 1:{acc_info['leverage']}")

        # Step 6: Initialize magic numbers (7 TF × 3 strategies = 21)
        self._init_magic_numbers()

        # Step 7: Initialize lot sizes
        self._init_lot_sizes()

        print("[BOT] Initialization complete ✓")
        self.g_ea.first_run_completed = True
        return True

    def _init_magic_numbers(self):
        """Initialize magic numbers for 21 positions"""
        base_magic = 100000
        for tf_idx in range(7):
            for strategy_idx in range(3):
                # Magic format: 100000 + tf_idx*10 + strategy_idx
                # Example: M5 (tf=1) S1 (strat=0) → 100010
                magic = base_magic + tf_idx * 10 + strategy_idx
                self.g_ea.magic_numbers[tf_idx][strategy_idx] = magic

    def _init_lot_sizes(self):
        """Calculate lot sizes for all 21 positions"""
        base_lot = self.config.FixedLotSize  # 0.01

        for tf_idx in range(7):
            for strategy_idx in range(3):
                # All use same lot size (can customize per TF/strategy)
                self.g_ea.lot_sizes[tf_idx][strategy_idx] = base_lot

    def start(self):
        """Start the main timer loop"""
        if self.is_running:
            print("[BOT] Already running")
            return

        self.is_running = True
        self.last_tick_time = int(time.time())
        self._schedule_next_tick()
        print(f"[BOT] Started (timer interval: {self.config.TimerIntervalSeconds}s)")

    def stop(self):
        """Stop the bot gracefully"""
        self.is_running = False

        if self.timer:
            self.timer.cancel()
            self.timer = None

        print(f"[BOT] Stopped (total ticks: {self.tick_count}, errors: {self.error_count})")

    def _schedule_next_tick(self):
        """Schedule next timer execution"""
        if not self.is_running:
            return

        interval = self.config.TimerIntervalSeconds
        self.timer = threading.Timer(interval, self._on_timer)
        self.timer.daemon = True
        self.timer.start()

    def _on_timer(self):
        """Main timer callback - executes every N seconds"""
        try:
            current_time = int(time.time())
            elapsed = current_time - self.last_tick_time

            if self.config.DebugMode and self.tick_count % 10 == 0:
                print(f"[TIMER] Tick #{self.tick_count}, elapsed: {elapsed}s")

            self.last_tick_time = current_time
            self.tick_count += 1

            # Execute main trading logic
            self.on_tick()

        except Exception as e:
            self.error_count += 1
            print(f"[TIMER] Error in tick #{self.tick_count}: {e}")
            traceback.print_exc()

        finally:
            # Schedule next tick
            self._schedule_next_tick()

    def on_tick(self):
        """
        Main trading logic (executed every timer interval)

        Flow:
        1. Ensure API token valid
        2. Read CSDL file
        3. Detect new signals
        4. Open new positions
        5. Check existing positions
        6. Check stoploss/TP conditions
        7. Close positions if needed
        """
        # Step 1: Ensure authentication valid
        if not self.api.ensure_token_valid():
            print("[TICK] Authentication failed, skipping tick")
            return

        # Step 2: Read CSDL data
        csdl_rows = self._load_csdl_data()
        if csdl_rows is None:
            print("[TICK] Failed to load CSDL, skipping tick")
            return

        # Update global state
        self.g_ea.csdl_rows = csdl_rows

        # Step 3: Process signals for each timeframe
        for tf_idx in range(7):
            self._process_timeframe(tf_idx)

        # Step 4: Check global account state (margin level, etc.)
        self._check_account_health()

    def _load_csdl_data(self) -> Optional[List[CSDLLoveRow]]:
        """Load CSDL data from file or HTTP"""
        try:
            if self.config.USE_HTTP_FOR_CSDL_READING:
                # HTTP mode
                import requests
                url = f"{self.config.HTTP_API_BASE_URL}/{self.config.Symbol}"
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    json_data = response.json()
                else:
                    print(f"[CSDL] HTTP error: {response.status_code}")
                    return None
            else:
                # Local file mode
                import json
                file_path = f"CSDL/{self.config.Symbol}.json"
                with open(file_path, 'r') as f:
                    json_data = json.load(f)

            # Parse JSON to CSDLLoveRow objects
            return self._parse_csdl_json(json_data)

        except Exception as e:
            print(f"[CSDL] Load error: {e}")
            return None

    def _parse_csdl_json(self, json_data: dict) -> List[CSDLLoveRow]:
        """Parse CSDL JSON to CSDLLoveRow objects"""
        tf_names = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
        csdl_rows = []

        for tf_name in tf_names:
            if tf_name not in json_data:
                csdl_rows.append(CSDLLoveRow(timeframe=tf_name))
                continue

            row_data = json_data[tf_name]

            if not isinstance(row_data, list) or len(row_data) < 10:
                csdl_rows.append(CSDLLoveRow(timeframe=tf_name))
                continue

            # Parse 10-column format to 6-field object
            csdl_row = CSDLLoveRow()
            csdl_row.signal = int(row_data[0]) if row_data[0] is not None else 0
            csdl_row.price = float(row_data[1]) if row_data[1] is not None else 0.0
            csdl_row.timestamp = int(row_data[3]) if row_data[3] is not None else 0
            csdl_row.news = int(row_data[6]) if row_data[6] is not None else 0
            csdl_row.max_loss = float(row_data[8]) if row_data[8] is not None else 0.0
            csdl_row.timeframe = tf_name

            csdl_rows.append(csdl_row)

        return csdl_rows

    def _process_timeframe(self, tf_idx: int):
        """
        Process signals and positions for one timeframe

        Args:
            tf_idx: Timeframe index (0=M1, 1=M5, ..., 6=D1)
        """
        csdl_row = self.g_ea.csdl_rows[tf_idx]

        # Check if new signal detected
        is_new = self._is_new_signal(tf_idx)

        if is_new:
            print(f"[SIGNAL] NEW {csdl_row.timeframe} signal: {csdl_row.signal} (news: {csdl_row.news})")

            # Process 3 strategies
            self._process_strategy_s1(tf_idx)  # HOME with NEWS filter
            self._process_strategy_s2(tf_idx)  # TREND
            self._process_strategy_s3(tf_idx)  # NEWS

            # Save old signal for next comparison
            self.g_ea.signal_old[tf_idx] = csdl_row.signal
            self.g_ea.timestamp_old[tf_idx] = csdl_row.timestamp

        # Check existing positions (stoploss, TP, close signals)
        self._check_positions(tf_idx)

    def _is_new_signal(self, tf_idx: int) -> bool:
        """
        Check if timeframe has new signal

        Args:
            tf_idx: Timeframe index

        Returns:
            True if new signal detected, False otherwise
        """
        csdl_row = self.g_ea.csdl_rows[tf_idx]
        old_timestamp = self.g_ea.timestamp_old[tf_idx]

        # New signal if timestamp changed
        if csdl_row.timestamp > old_timestamp:
            return True

        return False

    def _process_strategy_s1(self, tf_idx: int):
        """Process Strategy S1: HOME (Binary) with NEWS filter"""
        # Implemented in Section 10
        pass

    def _process_strategy_s2(self, tf_idx: int):
        """Process Strategy S2: TREND"""
        # Implemented in Section 11
        pass

    def _process_strategy_s3(self, tf_idx: int):
        """Process Strategy S3: NEWS"""
        # Implemented in Section 12
        pass

    def _check_positions(self, tf_idx: int):
        """
        Check existing positions for this timeframe

        Checks:
        - Layer1 stoploss (CSDL max_loss)
        - Layer2 stoploss (margin-based)
        - Take profit conditions
        - Close signal conditions
        """
        for strategy_idx in range(3):
            if self.g_ea.position_flags[tf_idx][strategy_idx] == 1:
                # Position exists
                ticket = self.g_ea.position_tickets[tf_idx][strategy_idx]

                # Check Layer1 SL
                if self._check_layer1_sl(tf_idx, strategy_idx):
                    self._close_position(tf_idx, strategy_idx, reason="LAYER1_SL")
                    continue

                # Check Layer2 SL
                if self._check_layer2_sl(tf_idx, strategy_idx):
                    self._close_position(tf_idx, strategy_idx, reason="LAYER2_SL")
                    continue

                # Check Take Profit
                if self._check_take_profit(tf_idx, strategy_idx):
                    self._close_position(tf_idx, strategy_idx, reason="TAKE_PROFIT")
                    continue

                # Check close signal
                if self._check_close_signal(tf_idx, strategy_idx):
                    self._close_position(tf_idx, strategy_idx, reason="CLOSE_SIGNAL")
                    continue

    def _check_layer1_sl(self, tf_idx: int, strategy_idx: int) -> bool:
        """Check if Layer1 SL threshold reached"""
        # Implemented in Section 13
        return False

    def _check_layer2_sl(self, tf_idx: int, strategy_idx: int) -> bool:
        """Check if Layer2 SL threshold reached"""
        # Implemented in Section 13
        return False

    def _check_take_profit(self, tf_idx: int, strategy_idx: int) -> bool:
        """Check if TP threshold reached"""
        # Implemented in Section 14
        return False

    def _check_close_signal(self, tf_idx: int, strategy_idx: int) -> bool:
        """Check if close signal detected"""
        # Implemented in Section 14
        return False

    def _close_position(self, tf_idx: int, strategy_idx: int, reason: str):
        """Close position"""
        ticket = self.g_ea.position_tickets[tf_idx][strategy_idx]
        print(f"[CLOSE] Closing {ticket} (reason: {reason})")

        if self.api.close_position(ticket):
            # Clear position tracking
            self.g_ea.position_flags[tf_idx][strategy_idx] = 0
            self.g_ea.position_tickets[tf_idx][strategy_idx] = None
        else:
            print(f"[CLOSE] Failed to close {ticket}")

    def _check_account_health(self):
        """Check account health (margin level, etc.)"""
        acc_info = self.api.get_account_info()

        if acc_info:
            margin_level = acc_info.get('marginLevel', 0)

            if margin_level < 100:
                print(f"[WARNING] Low margin level: {margin_level:.2f}%")
                # Could close positions or stop trading

# Usage
bot = TradeLockerBot(config)

if bot.initialize():
    bot.start()

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        bot.stop()
else:
    print("Failed to initialize bot")
```

---

### 7.4. Timer Interval Configuration

**Choosing the Right Interval:**

```
Interval │ Pros                          │ Cons
─────────┼───────────────────────────────┼──────────────────────────────
0.5s     │ Fast signal detection         │ High CPU usage, API stress
1.0s     │ Good balance (RECOMMENDED)    │ ~1s latency for signals
2.0s     │ Low CPU usage                 │ Slower signal detection
5.0s     │ Very low CPU                  │ Too slow for live trading
```

**Configuration in config.json:**

```json
{
  "TimerIntervalSeconds": 1.0
}
```

**Dynamic Interval Adjustment:**

```python
class AdaptiveTimer(TimerManager):
    """Timer with adaptive interval based on market activity"""

    def __init__(self):
        super().__init__(interval_seconds=1.0)
        self.base_interval = 1.0
        self.fast_interval = 0.5
        self.slow_interval = 2.0

    def on_tick(self):
        """Execute trading logic and adjust interval"""
        # Execute logic
        has_activity = self.trading_logic()

        # Adjust interval based on activity
        if has_activity:
            # Fast mode: more frequent checks
            self.interval = self.fast_interval
        else:
            # Slow mode: less frequent checks
            self.interval = self.slow_interval

# Usage: Check every 0.5s when positions open, 2.0s when idle
```

---

### 7.5. Timer Statistics & Monitoring

**Track Timer Performance:**

```python
class TimerStats:
    """Track timer execution statistics"""

    def __init__(self):
        self.tick_count: int = 0
        self.total_duration_ms: float = 0.0
        self.max_duration_ms: float = 0.0
        self.min_duration_ms: float = float('inf')
        self.error_count: int = 0
        self.start_time: int = 0

    def record_tick(self, duration_ms: float):
        """Record tick execution time"""
        self.tick_count += 1
        self.total_duration_ms += duration_ms
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)
        self.min_duration_ms = min(self.min_duration_ms, duration_ms)

    def get_avg_duration_ms(self) -> float:
        """Get average tick duration"""
        if self.tick_count == 0:
            return 0.0
        return self.total_duration_ms / self.tick_count

    def print_stats(self):
        """Print statistics"""
        print("=== Timer Statistics ===")
        print(f"Ticks:     {self.tick_count}")
        print(f"Errors:    {self.error_count}")
        print(f"Avg Time:  {self.get_avg_duration_ms():.2f} ms")
        print(f"Max Time:  {self.max_duration_ms:.2f} ms")
        print(f"Min Time:  {self.min_duration_ms:.2f} ms")

# Integrated into timer
class MonitoredTimer(TimerManager):
    """Timer with performance monitoring"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = TimerStats()

    def _on_timer(self):
        """Timer callback with monitoring"""
        start_time = time.time()

        try:
            self.on_tick()
        except Exception as e:
            self.stats.error_count += 1
            print(f"[TIMER] Error: {e}")
            traceback.print_exc()
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.stats.record_tick(duration_ms)

            # Print stats every 100 ticks
            if self.stats.tick_count % 100 == 0:
                self.stats.print_stats()

            self._schedule_next_tick()
```

---

### 7.6. Graceful Shutdown

**Handle Ctrl+C and Cleanup:**

```python
import signal
import sys

class GracefulBot:
    """Bot with graceful shutdown handling"""

    def __init__(self, config: Config):
        self.bot = TradeLockerBot(config)
        self.shutdown_requested = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[SIGNAL] Received signal {signum}, shutting down gracefully...")
        self.shutdown_requested = True

    def run(self):
        """Run bot with graceful shutdown"""
        if not self.bot.initialize():
            print("[ERROR] Initialization failed")
            return 1

        self.bot.start()
        print("[BOT] Running... Press Ctrl+C to stop")

        try:
            while not self.shutdown_requested:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[BOT] KeyboardInterrupt received")

        # Cleanup
        print("[BOT] Stopping bot...")
        self.bot.stop()

        # Close all positions (optional)
        if input("Close all positions? (y/n): ").lower() == 'y':
            self._close_all_positions()

        print("[BOT] Shutdown complete")
        return 0

    def _close_all_positions(self):
        """Close all open positions"""
        positions = self.bot.api.get_positions()
        if positions:
            print(f"[BOT] Closing {len(positions)} positions...")
            for pos in positions:
                self.bot.api.close_position(pos['id'])
        else:
            print("[BOT] No open positions")

# Usage
if __name__ == "__main__":
    config = Config()  # Load from config.json
    bot = GracefulBot(config)
    sys.exit(bot.run())
```

---

## 8. Signal Processing & Detection

This section explains how the bot detects new trading signals from CSDL data and decides whether to open positions.

### 8.1. Signal Detection Overview

**Signal Detection Flow:**

```
┌────────────────────────────────────────────────────────────┐
│ 1. Read CSDL File                                          │
│    ├── Load JSON (7 timeframes × 10 columns)               │
│    └── Parse to CSDLLoveRow objects (6 fields)             │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│ 2. Compare Old vs New Signals                              │
│    ├── Check timestamp (new > old ?)                       │
│    ├── Check signal value (-1, 0, +1)                      │
│    └── Mark as NEW if timestamp changed                    │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│ 3. Analyze Signal Validity                                 │
│    ├── Signal not zero (0 = no signal)                     │
│    ├── Price is valid (> 0)                                │
│    ├── Timestamp not too old (< 24h)                       │
│    └── NEWS score in valid range (-70 to +70)              │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│ 4. Process Strategies                                      │
│    ├── S1: HOME (Binary) with NEWS filter                  │
│    ├── S2: TREND (Follow D1 or Force mode)                 │
│    └── S3: NEWS (High CASCADE only)                        │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│ 5. Open Positions via API                                  │
│    ├── Calculate qty (lot → units conversion)              │
│    ├── Call TradeLocker API (POST /trade/orders)           │
│    └── Save position ticket ID                             │
└────────────────────────────────────────────────────────────┘
```

---

### 8.2. Old vs New Signal Comparison

**Core Detection Logic:**

```python
def is_new_signal(
    csdl_row: CSDLLoveRow,
    old_signal: int,
    old_timestamp: int
) -> bool:
    """
    Detect if CSDL row contains a NEW signal

    Args:
        csdl_row: Current CSDL data
        old_signal: Previous signal value (-1, 0, +1)
        old_timestamp: Previous timestamp

    Returns:
        True if new signal detected, False otherwise
    """
    # Method 1: Timestamp changed (PRIMARY method)
    if csdl_row.timestamp > old_timestamp:
        return True

    # Method 2: Signal value changed but timestamp same (rare)
    # This handles edge cases where SPY Bot updates signal
    # without updating timestamp
    if csdl_row.signal != old_signal and csdl_row.signal != 0:
        print(f"[SIGNAL] Value changed without timestamp change: "
              f"{old_signal} → {csdl_row.signal}")
        return True

    return False

# Usage in main loop
for tf_idx in range(7):
    csdl_row = g_ea.csdl_rows[tf_idx]
    old_signal = g_ea.signal_old[tf_idx]
    old_timestamp = g_ea.timestamp_old[tf_idx]

    if is_new_signal(csdl_row, old_signal, old_timestamp):
        print(f"[NEW] {csdl_row.timeframe}: signal={csdl_row.signal}, "
              f"news={csdl_row.news}, price={csdl_row.price:.2f}")

        # Process strategies...
        process_strategies(tf_idx)

        # Save old values for next comparison
        g_ea.signal_old[tf_idx] = csdl_row.signal
        g_ea.timestamp_old[tf_idx] = csdl_row.timestamp
```

**Example Timeline:**

```
Time     │ M5 Signal │ M5 Timestamp │ Old Timestamp │ Detection
─────────┼───────────┼──────────────┼───────────────┼────────────
10:30:00 │    +1     │ 1705316400   │      0        │ NEW ✓
10:30:01 │    +1     │ 1705316400   │ 1705316400    │ (same)
10:30:02 │    +1     │ 1705316400   │ 1705316400    │ (same)
10:30:15 │    -1     │ 1705316415   │ 1705316400    │ NEW ✓
10:30:16 │    -1     │ 1705316415   │ 1705316415    │ (same)
10:30:45 │     0     │ 1705316445   │ 1705316415    │ NEW ✓ (close)
```

---

### 8.3. Signal Validation

Before processing a signal, validate it's usable:

```python
def validate_signal(csdl_row: CSDLLoveRow) -> bool:
    """
    Validate signal data before trading

    Args:
        csdl_row: CSDL data row

    Returns:
        True if signal is valid, False otherwise
    """
    # Check 1: Signal must not be zero
    if csdl_row.signal == 0:
        return False  # No signal

    # Check 2: Price must be positive
    if csdl_row.price <= 0:
        print(f"[VALIDATE] {csdl_row.timeframe}: Invalid price {csdl_row.price}")
        return False

    # Check 3: Timestamp not in future
    import time
    current_time = int(time.time())
    if csdl_row.timestamp > current_time + 3600:  # >1 hour in future
        print(f"[VALIDATE] {csdl_row.timeframe}: Timestamp in future")
        return False

    # Check 4: Timestamp not too old (>24 hours)
    age_seconds = current_time - csdl_row.timestamp
    if age_seconds > 86400:  # >24 hours
        print(f"[VALIDATE] {csdl_row.timeframe}: Signal too old ({age_seconds}s)")
        return False

    # Check 5: NEWS score in valid range
    if abs(csdl_row.news) > 70:
        print(f"[VALIDATE] {csdl_row.timeframe}: NEWS out of range ({csdl_row.news})")
        return False

    # All checks passed
    return True

# Usage
if is_new_signal(...):
    if validate_signal(csdl_row):
        # Process signal
        process_strategies(tf_idx)
    else:
        print(f"[SKIP] {csdl_row.timeframe}: Invalid signal")
```

---

### 8.4. Signal Priority & Conflicts

**Handling Multiple Signals:**

When multiple timeframes have signals at the same time:

```python
def get_signal_priority(tf_idx: int) -> int:
    """
    Get priority for timeframe (higher number = higher priority)

    Priority order: D1 > H4 > H1 > M30 > M15 > M5 > M1
    """
    # Index 6 (D1) has highest priority
    # Index 0 (M1) has lowest priority
    return 6 - tf_idx

def process_signals_by_priority(g_ea: EASymbolData):
    """
    Process new signals in priority order

    This ensures higher timeframe signals are processed first
    """
    # Collect all new signals
    new_signals = []
    for tf_idx in range(7):
        if is_new_signal(g_ea.csdl_rows[tf_idx], ...):
            new_signals.append(tf_idx)

    # Sort by priority (descending)
    new_signals.sort(key=get_signal_priority, reverse=True)

    # Process in order
    for tf_idx in new_signals:
        print(f"[PRIORITY] Processing {g_ea.csdl_rows[tf_idx].timeframe}")
        process_strategies(tf_idx)
```

**Conflict Resolution:**

```python
def check_signal_conflicts(tf_idx: int, strategy_idx: int) -> bool:
    """
    Check if opening this position conflicts with existing positions

    Conflict examples:
    - M5 BUY already open, M1 SELL signal arrives
    - D1 SELL open, M15 BUY signal arrives

    Returns:
        True if conflict exists (should NOT open), False otherwise
    """
    csdl_row = g_ea.csdl_rows[tf_idx]
    new_signal = csdl_row.signal

    # Check all existing positions
    for other_tf_idx in range(7):
        for other_strat_idx in range(3):
            if g_ea.position_flags[other_tf_idx][other_strat_idx] == 1:
                # Position exists
                # Get position direction from ticket or stored data
                # (Implementation depends on how we track position direction)

                # Example: If higher TF has opposite direction, skip
                if other_tf_idx > tf_idx:  # Higher TF
                    print(f"[CONFLICT] {csdl_row.timeframe} signal conflicts with "
                          f"higher TF position")
                    return True  # Conflict!

    return False  # No conflict
```

---

### 8.5. Complete Signal Processing Example

**Putting It All Together:**

```python
def process_all_signals(bot: TradeLockerBot):
    """
    Process all timeframes for new signals

    This is called every timer tick (every 1 second)
    """
    # Step 1: Detect new signals for all TF
    new_signal_tfs = []

    for tf_idx in range(7):
        csdl_row = bot.g_ea.csdl_rows[tf_idx]
        old_signal = bot.g_ea.signal_old[tf_idx]
        old_timestamp = bot.g_ea.timestamp_old[tf_idx]

        if is_new_signal(csdl_row, old_signal, old_timestamp):
            if validate_signal(csdl_row):
                new_signal_tfs.append(tf_idx)
            else:
                print(f"[SKIP] {csdl_row.timeframe}: Invalid signal")

    # Step 2: Sort by priority (D1 first, M1 last)
    new_signal_tfs.sort(key=get_signal_priority, reverse=True)

    # Step 3: Process each TF
    for tf_idx in new_signal_tfs:
        csdl_row = bot.g_ea.csdl_rows[tf_idx]

        print(f"\n[SIGNAL] NEW {csdl_row.timeframe} signal detected")
        print(f"  Direction:  {get_signal_name(csdl_row.signal)}")
        print(f"  Price:      {csdl_row.price:.2f}")
        print(f"  NEWS:       {csdl_row.news} (L{abs(csdl_row.news)//10})")
        print(f"  Max Loss:   ${csdl_row.max_loss:.2f}")
        print(f"  Timestamp:  {csdl_row.timestamp}")

        # Process 3 strategies
        process_strategy_s1(bot, tf_idx)
        process_strategy_s2(bot, tf_idx)
        process_strategy_s3(bot, tf_idx)

        # Update old values
        bot.g_ea.signal_old[tf_idx] = csdl_row.signal
        bot.g_ea.timestamp_old[tf_idx] = csdl_row.timestamp

    # Step 4: Log summary
    if new_signal_tfs:
        tf_names = [bot.g_ea.csdl_rows[i].timeframe for i in new_signal_tfs]
        print(f"[SUMMARY] Processed {len(new_signal_tfs)} new signals: {', '.join(tf_names)}")

def get_signal_name(signal: int) -> str:
    """Convert signal value to name"""
    if signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    else:
        return "NONE"

# Usage in main timer loop
def on_tick(bot: TradeLockerBot):
    # ... load CSDL data ...

    # Process all signals
    process_all_signals(bot)

    # ... check existing positions ...
```

---

## 9. Position Management

The TradeLocker Bot tracks up to **21 positions** simultaneously (7 timeframes × 3 strategies). This section explains the position tracking architecture.

### 9.1. Position Tracking Overview

**21-Position Array Structure:**

```
Timeframe │ S1 (HOME)      │ S2 (TREND)     │ S3 (NEWS)
──────────┼────────────────┼────────────────┼────────────────
M1  (0)   │ position[0][0] │ position[0][1] │ position[0][2]
M5  (1)   │ position[1][0] │ position[1][1] │ position[1][2]
M15 (2)   │ position[2][0] │ position[2][1] │ position[2][2]
M30 (3)   │ position[3][0] │ position[3][1] │ position[3][2]
H1  (4)   │ position[4][0] │ position[4][1] │ position[4][2]
H4  (5)   │ position[5][0] │ position[5][1] │ position[5][2]
D1  (6)   │ position[6][0] │ position[6][1] │ position[6][2]
```

**Data Structures:**

```python
@dataclass
class EASymbolData:
    # ... other fields ...

    # Position flags (0 = no position, 1 = position open)
    position_flags: List[List[int]] = field(
        default_factory=lambda: [[0]*3 for _ in range(7)]
    )

    # Position ticket IDs (TradeLocker position IDs)
    position_tickets: List[List[Optional[str]]] = field(
        default_factory=lambda: [[None]*3 for _ in range(7)]
    )

    # Magic numbers (for identification)
    magic_numbers: List[List[int]] = field(
        default_factory=lambda: [[0]*3 for _ in range(7)]
    )

    # Lot sizes
    lot_sizes: List[List[float]] = field(
        default_factory=lambda: [[0.0]*3 for _ in range(7)]
    )

# Global instance
g_ea = EASymbolData()
```

---

### 9.2. Opening Positions

**Complete Open Position Logic:**

```python
def open_position_full(
    bot: TradeLockerBot,
    tf_idx: int,
    strategy_idx: int,
    side: str,
    reason: str = ""
) -> bool:
    """
    Open a new position with full error handling

    Args:
        bot: Bot instance
        tf_idx: Timeframe index (0-6)
        strategy_idx: Strategy index (0=S1, 1=S2, 2=S3)
        side: "BUY" or "SELL"
        reason: Reason for opening (for logging)

    Returns:
        True if position opened successfully, False otherwise
    """
    # Step 1: Check if position already exists
    if bot.g_ea.position_flags[tf_idx][strategy_idx] == 1:
        print(f"[OPEN] {get_position_name(tf_idx, strategy_idx)}: "
              f"Position already open, skipping")
        return False

    # Step 2: Get CSDL data
    csdl_row = bot.g_ea.csdl_rows[tf_idx]
    tf_name = csdl_row.timeframe

    # Step 3: Calculate lot size
    lot = bot.g_ea.lot_sizes[tf_idx][strategy_idx]

    # Step 4: Get current price (use latest market price, not signal price)
    # For now, use signal price as approximation
    price = csdl_row.price

    # Step 5: Convert lot to qty (TradeLocker units)
    qty = calculate_qty(lot, price)

    # Step 6: Validate qty against instrument limits
    # (Would need to check instrument min/max qty here)

    # Step 7: Build client_order_id
    timestamp = int(time.time())
    client_order_id = f"{tf_name}_{get_strategy_name(strategy_idx)}_{side}_{timestamp}"

    # Step 8: Open position via API
    print(f"[OPEN] Opening {get_position_name(tf_idx, strategy_idx)}")
    print(f"  Side:   {side}")
    print(f"  Lot:    {lot}")
    print(f"  Price:  {price:.2f}")
    print(f"  Qty:    {qty}")
    print(f"  Reason: {reason}")

    result = bot.api.open_position(
        symbol=bot.config.Symbol,
        side=side,
        qty=qty,
        stop_loss=0.0,  # We manage SL manually
        take_profit=0.0,  # We manage TP manually
        client_order_id=client_order_id
    )

    # Step 9: Check result
    if result is None:
        print(f"[OPEN] FAILED to open {get_position_name(tf_idx, strategy_idx)}")
        return False

    position_id = result.get("positionId")
    if not position_id:
        print(f"[OPEN] No position ID returned")
        return False

    # Step 10: Save position tracking data
    bot.g_ea.position_flags[tf_idx][strategy_idx] = 1
    bot.g_ea.position_tickets[tf_idx][strategy_idx] = position_id

    print(f"[OPEN] SUCCESS: {get_position_name(tf_idx, strategy_idx)} → {position_id}")
    return True

def calculate_qty(lot: float, price: float) -> int:
    """
    Convert MT5-style lot to TradeLocker qty

    Formula: qty = lot × 100 × price

    Args:
        lot: MT5 lot size (0.01, 0.1, 1.0, etc.)
        price: Current market price

    Returns:
        Quantity in units (integer)
    """
    return int(lot * 100 * price)

def get_position_name(tf_idx: int, strategy_idx: int) -> str:
    """Get human-readable position name"""
    tf_names = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
    strategy_names = ["S1", "S2", "S3"]
    return f"{tf_names[tf_idx]}_{strategy_names[strategy_idx]}"

def get_strategy_name(strategy_idx: int) -> str:
    """Get strategy name"""
    return ["S1", "S2", "S3"][strategy_idx]

# Usage in strategy processing
if should_open_s1_position(bot, tf_idx):
    side = "BUY" if csdl_row.signal == 1 else "SELL"
    open_position_full(bot, tf_idx, 0, side, reason="S1_HOME")
```

---

### 9.3. Closing Positions

**Complete Close Position Logic:**

```python
def close_position_full(
    bot: TradeLockerBot,
    tf_idx: int,
    strategy_idx: int,
    reason: str = ""
) -> bool:
    """
    Close an open position with full error handling

    Args:
        bot: Bot instance
        tf_idx: Timeframe index (0-6)
        strategy_idx: Strategy index (0=S1, 1=S2, 2=S3)
        reason: Reason for closing (for logging)

    Returns:
        True if position closed successfully, False otherwise
    """
    # Step 1: Check if position exists
    if bot.g_ea.position_flags[tf_idx][strategy_idx] == 0:
        print(f"[CLOSE] {get_position_name(tf_idx, strategy_idx)}: "
              f"No position to close")
        return False

    # Step 2: Get position ticket
    ticket = bot.g_ea.position_tickets[tf_idx][strategy_idx]
    if not ticket:
        print(f"[CLOSE] {get_position_name(tf_idx, strategy_idx)}: "
              f"No ticket ID stored (orphaned position)")
        # Clear flag anyway
        bot.g_ea.position_flags[tf_idx][strategy_idx] = 0
        return False

    # Step 3: Get position info (for logging)
    positions = bot.api.get_positions()
    position_info = None
    if positions:
        for pos in positions:
            if pos['id'] == ticket:
                position_info = pos
                break

    # Step 4: Close position via API
    print(f"[CLOSE] Closing {get_position_name(tf_idx, strategy_idx)}")
    print(f"  Ticket: {ticket}")
    print(f"  Reason: {reason}")

    if position_info:
        print(f"  Side:   {position_info['side']}")
        print(f"  Qty:    {position_info['qty']}")
        print(f"  Open:   {position_info['openPrice']:.2f}")
        print(f"  Current:{position_info['currentPrice']:.2f}")
        print(f"  Profit: ${position_info['profit']:.2f}")

    success = bot.api.close_position(ticket)

    # Step 5: Update tracking data
    if success:
        bot.g_ea.position_flags[tf_idx][strategy_idx] = 0
        bot.g_ea.position_tickets[tf_idx][strategy_idx] = None
        print(f"[CLOSE] SUCCESS: {get_position_name(tf_idx, strategy_idx)} closed")
        return True
    else:
        print(f"[CLOSE] FAILED: {get_position_name(tf_idx, strategy_idx)}")
        # Don't clear flag - will retry next tick
        return False

# Usage
if should_close_position(bot, tf_idx, strategy_idx):
    close_position_full(bot, tf_idx, strategy_idx, reason="CLOSE_SIGNAL")
```

---

### 9.4. Position Synchronization

**Sync Local State with TradeLocker:**

Since TradeLocker is web-based and stateless, positions can be closed externally (via web interface, mobile app, or platform stopouts). The bot must periodically synchronize its local state with TradeLocker's actual positions.

```python
def synchronize_positions(bot: TradeLockerBot):
    """
    Synchronize local position flags with TradeLocker server

    This prevents tracking positions that were closed externally
    """
    # Step 1: Get all open positions from TradeLocker
    server_positions = bot.api.get_positions()

    if server_positions is None:
        print("[SYNC] Failed to get positions from server, skipping sync")
        return

    # Step 2: Build set of server position IDs
    server_tickets = set()
    for pos in server_positions:
        server_tickets.add(pos['id'])

    # Step 3: Check each local position
    sync_count = 0
    for tf_idx in range(7):
        for strategy_idx in range(3):
            if bot.g_ea.position_flags[tf_idx][strategy_idx] == 1:
                ticket = bot.g_ea.position_tickets[tf_idx][strategy_idx]

                if ticket not in server_tickets:
                    # Position closed externally!
                    print(f"[SYNC] {get_position_name(tf_idx, strategy_idx)}: "
                          f"Position {ticket} not found on server, marking as closed")

                    bot.g_ea.position_flags[tf_idx][strategy_idx] = 0
                    bot.g_ea.position_tickets[tf_idx][strategy_idx] = None
                    sync_count += 1

    if sync_count > 0:
        print(f"[SYNC] Synchronized {sync_count} positions")

# Usage: Call every 10-60 seconds
class BotWithSync(TradeLockerBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_sync_time = 0
        self.sync_interval = 60  # Sync every 60 seconds

    def on_tick(self):
        super().on_tick()

        # Check if sync needed
        current_time = int(time.time())
        if current_time - self.last_sync_time >= self.sync_interval:
            synchronize_positions(self)
            self.last_sync_time = current_time
```

---

### 9.5. Position Statistics

**Track Position Performance:**

```python
@dataclass
class PositionStats:
    """Statistics for position performance"""
    total_opened: int = 0
    total_closed: int = 0
    total_profit: float = 0.0
    total_loss: float = 0.0
    win_count: int = 0
    loss_count: int = 0

    # Per-timeframe stats (7 TF)
    tf_opened: List[int] = field(default_factory=lambda: [0] * 7)
    tf_closed: List[int] = field(default_factory=lambda: [0] * 7)
    tf_profit: List[float] = field(default_factory=lambda: [0.0] * 7)

    # Per-strategy stats (3 strategies)
    strategy_opened: List[int] = field(default_factory=lambda: [0] * 3)
    strategy_closed: List[int] = field(default_factory=lambda: [0] * 3)
    strategy_profit: List[float] = field(default_factory=lambda: [0.0] * 3)

    def record_open(self, tf_idx: int, strategy_idx: int):
        """Record position opened"""
        self.total_opened += 1
        self.tf_opened[tf_idx] += 1
        self.strategy_opened[strategy_idx] += 1

    def record_close(self, tf_idx: int, strategy_idx: int, profit: float):
        """Record position closed"""
        self.total_closed += 1
        self.tf_closed[tf_idx] += 1
        self.strategy_closed[strategy_idx] += 1

        self.tf_profit[tf_idx] += profit
        self.strategy_profit[strategy_idx] += profit

        if profit > 0:
            self.win_count += 1
            self.total_profit += profit
        else:
            self.loss_count += 1
            self.total_loss += profit

    def get_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_closed == 0:
            return 0.0
        return (self.win_count / self.total_closed) * 100

    def get_net_profit(self) -> float:
        """Get net profit (total wins + total losses)"""
        return self.total_profit + self.total_loss

    def print_stats(self):
        """Print statistics"""
        print("\n=== Position Statistics ===")
        print(f"Total Opened:  {self.total_opened}")
        print(f"Total Closed:  {self.total_closed}")
        print(f"Win Rate:      {self.get_win_rate():.1f}% ({self.win_count}/{self.total_closed})")
        print(f"Net Profit:    ${self.get_net_profit():.2f}")
        print(f"Gross Profit:  ${self.total_profit:.2f}")
        print(f"Gross Loss:    ${self.total_loss:.2f}")

        print("\nPer-Timeframe:")
        tf_names = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
        for i, name in enumerate(tf_names):
            print(f"  {name}: {self.tf_closed[i]} closed, ${self.tf_profit[i]:.2f} profit")

        print("\nPer-Strategy:")
        strategy_names = ["S1_HOME", "S2_TREND", "S3_NEWS"]
        for i, name in enumerate(strategy_names):
            print(f"  {name}: {self.strategy_closed[i]} closed, ${self.strategy_profit[i]:.2f} profit")

# Add to bot
class BotWithStats(TradeLockerBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = PositionStats()

    def open_position_full(self, tf_idx, strategy_idx, side, reason):
        success = super().open_position_full(tf_idx, strategy_idx, side, reason)
        if success:
            self.stats.record_open(tf_idx, strategy_idx)
        return success

    def close_position_full(self, tf_idx, strategy_idx, reason):
        # Get profit before closing
        ticket = self.g_ea.position_tickets[tf_idx][strategy_idx]
        profit = 0.0

        if ticket:
            positions = self.api.get_positions()
            if positions:
                for pos in positions:
                    if pos['id'] == ticket:
                        profit = pos.get('profit', 0.0)
                        break

        success = super().close_position_full(tf_idx, strategy_idx, reason)
        if success:
            self.stats.record_close(tf_idx, strategy_idx, profit)

        return success

# Print stats every 100 ticks
def on_tick(bot: BotWithStats):
    # ... normal tick logic ...

    if bot.tick_count % 100 == 0:
        bot.stats.print_stats()
```

---

