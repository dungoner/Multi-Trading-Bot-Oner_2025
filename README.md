# 🤖 Multi-Trading Bot System - Hướng Dẫn Cho Người Mới

> **Dành cho:** Lập trình viên mới tham gia dự án hoặc newchat session
> **Mục đích:** Hiểu hệ thống từ TỔNG QUAN → CHI TIẾT, từ CHỨC NĂNG → CODE

---

## 📋 MỤC LỤC

1. [HỆ THỐNG LÀ GÌ?](#1-hệ-thống-là-gì) ⭐ **ĐỌC ĐẦU TIÊN**
2. [MỐC NỐI - ĐIỂM QUAN TRỌNG NHẤT](#2-mốc-nối---điểm-quan-trọng-nhất) ⭐⭐⭐
3. [CHỨC NĂNG CHÍNH (4 chức năng)](#3-chức-năng-chính-4-chức-năng)
4. [CHỨC NĂNG PHỤ (3 chức năng)](#4-chức-năng-phụ-3-chức-năng)
5. [CHI TIẾT BOT SPY](#5-chi-tiết-bot-spy)
6. [CHI TIẾT BOT EA AUTO](#6-chi-tiết-bot-ea-auto)
7. [CẤU TRÚC CSDL](#7-cấu-trúc-csdl)
8. [LUỒNG DỮ LIỆU HOÀN CHỈNH](#8-luồng-dữ-liệu-hoàn-chỉnh)

---

## 1. HỆ THỐNG LÀ GÌ?

### 📖 Giải thích đơn giản

Hệ thống này là **2 con bot** làm việc **kết hợp** để giao dịch forex/crypto tự động:

1. **Bot SPY** (Super_Spy7TF_V2.mq4) - **GIÁM SÁT**
   - Đọc tín hiệu từ WallStreet EA
   - Phân tích NEWS CASCADE
   - **GHI** dữ liệu vào file JSON

2. **Bot EA AUTO** (Eas_Smf_Oner_V2.mq4) - **GIAO DỊCH**
   - **ĐỌC** dữ liệu từ file JSON
   - Mở/đóng lệnh tự động
   - Quản lý stoploss/takeprofit

### 🎯 Câu hỏi quan trọng: 2 bot giao tiếp như thế nào?

**TRẢ LỜI:** Qua file JSON với **2 MỐC NỐI** (xem phần 2)

---

## 2. MỐC NỐI - ĐIỂM QUAN TRỌNG NHẤT

> ⚠️ **QUAN TRỌNG:** Đây là phần BẮT BUỘC phải hiểu để làm việc với hệ thống!

### 🔗 CÓ 2 MỐC NỐI

Hệ thống có **2 luồng dữ liệu độc lập** giữa 2 bot:

```
┌──────────────┐                    ┌──────────────┐
│   SPY BOT    │                    │   EA AUTO    │
└──────┬───────┘                    └───────┬──────┘
       │                                    │
       ├─→ MỐC NỐI 1: Column 2 ────────────┼─→ S1 + S2 đọc
       │   (signal: -1/0/1)                 │
       │                                    │
       └─→ MỐC NỐI 2: Column 8 ────────────┴─→ S3 đọc
           (news: ±11~±16)
```

### 📊 MỐC NỐI 1: Column 2 - Tín hiệu gốc

**TÊN:** `signal`
**GIÁ TRỊ:** `-1` (SELL) / `0` (NONE) / `1` (BUY)
**NGUỒN GỐC:** WallStreet EA
**XỬ LÝ:** SPY Bot (đọc GlobalVariable → ghi file)
**NGƯỜI DÙNG:** EA Auto strategies S1 + S2

**LUỒNG:**
```
WallStreet EA → GlobalVariable → SPY Bot → Column 2 → EA Auto (S1+S2)
```

**CODE REFERENCE:**
- SPY ghi: `Super_Spy7TF_V2.mq4:704` (trong `ProcessSignalForTF`)
- EA đọc: `Eas_Smf_Oner_V2.mq4:462` (trong `ParseLoveRow`)

---

### 📊 MỐC NỐI 2: Column 8 - NEWS CASCADE

**TÊN:** `news`
**GIÁ TRỊ:** `0` / `±11~±16` (Category 1) / `±1~±7` (Category 2)
**NGUỒN GỐC:** SPY Bot phân tích
**XỬ LÝ:** SPY Bot (DetectCASCADE_New function)
**NGƯỜI DÙNG:** EA Auto strategy S3

**LUỒNG:**
```
SPY Bot → DetectCASCADE_New() → Column 8 → EA Auto (S3)
```

**GIẢI THÍCH CHI TIẾT:**

NEWS CASCADE có **7 cấp độ** (L1-L7) và **2 category**:

#### Category 1: Cho EA Trading (Scores 10-70)
- **L1:** LiveDiff > 2.5 USD → Score = ±10
- **L2:** LiveDiff > 3.0 USD + M5→M1 cascade → Score = ±20
- **L3:** LiveDiff > 3.5 USD + M15→M5→M1 cascade → Score = ±30
- **L4-L7:** Tương tự với ngưỡng tăng dần...

#### Category 2: Cho User Reference (Scores 1-7)
- **L1:** LiveDiff > 0.1 USD + Time < 2 min → Score = ±1
- **L2:** LiveDiff > 0.2 USD + Time < 4 min → Score = ±2
- **L3-L7:** Tương tự với ngưỡng tăng dần...

**CODE REFERENCE:**
- SPY tính: `Super_Spy7TF_V2.mq4:1682` (function `DetectCASCADE_New`)
- EA đọc: `Eas_Smf_Oner_V2.mq4:1128` (function `ProcessS3Strategy`)

---

### 🎓 TẠI SAO CẦN 2 MỐC NỐI?

**Câu hỏi:** Tại sao không chỉ dùng 1 signal?

**Trả lời:**
1. **Column 2 (signal)** = Tín hiệu GỐC từ WallStreet EA
   - Phản ánh phân tích kỹ thuật cơ bản
   - S1 + S2 dùng để giao dịch nhanh

2. **Column 8 (news)** = Tín hiệu NÂNG CAO từ SPY Bot
   - Phản ánh độ mạnh đột phá (breakout strength)
   - S3 dùng để bắt tin tức lớn (high-impact events)

**VÍ DỤ THỰC TẾ:**
```
TF=M1:
- Column 2 (signal) = 1 (BUY)    ← WallStreet EA phát hiện xu hướng tăng
- Column 8 (news) = +30 (L3)     ← SPY Bot phát hiện đột phá mạnh

→ S1: MỞ lệnh BUY (theo signal)
→ S2: MỞ lệnh BUY (nếu D1 trend = BUY)
→ S3: MỞ lệnh BUY + BONUS (vì news=+30 rất mạnh)
```

---

## 3. CHỨC NĂNG CHÍNH (4 chức năng)

Hệ thống có **4 chức năng chính** tương ứng với **2 phần của mỗi bot**:

```
┌────────────────────────────────────────────────────────┐
│                      SPY BOT                           │
├────────────────────────────────────────────────────────┤
│  PHẦN 1: Xử lý TÍN HIỆU GỐC                           │
│  └─ ProcessSignalForTF() → Ghi Column 2               │
│                                                        │
│  PHẦN 2: Xử lý NEWS CASCADE                           │
│  └─ DetectCASCADE_New() → Ghi Column 8                │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                    EA AUTO BOT                         │
├────────────────────────────────────────────────────────┤
│  PHẦN 1: Giao dịch theo SIGNAL (S1 + S2)             │
│  ├─ S1: ProcessS1Strategy() → Đọc Column 2           │
│  └─ S2: ProcessS2Strategy() → Đọc Column 2 (D1)      │
│                                                        │
│  PHẦN 2: Giao dịch theo NEWS (S3)                    │
│  └─ S3: ProcessS3Strategy() → Đọc Column 8           │
└────────────────────────────────────────────────────────┘
```

### 🔄 Mối quan hệ giữa 4 chức năng

```
SPY PHẦN 1 ──────┐
                 ├─→ EA PHẦN 1 (S1+S2)
SPY PHẦN 2 ──────┘

SPY PHẦN 2 ──────→ EA PHẦN 2 (S3)
```

**CHÚ THÍCH:**
- SPY PHẦN 1 phục vụ EA PHẦN 1
- SPY PHẦN 2 phục vụ EA PHẦN 2
- Hai luồng này **ĐỘC LẬP** nhau!

---

## 4. CHỨC NĂNG PHỤ (3 chức năng)

Ngoài 4 chức năng chính, hệ thống có 3 chức năng phụ:

### 4.1 MidnightReset (SPY Bot)
- **Thời gian:** 0h:00 hàng ngày
- **Mục đích:** Reset lại các biến, làm mới GlobalVariables
- **Code:** `Super_Spy7TF_V2.mq4:2887`

### 4.2 HealthCheck (Cả 2 bot)
- **Thời gian:**
  - SPY: 5h, 10h, 15h, 20h
  - EA: 8h, 16h
- **Mục đích:** Kiểm tra bot có đang hoạt động, nếu treo → tự reset
- **Code:**
  - SPY: `Super_Spy7TF_V2.mq4:2856`
  - EA: `Eas_Smf_Oner_V2.mq4:1459`

### 4.3 Dashboard (Cả 2 bot)
- **Thời gian:** Cập nhật liên tục (mỗi giây)
- **Mục đích:** Hiển thị trạng thái bot trên chart
- **Code:**
  - SPY: `Super_Spy7TF_V2.mq4:748`
  - EA: `Eas_Smf_Oner_V2.mq4:1812`

---

## 5. CHI TIẾT BOT SPY

### 5.1 Tổng quan

**File:** `MQL4/Indicators/Super_Spy7TF_V2.mq4` (2946 dòng)
**Loại:** Indicator (hiển thị trên chart)
**Chạy trên:** 7 charts (M1, M5, M15, M30, H1, H4, D1) - CÙNG 1 symbol

### 5.2 Nhiệm vụ chính

#### A. ĐỌC tín hiệu từ WallStreet EA (PHẦN 1)

**NGUỒN:** GlobalVariable
**TÊN BIẾN:** `{SYMBOL}_{TF}_SignalType1`
**VÍ DỤ:** `LTCUSD_M1_SignalType1`, `LTCUSD_M5_SignalType1`...

**XỬ LÝ:**
1. Đọc signal mới từ GlobalVariable
2. Tính PriceDiff (USD) = chênh lệch giá so với signal trước
3. Tính TimeDiff (minutes) = thời gian kể từ signal trước
4. Ghi vào Column 2, 7, 8 của CSDL

**CODE:**
```mql4
// Super_Spy7TF_V2.mq4:2714-2734
void ProcessAllSignals() {
    for(int i = 0; i < 7; i++) {
        string signal_var = g_target_symbol + "_" + tf_names[i] + "_SignalType1";
        string time_var = g_target_symbol + "_" + tf_names[i] + "_LastSignalTime";

        int current_signal = (int)GlobalVariableGet(signal_var);
        long current_signal_time = (long)GlobalVariableGet(time_var);

        if(current_signal != 0 &&
           current_signal_time > g_symbol_data.processed_timestamps[i]) {
            ProcessSignalForTF(i, current_signal, current_signal_time);
        }
    }
}
```

#### B. PHÂN TÍCH NEWS CASCADE (PHẦN 2)

**NGUỒN:** Dữ liệu từ CSDL (7 TF)
**XỬ LÝ:** Hàm `DetectCASCADE_New()`

**LOGIC:**
1. Kiểm tra 7 level (L1-L7) **ĐỘC LẬP**
2. Mỗi level có 2 category (EA Trading vs User Reference)
3. Ghi kết quả vào Column 8

**VÍ DỤ L2 (Category 1):**
```mql4
// Super_Spy7TF_V2.mq4:1736-1750
// L2: M5→M1 aligned + live_diff > 3.0 USD → Score 20
if(m5_signal != 0 && m1_signal != 0 && m1_signal == m5_signal) {
    if(m5_cross == m1_time) {  // M5.cross = M1.timestamp
        double l2_threshold = NewsBaseLiveDiff + (NewsLiveDiffStep * 1);  // 3.0 USD
        if(live_usd_diff > l2_threshold && IsWithinOneCandle(1, m5_time)) {
            g_symbol_data.news_results[1] = m5_signal * 20;  // Score
        } else {
            g_symbol_data.news_results[1] = 0;
        }
    } else {
        g_symbol_data.news_results[1] = 0;
    }
} else {
    g_symbol_data.news_results[1] = 0;
}
```

#### C. GHI FILE

**3 file được ghi:**
1. **File A:** `DataAutoOner/{SYMBOL}.json` (CSDL1 - 10 columns + history)
2. **File B:** `DataAutoOner2/{SYMBOL}_LIVE.json` (CSDL2 - 6 columns, no history)
3. **File C:** `DataAutoOner3/{SYMBOL}_LIVE.json` (CSDL2 - for Python)

**GHI KHI NÀO:**
- Khi có signal mới: Ghi cả CSDL1 + CSDL2
- Mỗi 2 giây: Cập nhật NEWS → Ghi cả CSDL1 + CSDL2

**CODE:**
```mql4
// Super_Spy7TF_V2.mq4:730-731
WriteCSDL1ArrayToFile();   // CSDL1: SYMBOL.json (10 columns + history)
WriteCSDL2ArrayToFile();   // CSDL2: SYMBOL_LIVE.json (6 columns, no history, 3 folders)
```

### 5.3 Cấu trúc dữ liệu chính

```mql4
// Super_Spy7TF_V2.mq4:69-120
struct SymbolCSDL1Data {
    string symbol;                    // Symbol name

    // CSDL1 CURRENT DATA - 7 TF × 10 COLUMNS
    int signals[7];                   // Column 3: Signal (-1, 0, 1)
    double prices[7];                 // Column 4: Price
    long crosses[7];                  // Column 5: Cross (timestamp of prev TF)
    long timestamps[7];               // Column 6: Timestamp
    double pricediffs[7];             // Column 7: PriceDiff USD
    int timediffs[7];                 // Column 8: TimeDiff minutes
    int news_results[7];              // Column 9: NEWS CASCADE (±11-16 or 0)
    double max_losses[7];             // Column 10: Max Loss

    // HISTORY ARRAYS - 7 TF × 7 ENTRIES
    SignalHistoryEntry m1_history[HISTORY_SIZE];
    SignalHistoryEntry m5_history[HISTORY_SIZE];
    // ... (các TF khác)
};
```

---

## 6. CHI TIẾT BOT EA AUTO

### 6.1 Tổng quan

**File:** `MQL4/Experts/Eas_Smf_Oner_V2.mq4` (2050 dòng)
**Loại:** Expert Advisor (EA - tự động giao dịch)
**Chạy trên:** 7 charts (M1, M5, M15, M30, H1, H4, D1) - CÙNG 1 symbol

### 6.2 3 Chiến lược giao dịch

#### A. S1 (HOME) - Giao dịch theo signal gốc

**ĐỌC:** Column 2 (signal)
**LOGIC:**
- Nếu signal = 1 → MỞ lệnh BUY
- Nếu signal = -1 → MỞ lệnh SELL
- Có 2 mode: BASIC (không check NEWS) vs NEWS Filter (phải có NEWS đủ mạnh)

**CODE:**
```mql4
// Eas_Smf_Oner_V2.mq4:1014-1018
void ProcessS1BasicStrategy(int tf) {
    int current_signal = g_ea.csdl_rows[tf].signal;
    if(current_signal == 1 || current_signal == -1) {
        OpenS1Order(tf, current_signal, "BASIC");
    }
}
```

#### B. S2 (TREND) - Theo xu hướng D1

**ĐỌC:** Column 2 (signal) của D1
**LOGIC:**
- Đọc D1 signal → Xác định trend
- Chỉ mở lệnh khi signal TF hiện tại KHỚP với trend D1

**VÍ DỤ:**
```
D1 signal = 1 (BUY trend)
→ M1 signal = 1 → MỞ lệnh BUY (khớp)
→ M1 signal = -1 → BỎ QUA (không khớp)
```

**CODE:**
```mql4
// Eas_Smf_Oner_V2.mq4:1062-1084
void ProcessS2Strategy(int tf) {
    int current_signal = g_ea.csdl_rows[tf].signal;
    int trend_to_follow = g_ea.trend_d1;  // D1 trend

    if(current_signal != trend_to_follow) {
        return;  // Skip nếu không khớp
    }

    // Mở lệnh...
}
```

#### C. S3 (NEWS) - Giao dịch theo NEWS CASCADE

**ĐỌC:** Column 8 (news)
**LOGIC:**
- Kiểm tra news >= MinNewsLevelS3 (default: 20)
- Kiểm tra hướng news KHỚP với signal
- Nếu đủ điều kiện → MỞ lệnh

**BONUS:**
- Nếu EnableBonusNews = true
- Và news >= MinNewsLevelBonus
- → Mở thêm N lệnh (BonusOrderCount)

**CODE:**
```mql4
// Eas_Smf_Oner_V2.mq4:1126-1146
void ProcessS3Strategy(int tf) {
    int tf_news = g_ea.csdl_rows[tf].news;
    int news_abs = MathAbs(tf_news);

    if(news_abs < MinNewsLevelS3) {
        return;  // NEWS quá yếu, bỏ qua
    }

    int news_direction = (tf_news > 0) ? 1 : -1;
    int current_signal = g_ea.csdl_rows[tf].signal;

    if(current_signal != news_direction) {
        return;  // Hướng không khớp, bỏ qua
    }

    // Mở lệnh...
}
```

### 6.3 Quản lý rủi ro

#### A. Stoploss (2 layers)

**Layer 1 (CSDL-based):**
- Dùng max_loss từ CSDL (Column 10)
- Threshold = max_loss × lot
- VÍ DỤ: max_loss = -1000, lot = 0.1 → SL = -100 USD

**Layer 2 (Margin-based - Emergency):**
- Dùng margin / divisor
- VÍ DỤ: margin = 500 USD, divisor = 5 → SL = -100 USD

**CODE:**
```mql4
// Eas_Smf_Oner_V2.mq4:1286-1298
if(StoplossMode == LAYER1_MAXLOSS) {
    sl_threshold = g_ea.layer1_thresholds[tf][s];
}
else if(StoplossMode == LAYER2_MARGIN) {
    double margin_usd = OrderLots() * MarketInfo(Symbol(), MODE_MARGINREQUIRED);
    sl_threshold = -(margin_usd / Layer2_Divisor);
}

if(profit <= sl_threshold) {
    CloseOrderSafely(ticket, "STOPLOSS");
    g_ea.position_flags[tf][s] = 0;
}
```

#### B. TakeProfit (optional)

- Nếu UseTakeProfit = true
- Threshold = max_loss × lot × multiplier
- VÍ DỤ: max_loss = -1000, lot = 0.1, multiplier = 3 → TP = +300 USD

---

## 7. CẤU TRÚC CSDL

### 7.1 CSDL1 (Main Database)

**File:** `DataAutoOner/{SYMBOL}.json`
**Cấu trúc:** 7 rows (TF) × 10 columns
**Có history:** Có (7 signal gần nhất mỗi TF)

**10 COLUMNS:**

| Column | Tên | Kiểu | Mô tả | Người dùng |
|--------|-----|------|-------|------------|
| 1 | timeframe_name | string | "M1", "M5"... | Display |
| 2 | timeframe | int | 1, 5, 15... | Parser |
| **3** | **signal** | **int** | **-1/0/1** | **S1+S2 (MỐC NỐI 1)** |
| 4 | price | double | Entry price | Calculate diff |
| 5 | cross | long | Prev TF timestamp | Cascade check |
| 6 | timestamp | long | Signal time | Sync check |
| 7 | pricediff | double | USD diff | Display |
| 8 | timediff | int | Minutes diff | Display |
| **9** | **news** | **int** | **±11~±16** | **S3 (MỐC NỐI 2)** |
| 10 | max_loss | double | Max loss/lot | Stoploss |

### 7.2 CSDL2 (Live Database)

**File:** `DataAutoOner2/{SYMBOL}_LIVE.json`
**Cấu trúc:** 7 rows (TF) × 6 columns
**Có history:** KHÔNG

**6 COLUMNS:**

| Column | Tên | Mô tả |
|--------|-----|-------|
| 1 | max_loss | Max loss/lot |
| 2 | timestamp | Signal time |
| **3** | **signal** | **-1/0/1 (MỐC NỐI 1)** |
| 4 | pricediff | USD diff |
| 5 | timediff | Minutes diff |
| **6** | **news** | **±11~±16 (MỐC NỐI 2)** |

### 7.3 Tại sao có 2 CSDL?

**CSDL1:**
- Đầy đủ, có history
- Dùng cho phân tích, dashboard
- Dung lượng lớn hơn

**CSDL2:**
- Nhỏ gọn, chỉ dữ liệu hiện tại
- Dùng cho EA giao dịch (đọc nhanh)
- Có 3 bản copy (DataAutoOner, DataAutoOner2, DataAutoOner3)

---

## 8. LUỒNG DỮ LIỆU HOÀN CHỈNH

### 8.1 Sơ đồ chi tiết theo thời gian

```
GIÂY 0 (SPY Bot - EVEN second):
┌──────────────────────────────────────────┐
│ 1. Đọc GlobalVariable                    │
│    └─ LTCUSD_M1_SignalType1 = 1         │
│                                          │
│ 2. ProcessSignalForTF(0, 1, timestamp)  │
│    ├─ Tính PriceDiff = +2.5 USD         │
│    ├─ Tính TimeDiff = 5 minutes         │
│    └─ g_symbol_data.signals[0] = 1      │
│                                          │
│ 3. DetectCASCADE_New()                  │
│    ├─ L1: LiveDiff = 3.0 > 2.5 ✓        │
│    └─ news_results[0] = +10              │
│                                          │
│ 4. WriteCSDL1ArrayToFile()              │
│    └─ Ghi vào DataAutoOner/LTCUSD.json  │
│                                          │
│ 5. WriteCSDL2ArrayToFile()              │
│    ├─ Ghi DataAutoOner/LTCUSD_LIVE.json │
│    ├─ Ghi DataAutoOner2/LTCUSD_LIVE.json│
│    └─ Ghi DataAutoOner3/LTCUSD_LIVE.json│
└──────────────────────────────────────────┘
           ▼
GIÂY 1 (EA Auto - ODD second):
┌──────────────────────────────────────────┐
│ 1. ReadCSDLFile()                        │
│    └─ Đọc DataAutoOner2/LTCUSD_LIVE.json│
│                                          │
│ 2. ParseCSDLLoveJSON()                   │
│    ├─ csdl_rows[0].signal = 1           │
│    └─ csdl_rows[0].news = +10           │
│                                          │
│ 3. HasValidS2BaseCondition(0)           │
│    ├─ signal_old = 0                    │
│    ├─ signal_new = 1                    │
│    └─ return true (có thay đổi!)        │
│                                          │
│ 4. ProcessS1Strategy(0)                 │
│    └─ OrderSend(BUY, 0.11 lot)          │
│       → Ticket #12345                    │
│                                          │
│ 5. ProcessS2Strategy(0)                 │
│    ├─ trend_d1 = 1 (BUY trend)          │
│    ├─ signal = 1 (khớp!)                │
│    └─ OrderSend(BUY, 0.12 lot)          │
│       → Ticket #12346                    │
│                                          │
│ 6. ProcessS3Strategy(0)                 │
│    ├─ news = +10 (< 20, quá yếu)        │
│    └─ BỎ QUA                             │
│                                          │
│ 7. UpdateDashboard()                     │
│    └─ Hiển thị: M1 [BUY] S1:✓ S2:✓ S3:○ │
└──────────────────────────────────────────┘
```

### 8.2 Timeline so sánh 2 bot

```
TIME │ SPY BOT (Indicator)          │ EA AUTO (Expert Advisor)
─────┼──────────────────────────────┼─────────────────────────────
0.0s │ Đọc GlobalVariable           │
0.5s │ Phân tích NEWS CASCADE       │
0.8s │ Ghi file CSDL1 + CSDL2       │
     │                              │
1.0s │                              │ Đọc file CSDL2
1.2s │                              │ Parse JSON
1.5s │                              │ Kiểm tra signal thay đổi
1.8s │                              │ Mở lệnh S1, S2, S3
     │                              │
2.0s │ Cập nhật NEWS (mỗi 2s)      │
2.5s │ Ghi lại file CSDL1 + CSDL2   │
     │                              │
3.0s │                              │ Kiểm tra stoploss
3.5s │                              │ Cập nhật dashboard
```

---

## 9. HƯỚNG DẪN NHANH CHO NEWCHAT

### Bạn là newchat session mới? Đọc theo thứ tự:

1. ✅ Đọc phần 1: **HỆ THỐNG LÀ GÌ?**
2. ⭐⭐⭐ Đọc phần 2: **MỐC NỐI** (QUAN TRỌNG NHẤT!)
3. ✅ Đọc phần 3: **CHỨC NĂNG CHÍNH**
4. ✅ Đọc phần 8: **LUỒNG DỮ LIỆU HOÀN CHỈNH**
5. 📖 Sau đó đọc phần 5, 6, 7 nếu cần chi tiết

### Câu hỏi thường gặp:

**Q: Làm sao biết S1 đọc ở đâu?**
A: Đọc phần 2 → MỐC NỐI 1 → Column 2

**Q: Làm sao biết S3 đọc ở đâu?**
A: Đọc phần 2 → MỐC NỐI 2 → Column 8

**Q: NEWS CASCADE là gì?**
A: Đọc phần 2 → MỐC NỐI 2 → Giải thích chi tiết

**Q: Tại sao có 2 bot?**
A: SPY giám sát + phân tích, EA giao dịch. Tách biệt để dễ bảo trì.

**Q: File nào EA đọc?**
A: DataAutoOner2/{SYMBOL}_LIVE.json (CSDL2)

---

## 10. TÀI LIỆU THAM KHẢO

### Code References (Các dòng code quan trọng)

**SPY Bot:**
- ProcessSignalForTF: `Super_Spy7TF_V2.mq4:658`
- DetectCASCADE_New: `Super_Spy7TF_V2.mq4:1682`
- WriteCSDL1ArrayToFile: `Super_Spy7TF_V2.mq4:376`
- WriteCSDL2ArrayToFile: `Super_Spy7TF_V2.mq4:472`

**EA Auto:**
- ParseCSDLLoveJSON: `Eas_Smf_Oner_V2.mq4:502`
- ProcessS1Strategy: `Eas_Smf_Oner_V2.mq4:1051`
- ProcessS2Strategy: `Eas_Smf_Oner_V2.mq4:1062`
- ProcessS3Strategy: `Eas_Smf_Oner_V2.mq4:1126`
- CheckStoplossAndTakeProfit: `Eas_Smf_Oner_V2.mq4:1259`

### Các file quan trọng

```
Multi-Trading-Bot-Oner_2025/
├── MQL4/
│   ├── Indicators/
│   │   └── Super_Spy7TF_V2.mq4          (2946 dòng)
│   └── Experts/
│       └── Eas_Smf_Oner_V2.mq4          (2050 dòng)
├── Files/
│   ├── DataAutoOner/                     (CSDL1 + CSDL2 A)
│   ├── DataAutoOner2/                    (CSDL2 B - EA đọc)
│   └── DataAutoOner3/                    (CSDL2 C - Python)
└── README.md                             (File này)
```

---

## 📝 LƯU Ý QUAN TRỌNG

1. **2 MỐC NỐI** là khái niệm quan trọng nhất
2. **4 CHỨC NĂNG CHÍNH** = 2 phần của mỗi bot
3. **3 CHỨC NĂNG PHỤ** chỉ hỗ trợ, không liên quan đến giao dịch chính
4. Đọc từ TỔNG QUAN → CHI TIẾT, đừng nhảy vào code ngay!

---

**Cập nhật:** 2025-01-03
**Người viết:** AI Assistant
**Mục đích:** Giúp newchat session hiểu hệ thống nhanh chóng
