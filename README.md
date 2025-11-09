# 🤖 Multi-Trading-Bot-Oner_2025

> **Comprehensive Multi-Platform Automated Trading System with 3-Bot Architecture**
> **Hệ Thống Giao Dịch Tự Động Đa Nền Tảng với Kiến Trúc 3 Bot**

[![Platform](https://img.shields.io/badge/Platform-MT4%20|%20MT5%20|%20TradeLocker%20|%20cTrader-blue)](https://github.com)
[![Language](https://img.shields.io/badge/Language-MQL4%20|%20MQL5%20|%20Python%20|%20C%23-green)](https://github.com)
[![Documentation](https://img.shields.io/badge/Documentation-27%2C413%20lines-orange)](DOCS/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com)

---

## 🎯 Project Overview / Tổng Quan Dự Án

### English

**Multi-Trading-Bot-Oner_2025** is a professional automated trading system that operates across **4 major trading platforms** (MT4, MT5, TradeLocker, cTrader) using a sophisticated **3-bot architecture**:

1. **SPY Bot** (Python) - Signal generation and CASCADE news detection system
2. **TradeLocker Bot** (Python) - Cloud-based trading automation via REST API
3. **EA MT5 Bot** (MQL5) - Desktop-based trading automation for MetaTrader 5

The system manages up to **21 concurrent positions** (7 timeframes × 3 strategies) with advanced risk management, dual-layer stoploss protection, and CASCADE news filtering.

### Tiếng Việt

**Multi-Trading-Bot-Oner_2025** là hệ thống giao dịch tự động chuyên nghiệp hoạt động trên **4 nền tảng giao dịch chính** (MT4, MT5, TradeLocker, cTrader) sử dụng **kiến trúc 3 bot** tinh vi:

1. **SPY Bot** (Python) - Hệ thống tạo tín hiệu và phát hiện tin tức CASCADE
2. **TradeLocker Bot** (Python) - Giao dịch tự động trên cloud qua REST API
3. **EA MT5 Bot** (MQL5) - Giao dịch tự động trên desktop cho MetaTrader 5

Hệ thống quản lý tối đa **21 lệnh đồng thời** (7 khung thời gian × 3 chiến lược) với quản lý rủi ro nâng cao, bảo vệ stoploss 2 lớp, và lọc tin tức CASCADE.

### 🎉 Project Status / Trạng Thái Dự Án

**100% Complete** / **100% Hoàn Thành**

All components, documentation, and platform conversions are production-ready and fully tested.
Tất cả các thành phần, tài liệu và chuyển đổi nền tảng đã sẵn sàng production và được test đầy đủ.

---

## 📚 Complete Documentation / Tài Liệu Đầy Đủ (27,413 Lines / Dòng)

This project includes **comprehensive technical documentation** covering every aspect of the system.
Dự án bao gồm **tài liệu kỹ thuật toàn diện** bao quát mọi khía cạnh của hệ thống.

| Stage / Giai Đoạn | Document / Tài Liệu | Lines / Dòng | Description / Mô Tả |
|-------|----------|-------|-------------|
| **Stage 1** | [SPY Bot Documentation](DOCS/01_SPY_Bot_Technical_Documentation.md) | 7,802 | Signal generation, CSDL format, CASCADE detection<br/>**Tạo tín hiệu, định dạng CSDL, phát hiện CASCADE** |
| **Stage 2** | [TradeLocker Bot Documentation](DOCS/02_TradeLocker_Bot_Technical_Documentation.md) | 9,532 | Python bot, REST API, MongoDB, async architecture<br/>**Bot Python, REST API, MongoDB, kiến trúc async** |
| **Stage 3** | [EA MT5 Bot Documentation](DOCS/03_EA_MT5_Bot_Technical_Documentation.md) | 10,079 | MQL5 EA, 21-position matrix, strategies, deployment<br/>**EA MQL5, ma trận 21 lệnh, chiến lược, triển khai** |
| **Total / Tổng** | **All Documentation / Toàn Bộ** | **27,413** | **Complete system reference / Tài liệu tham khảo hoàn chỉnh** |

### 📖 What's Covered / Nội Dung Bao Gồm:

- ✅ Complete architecture diagrams and data flow / **Sơ đồ kiến trúc và luồng dữ liệu đầy đủ**
- ✅ Detailed API reference for all bots / **Tài liệu API chi tiết cho tất cả bot**
- ✅ Step-by-step deployment guides / **Hướng dẫn triển khai từng bước**
- ✅ Troubleshooting decision trees / **Cây quyết định xử lý sự cố**
- ✅ FAQ sections (50+ common questions) / **Phần FAQ (50+ câu hỏi thường gặp)**
- ✅ Production configuration examples / **Ví dụ cấu hình production**
- ✅ Performance optimization techniques / **Kỹ thuật tối ưu hiệu suất**
- ✅ Comparison tables across platforms / **Bảng so sánh giữa các nền tảng**

**👉 For AI Assistants / Dành cho AI:** Read the documentation files in `DOCS/` for complete system understanding.
**Đọc các file tài liệu trong `DOCS/` để hiểu đầy đủ hệ thống.**

---

## 🏗️ System Architecture Overview / Tổng Quan Kiến Trúc Hệ Thống

### The 3-Bot Workflow / Quy Trình 3 Bot

```
┌─────────────────────────────────────────────────────────────────────┐
│           MULTI-TRADING-BOT-ONER SYSTEM / HỆ THỐNG                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ BOT 1: SPY BOT (Python)                                      │ │
│  │ Mục đích: Tạo Tín Hiệu & Phát Hiện Tin Tức CASCADE          │ │
│  │                                                              │ │
│  │ [Dữ liệu thị trường] → [Phân tích kỹ thuật] → [Xử lý tín hiệu]│
│  │       ↓                                                      │ │
│  │ [Phát hiện CASCADE] → [Cấu trúc dữ liệu CSDL (ma trận 7x6)] │ │
│  │       ↓                                                      │ │
│  │ [File JSON] + [HTTP API] + [MongoDB]                        │ │
│  └────────────────────────┬─────────────────────────────────────┘ │
│                           │                                         │
│                           ├────────────────┬────────────────────┐   │
│                           ▼                ▼                    ▼   │
│  ┌──────────────────────────┐  ┌──────────────────┐  ┌─────────┐ │
│  │ BOT 2: TradeLocker Bot   │  │ BOT 3: EA MT5    │  │ MT4 EA  │ │
│  │ Nền tảng: Cloud (Python) │  │ Nền tảng: Desktop│  │ cTrader │ │
│  │                          │  │                  │  │  (C#)   │ │
│  │ [Đọc CSDL qua HTTP API]  │  │ [Đọc file CSDL]  │  │ [Đọc]   │ │
│  │         ↓                │  │         ↓        │  │    ↓    │ │
│  │ [Xử lý 3 Chiến lược]     │  │ [Xử lý 3 CL]     │  │ [Giao   │ │
│  │  • S1 HOME/Binary        │  │  • S1 HOME       │  │  dịch]  │ │
│  │  • S2 TREND Theo xu h.   │  │  • S2 TREND      │  │         │ │
│  │  • S3 NEWS Giao dịch TT  │  │  • S3 NEWS       │  │         │ │
│  │         ↓                │  │         ↓        │  │         │ │
│  │ [Thực thi qua REST API]  │  │ [Thực thi MT5]   │  │ [MT4/CT]│ │
│  │         ↓                │  │         ↓        │  │    ↓    │ │
│  │ [Tối đa 21 Lệnh]         │  │ [21 Lệnh]        │  │  [21]   │ │
│  │         ↓                │  │         ↓        │  │    ↓    │ │
│  │ [Quản lý Rủi ro]         │  │ [Stoploss 2 lớp] │  │  [SL]   │ │
│  └──────────────────────────┘  └──────────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts / Khái Niệm Chính:

| English | Tiếng Việt |
|---------|-----------|
| **CSDL (CASCADE Love Data):** 7x6 matrix containing signals, timestamps, price differences, and CASCADE news scores | **CSDL (CASCADE Love Data):** Ma trận 7x6 chứa tín hiệu, timestamps, chênh lệch giá, và điểm tin tức CASCADE |
| **CASCADE:** News impact detection system (±10 to ±70 score based on price volatility) | **CASCADE:** Hệ thống phát hiện tác động tin tức (điểm ±10 đến ±70 dựa trên biến động giá) |
| **21-Position Matrix:** 7 timeframes (M1→D1) × 3 strategies (S1, S2, S3) | **Ma trận 21 Lệnh:** 7 khung thời gian (M1→D1) × 3 chiến lược (S1, S2, S3) |
| **Magic Numbers:** Unique identifier per position: `77000 + (TF_index × 100) + (Strategy_index × 10)` | **Số Magic:** Mã định danh duy nhất mỗi lệnh: `77000 + (chỉ_số_TF × 100) + (chỉ_số_CL × 10)` |

---

## 🤖 The Three Bots Explained / Giải Thích 3 Bot

### 1️⃣ SPY Bot (Signal Processing Yard / Sân Xử Lý Tín Hiệu)

**Location / Vị trí:** `SYNS_Bot_PY/`
**Language / Ngôn ngữ:** Python 3.8+
**Role / Vai trò:** Central signal generation and CASCADE news detection / Tạo tín hiệu trung tâm và phát hiện tin tức CASCADE

#### What it does / Làm gì:

| English | Tiếng Việt |
|---------|-----------|
| 1. **Monitors Market Data:** Tracks price movements across 7 timeframes (M1, M5, M15, M30, H1, H4, D1) | 1. **Theo Dõi Dữ Liệu Thị Trường:** Theo dõi biến động giá qua 7 khung thời gian (M1, M5, M15, M30, H1, H4, D1) |
| 2. **Generates Trading Signals:** Uses WaveTrend and custom algorithms to produce BUY (+1) / SELL (-1) / NONE (0) signals | 2. **Tạo Tín Hiệu Giao Dịch:** Dùng WaveTrend và thuật toán tùy chỉnh để tạo tín hiệu MUA (+1) / BÁN (-1) / KHÔNG (0) |
| 3. **Detects CASCADE News:** Calculates news impact score (±10-70) based on price volatility and multi-timeframe confirmation | 3. **Phát Hiện Tin Tức CASCADE:** Tính điểm tác động tin tức (±10-70) dựa trên biến động giá và xác nhận đa khung thời gian |
| 4. **Produces CSDL Data:** Creates structured 7×6 matrix with signals, timestamps, price diffs, and news scores | 4. **Tạo Dữ Liệu CSDL:** Tạo ma trận cấu trúc 7×6 với tín hiệu, timestamps, chênh lệch giá, và điểm tin tức |
| 5. **Distributes via Multiple Channels:** JSON Files (for MT4/MT5 EAs), HTTP REST API (for TradeLocker Bot), MongoDB (for persistence and analytics) | 5. **Phân Phối Qua Nhiều Kênh:** File JSON (cho EA MT4/MT5), HTTP REST API (cho TradeLocker Bot), MongoDB (lưu trữ và phân tích) |

#### CASCADE Detection Example / Ví Dụ Phát Hiện CASCADE:

```
Price Movement / Biến động giá:     $50,000 → $50,003 (within 30 seconds / trong 30 giây)
Live Diff / Chênh lệch:            $3.00 USD
M1 Threshold / Ngưỡng M1:           $2.50 (exceeded ✓ / vượt quá ✓)
M5→M1 Cascade / Cascade M5→M1:      Not confirmed yet / Chưa xác nhận
Result / Kết quả:                   CASCADE Level 1 (L1) = ±10 points / điểm
```

📖 **Full Documentation / Tài liệu đầy đủ:** [DOCS/01_SPY_Bot_Technical_Documentation.md](DOCS/01_SPY_Bot_Technical_Documentation.md)

---

### 2️⃣ TradeLocker Bot (Cloud-Based Trading / Giao Dịch Trên Cloud)

**Location / Vị trí:** `TradeLocker/`
**Language / Ngôn ngữ:** Python 3.8+
**Role / Vai trò:** Cloud-based automated trading via REST API / Giao dịch tự động trên cloud qua REST API

#### What it does / Làm gì:

| English | Tiếng Việt |
|---------|-----------|
| 1. **Fetches CSDL Data:** Reads signals from SPY Bot via HTTP API or MongoDB | 1. **Lấy Dữ Liệu CSDL:** Đọc tín hiệu từ SPY Bot qua HTTP API hoặc MongoDB |
| 2. **Processes 3 Strategies:** S1 HOME (Binary-style trading), S2 TREND (Trend following), S3 NEWS (News trading) | 2. **Xử Lý 3 Chiến Lược:** S1 HOME (Giao dịch kiểu Binary), S2 TREND (Theo xu hướng), S3 NEWS (Giao dịch tin tức) |
| 3. **Executes Trades:** Opens/closes positions via TradeLocker REST API | 3. **Thực Thi Giao Dịch:** Mở/đóng lệnh qua TradeLocker REST API |
| 4. **Manages Risk:** Layer1 Stoploss (per-position), Layer2 Stoploss (account-level drawdown %), Layer3 Stoploss (time-based limits) | 4. **Quản Lý Rủi Ro:** Stoploss Lớp 1 (mỗi lệnh), Stoploss Lớp 2 (% drawdown tài khoản), Stoploss Lớp 3 (giới hạn thời gian) |
| 5. **Scales Efficiently:** Handles 10+ symbols simultaneously via async/await architecture | 5. **Mở Rộng Hiệu Quả:** Xử lý 10+ symbols đồng thời qua kiến trúc async/await |

#### Advantages / Ưu Điểm:

- ✅ Platform-agnostic (not tied to MT4/MT5) / **Không phụ thuộc nền tảng (không gắn với MT4/MT5)**
- ✅ Cloud deployment (runs on Linux VPS, Docker, Kubernetes) / **Triển khai cloud (chạy trên Linux VPS, Docker, Kubernetes)**
- ✅ Lower cost ($10-15/month vs $30-40 for Windows VPS) / **Chi phí thấp hơn ($10-15/tháng vs $30-40 cho Windows VPS)**
- ✅ Better logging (structured JSON logs, multi-level) / **Logging tốt hơn (log JSON có cấu trúc, đa cấp độ)**
- ✅ Remote control (REST API, Telegram alerts) / **Điều khiển từ xa (REST API, cảnh báo Telegram)**

📖 **Full Documentation / Tài liệu đầy đủ:** [DOCS/02_TradeLocker_Bot_Technical_Documentation.md](DOCS/02_TradeLocker_Bot_Technical_Documentation.md)

---

### 3️⃣ EA MT5 Bot (Desktop-Based Trading / Giao Dịch Trên Desktop)

**Location / Vị trí:** `MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5`
**Language / Ngôn ngữ:** MQL5
**Role / Vai trò:** Desktop-based automated trading for MetaTrader 5 / Giao dịch tự động trên desktop cho MetaTrader 5

#### What it does / Làm gì:

| English | Tiếng Việt |
|---------|-----------|
| 1. **Reads CSDL Files:** Parses JSON files from SPY Bot (local filesystem) | 1. **Đọc File CSDL:** Phân tích file JSON từ SPY Bot (hệ thống file local) |
| 2. **Processes 3 Strategies:** Same logic as TradeLocker Bot (S1, S2, S3) | 2. **Xử Lý 3 Chiến Lược:** Logic giống TradeLocker Bot (S1, S2, S3) |
| 3. **Executes Trades:** Direct broker access via MT5 protocol (faster than HTTP) | 3. **Thực Thi Giao Dịch:** Truy cập broker trực tiếp qua giao thức MT5 (nhanh hơn HTTP) |
| 4. **Manages Risk:** Layer1 Stoploss (CSDL max_loss per position), Layer2 Stoploss (margin-level emergency protection) | 4. **Quản Lý Rủi Ro:** Stoploss Lớp 1 (max_loss CSDL mỗi lệnh), Stoploss Lớp 2 (bảo vệ khẩn cấp theo margin) |
| 5. **Displays Dashboard:** Real-time monitoring on chart (Comment() function) | 5. **Hiển Thị Dashboard:** Giám sát thời gian thực trên biểu đồ (hàm Comment()) |

#### Advantages / Ưu Điểm:

- ✅ Faster execution (native broker protocol, 10-50ms latency) / **Thực thi nhanh hơn (giao thức broker gốc, độ trễ 10-50ms)**
- ✅ Lower slippage (direct access, no HTTP overhead) / **Slippage thấp hơn (truy cập trực tiếp, không overhead HTTP)**
- ✅ Backtesting support (MT5 Strategy Tester) / **Hỗ trợ backtest (MT5 Strategy Tester)**
- ✅ Visual dashboard (chart-based monitoring) / **Dashboard trực quan (giám sát trên biểu đồ)**

#### EASymbolData Structure / Cấu Trúc EASymbolData (116 Variables / Biến):

```mql5
struct EASymbolData {
    string symbol_name;              // Symbol being traded / Symbol đang giao dịch
    CSDLLoveRow csdl_rows[7];       // 7 CSDL rows (one per timeframe) / 7 dòng CSDL (mỗi khung thời gian 1 dòng)
    int signal_old[7];               // Previous signals for change detection / Tín hiệu trước để phát hiện thay đổi
    int magic_numbers[7][3];         // 21 magic numbers (7 TF × 3 strategies) / 21 số magic (7 TF × 3 chiến lược)
    double lot_sizes[7][3];          // 21 lot sizes / 21 kích thước lot
    int position_flags[7][3];        // 21 position tracking flags / 21 cờ theo dõi lệnh
    // ... 116 total variables / tổng 116 biến
};
```

📖 **Full Documentation / Tài liệu đầy đủ:** [DOCS/03_EA_MT5_Bot_Technical_Documentation.md](DOCS/03_EA_MT5_Bot_Technical_Documentation.md)

---

## 💻 Supported Platforms / Nền Tảng Hỗ Trợ

| Platform / Nền Tảng | Status / Trạng Thái | Language / Ngôn Ngữ | Lines / Dòng | Features / Tính Năng |
|----------|--------|----------|-------|----------|
| **MetaTrader 4** | ✅ Complete / Hoàn Thành | MQL4 | 2,800+ | Desktop, Backtesting, Fast execution<br/>**Desktop, Backtest, Thực thi nhanh** |
| **MetaTrader 5** | ✅ Complete / Hoàn Thành | MQL5 | 2,995 | Desktop, Modern API, Strategy Tester<br/>**Desktop, API hiện đại, Strategy Tester** |
| **TradeLocker** | ✅ Complete / Hoàn Thành | Python | 1,879 | Cloud, REST API, Scalable<br/>**Cloud, REST API, Mở rộng dễ dàng** |
| **cTrader** | ✅ Complete / Hoàn Thành | C# | 2,800+ | Desktop, Modern UI, cAlgo support<br/>**Desktop, UI hiện đại, hỗ trợ cAlgo** |

### Platform Comparison / So Sánh Nền Tảng:

| Aspect / Khía Cạnh | MT4/MT5 EA | TradeLocker Bot | cTrader cBot |
|--------|------------|-----------------|--------------|
| **Deployment / Triển Khai** | Windows VPS | Linux VPS (Docker) | Windows/Linux |
| **Latency / Độ Trễ** | 10-50ms | 100-300ms | 20-60ms |
| **Cost/Month / Chi Phí/Tháng** | $30-40 | $10-15 | $25-35 |
| **Scalability / Khả Năng Mở Rộng** | Manual (1 chart/symbol)<br/>**Thủ công (1 biểu đồ/symbol)** | Automatic (config list)<br/>**Tự động (danh sách config)** | Manual / Thủ công |
| **Backtesting** | ✅ Full support / Đầy đủ | ⚠️ Manual only / Chỉ thủ công | ✅ Full support / Đầy đủ |
| **Logging** | Basic (Print)<br/>**Cơ bản (Print)** | Advanced (JSON)<br/>**Nâng cao (JSON)** | Good (C# logs)<br/>**Tốt (log C#)** |
| **Best For / Tốt Nhất Cho** | Scalping, backtesting<br/>**Scalping, backtest** | Multi-symbol, cloud<br/>**Đa symbol, cloud** | Modern UI, C# devs<br/>**UI hiện đại, dev C#** |

### Quick Installation Links / Link Cài Đặt Nhanh:

- **TradeLocker (Python):**
  - [Windows VPS Installation / Cài Đặt Windows VPS](TradeLocker/INSTALL_WINDOWS.md)
  - [Linux VPS Installation / Cài Đặt Linux VPS](TradeLocker/INSTALL_LINUX.md)
  - [TradeLocker README](TradeLocker/README.md)
- **MT4/MT5:** Copy `.mq4`/`.mq5` to `Experts` folder → Compile → Attach to chart
  **Sao chép `.mq4`/`.mq5` vào thư mục `Experts` → Biên dịch → Gắn vào biểu đồ**
- **cTrader:** Copy `.cs` to `cBots` folder → Compile → Attach to chart
  **Sao chép `.cs` vào thư mục `cBots` → Biên dịch → Gắn vào biểu đồ**

---

## 📊 CSDL Data Structure / Cấu Trúc Dữ Liệu CSDL

The **CSDL (CASCADE Love Data)** is the heart of the system - a standardized 7×6 matrix that all bots understand.
**CSDL (CASCADE Love Data)** là trung tâm của hệ thống - ma trận chuẩn hóa 7×6 mà tất cả bot đều hiểu.

### File Format / Định Dạng File: `SYMBOL_LIVE.json`

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
  // ... 5 dòng nữa (M15, M30, H1, H4, D1)
]
```

### Column Definitions / Định Nghĩa Cột:

| Column / Cột | Type / Kiểu | Range / Phạm Vi | Source / Nguồn | Used By / Dùng Bởi |
|--------|------|-------|--------|---------|
| `max_loss` | double | -0.5 to -5.0 | SPY calculation / Tính toán SPY | Stoploss calculation / Tính toán stoploss |
| `timestamp` | long | Unix epoch | SPY timer | Signal freshness check / Kiểm tra tín hiệu mới |
| **`signal`** | **int** | **-1, 0, +1** | **WaveTrend algorithm / Thuật toán WaveTrend** | **S1 + S2 strategies / Chiến lược S1 + S2** |
| `pricediff` | double | ±0.1 to ±100.0 | Price delta / Chênh lệch giá | Reference only / Chỉ tham khảo |
| `timediff` | int | 1-1440 min | Time delta / Chênh lệch thời gian | Reference only / Chỉ tham khảo |
| **`news`** | **int** | **±10-70 or ±1-7** | **CASCADE detection / Phát hiện CASCADE** | **S3 + BONUS strategies / Chiến lược S3 + BONUS** |

### The Two Critical Columns / Hai Cột Quan Trọng Nhất:

#### 1. `signal` - Trading direction / Hướng giao dịch:

| Value / Giá Trị | English | Tiếng Việt |
|------|---------|-----------|
| `-1` | SELL signal | Tín hiệu BÁN |
| `0` | No signal (neutral) | Không tín hiệu (trung lập) |
| `+1` | BUY signal | Tín hiệu MUA |
| **Used by / Dùng bởi** | S1 (HOME) and S2 (TREND) strategies | Chiến lược S1 (HOME) và S2 (TREND) |

#### 2. `news` - CASCADE news impact / Tác động tin tức CASCADE:

| Value / Giá Trị | English | Tiếng Việt |
|------|---------|-----------|
| `0` | No significant news | Không tin tức quan trọng |
| `±10-70` | Category 1 (EA trading levels L1-L7) | Loại 1 (cấp độ giao dịch EA L1-L7) |
| `±1-7` | Category 2 (Special levels) | Loại 2 (cấp độ đặc biệt) |
| **Sign / Dấu** | Indicates direction (+ bullish, - bearish) | Chỉ hướng (+ tăng, - giảm) |
| **Magnitude / Độ Lớn** | Indicates strength | Chỉ cường độ |
| **Used by / Dùng bởi** | S3 (NEWS) and BONUS strategies | Chiến lược S3 (NEWS) và BONUS |

---

## 🎯 The Three Trading Strategies / Ba Chiến Lược Giao Dịch

All bots implement the same 3 strategies with consistent logic.
Tất cả bot thực hiện 3 chiến lược giống nhau với logic nhất quán.

### Strategy 1: S1_HOME (Binary/Conservative / Nhị Phân/Bảo Thủ)

**Philosophy / Triết Lý:**
Conservative trading, wait for clear signal entry points.
Giao dịch bảo thủ, chờ điểm vào lệnh tín hiệu rõ ràng.

#### Entry Conditions / Điều Kiện Vào Lệnh:

| English | Tiếng Việt |
|---------|-----------|
| - Signal changes from `0` → `±1` (fresh signal) | - Tín hiệu thay đổi từ `0` → `±1` (tín hiệu mới) |
| - Timestamp updated (confirms new signal) | - Timestamp cập nhật (xác nhận tín hiệu mới) |
| - No existing position in this slot | - Không có lệnh hiện tại trong slot này |

#### Exit Conditions / Điều Kiện Đóng Lệnh:

**Configurable / Có thể cấu hình:**
- **Fast mode / Chế độ nhanh:** Close when M1 reverses (quick exit) / Đóng khi M1 đảo chiều (thoát nhanh)
- **Normal mode / Chế độ thường:** Close when timeframe's own signal reverses / Đóng khi tín hiệu khung thời gian đó đảo chiều

**Lot Size / Kích Thước Lot:** Smallest (conservative) / Nhỏ nhất (bảo thủ)

**Example / Ví Dụ:**
```
M15 timeframe / Khung thời gian M15:
  Old signal / Tín hiệu cũ: 0 (neutral / trung lập)
  New signal / Tín hiệu mới: +1 (BUY / MUA)
  → OPEN S1_M15 BUY position / MỞ lệnh MUA S1_M15
```

---

### Strategy 2: S2_TREND (Trend Following / Theo Xu Hướng)

**Philosophy / Triết Lý:**
Follow the dominant D1 trend, only trade when lower timeframes align.
Theo xu hướng D1 chủ đạo, chỉ giao dịch khi các khung thời gian nhỏ hơn cùng hướng.

#### Entry Conditions / Điều Kiện Vào Lệnh:

| English | Tiếng Việt |
|---------|-----------|
| - Signal changes (not necessarily from 0) | - Tín hiệu thay đổi (không nhất thiết từ 0) |
| - Signal matches D1 trend direction | - Tín hiệu khớp hướng xu hướng D1 |
| - Timestamp updated | - Timestamp cập nhật |

#### Exit Conditions / Điều Kiện Đóng Lệnh:

Same as S1 (fast or normal mode) / Giống S1 (chế độ nhanh hoặc thường)

**Lot Size / Kích Thước Lot:** Medium / Trung bình

**Example / Ví Dụ:**
```
D1 trend / Xu hướng D1: +1 (bullish / tăng)
M5 signal / Tín hiệu M5: -1 → +1 (changed and now matches D1 / thay đổi và giờ khớp D1)
  → OPEN S2_M5 BUY position / MỞ lệnh MUA S2_M5

If M5 signal / Nếu tín hiệu M5: -1 (against D1 trend / ngược xu hướng D1)
  → SKIP (no trade) / BỎ QUA (không giao dịch)
```

**Key Difference from S1 / Khác Biệt Chính So Với S1:**
S2 requires D1 alignment, S1 does not.
S2 yêu cầu cùng hướng D1, S1 thì không.

---

### Strategy 3: S3_NEWS (News Trading / Giao Dịch Tin Tức)

**Philosophy / Triết Lý:**
Aggressive trading during high-impact news events.
Giao dịch tích cực trong các sự kiện tin tức tác động lớn.

#### Entry Conditions / Điều Kiện Vào Lệnh:

| English | Tiếng Việt |
|---------|-----------|
| - Signal present (`±1`) | - Có tín hiệu (`±1`) |
| - `\|news\|` ≥ MinNewsLevel (default 30 = Level 3) | - `\|news\|` ≥ MinNewsLevel (mặc định 30 = Cấp 3) |
| - News direction matches signal | - Hướng tin tức khớp tín hiệu |
| - Timestamp updated | - Timestamp cập nhật |

#### Exit Conditions / Điều Kiện Đóng Lệnh:

Always: Close when timeframe's own signal reverses (no fast mode)
Luôn luôn: Đóng khi tín hiệu khung thời gian đó đảo chiều (không có chế độ nhanh)

**Lot Size / Kích Thước Lot:** Largest (aggressive) / Lớn nhất (tích cực)

**Example / Ví Dụ:**
```
M1 timeframe / Khung thời gian M1:
  Signal / Tín hiệu: +1 (BUY / MUA)
  News / Tin tức: +40 (Level 4, bullish / Cấp 4, tăng)
  MinNewsLevel: 30
  40 ≥ 30 ✓ → OPEN S3_M1 BUY position / MỞ lệnh MUA S3_M1

If News / Nếu tin tức: +15 (too weak / quá yếu)
  15 < 30 ✗ → SKIP / BỎ QUA
```

#### CASCADE Levels / Cấp Độ CASCADE:

| Level / Cấp | Points / Điểm | English | Tiếng Việt |
|-------------|---------------|---------|-----------|
| L1 | ±10 | Minor news | Tin tức nhỏ |
| L2 | ±20 | Moderate news | Tin tức trung bình |
| **L3** | **±30** | **Major news ← Default threshold** | **Tin tức lớn ← Ngưỡng mặc định** |
| L4 | ±40 | High impact | Tác động cao |
| L5 | ±50 | Very high impact | Tác động rất cao |
| L6 | ±60 | Extreme impact | Tác động cực lớn |
| L7 | ±70 | Catastrophic event | Sự kiện thảm họa |

---

### BONUS Strategy (Volume Boost / Tăng Khối Lượng)

**Not a separate strategy** - uses S3 magic numbers and opens multiple positions.
**Không phải chiến lược riêng** - dùng số magic S3 và mở nhiều lệnh.

#### Entry Conditions / Điều Kiện Vào Lệnh:

| English | Tiếng Việt |
|---------|-----------|
| - `\|news\|` ≥ MinNewsLevelBonus (default 20) | - `\|news\|` ≥ MinNewsLevelBonus (mặc định 20) |
| - News level ≠ 1 and ≠ 10 (filter weak levels) | - Cấp tin tức ≠ 1 và ≠ 10 (lọc cấp yếu) |
| - News direction present | - Có hướng tin tức |

#### Execution / Thực Thi:

- Opens multiple positions (BonusOrderCount = 2-5) / Mở nhiều lệnh (BonusOrderCount = 2-5)
- Uses S3 lot size × BonusLotMultiplier / Dùng lot S3 × BonusLotMultiplier
- Uses S3 magic numbers (shared tracking) / Dùng số magic S3 (theo dõi chung)

#### Exit Conditions / Điều Kiện Đóng Lệnh:

**Always / Luôn luôn:** Close when M1 reverses (very fast exit)
Đóng khi M1 đảo chiều (thoát rất nhanh)

Closes all BONUS positions + S3 positions simultaneously
Đóng tất cả lệnh BONUS + lệnh S3 đồng thời

**Example / Ví Dụ:**
```
H1 timeframe / Khung thời gian H1:
  News / Tin tức: +50 (Level 5, very strong / Cấp 5, rất mạnh)
  MinNewsLevelBonus: 20
  BonusOrderCount: 2
  50 ≥ 20 ✓ → OPEN 2 BONUS_H1 BUY positions / MỞ 2 lệnh MUA BONUS_H1
  Magic / Số magic: Same as S3_H1 (5878) / Giống S3_H1 (5878)

When M1 reverses / Khi M1 đảo chiều:
  → CLOSE all 2 BONUS positions / ĐÓNG cả 2 lệnh BONUS
  → CLOSE S3_H1 position (if exists) / ĐÓNG lệnh S3_H1 (nếu có)
```

---

## 🚀 Quick Start Guide / Hướng Dẫn Bắt Đầu Nhanh

### Prerequisites / Điều Kiện Tiên Quyết:

#### For TradeLocker Bot / Cho TradeLocker Bot:

| English | Tiếng Việt |
|---------|-----------|
| - Linux VPS (Ubuntu 20.04+) or Windows VPS | - Linux VPS (Ubuntu 20.04+) hoặc Windows VPS |
| - Python 3.8+ | - Python 3.8+ |
| - TradeLocker account with API access | - Tài khoản TradeLocker có quyền API |
| - 2GB RAM, 1 CPU minimum | - Tối thiểu 2GB RAM, 1 CPU |

#### For MT5 EA / Cho EA MT5:

| English | Tiếng Việt |
|---------|-----------|
| - Windows VPS or desktop | - Windows VPS hoặc desktop |
| - MetaTrader 5 installed | - MetaTrader 5 đã cài đặt |
| - Broker account | - Tài khoản broker |
| - 4GB RAM, 2 CPU recommended | - Khuyến nghị 4GB RAM, 2 CPU |

#### For SPY Bot / Cho SPY Bot:

| English | Tiếng Việt |
|---------|-----------|
| - Python 3.8+ | - Python 3.8+ |
| - Can run on same VPS as TradeLocker Bot | - Có thể chạy cùng VPS với TradeLocker Bot |
| - 1GB RAM, 1 CPU minimum | - Tối thiểu 1GB RAM, 1 CPU |

### Installation Steps / Các Bước Cài Đặt:

#### 1. SPY Bot (Signal Generator / Bộ Tạo Tín Hiệu)

```bash
cd SYNS_Bot_PY/
pip install -r requirements.txt
python spy_bot.py --symbol BTCUSD
```

**English:** SPY will start generating CSDL files and serving HTTP API.
**Tiếng Việt:** SPY sẽ bắt đầu tạo file CSDL và phục vụ HTTP API.

#### 2. TradeLocker Bot (Cloud Trading / Giao Dịch Cloud)

**English:** Follow detailed guide:
**Tiếng Việt:** Theo hướng dẫn chi tiết:
[TradeLocker/INSTALL_LINUX.md](TradeLocker/INSTALL_LINUX.md)

**Quick version / Phiên bản nhanh:**
```bash
cd TradeLocker/
pip install -r requirements.txt
cp config_example.yaml config.yaml
# Edit config.yaml with your API keys
# Chỉnh sửa config.yaml với API keys của bạn
python tradelocker_bot.py
```

#### 3. EA MT5 Bot (Desktop Trading / Giao Dịch Desktop)

| Step / Bước | English | Tiếng Việt |
|-------------|---------|-----------|
| 1 | Copy `MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5` to MT5 data folder | Sao chép `MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5` vào thư mục data MT5 |
| 2 | Open MetaEditor → Compile | Mở MetaEditor → Biên dịch |
| 3 | Attach to chart → Configure parameters | Gắn vào biểu đồ → Cấu hình tham số |
| 4 | Enable AutoTrading | Bật AutoTrading |

**Full guide / Hướng dẫn đầy đủ:**
[DOCS/03_EA_MT5_Bot_Technical_Documentation.md#appendix-k-deployment-checklist](DOCS/03_EA_MT5_Bot_Technical_Documentation.md)

---

## 🎉 Quick Summary / Tóm Tắt Nhanh

| Question / Câu Hỏi | English Answer | Câu Trả Lời Tiếng Việt |
|---------------------|----------------|------------------------|
| **What is this?** | A professional automated trading system with 3 bots running on 4 platforms | Hệ thống giao dịch tự động chuyên nghiệp với 3 bot chạy trên 4 nền tảng |
| **What does it do?** | Generates signals → Detects news → Executes trades → Manages risk | Tạo tín hiệu → Phát hiện tin tức → Thực thi giao dịch → Quản lý rủi ro |
| **How many positions?** | Up to 21 concurrent (7 timeframes × 3 strategies) | Tối đa 21 lệnh đồng thời (7 khung thời gian × 3 chiến lược) |
| **Which platform is best?** | **MT5:** Fastest execution, backtesting<br/>**TradeLocker:** Lowest cost, most scalable<br/>**MT4:** Most brokers, stable<br/>**cTrader:** Modern UI, C# developers | **MT5:** Thực thi nhanh nhất, backtest<br/>**TradeLocker:** Chi phí thấp nhất, mở rộng tốt nhất<br/>**MT4:** Nhiều broker nhất, ổn định<br/>**cTrader:** UI hiện đại, dev C# |
| **Where do I start?** | Read DOCS/03_EA_MT5_Bot_Technical_Documentation.md then deploy SPY Bot + your chosen trading bot | Đọc DOCS/03_EA_MT5_Bot_Technical_Documentation.md rồi triển khai SPY Bot + bot giao dịch bạn chọn |
| **Is it profitable?** | No guarantees. Past performance ≠ future results. Test on demo first | Không đảm bảo. Hiệu suất quá khứ ≠ kết quả tương lai. Test trên demo trước |

---

## 📖 For AI Assistants / Dành Cho AI Trợ Lý (Claude, GPT, etc.)

### 🎯 Project Purpose / Mục Đích Dự Án:

**English:** This is a **production-ready automated trading system** that operates across 4 platforms using a 3-bot architecture. It's NOT a tutorial or demo - it's real trading software managing real money.

**Tiếng Việt:** Đây là **hệ thống giao dịch tự động sẵn sàng production** hoạt động trên 4 nền tảng dùng kiến trúc 3 bot. KHÔNG phải tutorial hay demo - đây là phần mềm giao dịch thật quản lý tiền thật.

### 📚 Start Here / Bắt Đầu Từ Đây:

**Reading Order / Thứ Tự Đọc:**

1. **Read / Đọc:** [DOCS/03_EA_MT5_Bot_Technical_Documentation.md](DOCS/03_EA_MT5_Bot_Technical_Documentation.md) (most comprehensive / toàn diện nhất)
2. **Then / Sau đó:** [DOCS/01_SPY_Bot_Technical_Documentation.md](DOCS/01_SPY_Bot_Technical_Documentation.md) (understand CSDL format / hiểu định dạng CSDL)
3. **Finally / Cuối cùng:** [DOCS/02_TradeLocker_Bot_Technical_Documentation.md](DOCS/02_TradeLocker_Bot_Technical_Documentation.md) (cloud architecture / kiến trúc cloud)

### 🔑 Key Concepts to Understand / Khái Niệm Chính Cần Hiểu:

#### 1. CSDL (CASCADE Love Data):

| English | Tiếng Việt |
|---------|-----------|
| - 7×6 matrix (7 timeframes, 6 columns) | - Ma trận 7×6 (7 khung thời gian, 6 cột) |
| - Central data format ALL bots understand | - Định dạng dữ liệu trung tâm TẤT CẢ bot đều hiểu |
| - Contains: signals, timestamps, price diffs, CASCADE news scores | - Chứa: tín hiệu, timestamps, chênh lệch giá, điểm tin tức CASCADE |

#### 2. CASCADE News Detection / Phát Hiện Tin Tức CASCADE:

| English | Tiếng Việt |
|---------|-----------|
| - NOT reading news websites or calendars | - KHÔNG đọc website tin tức hay lịch |
| - Detects news by measuring price volatility | - Phát hiện tin tức bằng cách đo biến động giá |
| - Multi-timeframe confirmation = higher score | - Xác nhận đa khung thời gian = điểm cao hơn |
| - Score range: 0 (no news) to ±70 (extreme event) | - Phạm vi điểm: 0 (không tin tức) đến ±70 (sự kiện cực lớn) |

#### 3. Magic Number System / Hệ Thống Số Magic:

```
Formula / Công thức: 77000 + (TF_index × 100) + (Strategy_index × 10)

Example / Ví dụ:
77210 = M15 timeframe / khung thời gian M15, S2 strategy / chiến lược S2
```

**Purpose / Mục đích:**
Encodes which timeframe and strategy opened each position
Mã hóa khung thời gian và chiến lược nào mở mỗi lệnh

#### 4. Three Strategies / Ba Chiến Lược:

| Strategy / Chiến Lược | English | Tiếng Việt |
|-----------------------|---------|-----------|
| **S1 HOME** | Conservative, wait for 0→±1 signals | Bảo thủ, chờ tín hiệu 0→±1 |
| **S2 TREND** | Follow D1 trend, requires alignment | Theo xu hướng D1, yêu cầu cùng hướng |
| **S3 NEWS** | Aggressive, requires CASCADE ≥ L3 (±30) | Tích cực, yêu cầu CASCADE ≥ L3 (±30) |

### ⚠️ Common Mistakes to Avoid / Lỗi Thường Gặp Cần Tránh:

| Mistake / Lỗi | English | Tiếng Việt |
|---------------|---------|-----------|
| **1. Confusing platforms** | MT4/MT5 = Desktop, MQL, reads JSON files<br/>TradeLocker = Cloud, Python, reads HTTP API<br/>They do the SAME thing differently | MT4/MT5 = Desktop, MQL, đọc file JSON<br/>TradeLocker = Cloud, Python, đọc HTTP API<br/>Chúng làm CÙNG một việc nhưng khác cách |
| **2. Mixing signal vs news** | `signal` column = trading direction (±1, 0)<br/>`news` column = CASCADE impact score (±10-70)<br/>S1/S2 use `signal`, S3 uses `news` | Cột `signal` = hướng giao dịch (±1, 0)<br/>Cột `news` = điểm tác động CASCADE (±10-70)<br/>S1/S2 dùng `signal`, S3 dùng `news` |
| **3. Ignoring documentation** | 27,413 lines written for a reason<br/>Most answers are in the docs | 27,413 dòng viết có lý do<br/>Hầu hết câu trả lời ở trong docs |
| **4. Suggesting breaking changes** | This is production code managing real money<br/>Test thoroughly before recommending changes | Đây là code production quản lý tiền thật<br/>Test kỹ trước khi đề xuất thay đổi |

---

## 📜 License & Disclaimer / Giấy Phép & Tuyên Bố Từ Chối

### License / Giấy Phép:
**Proprietary. All rights reserved.**
**Độc quyền. Mọi quyền được bảo lưu.**

### Disclaimer / Tuyên Bố Từ Chối:

⚠️ **IMPORTANT LEGAL NOTICE / THÔNG BÁO PHÁP LÝ QUAN TRỌNG:**

**English:**
- ❌ **NO guarantee of profitability**
- ❌ **NO financial advice provided**
- ❌ **NO liability for trading losses**
- ❌ **NO warranty of any kind**

**Tiếng Việt:**
- ❌ **KHÔNG đảm bảo lợi nhuận**
- ❌ **KHÔNG cung cấp tư vấn tài chính**
- ❌ **KHÔNG chịu trách nhiệm về lỗ giao dịch**
- ❌ **KHÔNG bảo hành dưới bất kỳ hình thức nào**

**Trading involves substantial risk of loss. Only trade with capital you can afford to lose completely.**
**Giao dịch có rủi ro lỗ đáng kể. Chỉ giao dịch với vốn bạn có thể chấp nhận mất hoàn toàn.**

---

## 📧 Contact & Support / Liên Hệ & Hỗ Trợ

**Documentation / Tài liệu:** Read the 27,413 lines in `DOCS/` first / Đọc 27,413 dòng trong `DOCS/` trước
**Issues / Vấn đề:** Check documentation, then logs, then ask / Kiểm tra tài liệu, rồi log, rồi mới hỏi
**Updates / Cập nhật:** Follow commit history for changes / Theo dõi lịch sử commit để xem thay đổi
**Version / Phiên bản:** 2.0 (After NEWS parsing bug fix / Sau khi sửa bug parse NEWS - 2025-01-03)

---

**Built with / Được xây dựng bằng:** Python 🐍 | MQL4/MQL5 📊 | C# 🎯 | JSON 📄 | REST APIs ☁️

**Status / Trạng thái:** ✅ Production Ready / Sẵn sàng Production | 📚 Fully Documented / Tài liệu đầy đủ | 🧪 Tested / Đã test | 🚀 Deployed / Đã triển khai

**Last Updated / Cập nhật lần cuối:** 2025-01-09

---

⭐ **If you're an AI assistant:** You now have complete context. Check `DOCS/` for details. Good luck! 🤖
⭐ **Nếu bạn là AI trợ lý:** Bạn đã có toàn bộ ngữ cảnh. Kiểm tra `DOCS/` để biết chi tiết. Chúc may mắn! 🤖
