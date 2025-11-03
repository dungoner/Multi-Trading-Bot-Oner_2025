# 🤖 Multi-Trading Bot System - Architecture Guide

## 📋 MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
   - 1.1 [Kiến trúc 2-Bot System](#11-kiến-trúc-2-bot-system)
   - 1.2 [LUỒNG HOẠT ĐỘNG CHÍNH](#12-luồng-hoạt-động-chính)
2. [BOT SPY - Thu thập & Phân tích](#2-bot-spy---thu-thập--phân-tích)
3. [BOT EA AUTO - Giao dịch tự động](#3-bot-ea-auto---giao-dịch-tự-động)
4. [Cấu trúc dữ liệu CSDL](#4-cấu-trúc-dữ-liệu-csdl)
5. [Reset & HealthCheck](#5-reset--healthcheck)
6. [Timeline hoạt động](#6-timeline-hoạt-động)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Kiến trúc 2-Bot System

```
┌─────────────────────────────────────────────────────────────────┐
│                     MT4 PLATFORM (VPS)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────┐          ┌─────────────────────┐       │
│  │  WALLSTREET EA     │ ══════>  │    BOT SPY V2       │       │
│  │  (7 charts)        │ Global   │    (Indicator)      │       │
│  │                    │ Variable │                     │       │
│  │  M1, M5, M15       │          │  Thu thập & Phân    │       │
│  │  M30, H1, H4, D1   │          │  tích 7 TF          │       │
│  └────────────────────┘          └──────────┬──────────┘       │
│                                              │                  │
│                                              ▼                  │
│                                  ┌────────────────────┐         │
│                                  │   CSDL FILES       │         │
│                                  │   (.json format)   │         │
│                                  │   10 cột × 7 TF    │         │
│                                  └──────────┬─────────┘         │
│                                              │                  │
│                                              ▼                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │        BOT EA AUTO (7 EA - Auto Trading)                  │ │
│  │     M1-EA  M5-EA  M15-EA  M30-EA  H1-EA  H4-EA  D1-EA     │ │
│  │     3 Strategies: S1 (HOME) + S2 (TREND) + S3 (NEWS)      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│                          BROKER                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 LUỒNG HOẠT ĐỘNG CHÍNH

#### Sơ đồ luồng tổng quan

```
STEP 1: WALLSTREET EA → GlobalVariable (Tín hiệu gốc)
   ↓
STEP 2: BOT SPY → Đọc GlobalVariable
   ↓
   ├─→ PHẦN 1: Xử lý TÍN HIỆU GỐC (Column 2)
   │   ├─ Đọc 14 GlobalVariables (7 TF × 2 biến)
   │   ├─ Lưu signal: -1 (SELL), 0 (NONE), 1 (BUY)
   │   ├─ Tính PriceDiff USD
   │   └─ Tính TimeDiff minutes
   │
   └─→ PHẦN 2: Xử lý TÍN HIỆU NEWS (Column 8)
       ├─ Phân tích NEWS CASCADE patterns
       ├─ Tính toán tác động tin tức (L1-L7)
       └─ Kết quả: ±11 đến ±16 hoặc 0
   ↓
STEP 3: GHI CSDL FILES (10 cột × 7 TF)
   ↓
STEP 4: BOT EA AUTO → Đọc CSDL Files
   ↓
   ├─→ PHẦN 1: Giao dịch theo TÍN HIỆU GỐC (đọc Column 2)
   │   ├─ S1 (HOME): Binary signal + NEWS filter
   │   └─ S2 (TREND): Follow D1 trend
   │
   └─→ PHẦN 2: Giao dịch theo TÍN HIỆU NEWS (đọc Column 8)
       └─ S3 (NEWS): News trading theo CASCADE
   ↓
STEP 5: Gửi lệnh BUY/SELL → BROKER
```

#### Chi tiết 2 phần xử lý

**BOT SPY - Chia 2 phần:**

```
┌─────────────────────────────────────────────────────────────┐
│        PHẦN 1: XỬ LÝ TÍN HIỆU GỐC → Column 2 (signal)      │
├─────────────────────────────────────────────────────────────┤
│  INPUT:  GlobalVariable từ 7 WallStreet EA                  │
│          Format: SYMBOL_TF_SignalType1 = -1/0/1             │
│                                                             │
│  PROCESS:                                                   │
│  • Đọc signal mỗi giây                                      │
│  • So sánh timestamp (tránh duplicate)                      │
│  • Tính PriceDiff = |Current Price - Last Signal Price|    │
│  • Tính TimeDiff = Current Time - Last Signal Time         │
│                                                             │
│  OUTPUT:                                                    │
│  • Column 2: Signal (-1/0/1)                                │
│  • Column 3: Price                                          │
│  • Column 6: PriceDiff USD                                  │
│  • Column 7: TimeDiff minutes                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│       PHẦN 2: XỬ LÝ TÍN HIỆU NEWS → Column 8 (news)        │
├─────────────────────────────────────────────────────────────┤
│  INPUT:  Signal + PriceDiff + TimeDiff từ PHẦN 1           │
│                                                             │
│  PROCESS:                                                   │
│  • Phân tích NEWS CASCADE patterns                          │
│  • Category 1 (EA Trading): LiveDiff threshold              │
│    └─ L1: 2.5 USD, L2: 3.0 USD, ... L7: 5.5 USD            │
│  • Category 2 (User Reference): Time-based                  │
│    └─ L1: 2min, L2: 4min, ... L7: 128min                    │
│  • Kết hợp 2 categories → Tính NEWS level                   │
│                                                             │
│  OUTPUT:                                                    │
│  • Column 8: NEWS result                                    │
│    └─ +11 đến +16 (BUY L1-L7)                               │
│    └─ -11 đến -16 (SELL L1-L7)                              │
│    └─ 0 (No NEWS)                                           │
└─────────────────────────────────────────────────────────────┘
```

**BOT EA AUTO - Chia 2 phần:**

```
┌─────────────────────────────────────────────────────────────┐
│   PHẦN 1: Giao dịch theo TÍN HIỆU GỐC (đọc Column 2)       │
├─────────────────────────────────────────────────────────────┤
│  S1 (HOME) - Binary Signal Trading:                         │
│  ├─ Đọc: signal (Column 2)                                  │
│  ├─ Filter: NEWS filter (nếu bật S1_UseNewsFilter)          │
│  ├─ Logic: Signal = 1 → BUY, Signal = -1 → SELL            │
│  └─ Đóng: Khi signal đảo chiều                              │
│                                                             │
│  S2 (TREND) - Follow D1 Trend:                              │
│  ├─ Đọc: signal (Column 2) của D1                           │
│  ├─ Logic: D1 signal = 1 → CHỈ BUY tất cả TF                │
│  │         D1 signal = -1 → CHỈ SELL tất cả TF              │
│  └─ Đóng: Khi D1 signal đảo chiều                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│   PHẦN 2: Giao dịch theo TÍN HIỆU NEWS (đọc Column 8)      │
├─────────────────────────────────────────────────────────────┤
│  S3 (NEWS) - News CASCADE Trading:                          │
│  ├─ Đọc: news (Column 8)                                    │
│  ├─ Filter: news_abs >= MinNewsLevelS3 (20-70)             │
│  ├─ Logic: news = +11~+16 → BUY                             │
│  │         news = -11~-16 → SELL                            │
│  │         news = 0 → SKIP                                  │
│  ├─ Bonus: Nếu EnableBonusNews = true                       │
│  │   └─ Quét 7 TF, mở thêm BonusOrderCount lệnh            │
│  └─ Đóng: Khi signal đảo chiều                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. BOT SPY - Thu thập & Phân tích

### 2.1 Thông tin cơ bản

**File:** `MQL4/Indicators/Super_Spy7TF_V2.mq4`
**Loại:** Indicator (chạy trên 1 chart, monitor 7 TF)
**Chức năng:** Thu thập GlobalVariable → Phân tích → Ghi CSDL files

### 2.2 Cấu trúc dữ liệu chính

```cpp
struct SymbolCSDL1Data {
    // === 10 CỘT CSDL (7 TF) ===
    int signals[7];           // Column 2: Signal (-1, 0, 1)
    double prices[7];         // Column 3: Price
    long crosses[7];          // Column 4: Cross (timestamp prev TF)
    long timestamps[7];       // Column 5: Timestamp
    double pricediffs[7];     // Column 6: PriceDiff USD
    int timediffs[7];         // Column 7: TimeDiff minutes
    int news_results[7];      // Column 8: NEWS CASCADE (±11-16 or 0)
    double max_losses[7];     // Column 9: Max Loss

    // === TRACKING (TRÁNH DUPLICATE) ===
    long processed_timestamps[7];  // Đã xử lý timestamp nào
    int signals_last[7];           // Signal trước đó
    double prices_last[7];         // Price trước đó

    // === HISTORY (7 TF × 7 entries) ===
    SignalHistoryEntry m1_history[7];
    SignalHistoryEntry m5_history[7];
    // ... (M15, M30, H1, H4, D1)

    // === METADATA ===
    int files_written;        // Số lần ghi file
};

SymbolCSDL1Data g_symbol_data;  // GLOBAL STRUCT DUY NHẤT
```

### 2.3 OnInit - Khởi động

```cpp
int OnInit() {
    1. DiscoverSymbolFromChart()     // Auto detect: LTCUSD, BTCUSD...
    2. InitSymbolData()               // Khởi tạo arrays 7 TF
    3. CreateFolderStructure()        // Tạo DataAutoOner/
    4. CreateEmptyCSDL1File()         // Tạo JSON rỗng (nếu chưa có)
    5. LoadCSDL1FileIntoArray()       // Load history từ file
    6. EventSetTimer(1)               // Start timer 1 giây

    return INIT_SUCCEEDED;
}
```

### 2.4 OnTimer - Xử lý mỗi giây

```cpp
void OnTimer() {
    int current_second = TimeSeconds(TimeCurrent());

    // ═══════════════════════════════════════
    // PHASE 1: XỬ LÝ TÍN HIỆU (MỌI GIÂY)
    // ═══════════════════════════════════════
    if(ProcessSignalOnOddSecond) {
        if(current_second % 2 == 1) {
            ProcessAllSignals();  // Giây lẻ: 1,3,5,7,9...
        }
    } else {
        ProcessAllSignals();      // Mọi giây
    }

    // ═══════════════════════════════════════
    // PHASE 2: CHỨC NĂNG PHỤ (GIÂY CHẴN)
    // ═══════════════════════════════════════
    if(current_second % 2 == 0) {
        UpdateLiveNEWS();                  // Update NEWS realtime
        RunMidnightAndHealthCheck();       // 0h reset / 5h,10h,15h,20h check
        RunDashboardUpdate();              // Update on-chart info
    }
}
```

### 2.5 ProcessAllSignals - Vòng lặp 7 TF

```cpp
void ProcessAllSignals() {
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};

    for(int i = 0; i < 7; i++) {
        // ĐỌC GlobalVariable
        string signal_var = g_target_symbol + "_" + tf_names[i] + "_SignalType1";
        string time_var = g_target_symbol + "_" + tf_names[i] + "_LastSignalTime";

        int signal = (int)GlobalVariableGet(signal_var);
        long signal_time = (long)GlobalVariableGet(time_var);

        // KIỂM TRA: Signal mới && Timestamp mới
        if(signal != 0 && signal_time > g_symbol_data.processed_timestamps[i]) {
            ProcessSignalForTF(i, signal, signal_time);
        }
    }
}
```

### 2.6 ProcessSignalForTF - Xử lý 1 TF

```cpp
bool ProcessSignalForTF(int tf_idx, int signal, long signal_time) {

    // ═══════════════════════════════════════════════════
    // PHẦN 1: XỬ LÝ TÍN HIỆU GỐC → Column 2,3,6,7
    // ═══════════════════════════════════════════════════
    double current_price = (signal > 0) ? Ask : Bid;
    double pricediff_usd = CalculatePriceDiffUSD(...);  // Column 6
    int timediff_min = CalculateTimeDiffMinutes(...);    // Column 7

    // ═══════════════════════════════════════════════════
    // PHẦN 2: XỬ LÝ TÍN HIỆU NEWS → Column 8
    // ═══════════════════════════════════════════════════
    int news_result = AnalyzeNEWS_CASCADE(signal, pricediff_usd, timediff_min);

    // CẬP NHẬT ARRAYS
    g_symbol_data.signals[tf_idx] = signal;          // Column 2
    g_symbol_data.prices[tf_idx] = current_price;    // Column 3
    g_symbol_data.timestamps[tf_idx] = signal_time;  // Column 5
    g_symbol_data.pricediffs[tf_idx] = pricediff_usd; // Column 6
    g_symbol_data.timediffs[tf_idx] = timediff_min;   // Column 7
    g_symbol_data.news_results[tf_idx] = news_result; // Column 8

    // UPDATE HISTORY (7 entries)
    UpdateSignalHistory(tf_idx);

    // GHI FILES
    WriteCSDL1ArrayToFile();   // SYMBOL.json (10 cột + history)
    WriteCSDL2ArrayToFile();   // SYMBOL_LIVE.json (6 cột, 3 files)

    // ĐÁNH DẤU ĐÃ XỬ LÝ
    g_symbol_data.processed_timestamps[tf_idx] = signal_time;

    return true;
}
```

### 2.7 GlobalVariable Format

**WallStreet EA gửi 14 biến/symbol:**

```cpp
// 7 TF × 2 biến = 14 biến
LTCUSD_M1_SignalType1       = -1    // Signal: -1=SELL, 0=NONE, 1=BUY
LTCUSD_M1_LastSignalTime    = 1760340720  // Timestamp

LTCUSD_M5_SignalType1       = 1
LTCUSD_M5_LastSignalTime    = 1760340800

// ... M15, M30, H1, H4, D1
```

**Cách xem:** F3 → Terminal → Global Variables → Tìm "LTCUSD_M1_"

---

## 3. BOT EA AUTO - Giao dịch tự động

### 3.1 Thông tin cơ bản

**File:** `MQL4/Experts/Eas_Smf_Oner_V2.mq4`
**Loại:** Expert Advisor (mỗi EA chạy trên 1 TF)
**Chức năng:** Đọc CSDL → Mở/đóng lệnh theo 3 strategies

### 3.2 Input Parameters

```cpp
// A. CORE SETTINGS
input bool TF_M1 = true;    // Bật/tắt từng TF
input bool TF_M5 = true;
// ... (M15, M30, H1, H4, D1)

input bool S1_HOME = true;   // S1: Binary signal
input bool S2_TREND = true;  // S2: Follow D1
input bool S3_NEWS = true;   // S3: News trading

input double FixedLotSize = 0.1;
input CSDL_SOURCE_ENUM CSDL_Source = FOLDER_2;  // DataAutoOner, 2, 3

// B. STRATEGY CONFIG
input bool S1_UseNewsFilter = true;       // S1: Lọc NEWS
input int MinNewsLevelS1 = 20;            // S1: Ngưỡng NEWS

input S2_TREND_MODE S2_TrendMode = S2_FOLLOW_D1;  // S2: Auto/Manual

input int MinNewsLevelS3 = 20;            // S3: Ngưỡng NEWS
input bool EnableBonusNews = true;        // S3: Bonus orders
input int BonusOrderCount = 2;            // S3: Số lệnh bonus

// C. RISK PROTECTION
input STOPLOSS_MODE StoplossMode = LAYER1_MAXLOSS;
input double Layer2_Divisor = 5.0;
input bool UseTakeProfit = false;

// D. AUXILIARY
input bool EnableWeekendReset = true;
input bool EnableHealthCheck = true;
input bool ShowDashboard = true;
```

### 3.3 Cấu trúc dữ liệu EA

```cpp
struct EASymbolData {
    // === CSDL ROWS (7 TF) ===
    CSDLLoveRow csdl_rows[7];  // Đọc từ CSDL file
    // struct CSDLLoveRow {
    //     double max_loss;
    //     long timestamp;
    //     int signal;        ← PHẦN 1: S1+S2 đọc
    //     double pricediff;
    //     int timediff;
    //     int news;          ← PHẦN 2: S3 đọc
    // }

    // === TRACKING (7 TF) ===
    int signal_old[7];         // Signal cũ (để so sánh đảo chiều)
    datetime timestamp_old[7]; // Timestamp cũ

    // === MAGIC NUMBERS (7 TF × 3 Strategies = 21) ===
    int magic_numbers[7][3];   // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // === LOT SIZES (21) ===
    double lot_sizes[7][3];    // Pre-calculated từ FixedLotSize

    // === POSITION FLAGS (21) ===
    int position_flags[7][3];  // 0=No order, 1=Order open

    // === STOPLOSS THRESHOLDS (21) ===
    double layer1_thresholds[7][3];  // max_loss × lot
};

EASymbolData g_ea;  // GLOBAL STRUCT DUY NHẤT
```

### 3.4 OnTimer - Vòng lặp chính

```cpp
void OnTimer() {
    // STEP 1: ĐỌC CSDL FILE
    if(!ReadCSDLToArray()) {
        // Nếu fail → Dùng MaxLoss_Fallback (-1000 USD)
        return;
    }

    // STEP 2: QUÉT 7 TF
    for(int tf = 0; tf < 7; tf++) {
        if(!IsTFEnabled(tf)) continue;

        // KIỂM TRA: Signal đảo chiều?
        bool signal_changed = (g_ea.signal_old[tf] != g_ea.csdl_rows[tf].signal);
        bool timestamp_new = (g_ea.timestamp_old[tf] != (datetime)g_ea.csdl_rows[tf].timestamp);

        if(signal_changed && timestamp_new) {

            // STEP 2.1: Đóng lệnh cũ (ALL 3 strategies)
            CloseAllStrategiesByMagicForTF(tf);

            // STEP 2.2: Mở lệnh mới
            if(S1_HOME) ProcessS1Strategy(tf);
            if(S2_TREND) ProcessS2Strategy(tf);
            if(S3_NEWS) ProcessS3Strategy(tf);

            // STEP 2.3: Update baseline
            g_ea.signal_old[tf] = g_ea.csdl_rows[tf].signal;
            g_ea.timestamp_old[tf] = (datetime)g_ea.csdl_rows[tf].timestamp;
        }
    }

    // STEP 3: KIỂM TRA STOPLOSS (Mọi vòng)
    if(StoplossMode != NONE) {
        CheckAndCloseStoploss();
    }
}
```

### 3.5 ProcessS1Strategy - Binary Signal

```cpp
void ProcessS1Strategy(int tf) {
    // ═══════════════════════════════════════
    // ĐỌC PHẦN 1: TÍN HIỆU GỐC (Column 2)
    // ═══════════════════════════════════════
    int current_signal = g_ea.csdl_rows[tf].signal;  // Column 2

    if(current_signal == 0) return;

    // FILTER: NEWS filter (nếu bật)
    if(S1_UseNewsFilter) {
        int news_abs = MathAbs(g_ea.csdl_rows[tf].news);
        if(news_abs < MinNewsLevelS1) return;

        if(S1_RequireNewsDirection) {
            int news_dir = (g_ea.csdl_rows[tf].news > 0) ? 1 : -1;
            if(current_signal != news_dir) return;
        }
    }

    // MỞ LỆNH
    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, ...);
        if(ticket > 0) g_ea.position_flags[tf][0] = 1;
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, ...);
        if(ticket > 0) g_ea.position_flags[tf][0] = 1;
    }
}
```

### 3.6 ProcessS2Strategy - Follow Trend

```cpp
void ProcessS2Strategy(int tf) {
    // ═══════════════════════════════════════
    // ĐỌC PHẦN 1: TÍN HIỆU GỐC D1 (Column 2)
    // ═══════════════════════════════════════
    int current_signal = g_ea.csdl_rows[tf].signal;  // Column 2
    int trend_to_follow = g_ea.csdl_rows[6].signal;  // D1 (tf_idx=6)

    // OVERRIDE: Manual mode
    if(S2_TrendMode == S2_FORCE_BUY) trend_to_follow = 1;
    else if(S2_TrendMode == S2_FORCE_SELL) trend_to_follow = -1;

    // FILTER: Signal phải match trend
    if(current_signal != trend_to_follow) return;

    // MỞ LỆNH
    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, ...);
        if(ticket > 0) g_ea.position_flags[tf][1] = 1;
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, ...);
        if(ticket > 0) g_ea.position_flags[tf][1] = 1;
    }
}
```

### 3.7 ProcessS3Strategy - News Trading

```cpp
void ProcessS3Strategy(int tf) {
    // ═══════════════════════════════════════
    // ĐỌC PHẦN 2: TÍN HIỆU NEWS (Column 8)
    // ═══════════════════════════════════════
    int tf_news = g_ea.csdl_rows[tf].news;  // Column 8
    int news_abs = MathAbs(tf_news);
    int current_signal = g_ea.csdl_rows[tf].signal;

    // FILTER: NEWS >= MinNewsLevelS3
    if(news_abs < MinNewsLevelS3) return;

    // FILTER: NEWS direction phải match signal
    int news_direction = (tf_news > 0) ? 1 : -1;
    if(current_signal != news_direction) return;

    // MỞ LỆNH
    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, ...);
        if(ticket > 0) g_ea.position_flags[tf][2] = 1;
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, ...);
        if(ticket > 0) g_ea.position_flags[tf][2] = 1;
    }
}
```

### 3.8 Bonus NEWS - Quét 7 TF

```cpp
void ProcessBonusNews() {
    // SCAN 7 TF để tìm NEWS cao
    for(int tf = 0; tf < 7; tf++) {
        if(!IsTFEnabled(tf)) continue;

        int news_abs = MathAbs(g_ea.csdl_rows[tf].news);

        // Nếu NEWS >= MinNewsLevelBonus
        if(news_abs >= MinNewsLevelBonus) {
            int signal = g_ea.csdl_rows[tf].signal;

            // Mở BonusOrderCount lệnh
            for(int i = 0; i < BonusOrderCount; i++) {
                double bonus_lot = g_ea.lot_sizes[tf][2] * BonusLotMultiplier;
                if(signal == 1) {
                    OrderSendSafe(tf, Symbol(), OP_BUY, bonus_lot, ...);
                } else if(signal == -1) {
                    OrderSendSafe(tf, Symbol(), OP_SELL, bonus_lot, ...);
                }
            }
        }
    }
}
```

---

## 4. CẤU TRÚC DỮ LIỆU CSDL

### 4.1 CSDL1 File - SYMBOL.json (10 cột + History)

**Path:** `MQL4/Files/DataAutoOner/LTCUSD.json`

**Cấu trúc:**
```json
{
  "symbol": "LTCUSD",
  "type": "main",
  "timestamp": 1760340800,
  "rows": 7,
  "columns": 10,
  "data": [
    {
      "tf_idx": 0,
      "timeframe_name": "M1",
      "timeframe_value": 1,
      "signal": -1,              ← Column 2: TÍN HIỆU GỐC
      "price": 97.85,            ← Column 3
      "cross": 1760340720,       ← Column 4
      "timestamp": 1760340720,   ← Column 5
      "pricediff_usd": 0.52,     ← Column 6
      "timediff_min": 2,         ← Column 7
      "news": -12,               ← Column 8: TÍN HIỆU NEWS
      "max_loss": -889.41        ← Column 9
    },
    // ... 6 TF khác (M5, M15, M30, H1, H4, D1)
  ],
  "history": {
    "m1": [
      {
        "timeframe_name": "M1",
        "signal_3col": -1,
        "price_4col": 97.85,
        "cross_5col": 1760340720,
        "timestamp_6col": 1760340720,
        "pricediff_7col": 0.52,
        "timediff_8col": 2,
        "news_result_9col": -12
      }
      // ... 6 entries khác
    ],
    "m5": [...],
    // ... (M15, M30, H1, H4, D1)
  }
}
```

**Giải thích 10 cột:**

| Cột | Tên | Kiểu | Mô tả | Phần xử lý |
|-----|-----|------|-------|------------|
| 0 | Placeholder | int | Luôn = 0 | - |
| 1 | TF Period | int | 1, 5, 15, 30, 60, 240, 1440 | - |
| **2** | **Signal** | int | **-1=SELL, 0=NONE, 1=BUY** | **PHẦN 1: TÍN HIỆU GỐC** |
| 3 | Price | double | Giá vào lệnh | PHẦN 1 |
| 4 | Cross | long | Timestamp TF trước | PHẦN 1 |
| 5 | Timestamp | long | Thời gian tín hiệu | PHẦN 1 |
| 6 | PriceDiff USD | double | Chênh lệch giá USD | PHẦN 1 |
| 7 | TimeDiff min | int | Chênh lệch thời gian phút | PHẦN 1 |
| **8** | **NEWS** | int | **±11~±16 (L1-L7) hoặc 0** | **PHẦN 2: TÍN HIỆU NEWS** |
| 9 | MaxLoss | double | Lỗ tối đa (âm) | - |

### 4.2 CSDL2 Files - SYMBOL_LIVE.json (6 cột, 3 files)

**EA đọc file này (đơn giản hơn CSDL1):**

**Path:**
- `DataAutoOner/LTCUSD_LIVE.json` (File A - Direct write)
- `DataAutoOner/LTCUSD_LIVE_B.json` (File B - Atomic backup)
- `DataAutoOner/LTCUSD_LIVE_C.json` (File C - Atomic backup)

**Cấu trúc:**
```json
[
  {
    "tf_idx": 0,
    "max_loss": -889.41,
    "timestamp": 1760340720,
    "signal": -1,           ← S1+S2 đọc (PHẦN 1)
    "pricediff": 0.52,
    "timediff": 2,
    "news": -12             ← S3 đọc (PHẦN 2)
  },
  // ... 6 TF khác
]
```

### 4.3 NEWS CASCADE Levels

**Category 1 (EA Trading) - LiveDiff threshold:**

| Level | NEWS Value | LiveDiff USD | Mô tả |
|-------|------------|--------------|-------|
| L1 | ±11 | 2.5 | Base level |
| L2 | ±12 | 3.0 | +0.5 USD |
| L3 | ±13 | 3.5 | +0.5 USD |
| L4 | ±14 | 4.0 | +0.5 USD |
| L5 | ±15 | 4.5 | +0.5 USD |
| L6 | ±16 | 5.0 | +0.5 USD |
| L7 | ±17 | 5.5 | +0.5 USD |

**Category 2 (User Reference) - Time-based:**

| Level | TimeDiff | Formula |
|-------|----------|---------|
| L1 | 2 min | 2 × 2^0 |
| L2 | 4 min | 2 × 2^1 |
| L3 | 8 min | 2 × 2^2 |
| L4 | 16 min | 2 × 2^3 |
| L5 | 32 min | 2 × 2^4 |
| L6 | 64 min | 2 × 2^5 |
| L7 | 128 min | 2 × 2^6 |

**Ví dụ:**
- Signal = BUY (+1), PriceDiff = 3.2 USD, TimeDiff = 5 min
- Category 1: 3.2 > 3.0 (L2) → Result = +12
- Category 2: 5 min > 4 min (L2) → Confirm L2
- **NEWS Result = +12** (BUY L2)

---

## 5. RESET & HEALTHCHECK

### 5.1 MidnightReset - Reset lúc 0h:0m mỗi ngày

**File:** `Super_Spy7TF_V2.mq4` (BOT SPY)

**Mục đích:** Reset 7 charts để tránh lỗi tích lũy

**Thời gian:** 0h:0m:0s (CHÍNH XÁC mỗi ngày)

**Code:**
```cpp
void MidnightReset() {
    if(!EnableMidnightReset) return;

    // SỬ DỤNG GlobalVariable thay vì static variable
    // (Tránh bị reset khi SmartTFReset() trigger OnInit())
    string gv_last_reset_time = g_target_symbol + "_LastMidnightResetTime";

    if(!GlobalVariableCheck(gv_last_reset_time)) {
        GlobalVariableSet(gv_last_reset_time, 0);
    }

    datetime last_reset = (datetime)GlobalVariableGet(gv_last_reset_time);
    datetime current_time = TimeCurrent();
    int current_hour = TimeHour(current_time);
    int current_minute = TimeMinute(current_time);

    // 4 ĐIỀU KIỆN để reset 1 lần duy nhất:
    // 1. Ngày mới (TimeDay khác)
    // 2. Đúng 0h:0m
    // 3. Ít nhất 1h từ lần reset trước (3600s)
    // 4. EnableMidnightReset = true
    if(TimeDay(last_reset) != TimeDay(current_time) &&
       current_hour == 0 &&
       current_minute == 0 &&
       (current_time - last_reset) >= 3600) {

        Print("✅ MidnightReset: ", g_target_symbol, " | New day at 0h:0m");
        SmartTFReset();  // Reset all 7 charts
        GlobalVariableSet(gv_last_reset_time, current_time);
    }
}
```

**SmartTFReset Mechanism:**
1. Tìm tất cả charts của cùng symbol (7 charts)
2. Chuyển chart → W1 → Chờ 2s → Chuyển về TF gốc
3. Reset 6 charts khác trước → Chart hiện tại cuối cùng
4. **KHÔNG XÓA DỮ LIỆU** - Chỉ refresh charts để clear memory

**Lý do dùng GlobalVariable thay vì static:**
- `static int last_day` bị reset về 99 khi `SmartTFReset()` trigger `OnInit()`
- `ChartSetSymbolPeriod()` → OnInit() → static reset → Infinite loop
- GlobalVariable persistent trong session MT4 → Không bị reset

### 5.2 HealthCheck - Kiểm tra 4 lần/ngày

**Mục đích:** Phát hiện WallStreet EA bị treo → Auto reset

**Thời gian:** 5h:0m, 10h:0m, 15h:0m, 20h:0m (4 lần/ngày)

**Code:**
```cpp
void HealthCheck() {
    if(!EnableHealthCheck) return;

    // Kiểm tra file CSDL1 modification time
    string csdl1_file = DataFolder + g_target_symbol + ".json";
    int handle = FileOpen(csdl1_file, FILE_READ|FILE_TXT);
    if(handle == INVALID_HANDLE) return;

    datetime current_modified = (datetime)FileGetInteger(handle, FILE_MODIFY_DATE);
    FileClose(handle);

    // Lần đầu: Lưu timestamp
    if(g_last_csdl1_modified == 0) {
        g_last_csdl1_modified = current_modified;
        Print("ℹ️ HealthCheck: First run - Baseline: ", TimeToString(current_modified));
        return;
    }

    // Nếu file KHÔNG thay đổi từ lần check trước (5h)
    if(current_modified == g_last_csdl1_modified) {
        Print("⚠️ HealthCheck: BOT STUCK! File unchanged since ", TimeToString(current_modified));
        Print("⚠️ HealthCheck: Auto reset triggered!");
        Alert("Bot SPY stuck - Auto reset!");
        SmartTFReset();
        g_last_csdl1_modified = TimeCurrent();
    } else {
        g_last_csdl1_modified = current_modified;
        Print("✅ HealthCheck: OK - File updated at ", TimeToString(current_modified));
    }
}
```

**Trigger Logic:**
- File không update trong 5 giờ → WallStreet EA bị lỗi
- Auto reset → EA khởi động lại → Gửi signal tiếp

### 5.3 RunMidnightAndHealthCheck - Điều phối

```cpp
void RunMidnightAndHealthCheck() {
    datetime current_time = TimeCurrent();
    int current_hour = TimeHour(current_time);
    int current_minute = TimeMinute(current_time);
    static int last_check_hour = -2;  // Init -2 (not 0)

    // Midnight Reset: 0h:0m
    if(EnableMidnightReset &&
       current_hour == 0 &&
       current_minute == 0 &&
       current_hour != last_check_hour) {
        MidnightReset();
        last_check_hour = current_hour;
    }

    // Health Check: 5h, 10h, 15h, 20h (ĐÚNG GIỜ - 0 minutes)
    if(EnableHealthCheck &&
       current_minute == 0 &&
       (current_hour == 5 || current_hour == 10 ||
        current_hour == 15 || current_hour == 20) &&
       current_hour != last_check_hour) {
        HealthCheck();
        last_check_hour = current_hour;
    }
}
```

**Lưu ý:**
- `static int last_check_hour` dùng để tránh chạy nhiều lần trong cùng 1 phút
- `current_minute == 0` đảm bảo chỉ chạy ở phút thứ 0 (0h:0m, 5h:0m...)
- `last_check_hour != current_hour` tránh duplicate trong cùng giờ

### 5.4 Removed Feature - StartupReset

**Lý do bỏ:**
- StartupReset chạy 60s sau khi MT4 khởi động
- **CASE 1:** VPS restart lúc 0h → MidnightReset + StartupReset → DUPLICATE
- **CASE 2:** VPS restart lúc 10h → HealthCheck sẽ phát hiện stuck
- **Kết luận:** StartupReset THỪA → Đã XÓA hoàn toàn

**History (Tham khảo):**
```cpp
// REMOVED CODE - Do NOT use
void RunStartupReset() {
    static datetime init_time = TimeCurrent();
    datetime elapsed = TimeCurrent() - init_time;

    if(elapsed >= 60 && elapsed < 62) {
        SmartTFReset();
    }
}
```

---

## 6. TIMELINE HOẠT ĐỘNG

### 6.1 Timeline trong 1 ngày

```
00:00:00 → ✅ MidnightReset (reset 7 charts)
00:00:10 → OnTimer tiếp tục hoạt động bình thường

05:00:00 → ✅ HealthCheck (kiểm tra file CSDL1)
10:00:00 → ✅ HealthCheck
15:00:00 → ✅ HealthCheck
20:00:00 → ✅ HealthCheck

Mỗi giây → ProcessAllSignals() (nếu có tín hiệu mới)
```

### 6.2 Khi có tín hiệu mới (VD: M5 SELL)

```
Timeline - PHẦN 1 & 2 xử lý đồng thời:

T+0ms:    WallStreet EA (M5) phát hiện pattern SELL
T+10ms:   WallStreet EA ghi GlobalVariable:
          - LTCUSD_M5_SignalType1 = -1
          - LTCUSD_M5_LastSignalTime = 1760340800

T+1000ms: BOT SPY OnTimer() → ProcessAllSignals()
T+1010ms: Đọc GlobalVariable → Phát hiện tín hiệu mới

T+1020ms: ┌─────────────────────────────────────────┐
          │ PHẦN 1: Xử lý TÍN HIỆU GỐC             │
          ├─────────────────────────────────────────┤
          │ • Signal = -1 (SELL)                    │
          │ • Price = 97.85                         │
          │ • PriceDiff = 0.52 USD                  │
          │ • TimeDiff = 2 min                      │
          └─────────────────────────────────────────┘

T+1030ms: ┌─────────────────────────────────────────┐
          │ PHẦN 2: Xử lý TÍN HIỆU NEWS            │
          ├─────────────────────────────────────────┤
          │ • Input: signal=-1, pricediff=0.52,     │
          │          timediff=2                     │
          │ • Category 1: 0.52 < 2.5 → KHÔNG đủ L1  │
          │ • Category 2: 2min = L1 → ĐỦ L1         │
          │ • Result: NEWS = 0 (không đủ 2 cats)    │
          └─────────────────────────────────────────┘

T+1040ms: Ghi LTCUSD.json (10 cột)
T+1050ms: Ghi LTCUSD_LIVE.json (6 cột)

T+1100ms: BOT EA AUTO (M5) đọc file
T+1110ms: Phát hiện signal đảo chiều → Đóng lệnh cũ

T+1120ms: ┌─────────────────────────────────────────┐
          │ BOT EA - PHẦN 1: Mở lệnh theo GỐC      │
          ├─────────────────────────────────────────┤
          │ • S1 (HOME): signal=-1 → SELL order     │
          │ • S2 (TREND): D1=BUY → SKIP (không khớp)│
          └─────────────────────────────────────────┘

T+1130ms: ┌─────────────────────────────────────────┐
          │ BOT EA - PHẦN 2: Mở lệnh theo NEWS     │
          ├─────────────────────────────────────────┤
          │ • S3 (NEWS): news=0 → SKIP              │
          └─────────────────────────────────────────┘

T+1200ms: Lệnh SELL gửi đến Broker
```

### 6.3 Khi NEWS CASCADE xảy ra (VD: M1 BUY L2)

```
Timeline - NEWS CASCADE L2:

T+0ms:    WallStreet EA (M1) phát hiện BUY signal mạnh
T+10ms:   GlobalVariable: LTCUSD_M1_SignalType1 = +1

T+1000ms: BOT SPY xử lý

T+1020ms: ┌─────────────────────────────────────────┐
          │ PHẦN 1: Xử lý TÍN HIỆU GỐC             │
          ├─────────────────────────────────────────┤
          │ • Signal = +1 (BUY)                     │
          │ • PriceDiff = 3.2 USD ← CAO             │
          │ • TimeDiff = 5 min                      │
          └─────────────────────────────────────────┘

T+1030ms: ┌─────────────────────────────────────────┐
          │ PHẦN 2: Xử lý TÍN HIỆU NEWS            │
          ├─────────────────────────────────────────┤
          │ • Category 1: 3.2 USD > 3.0 → L2 ✓      │
          │ • Category 2: 5 min > 4 min → L2 ✓      │
          │ • Result: NEWS = +12 (BUY L2) 🔥        │
          └─────────────────────────────────────────┘

T+1040ms: Ghi file → Column 8: news = +12

T+1100ms: BOT EA AUTO đọc file

T+1120ms: ┌─────────────────────────────────────────┐
          │ BOT EA - PHẦN 1: Mở lệnh theo GỐC      │
          ├─────────────────────────────────────────┤
          │ • S1 (HOME): signal=+1 → BUY order      │
          │ • S2 (TREND): D1=BUY → BUY order        │
          └─────────────────────────────────────────┘

T+1130ms: ┌─────────────────────────────────────────┐
          │ BOT EA - PHẦN 2: Mở lệnh theo NEWS     │
          ├─────────────────────────────────────────┤
          │ • S3 (NEWS): news=+12 → BUY order 🚀    │
          │ • Bonus: EnableBonusNews=true           │
          │   → Mở thêm 2 BUY orders (BonusCount=2) │
          └─────────────────────────────────────────┘

T+1200ms: Tổng 5 lệnh BUY gửi Broker:
          - 1 × S1 (HOME)
          - 1 × S2 (TREND)
          - 1 × S3 (NEWS)
          - 2 × Bonus (NEWS L2)
```

### 6.4 Khi bot bị treo (Detected by HealthCheck)

```
10:00:00 → HealthCheck() chạy
10:00:01 → Đọc file: LTCUSD.json
10:00:02 → Last modified: 05:00:00 (5 giờ trước)
10:00:03 → ⚠️ STUCK detected! File không update 5h
10:00:04 → Alert("Bot SPY stuck - Auto reset!")
10:00:05 → SmartTFReset() → Reset 7 charts
10:00:07 → W1 → Wait 2s → Back to M1
10:00:09 → W1 → Wait 2s → Back to M5
10:00:11 → ... (M15, M30, H1, H4, D1)
10:00:20 → All charts reset complete
10:00:21 → WallStreet EA khởi động lại
10:00:22 → GlobalVariable gửi lại signal
10:00:23 → BOT SPY bắt đầu nhận signal lại ✅
```

---

## 🎯 TÓM TẮT CHO NEWCHAT MỚI

```
HỆ THỐNG 2-BOT:
├─ WallStreet EA (7 EA) → Tín hiệu gốc → GlobalVariable
└─ BOT SPY V2 (1 Indicator) → Đọc GV → Phân tích 2 phần → JSON
    ├─ PHẦN 1: Tín hiệu gốc (Column 2: signal)
    └─ PHẦN 2: Tín hiệu NEWS (Column 8: news)
└─ BOT EA AUTO (7 EA) → Đọc JSON → Giao dịch 2 phần
    ├─ PHẦN 1: S1+S2 theo signal (Column 2)
    └─ PHẦN 2: S3 theo news (Column 8)

LUỒNG DỮ LIỆU:
WallStreet EA → GlobalVariable → BOT SPY (2 phần) → JSON (10 cột)
→ BOT EA AUTO (2 phần) → Broker

CSDL FILES:
├─ CSDL1: SYMBOL.json (10 cột + history)
│   ├─ Column 2: signal (-1/0/1) ← S1+S2 đọc
│   └─ Column 8: news (±11~±16) ← S3 đọc
└─ CSDL2: SYMBOL_LIVE.json (6 cột, 3 files)

CHỨC NĂNG PHỤ:
✅ MidnightReset: 0h:0m mỗi ngày (GlobalVariable-based, NO LOOP)
✅ HealthCheck: 5h,10h,15h,20h (phát hiện stuck, auto reset)
❌ StartupReset: ĐÃ XÓA (redundant)

FILES:
├─ MQL4/Indicators/Super_Spy7TF_V2.mq4 (BOT SPY)
├─ MQL4/Experts/Eas_Smf_Oner_V2.mq4 (BOT EA AUTO)
└─ MQL4/Files/DataAutoOner/*.json (CSDL)

ĐIỂM MẠNH:
🚀 2 phần xử lý rõ ràng: Tín hiệu gốc + NEWS CASCADE
🚀 3 strategies linh hoạt: S1 (Binary), S2 (Trend), S3 (News)
🚀 Auto recovery: MidnightReset + HealthCheck
🚀 NO infinite loop: GlobalVariable thay static
🚀 Multi-symbol support: Mỗi symbol có struct riêng
```

---

## 📌 LƯU Ý QUAN TRỌNG

### Files quan trọng

1. **BOT SPY:** `MQL4/Indicators/Super_Spy7TF_V2.mq4`
2. **BOT EA AUTO:** `MQL4/Experts/Eas_Smf_Oner_V2.mq4`
3. **CSDL Folder:** `MQL4/Files/DataAutoOner/`

### Input Parameters

**BOT SPY:**
```cpp
input int Timer = 1;                        // 1 giây
input bool EnableHealthCheck = true;        // 5h,10h,15h,20h
input bool EnableMidnightReset = true;      // 0h:0m daily
input bool ProcessSignalOnOddSecond = false; // Giây lẻ (tránh conflict)
```

**BOT EA AUTO:**
```cpp
input bool S1_HOME = true;                  // Strategy 1
input bool S2_TREND = true;                 // Strategy 2
input bool S3_NEWS = true;                  // Strategy 3
input CSDL_SOURCE_ENUM CSDL_Source = FOLDER_2; // DataAutoOner2
input STOPLOSS_MODE StoplossMode = LAYER1_MAXLOSS;
```

### Debug & Monitoring

**Check GlobalVariables:**
- F3 → Terminal → Global Variables
- Tìm: `LTCUSD_M1_SignalType1`

**Check CSDL Files:**
- `MQL4/Files/DataAutoOner/LTCUSD.json`
- Xem Column 2 (signal) và Column 8 (news)

**Check Logs:**
- Experts tab → Filter: "SPY" hoặc "EA"
- Tìm: `[SPY] M1 BUY` hoặc `[OPEN] S1_HOME`

---

**📅 Last Updated:** 2025-11-03
**🔄 Latest Changes:**
- Viết lại phần 1.2 LUỒNG HOẠT ĐỘNG CHÍNH
- Làm rõ 2 phần của BOT SPY (Tín hiệu gốc + NEWS)
- Làm rõ 2 phần của BOT EA AUTO (S1+S2 vs S3)
- Tập hợp TẤT CẢ thông tin từ session cũ
- Removed StartupReset (không cần thiết)
- Optimized HealthCheck: 5h,10h,15h,20h

**✅ Status:** Production Ready - Tested with LTCUSD, BTCUSD
