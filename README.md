# 🤖 Multi-Trading-Bot-Oner_2025

> **Comprehensive Multi-Platform Automated Trading System with 3-Bot Architecture**

[![Platform](https://img.shields.io/badge/Platform-MT4%20|%20MT5%20|%20TradeLocker%20|%20cTrader-blue)](https://github.com)
[![Language](https://img.shields.io/badge/Language-MQL4%20|%20MQL5%20|%20Python%20|%20C%23-green)](https://github.com)
[![Documentation](https://img.shields.io/badge/Documentation-27%2C413%20lines-orange)](DOCS/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com)

---

## 🎯 Project Overview

**Multi-Trading-Bot-Oner_2025** is a professional automated trading system that operates across **4 major trading platforms** (MT4, MT5, TradeLocker, cTrader) using a sophisticated **3-bot architecture**:

1. **SPY Bot** (Python) - Signal generation and CASCADE news detection system
2. **TradeLocker Bot** (Python) - Cloud-based trading automation via REST API
3. **EA MT5 Bot** (MQL5) - Desktop-based trading automation for MetaTrader 5

The system manages up to **21 concurrent positions** (7 timeframes × 3 strategies) with advanced risk management, dual-layer stoploss protection, and CASCADE news filtering.

### 🎉 Project Status: 100% Complete

All components, documentation, and platform conversions are production-ready and fully tested.

---

## 📚 Complete Documentation (27,413 Lines)

This project includes **comprehensive technical documentation** covering every aspect of the system:

| Stage | Document | Lines | Description |
|-------|----------|-------|-------------|
| **Stage 1** | [SPY Bot Documentation](DOCS/01_SPY_Bot_Technical_Documentation.md) | 7,802 | Signal generation, CSDL format, CASCADE detection |
| **Stage 2** | [TradeLocker Bot Documentation](DOCS/02_TradeLocker_Bot_Technical_Documentation.md) | 9,532 | Python bot, REST API, MongoDB, async architecture |
| **Stage 3** | [EA MT5 Bot Documentation](DOCS/03_EA_MT5_Bot_Technical_Documentation.md) | 10,079 | MQL5 EA, 21-position matrix, strategies, deployment |
| **Total** | **All Documentation** | **27,413** | **Complete system reference** |

### 📖 What's Covered:

- ✅ Complete architecture diagrams and data flow
- ✅ Detailed API reference for all bots
- ✅ Step-by-step deployment guides
- ✅ Troubleshooting decision trees
- ✅ FAQ sections (50+ common questions)
- ✅ Production configuration examples
- ✅ Performance optimization techniques
- ✅ Comparison tables across platforms

**👉 For AI Assistants:** Read the documentation files in `DOCS/` for complete system understanding.

---

## 🏗️ System Architecture Overview

### The 3-Bot Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   MULTI-TRADING-BOT-ONER SYSTEM                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ BOT 1: SPY BOT (Python)                                      │ │
│  │ ─────────────────────────────────────────────────────────── │ │
│  │ Purpose: Signal Generation & CASCADE News Detection         │ │
│  │                                                              │ │
│  │ [Market Data] → [Technical Analysis] → [Signal Processing]  │ │
│  │       ↓                                                      │ │
│  │ [CASCADE Detection] → [CSDL Data Structure (7x6 matrix)]    │ │
│  │       ↓                                                      │ │
│  │ [JSON Files] + [HTTP API] + [MongoDB]                       │ │
│  └────────────────────────┬─────────────────────────────────────┘ │
│                           │                                         │
│                           ├────────────────┬────────────────────┐   │
│                           ▼                ▼                    ▼   │
│  ┌──────────────────────────┐  ┌──────────────────┐  ┌─────────┐ │
│  │ BOT 2: TradeLocker Bot   │  │ BOT 3: EA MT5    │  │ MT4 EA  │ │
│  │ ──────────────────────── │  │ ───────────────  │  │ cTrader │ │
│  │ Platform: Cloud (Python) │  │ Platform: Desktop│  │  (C#)   │ │
│  │                          │  │                  │  │         │ │
│  │ [Read CSDL via HTTP API] │  │ [Read CSDL File] │  │ [Read]  │ │
│  │         ↓                │  │         ↓        │  │    ↓    │ │
│  │ [Process 3 Strategies]   │  │ [Process 3 Strat]│  │ [Trade] │ │
│  │  • S1 HOME/Binary        │  │  • S1 HOME       │  │         │ │
│  │  • S2 TREND Following    │  │  • S2 TREND      │  │         │ │
│  │  • S3 NEWS Trading       │  │  • S3 NEWS       │  │         │ │
│  │         ↓                │  │         ↓        │  │         │ │
│  │ [Execute via REST API]   │  │ [Execute via MT5]│  │ [MT4/CT]│ │
│  │         ↓                │  │         ↓        │  │    ↓    │ │
│  │ [21 Positions Max]       │  │ [21 Positions]   │  │  [21]   │ │
│  │         ↓                │  │         ↓        │  │    ↓    │ │
│  │ [Risk Management]        │  │ [Dual-Layer SL]  │  │  [SL]   │ │
│  └──────────────────────────┘  └──────────────────┘  └─────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts:

- **CSDL (CASCADE Love Data):** 7x6 matrix containing signals, timestamps, price differences, and CASCADE news scores
- **CASCADE:** News impact detection system (±10 to ±70 score based on price volatility)
- **21-Position Matrix:** 7 timeframes (M1→D1) × 3 strategies (S1, S2, S3)
- **Magic Numbers:** Unique identifier per position: `77000 + (TF_index × 100) + (Strategy_index × 10)`

---

## 🤖 The Three Bots Explained

### 1️⃣ SPY Bot (Signal Processing Yard)

**Location:** `SYNS_Bot_PY/`
**Language:** Python 3.8+
**Role:** Central signal generation and CASCADE news detection

#### What it does:

1. **Monitors Market Data:** Tracks price movements across 7 timeframes (M1, M5, M15, M30, H1, H4, D1)
2. **Generates Trading Signals:** Uses WaveTrend and custom algorithms to produce BUY (+1) / SELL (-1) / NONE (0) signals
3. **Detects CASCADE News:** Calculates news impact score (±10-70) based on price volatility and multi-timeframe confirmation
4. **Produces CSDL Data:** Creates structured 7×6 matrix with signals, timestamps, price diffs, and news scores
5. **Distributes via Multiple Channels:**
   - JSON Files (for MT4/MT5 EAs)
   - HTTP REST API (for TradeLocker Bot)
   - MongoDB (for persistence and analytics)

#### CASCADE Detection Example:

```
Price Movement:     $50,000 → $50,003 (within 30 seconds)
Live Diff:          $3.00 USD
M1 Threshold:       $2.50 (exceeded ✓)
M5→M1 Cascade:      Not confirmed yet
Result:             CASCADE Level 1 (L1) = ±10 points
```

📖 **Full Documentation:** [DOCS/01_SPY_Bot_Technical_Documentation.md](DOCS/01_SPY_Bot_Technical_Documentation.md)

---

### 2️⃣ TradeLocker Bot (Cloud-Based Trading)

**Location:** `TradeLocker/`
**Language:** Python 3.8+
**Role:** Cloud-based automated trading via REST API

#### What it does:

1. **Fetches CSDL Data:** Reads signals from SPY Bot via HTTP API or MongoDB
2. **Processes 3 Strategies:**
   - **S1 HOME:** Binary-style trading (0→±1 signal changes)
   - **S2 TREND:** Trend following (signals must align with D1 direction)
   - **S3 NEWS:** News trading (requires CASCADE ≥ Level 3)
3. **Executes Trades:** Opens/closes positions via TradeLocker REST API
4. **Manages Risk:**
   - Layer1 Stoploss (per-position, CSDL max_loss based)
   - Layer2 Stoploss (account-level drawdown %)
   - Layer3 Stoploss (time-based position limits)
5. **Scales Efficiently:** Handles 10+ symbols simultaneously via async/await architecture

#### Advantages:

- ✅ Platform-agnostic (not tied to MT4/MT5)
- ✅ Cloud deployment (runs on Linux VPS, Docker, Kubernetes)
- ✅ Lower cost ($10-15/month vs $30-40 for Windows VPS)
- ✅ Better logging (structured JSON logs, multi-level)
- ✅ Remote control (REST API, Telegram alerts)

📖 **Full Documentation:** [DOCS/02_TradeLocker_Bot_Technical_Documentation.md](DOCS/02_TradeLocker_Bot_Technical_Documentation.md)

---

### 3️⃣ EA MT5 Bot (Desktop-Based Trading)

**Location:** `MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5`
**Language:** MQL5
**Role:** Desktop-based automated trading for MetaTrader 5

#### What it does:

1. **Reads CSDL Files:** Parses JSON files from SPY Bot (local filesystem)
2. **Processes 3 Strategies:** Same logic as TradeLocker Bot (S1, S2, S3)
3. **Executes Trades:** Direct broker access via MT5 protocol (faster than HTTP)
4. **Manages Risk:**
   - Layer1 Stoploss (CSDL max_loss per position)
   - Layer2 Stoploss (margin-level emergency protection)
5. **Displays Dashboard:** Real-time monitoring on chart (Comment() function)

#### Advantages:

- ✅ Faster execution (native broker protocol, 10-50ms latency)
- ✅ Lower slippage (direct access, no HTTP overhead)
- ✅ Backtesting support (MT5 Strategy Tester)
- ✅ Visual dashboard (chart-based monitoring)

#### EASymbolData Structure (116 Variables):

The EA uses a comprehensive struct to track all state:

```mql5
struct EASymbolData {
    string symbol_name;              // Symbol being traded
    CSDLLoveRow csdl_rows[7];       // 7 CSDL rows (one per timeframe)
    int signal_old[7];               // Previous signals for change detection
    int magic_numbers[7][3];         // 21 magic numbers (7 TF × 3 strategies)
    double lot_sizes[7][3];          // 21 lot sizes
    int position_flags[7][3];        // 21 position tracking flags
    // ... 116 total variables
};
```

📖 **Full Documentation:** [DOCS/03_EA_MT5_Bot_Technical_Documentation.md](DOCS/03_EA_MT5_Bot_Technical_Documentation.md)

---

## 💻 Supported Platforms

| Platform | Status | Language | Lines | Features |
|----------|--------|----------|-------|----------|
| **MetaTrader 4** | ✅ Complete | MQL4 | 2,800+ | Desktop, Backtesting, Fast execution |
| **MetaTrader 5** | ✅ Complete | MQL5 | 2,995 | Desktop, Modern API, Strategy Tester |
| **TradeLocker** | ✅ Complete | Python | 1,879 | Cloud, REST API, Scalable |
| **cTrader** | ✅ Complete | C# | 2,800+ | Desktop, Modern UI, cAlgo support |

### Platform Comparison:

| Aspect | MT4/MT5 EA | TradeLocker Bot | cTrader cBot |
|--------|------------|-----------------|--------------|
| **Deployment** | Windows VPS | Linux VPS (Docker) | Windows/Linux |
| **Latency** | 10-50ms | 100-300ms | 20-60ms |
| **Cost/Month** | $30-40 | $10-15 | $25-35 |
| **Scalability** | Manual (1 chart/symbol) | Automatic (config list) | Manual |
| **Backtesting** | ✅ Full support | ⚠️ Manual only | ✅ Full support |
| **Logging** | Basic (Print) | Advanced (JSON) | Good (C# logs) |
| **Best For** | Scalping, backtesting | Multi-symbol, cloud | Modern UI, C# devs |

### Quick Installation Links:

- **TradeLocker (Python):**
  - [Windows VPS Installation](TradeLocker/INSTALL_WINDOWS.md)
  - [Linux VPS Installation](TradeLocker/INSTALL_LINUX.md)
  - [TradeLocker README](TradeLocker/README.md)
- **MT4/MT5:** Copy `.mq4`/`.mq5` to `Experts` folder → Compile → Attach to chart
- **cTrader:** Copy `.cs` to `cBots` folder → Compile → Attach to chart

---

## 📊 CSDL Data Structure (Central Data Format)

The **CSDL (CASCADE Love Data)** is the heart of the system - a standardized 7×6 matrix that all bots understand.

### File Format: `SYMBOL_LIVE.json`

```json
[
  {
    "max_loss": 0.50,
    "timestamp": 1730620800,
    "signal": 1,
    "pricediff": 2.50,
    "timediff": 5,
    "news": 30
  },
  {
    "max_loss": 0.75,
    "timestamp": 1730620500,
    "signal": -1,
    "pricediff": -1.20,
    "timediff": 15,
    "news": -20
  }
  // ... 5 more rows (M15, M30, H1, H4, D1)
]
```

### Column Definitions:

| Column | Type | Range | Source | Used By |
|--------|------|-------|--------|---------|
| `max_loss` | double | -0.5 to -5.0 | SPY calculation | Stoploss calculation |
| `timestamp` | long | Unix epoch | SPY timer | Signal freshness check |
| **`signal`** | **int** | **-1, 0, +1** | **WaveTrend algorithm** | **S1 + S2 strategies** |
| `pricediff` | double | ±0.1 to ±100.0 | Price delta | Reference only |
| `timediff` | int | 1-1440 min | Time delta | Reference only |
| **`news`** | **int** | **±10-70 or ±1-7** | **CASCADE detection** | **S3 + BONUS strategies** |

### The Two Critical Columns:

1. **`signal`** - Trading direction:
   - `-1` = SELL signal
   - `0` = No signal (neutral)
   - `+1` = BUY signal
   - Used by: S1 (HOME) and S2 (TREND) strategies

2. **`news`** - CASCADE news impact:
   - `0` = No significant news
   - `±10-70` = Category 1 (EA trading levels L1-L7)
   - `±1-7` = Category 2 (Special levels)
   - Sign indicates direction (+ bullish, - bearish)
   - Magnitude indicates strength
   - Used by: S3 (NEWS) and BONUS strategies

---

## 🎯 The Three Trading Strategies

All bots implement the same 3 strategies with consistent logic:

### Strategy 1: S1_HOME (Binary/Conservative)

**Philosophy:** Conservative trading, wait for clear signal entry points

**Entry Conditions:**
- Signal changes from `0` → `±1` (fresh signal)
- Timestamp updated (confirms new signal)
- No existing position in this slot

**Exit Conditions:**
- Configurable:
  - **Fast mode:** Close when M1 reverses (quick exit)
  - **Normal mode:** Close when timeframe's own signal reverses

**Lot Size:** Smallest (conservative)

**Example:**
```
M15 timeframe:
  Old signal: 0 (neutral)
  New signal: +1 (BUY)
  → OPEN S1_M15 BUY position
```

---

### Strategy 2: S2_TREND (Trend Following)

**Philosophy:** Follow the dominant D1 trend, only trade when lower timeframes align

**Entry Conditions:**
- Signal changes (not necessarily from 0)
- Signal matches D1 trend direction
- Timestamp updated

**Exit Conditions:**
- Same as S1 (fast or normal mode)

**Lot Size:** Medium

**Example:**
```
D1 trend: +1 (bullish)
M5 signal: -1 → +1 (changed and now matches D1)
  → OPEN S2_M5 BUY position

If M5 signal: -1 (against D1 trend)
  → SKIP (no trade)
```

**Key Difference from S1:** S2 requires D1 alignment, S1 does not.

---

### Strategy 3: S3_NEWS (News Trading)

**Philosophy:** Aggressive trading during high-impact news events

**Entry Conditions:**
- Signal present (`±1`)
- `|news|` ≥ MinNewsLevel (default 30 = Level 3)
- News direction matches signal
- Timestamp updated

**Exit Conditions:**
- Always: Close when timeframe's own signal reverses (no fast mode)

**Lot Size:** Largest (aggressive)

**Example:**
```
M1 timeframe:
  Signal: +1 (BUY)
  News: +40 (Level 4, bullish)
  MinNewsLevel: 30
  40 ≥ 30 ✓ → OPEN S3_M1 BUY position

If News: +15 (too weak)
  15 < 30 ✗ → SKIP
```

**CASCADE Levels:**
- L1 (±10): Minor news
- L2 (±20): Moderate news
- **L3 (±30): Major news** ← Default threshold
- L4 (±40): High impact
- L5 (±50): Very high impact
- L6 (±60): Extreme impact
- L7 (±70): Catastrophic event

---

### BONUS Strategy (Volume Boost)

**Not a separate strategy** - uses S3 magic numbers and opens multiple positions

**Entry Conditions:**
- `|news|` ≥ MinNewsLevelBonus (default 20)
- News level ≠ 1 and ≠ 10 (filter weak levels)
- News direction present

**Execution:**
- Opens multiple positions (BonusOrderCount = 2-5)
- Uses S3 lot size × BonusLotMultiplier
- Uses S3 magic numbers (shared tracking)

**Exit Conditions:**
- **Always:** Close when M1 reverses (very fast exit)
- Closes all BONUS positions + S3 positions simultaneously

**Example:**
```
H1 timeframe:
  News: +50 (Level 5, very strong)
  MinNewsLevelBonus: 20
  BonusOrderCount: 2
  50 ≥ 20 ✓ → OPEN 2 BONUS_H1 BUY positions
  Magic: Same as S3_H1 (5878)

When M1 reverses:
  → CLOSE all 2 BONUS positions
  → CLOSE S3_H1 position (if exists)
```

---

## 🚀 Quick Start Guide

### Prerequisites:

- **For TradeLocker Bot:**
  - Linux VPS (Ubuntu 20.04+) or Windows VPS
  - Python 3.8+
  - TradeLocker account with API access
  - 2GB RAM, 1 CPU minimum

- **For MT5 EA:**
  - Windows VPS or desktop
  - MetaTrader 5 installed
  - Broker account
  - 4GB RAM, 2 CPU recommended

- **For SPY Bot:**
  - Python 3.8+
  - Can run on same VPS as TradeLocker Bot
  - 1GB RAM, 1 CPU minimum

### Installation Steps:

#### 1. SPY Bot (Signal Generator)

```bash
cd SYNS_Bot_PY/
pip install -r requirements.txt
python spy_bot.py --symbol BTCUSD
```

SPY will start generating CSDL files and serving HTTP API.

#### 2. TradeLocker Bot (Cloud Trading)

Follow detailed guide: [TradeLocker/INSTALL_LINUX.md](TradeLocker/INSTALL_LINUX.md)

Quick version:
```bash
cd TradeLocker/
pip install -r requirements.txt
cp config_example.yaml config.yaml
# Edit config.yaml with your API keys
python tradelocker_bot.py
```

#### 3. EA MT5 Bot (Desktop Trading)

1. Copy `MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5` to MT5 data folder
2. Open MetaEditor → Compile
3. Attach to chart → Configure parameters
4. Enable AutoTrading

Full guide: [DOCS/03_EA_MT5_Bot_Technical_Documentation.md#appendix-k-deployment-checklist](DOCS/03_EA_MT5_Bot_Technical_Documentation.md)

---

## 📁 Repository Structure

```
Multi-Trading-Bot-Oner_2025/
├── DOCS/                                   # 📚 Complete Documentation (27,413 lines)
│   ├── 01_SPY_Bot_Technical_Documentation.md        (7,802 lines)
│   ├── 02_TradeLocker_Bot_Technical_Documentation.md (9,532 lines)
│   └── 03_EA_MT5_Bot_Technical_Documentation.md     (10,079 lines)
│
├── SYNS_Bot_PY/                            # 🐍 SPY Bot (Python)
│   ├── spy_bot.py                          # Main signal generation
│   ├── cascade_detector.py                # CASCADE news detection
│   ├── csdl_generator.py                   # CSDL data structure
│   └── requirements.txt
│
├── TradeLocker/                            # ☁️ TradeLocker Bot (Python)
│   ├── tradelocker_bot.py                  # Main trading bot (1,879 lines)
│   ├── config_example.yaml                 # Configuration template
│   ├── INSTALL_LINUX.md                    # Linux installation guide
│   ├── INSTALL_WINDOWS.md                  # Windows installation guide
│   └── README.md
│
├── MQL4/                                   # 📊 MT4 Platform
│   └── Experts/
│       └── MT4_Eas_Smf_Oner_V2.mq4        # MT4 EA (2,800+ lines)
│
├── MQL5/                                   # 📊 MT5 Platform
│   └── Experts/
│       └── _MT5_EAs_MTF ONER_V2.mq5       # MT5 EA (2,995 lines)
│
├── cTrader/                                # 🎯 cTrader Platform
│   └── cBots/
│       └── MTF_ONER_V2.cs                 # cTrader cBot (2,800+ lines)
│
└── README.md                               # 📖 This file
```

---

## 🎯 Key Features

### Multi-Platform Support
- ✅ MT4, MT5, TradeLocker, cTrader
- ✅ Consistent strategy logic across all platforms
- ✅ Same CSDL data format for interoperability

### Advanced Risk Management
- ✅ Dual-layer stoploss (per-position + account-level)
- ✅ Dynamic lot sizing based on CSDL max_loss
- ✅ Emergency drawdown protection
- ✅ Position count limits (max 21 concurrent)

### CASCADE News Detection
- ✅ 7-level impact scoring (L1-L7)
- ✅ Multi-timeframe confirmation cascade
- ✅ Real-time price volatility analysis
- ✅ Directional news signals (bullish/bearish)

### Intelligent Signal Processing
- ✅ WaveTrend-based technical analysis
- ✅ 7 timeframe coverage (M1→D1)
- ✅ Signal change detection
- ✅ Trend alignment filtering (S2 strategy)

### Performance Optimization
- ✅ Even/Odd timer split (50% CPU reduction)
- ✅ Efficient CSDL parsing
- ✅ Async/await for TradeLocker (Python)
- ✅ Memory-efficient data structures

### Production-Ready
- ✅ Comprehensive error handling
- ✅ Detailed logging (debug, info, warning, error)
- ✅ Real-time dashboard monitoring
- ✅ Backup data sources (3 JSON files)
- ✅ API fallback mechanisms

---

## ⚙️ Technical Details

### Magic Number System

Each position has a unique magic number encoding its timeframe and strategy:

```
Formula: Magic = 77000 + (TF_index × 100) + (Strategy_index × 10)

Timeframe Indices:
  M1  = 0
  M5  = 1
  M15 = 2
  M30 = 3
  H1  = 4
  H4  = 5
  D1  = 6

Strategy Indices:
  S1 (HOME)  = 0
  S2 (TREND) = 1
  S3 (NEWS)  = 2

Examples:
  M1-S1  = 77000 + (0×100) + (0×10) = 77000
  M15-S2 = 77000 + (2×100) + (1×10) = 77210
  H4-S3  = 77000 + (5×100) + (2×10) = 77520
  D1-S3  = 77000 + (6×100) + (2×10) = 77620
```

This system allows:
- ✅ Unique identification of each position
- ✅ Strategy performance tracking
- ✅ Multi-EA operation without conflicts
- ✅ Easy decoding for analysis

### Data Flow Sequence (Every 2 Seconds)

```
Second 0.0: Market Data Collection
├─ 7 timeframe charts monitored
├─ Price movements tracked
└─ WaveTrend indicators calculated

Second 0.5: SPY Bot Processing
├─ Read signals from indicators/Global Variables
├─ Calculate price differences
├─ Detect CASCADE news (multi-TF volatility)
├─ Generate 7×6 CSDL matrix
├─ Write JSON files (3 copies)
├─ Update HTTP API endpoint
└─ Store to MongoDB (if enabled)

Second 1.0: Trading Bot Processing (EVEN second)
├─ Read CSDL data (file or API)
├─ Parse 7 rows × 6 columns
├─ Detect signal changes per timeframe
├─ Check CASCADE levels
├─ Process S1 strategy (all 7 TFs)
├─ Process S2 strategy (D1 alignment check)
├─ Process S3 strategy (news threshold check)
├─ Process BONUS orders (high CASCADE)
└─ Execute trades via broker API

Second 2.0: SPY Bot Update
└─ Recalculate CASCADE (live price monitoring)

Second 3.0: Trading Bot Monitoring (ODD second)
├─ Check stoploss conditions (Layer1 + Layer2)
├─ Check take profit targets
├─ Update dashboard display
├─ Log position status
└─ Check emergency conditions

... Repeat every 2 seconds
```

### Position Lifecycle Example

```
Timeline: S1 Strategy on M15 Timeframe

T=0s    CSDL Update:
        M15 signal: 0 → +1 (BUY signal appears)

T=1s    EA Processing:
        ├─ Detect signal change (0 → +1)
        ├─ Check no duplicate position
        ├─ Calculate lot size (from CSDL max_loss)
        ├─ Generate magic: 77200 (M15-S1)
        └─ OPEN BUY position

T=1s-   Position Opened:
300s    ├─ Ticket: #12345
        ├─ Magic: 77200
        ├─ Lot: 0.10
        ├─ Entry: $50,000.00
        └─ Running...

T=3s    Monitoring (ODD second):
        ├─ Check profit: +$5.50
        ├─ Check stoploss: -$5.00 threshold
        ├─ Status: OK (profit > threshold)
        └─ Continue holding

T=301s  CSDL Update:
        M15 signal: +1 → -1 (SELL signal, reversal!)

T=302s  EA Processing:
        ├─ Detect signal reversal (+1 → -1)
        ├─ Find position with magic 77200
        └─ CLOSE position #12345

T=302s+ Position Closed:
        ├─ Exit: $50,012.00
        ├─ Profit: +$12.00
        ├─ Duration: 300 seconds (5 minutes)
        └─ Position slot freed (can open new trade)
```

---

## 🐛 Known Issues & Fixes

### ✅ FIXED: NEWS Column Parsing Bug (2025-01-03)

**Problem:** The `news` column (last column in JSON) was never parsed correctly in MT4/MT5 EAs.

**Root Cause:**
```mql5
// OLD CODE (WRONG):
int end_pos = StringFind(temp, ",");  // Returns -1 for last column!
if(end_pos > 0) {  // Never true → never parsed!
    news = StringToInteger(...);
}
```

**Impact:**
- S3 strategy never activated (required `news ≥ 30`, but `news` always = 0)
- BONUS strategy never activated (same reason)
- Only S1 and S2 worked

**Fix:**
```mql5
// NEW CODE (CORRECT):
int end_pos = StringLen(temp);  // Default to full length
if(comma > 0 && bracket > 0) {
    end_pos = (comma < bracket) ? comma : bracket;
} else if(bracket > 0) {
    end_pos = bracket;
}
// Now always has valid end_pos → always parses!
```

**Files Updated:**
- `MQL4/Experts/MT4_Eas_Smf_Oner_V2.mq4` (commit a7eb5bd)
- `MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5` (commit 2497bcb)

**Status:** ✅ Resolved and tested in production

---

## 📖 For AI Assistants (Claude, GPT, etc.)

If you're an AI assistant helping with this project, **READ THIS SECTION FIRST**:

### 🎯 Project Purpose:
This is a **production-ready automated trading system** that operates across 4 platforms using a 3-bot architecture. It's NOT a tutorial or demo - it's real trading software managing real money.

### 📚 Start Here:
1. **Read:** [DOCS/03_EA_MT5_Bot_Technical_Documentation.md](DOCS/03_EA_MT5_Bot_Technical_Documentation.md) (most comprehensive)
2. **Then:** [DOCS/01_SPY_Bot_Technical_Documentation.md](DOCS/01_SPY_Bot_Technical_Documentation.md) (understand CSDL format)
3. **Finally:** [DOCS/02_TradeLocker_Bot_Technical_Documentation.md](DOCS/02_TradeLocker_Bot_Technical_Documentation.md) (cloud architecture)

### 🔑 Key Concepts to Understand:

1. **CSDL (CASCADE Love Data):**
   - 7×6 matrix (7 timeframes, 6 columns)
   - Central data format ALL bots understand
   - Contains: signals, timestamps, price diffs, CASCADE news scores

2. **CASCADE News Detection:**
   - NOT reading news websites or calendars
   - Detects news by measuring price volatility
   - Multi-timeframe confirmation = higher score
   - Score range: 0 (no news) to ±70 (extreme event)

3. **Magic Number System:**
   - Formula: `77000 + (TF_index × 100) + (Strategy_index × 10)`
   - Encodes which timeframe and strategy opened each position
   - Example: 77210 = M15 timeframe, S2 strategy

4. **Three Strategies:**
   - **S1 HOME:** Conservative, wait for 0→±1 signals
   - **S2 TREND:** Follow D1 trend, requires alignment
   - **S3 NEWS:** Aggressive, requires CASCADE ≥ L3 (±30)

5. **21-Position Matrix:**
   - 7 timeframes × 3 strategies = 21 possible positions
   - Each has unique magic number
   - Each tracked independently

### ⚠️ Common Mistakes to Avoid:

1. **Don't confuse platforms:**
   - MT4/MT5 = Desktop, MQL language, reads JSON files
   - TradeLocker = Cloud, Python, reads HTTP API
   - They do the SAME thing differently

2. **Don't mix up signal vs news:**
   - `signal` column = trading direction from WaveTrend (±1, 0)
   - `news` column = CASCADE impact score (±10-70)
   - S1/S2 use `signal`, S3 uses `news`

3. **Don't ignore documentation:**
   - 27,413 lines written for a reason
   - Most answers are in the docs
   - Check docs before asking user

4. **Don't suggest breaking changes:**
   - This is production code managing real money
   - Test thoroughly before recommending changes
   - Understand ripple effects across 4 platforms

### 🛠️ When Helping with Code:

- **MT4/MT5:** Check both platforms (MQL4 vs MQL5 syntax differs)
- **TradeLocker:** Python 3.8+, async/await patterns
- **CSDL Format:** ANY change affects ALL bots
- **Magic Numbers:** Don't change formula (breaks position tracking)
- **Strategies:** Keep logic consistent across platforms

### 📝 When Writing Documentation:

- Be precise (trading is unforgiving)
- Include examples (code + data)
- Show calculations step-by-step
- Mention platform differences
- Link to relevant doc sections

### 🔍 Debugging Tips:

1. **Check CSDL data first:** Most issues stem from bad data
2. **Verify magic numbers:** Decode them to confirm TF/strategy
3. **Compare across platforms:** If MT5 works but TradeLocker doesn't, compare implementations
4. **Read logs:** All bots have detailed logging
5. **Check timestamps:** Stale data = stale trades

---

## 📝 Contributing

This is a private trading system. Contributions are limited to authorized users.

If you need to modify the system:

1. **Test on demo account first** (always!)
2. **Update documentation** (if changing behavior)
3. **Maintain cross-platform consistency** (test all 4 platforms)
4. **Follow existing code style**
5. **Add comprehensive comments**

---

## 📜 License & Disclaimer

### License:
Proprietary. All rights reserved.

### Disclaimer:

⚠️ **IMPORTANT LEGAL NOTICE:**

This software is provided **for educational and research purposes only**.

- ❌ **NO guarantee of profitability**
- ❌ **NO financial advice provided**
- ❌ **NO liability for trading losses**
- ❌ **NO warranty of any kind**

**Trading involves substantial risk of loss.** Only trade with capital you can afford to lose completely.

**By using this software, you acknowledge:**
- You are solely responsible for all trading decisions
- Past performance does NOT indicate future results
- Automated trading does NOT eliminate risk
- You understand the risks of leveraged trading
- You have consulted with a qualified financial advisor (recommended)
- You comply with all applicable laws and regulations in your jurisdiction

**Regulatory Compliance:**
- Verify broker is licensed in your jurisdiction
- Understand tax implications of trading profits/losses
- Keep detailed records of all trades
- Consult with tax and legal professionals

**The authors and distributors:**
- Do NOT provide financial advice
- Are NOT responsible for trading losses
- Do NOT guarantee system performance
- Provide software "AS IS" without warranty

---

## 📧 Contact & Support

**Documentation:** Read the 27,413 lines in `DOCS/` first
**Issues:** Check documentation, then logs, then ask
**Updates:** Follow commit history for changes
**Version:** 2.0 (After NEWS parsing bug fix - 2025-01-03)

---

## 🎉 Quick Summary

**What is this?** A professional automated trading system with 3 bots running on 4 platforms.

**What does it do?** Generates signals → Detects news → Executes trades → Manages risk.

**How many positions?** Up to 21 concurrent (7 timeframes × 3 strategies).

**Which platform is best?**
- **MT5:** Fastest execution, backtesting
- **TradeLocker:** Lowest cost, most scalable
- **MT4:** Most brokers, stable
- **cTrader:** Modern UI, C# developers

**Where do I start?** Read [DOCS/03_EA_MT5_Bot_Technical_Documentation.md](DOCS/03_EA_MT5_Bot_Technical_Documentation.md) then deploy SPY Bot + your chosen trading bot.

**Is it profitable?** No guarantees. Past performance ≠ future results. Test on demo first.

**Can I customize it?** Yes, but maintain cross-platform consistency and test thoroughly.

**Need help?** Read docs → Check logs → Review code → Ask specific questions.

---

**Built with:** Python 🐍 | MQL4/MQL5 📊 | C# 🎯 | JSON 📄 | REST APIs ☁️

**Status:** ✅ Production Ready | 📚 Fully Documented | 🧪 Tested | 🚀 Deployed

**Last Updated:** 2025-01-09

---

⭐ **If you're an AI assistant:** You now have complete context. Check `DOCS/` for details. Good luck! 🤖
