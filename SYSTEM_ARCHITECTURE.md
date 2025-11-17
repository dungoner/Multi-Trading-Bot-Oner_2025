# 🏗️ KIẾN TRÚC HỆ THỐNG TRADING BOT - MULTI-TIMEFRAME ONER V2

**Dự án:** Multi-Trading-Bot-Oner V2
**Nền tảng:** WaveTrend (WT) Indicator - Tín hiệu gốc
**Phiên bản:** MT4 + MT5
**Ngày cập nhật:** 2025-11-01

---

## 📖 MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Nền tảng WaveTrend (WT)](#2-nền-tảng-wavetrend-wt)
3. [SPY Bot - Bộ giám sát tín hiệu](#3-spy-bot---bộ-giám-sát-tín-hiệu)
4. [EA Bot - Bộ thực thi giao dịch](#4-ea-bot---bộ-thực-thi-giao-dịch)
5. [Giao tiếp giữa 2 Bots](#5-giao-tiếp-giữa-2-bots)
6. [Sơ đồ luồng tổng thể](#6-sơ-đồ-luồng-tổng-thể)
7. [Chi tiết kỹ thuật](#7-chi-tiết-kỹ-thuật)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1. Kiến trúc 2 tầng

Hệ thống được thiết kế theo kiến trúc **2-tier** với phân tách rõ ràng:

```
┌─────────────────────────────────────────────────────────────┐
│                    HỆ THỐNG TRADING BOT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   SPY BOT        │  CSDL   │    EA BOT        │          │
│  │  (Indicator)     │ ──────> │ (Expert Advisor) │          │
│  │                  │  File   │                  │          │
│  │  • Tính tín hiệu │         │  • Đọc tín hiệu  │          │
│  │  • Phân tích WT  │         │  • Thực thi lệnh │          │
│  │  • NEWS CASCADE  │         │  • Quản lý rủi ro│          │
│  └──────────────────┘         └──────────────────┘          │
│         ▲                              │                     │
│         │                              ▼                     │
│  ┌──────┴───────┐            ┌────────────────┐             │
│  │  WT Indicator│            │  MT4/MT5 Broker│             │
│  │  (7 TF Data) │            │  (Live Trading)│             │
│  └──────────────┘            └────────────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2. Vai trò từng thành phần

| Thành phần | Loại | Vai trò | Vị trí |
|------------|------|---------|--------|
| **WaveTrend (WT)** | Indicator gốc | Tạo tín hiệu BUY/SELL nguyên bản | Tích hợp trong SPY |
| **SPY Bot** | Indicator MT4 | Giám sát 7 TF, tính NEWS CASCADE, ghi file | Chart bất kỳ (1 symbol) |
| **CSDL File** | JSON Data | Trung gian truyền dữ liệu | `DataAutoOner\[SYMBOL].json` |
| **EA Bot** | Expert Advisor | Đọc tín hiệu, thực thi lệnh, quản lý risk | Chart giao dịch |

### 1.3. Luồng dữ liệu tổng quát

```
WaveTrend (7 TF)
    ↓
SPY Bot (tính toán + phân tích)
    ↓
CSDL File (JSON)
    ↓
EA Bot (đọc file)
    ↓
Trading Execution (MT4/MT5)
```

---

## 2. NỀN TẢNG WAVETREND (WT)

### 2.1. WaveTrend là gì?

**WaveTrend** là oscillator indicator phổ biến trong trading, tương tự RSI nhưng mượt hơn và nhạy với momentum.

**Đặc điểm:**
- Range: -100 đến +100
- Cross zero line: Tín hiệu mua/bán
- Overbought/Oversold zones: ±60 thường được dùng
- Smooth curves: Giảm noise so với RSI

### 2.2. Tín hiệu WT trong hệ thống

SPY Bot sử dụng WT để tạo 3 loại tín hiệu:

```
WT > 0  AND  Crossing Up    →  SIGNAL = +1 (BUY)
WT < 0  AND  Crossing Down  →  SIGNAL = -1 (SELL)
No clear signal            →  SIGNAL = 0 (NEUTRAL)
```

### 2.3. Tại sao chọn WT?

1. **Smooth momentum**: Ít false signals hơn RSI
2. **Multi-timeframe consistency**: WT hoạt động tốt trên cả 7 TF
3. **Clear reversal points**: Cross-over/cross-under dễ xác định
4. **Proven track record**: Nhiều trader sử dụng thành công

### 2.4. WT trong 7 Timeframes

SPY Bot tính WT độc lập cho mỗi TF:

| Timeframe | WT Period | Smoothing | Sensitivity |
|-----------|-----------|-----------|-------------|
| **M1** | Fast | Low | Highest (scalping) |
| **M5** | Fast | Medium | High |
| **M15** | Medium | Medium | Medium-High |
| **M30** | Medium | Medium | Medium |
| **H1** | Slow | High | Medium-Low |
| **H4** | Slow | High | Low |
| **D1** | Very Slow | Very High | Lowest (swing) |

**Kết luận:** WT là trái tim của hệ thống, tạo nền tảng tín hiệu cho tất cả strategies.

---

## 3. SPY BOT - BỘ GIÁM SÁT TÍN HIỆU

### 3.1. Mục đích

**SPY Bot** = Signal Processing Yielder (Bộ tạo tín hiệu xử lý)

**Nhiệm vụ chính:**
1. ✅ Tính toán WaveTrend cho 7 timeframes
2. ✅ Phát hiện signal changes (BUY ↔ SELL)
3. ✅ Phân tích NEWS CASCADE (độ mạnh tín hiệu)
4. ✅ Tính PriceDiff và TimeDiff giữa các TF
5. ✅ Ghi dữ liệu vào file CSDL theo format chuẩn
6. ✅ Maintain history (7 signals per TF)

### 3.2. Cấu trúc dữ liệu - CSDL 10 Columns

SPY Bot tạo file JSON với **10 cột dữ liệu** cho mỗi timeframe:

| Cột | Tên | Ý nghĩa | Giá trị |
|-----|-----|---------|---------|
| 1 | Timeframe | Khung thời gian | M1/M5/M15/M30/H1/H4/D1 |
| 2 | Index | Chỉ số TF | 0-6 |
| 3 | **Signal** | Tín hiệu WT | +1 (BUY), -1 (SELL), 0 (NEUTRAL) |
| 4 | **Price** | Giá entry | Ask/Bid price |
| 5 | **Cross** | Cross reference | Timestamp của TF trước |
| 6 | **Timestamp** | Thời gian | Unix timestamp |
| 7 | **PriceDiff** | Chênh lệch giá | USD difference từ signal trước |
| 8 | **TimeDiff** | Chênh lệch thời gian | Minutes từ signal trước |
| 9 | **NEWS** | NEWS CASCADE | ±11 đến ±16 (level 1-6) hoặc 0 |
| 10 | **MaxLoss** | Max loss tracking | Negative value (USD) |

**Ví dụ dữ liệu CSDL:**
```json
{
  "M1": {
    "signal": 1,
    "price": 2045.50,
    "cross": 1730451234,
    "timestamp": 1730451240,
    "pricediff": 2.5,
    "timediff": 3,
    "news": 14,
    "maxloss": -15.50
  },
  "M5": {
    "signal": 1,
    "price": 2045.30,
    ...
  }
}
```

### 3.3. OnTimer() Flow - Chức năng chính

**SPY Bot chạy mỗi 1 giây** với OnTimer():

```
OnTimer() - Called every 1 second
│
├─ CHỨC NĂNG CHÍNH (Main Function)
│  │
│  ├─ EVEN/ODD Mode Check
│  │  ├─ If ProcessSignalOnOddSecond = true  → Run on ODD seconds only
│  │  └─ If ProcessSignalOnOddSecond = false → Run every second
│  │
│  └─ ProcessAllSignals()  ← CORE FUNCTION
│     │
│     ├─ Loop 7 TF (M1 → D1)
│     │  │
│     │  ├─ Switch to TF chart
│     │  │
│     │  ├─ Calculate WaveTrend
│     │  │  ├─ Read WT indicator values
│     │  │  ├─ Detect cross-over/cross-under
│     │  │  └─ Generate Signal: +1, -1, or 0
│     │  │
│     │  ├─ Calculate PriceDiff (USD)
│     │  │  └─ Current Price - Last Signal Price
│     │  │
│     │  ├─ Calculate TimeDiff (minutes)
│     │  │  └─ Current Time - Last Signal Time
│     │  │
│     │  ├─ Calculate NEWS CASCADE
│     │  │  ├─ Analyze 6 TFs alignment
│     │  │  ├─ Check LiveDiff threshold
│     │  │  ├─ Check TimeDiff threshold
│     │  │  └─ Return ±11 to ±16 (level 1-6)
│     │  │
│     │  ├─ Update MaxLoss tracking
│     │  │
│     │  └─ Save to CSDL array
│     │
│     └─ Write CSDL File
│        ├─ Format: JSON
│        └─ Path: DataAutoOner\[SYMBOL].json
│
└─ CHỨC NĂNG PHỤ (Auxiliary - Even seconds only)
   │
   ├─ UpdateLiveNEWS()
   │  └─ Update NEWS values in real-time
   │
   ├─ RunStartupReset()
   │  └─ Auto-reset 1 minute after MT4 starts
   │
   ├─ RunMidnightAndHealthCheck()
   │  ├─ Midnight reset at 0h daily
   │  └─ Health check at 8h & 16h
   │
   └─ RunDashboardUpdate()
      └─ Update visual dashboard on chart
```

### 3.4. NEWS CASCADE Strategy

**NEWS CASCADE** là phân tích độ mạnh của tín hiệu dựa trên:

**Công thức:**
```
NEWS Level = Count aligned TFs × Price momentum × Time factor

Level 1 (±11): 2-3 TFs aligned, weak momentum
Level 2 (±12): 3-4 TFs aligned, medium momentum
Level 3 (±13): 4-5 TFs aligned, good momentum
Level 4 (±14): 5-6 TFs aligned, strong momentum
Level 5 (±15): 6-7 TFs aligned, very strong momentum
Level 6 (±16): All 7 TFs aligned, extreme momentum
```

**Ứng dụng:**
- EA Bot sử dụng NEWS để filter signals (S3_NEWS strategy)
- Bonus orders mở khi NEWS >= threshold
- Risk management dựa trên NEWS level

### 3.5. File I/O Operations

**Write Operation:**
```cpp
void WriteToFile() {
    // Open file in DataAutoOner\ folder
    string filename = DataAutoOner\XAUUSD.json;

    // Format JSON with 10 columns for 7 TFs
    string json = "{\n";
    for(int tf = 0; tf < 7; tf++) {
        json += "  \"" + TF_NAMES[tf] + "\": {\n";
        json += "    \"signal\": " + signals[tf] + ",\n";
        json += "    \"price\": " + prices[tf] + ",\n";
        // ... 8 more columns
        json += "  },\n";
    }
    json += "}";

    // Write atomically (avoid corruption)
    FileWrite(handle, json);
    FileClose(handle);
}
```

**Retry Logic:**
- Retry up to 3 times if write fails
- Avoid file lock conflicts with EA Bot

### 3.6. Health Monitoring

SPY Bot tự động kiểm tra sức khỏe:

1. **Startup Reset** (1 minute after MT4 starts)
   - Refresh all 7 TF charts
   - Clear cache
   - Reinitialize data structures

2. **Midnight Reset** (0h daily)
   - Reset counters
   - Archive old data
   - Smart TF refresh

3. **Health Check** (8h & 16h)
   - Check if CSDL file is updating
   - If stuck → Auto-reset all TF charts
   - Alert user if bot frozen

---

## 4. EA BOT - BỘ THỰC THI GIAO DỊCH

### 4.1. Mục đích

**EA Bot** = Expert Advisor Bot (Bộ tư vấn chuyên gia)

**Nhiệm vụ chính:**
1. ✅ Đọc file CSDL từ SPY Bot
2. ✅ Map data vào 7 timeframes
3. ✅ Thực thi 3 strategies (S1, S2, S3) + BONUS
4. ✅ Quản lý 21 orders (7 TF × 3 strategies)
5. ✅ Risk management (stoploss, takeprofit, emergency)
6. ✅ Dashboard monitoring

### 4.2. Kiến trúc Strategies

EA Bot quản lý **4 loại strategy** trên **7 timeframes** = **28 strategy instances**:

```
┌────────────────────────────────────────────────────────────┐
│                   EA BOT STRATEGIES                        │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┬──────────┬──────────┬──────────┬──────────┐   │
│  │   TF    │  S1_HOME │ S2_TREND │ S3_NEWS  │ S3_BONUS │   │
│  ├─────────┼──────────┼──────────┼──────────┼──────────┤   │
│  │ M1 (0)  │  Magic 1 │ Magic 2  │ Magic 3  │ Magic 3  │   │
│  │ M5 (1)  │  Magic 4 │ Magic 5  │ Magic 6  │ Magic 6  │   │
│  │ M15 (2) │  Magic 7 │ Magic 8  │ Magic 9  │ Magic 9  │   │
│  │ M30 (3) │  Magic 10│ Magic 11 │ Magic 12 │ Magic 12 │   │
│  │ H1 (4)  │  Magic 13│ Magic 14 │ Magic 15 │ Magic 15 │   │
│  │ H4 (5)  │  Magic 16│ Magic 17 │ Magic 18 │ Magic 18 │   │
│  │ D1 (6)  │  Magic 19│ Magic 20 │ Magic 21 │ Magic 21 │   │
│  └─────────┴──────────┴──────────┴──────────┴──────────┘   │
│                                                             │
│  Total: 21 unique magic numbers (7 TF × 3 strategies)      │
│  BONUS uses same magic as S3_NEWS for each TF              │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 4.3. Chi tiết từng Strategy

#### **Strategy 1: S1_HOME (Binary Signal)**

**Logic:**
```
Mở lệnh KHI:
- Signal thay đổi từ 0 → +1 hoặc 0 → -1
- HOẶC Signal đảo chiều: +1 → -1 hoặc -1 → +1

Option: NEWS Filter
- Nếu bật: Chỉ mở khi NEWS != 0
- Nếu tắt: Mở mọi signal change
```

**Use case:** Scalping, theo sát mọi thay đổi tín hiệu

#### **Strategy 2: S2_TREND (Trend Following)**

**Logic:**
```
Mở lệnh KHI:
- D1 signal hỗ trợ (cùng hướng HOẶC neutral)
- Signal thay đổi
- Timestamp mới hơn timestamp cũ

Đóng lệnh KHI:
- Signal đảo chiều
```

**Use case:** Swing trading, theo xu hướng lớn

#### **Strategy 3: S3_NEWS (News Alignment)**

**Logic:**
```
Mở lệnh KHI:
- Signal cùng dấu với NEWS
- NEWS != 0
- Signal thay đổi

Đóng lệnh KHI:
- Signal thay đổi (không cần check NEWS)
```

**Use case:** High-momentum trading, tận dụng tin tức

#### **Strategy 4: S3_BONUS (Extra News Orders)**

**Logic:**
```
Mở lệnh KHI:
- M1 signal thay đổi
- NEWS >= MinNewsLevelBonus (e.g., 13)
- Mở NHIỀU lệnh (BonusOrderCount)
- Lot size = S3 lot × BonusLotMultiplier

Đóng lệnh KHI:
- M1 signal thay đổi lần nữa
- Đóng TẤT CẢ 7 TF bonus cùng lúc
```

**Use case:** Aggressive momentum capture

### 4.4. OnTimer() Flow - Chức năng chính

**EA Bot chạy mỗi 1 giây** với OnTimer():

```
OnTimer() - Called every 1 second
│
├─ Prevent duplicate execution
│
├─ GROUP 1: EVEN SECONDS (0,2,4,6,8...) - TRADING CORE
│  │
│  ├─ STEP 1: ReadCSDLFile()
│  │  ├─ Open DataAutoOner\[SYMBOL].json
│  │  ├─ Parse JSON (10 columns × 7 TF)
│  │  └─ Store in g_ea.csdl_rows[7]
│  │
│  ├─ STEP 2: MapCSDLToEAVariables()
│  │  └─ Copy CSDL data to EA working variables
│  │
│  └─ STEP 3: Strategy Loop (7 TF)
│     │
│     FOR tf = 0 to 6:
│     │
│     IF HasValidS2BaseCondition(tf):  ← Signal changed?
│     │
│     ├─ STEP 3.1: Close ALL Bonus Orders (M1 trigger)
│     │  IF (tf == 0 AND EnableBonusNews):
│     │     CloseAllBonusOrders()  ← Closes ALL 7 TF bonus
│     │
│     ├─ STEP 3.2: Close old orders for THIS TF
│     │  CloseAllStrategiesByMagicForTF(tf)
│     │  └─ Close magic[tf][0], magic[tf][1], magic[tf][2]
│     │
│     ├─ STEP 3.3: Open new orders (if TF enabled)
│     │  IF IsTFEnabled(tf):
│     │     IF S1_HOME:  ProcessS1Strategy(tf)
│     │     IF S2_TREND: ProcessS2Strategy(tf)
│     │     IF S3_NEWS:  ProcessS3Strategy(tf)
│     │
│     ├─ STEP 3.4: Process Bonus News (INSIDE loop, BEFORE old=new)
│     │  IF EnableBonusNews:
│     │     ProcessBonusNews()
│     │        └─ Scan ALL 7 TF for NEWS >= threshold
│     │           Open BonusOrderCount orders with bonus lot
│     │
│     └─ STEP 3.5: Update baseline
│        g_ea.signal_old[tf] = g_ea.csdl_rows[tf].signal
│        g_ea.timestamp_old[tf] = g_ea.csdl_rows[tf].timestamp
│
└─ GROUP 2: ODD SECONDS (1,3,5,7,9...) - AUXILIARY
   │
   ├─ CheckStoplossAndTakeProfit()
   │  ├─ Layer 1 Stoploss: Per-order max loss
   │  ├─ Layer 2 Stoploss: Per-TF cumulative loss
   │  └─ Take Profit: Per-order profit target
   │
   ├─ UpdateDashboard()
   │  └─ Display 21 orders status on chart
   │
   ├─ CheckAllEmergencyConditions()
   │  ├─ Equity drop emergency
   │  ├─ Drawdown emergency
   │  └─ Close all if threshold exceeded
   │
   ├─ CheckWeekendReset()
   │  └─ Reset flags on Monday
   │
   └─ CheckSPYBotHealth()
      └─ Alert if SPY bot not updating
```

### 4.5. Critical Logic - HasValidS2BaseCondition()

**Hàm quan trọng nhất** quyết định có xử lý TF hay không:

```cpp
bool HasValidS2BaseCondition(int tf) {
    int signal_old = g_ea.signal_old[tf];
    int signal_new = g_ea.csdl_rows[tf].signal;
    datetime timestamp_old = g_ea.timestamp_old[tf];
    datetime timestamp_new = g_ea.csdl_rows[tf].timestamp;

    // Chỉ xử lý KHI:
    // 1. Signal thay đổi (old != new)
    // 2. Signal mới hợp lệ (new != 0)
    // 3. Timestamp mới hơn (avoid duplicate)

    return (signal_old != signal_new &&
            signal_new != 0 &&
            timestamp_old < timestamp_new);
}
```

**Tại sao quan trọng?**
- Tránh spam orders khi signal không đổi
- Đảm bảo timestamp luôn tăng (không xử lý signal cũ)
- Filter neutral signals (0)

### 4.6. Risk Management - 3 Layers

#### **Layer 1: Per-Order Stoploss**
```
Check MỖI order:
- If profit < -MaxLossPerOrder
  → Close immediately
```

#### **Layer 2: Per-TF Cumulative Stoploss**
```
Check TỔNG profit của 3 strategies trong TF:
- Total = S1 profit + S2 profit + S3 profit
- If Total < -(MaxLossPerOrder × 3)
  → Close ALL 3 strategies của TF đó
```

#### **Layer 3: Emergency Conditions**
```
Check toàn bộ account:
- If Equity < Balance × (1 - EmergencyDrawdownPercent)
  → Close ALL 21 orders
  → Stop trading
```

### 4.7. Magic Number System

**Công thức tính magic number:**

```
Magic = BaseMagic + (TF_index × 3) + Strategy_index

Ví dụ:
- M1 (tf=0) + S1 (s=0) → Magic = 100 + (0×3) + 0 = 100
- M1 (tf=0) + S2 (s=1) → Magic = 100 + (0×3) + 1 = 101
- M1 (tf=0) + S3 (s=2) → Magic = 100 + (0×3) + 2 = 102
- M5 (tf=1) + S1 (s=0) → Magic = 100 + (1×3) + 0 = 103
- D1 (tf=6) + S3 (s=2) → Magic = 100 + (6×3) + 2 = 120
```

**21 magic numbers:**
```
TF  │ S1   │ S2   │ S3
────┼──────┼──────┼──────
M1  │ 100  │ 101  │ 102
M5  │ 103  │ 104  │ 105
M15 │ 106  │ 107  │ 108
M30 │ 109  │ 110  │ 111
H1  │ 112  │ 113  │ 114
H4  │ 115  │ 116  │ 117
D1  │ 118  │ 119  │ 120
```

**Lợi ích:**
- Unique identifier cho mỗi order
- Dễ debug: Nhìn magic biết ngay TF + Strategy
- Close by magic: Đóng chính xác strategy cần thiết

---

## 5. GIAO TIẾP GIỮA 2 BOTS

### 5.1. File-Based Communication

**Phương thức:** SPY ghi → EA đọc (file JSON)

**Lý do chọn file thay vì alternatives:**

| Phương án | Ưu điểm | Nhược điểm | Lựa chọn |
|-----------|---------|------------|----------|
| **File JSON** | Simple, reliable, debuggable | File I/O overhead | ✅ CHỌN |
| Global Variables | Fast | Limited size, MT4 only | ❌ |
| Named Pipes | Very fast | Complex, OS-dependent | ❌ |
| Memory Mapping | Fastest | Very complex, risky | ❌ |

### 5.2. File Format - CSDL JSON Structure

**File:** `DataAutoOner\XAUUSD.json`

```json
{
  "M1": {
    "signal": 1,
    "price": 2045.50,
    "cross": 1730451234,
    "timestamp": 1730451240,
    "pricediff": 2.5,
    "timediff": 3,
    "news": 14,
    "maxloss": -15.50
  },
  "M5": {
    "signal": -1,
    "price": 2045.30,
    "cross": 1730451180,
    "timestamp": 1730451200,
    "pricediff": -3.2,
    "timediff": 8,
    "news": -12,
    "maxloss": -8.20
  },
  ... (5 more TFs)
}
```

### 5.3. Timing Coordination

**Tránh file lock conflict:**

```
┌────────────────────────────────────────────────────────┐
│                  TIMELINE (1 Second)                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Second:  0    1    2    3    4    5    6    7    8... │
│           │    │    │    │    │    │    │    │    │    │
│  SPY:     │    W    │    W    │    W    │    W    │    │  W = Write
│           │    │    │    │    │    │    │    │    │    │
│  EA:      R    │    R    │    R    │    R    │    R... │  R = Read
│           │    │    │    │    │    │    │    │    │    │
└────────────────────────────────────────────────────────┘

SPY writes on ODD seconds (1, 3, 5, 7...)
EA reads on EVEN seconds (0, 2, 4, 6...)
→ NO CONFLICT!
```

**Cấu hình:**
- SPY: `ProcessSignalOnOddSecond = true`
- EA: `UseEvenOddMode = true`

### 5.4. Data Latency

**Độ trễ tối đa:** 1 giây

```
Time 0:00:01 - SPY detects signal change → Write CSDL
Time 0:00:02 - EA reads CSDL → Execute trade
Total latency: 1 second
```

**Chấp nhận được vì:**
- Trading timeframe nhỏ nhất là M1 (60 seconds)
- 1 second delay không ảnh hưởng entry price đáng kể
- Reliability > Speed trong trading

### 5.5. Error Handling

**SPY Bot:**
```cpp
int retry = 0;
while(retry < 3) {
    if(WriteToFile(data)) {
        break;  // Success
    }
    Sleep(100);
    retry++;
}
```

**EA Bot:**
```cpp
int retry = 0;
while(retry < 3) {
    if(ReadFromFile(data)) {
        if(ValidateData(data)) {
            break;  // Success
        }
    }
    Sleep(100);
    retry++;
}
// If all retries fail → Use old data, don't trade
```

---

## 6. SƠ ĐỒ LUỒNG TỔNG THỂ

### 6.1. Flowchart - Toàn hệ thống

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SYSTEM STARTUP                               │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │   SPY Bot Init   │        │    EA Bot Init   │
          │                  │        │                  │
          │ • Load settings  │        │ • Load settings  │
          │ • Init data      │        │ • Init magic #s  │
          │ • Start timer    │        │ • Start timer    │
          └────────┬─────────┘        └────────┬─────────┘
                   │                           │
                   ▼                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      MAIN LOOP (Every 1 Second)                      │
└──────────────────────────────────────────────────────────────────────┘
                   │                           │
       ┌───────────┴──────────┐    ┌───────────┴──────────┐
       │    SPY OnTimer()     │    │     EA OnTimer()     │
       │   (ODD seconds)      │    │   (EVEN seconds)     │
       └───────────┬──────────┘    └───────────┬──────────┘
                   │                           │
                   ▼                           │
       ┌───────────────────────┐               │
       │ Calculate WT (7 TF)   │               │
       │                       │               │
       │ FOR each TF:          │               │
       │  • Read WT values     │               │
       │  • Detect cross       │               │
       │  • Gen signal ±1/0    │               │
       └───────────┬───────────┘               │
                   ▼                           │
       ┌───────────────────────┐               │
       │ Analyze NEWS CASCADE  │               │
       │                       │               │
       │ • Check 7 TF align    │               │
       │ • Calc price momentum │               │
       │ • Calc time factor    │               │
       │ • Return ±11 to ±16   │               │
       └───────────┬───────────┘               │
                   ▼                           │
       ┌───────────────────────┐               │
       │ Update CSDL Data      │               │
       │                       │               │
       │ • 7 TF × 10 columns   │               │
       │ • Update history      │               │
       └───────────┬───────────┘               │
                   ▼                           │
       ┌───────────────────────┐               │
       │ Write JSON File       │               │
       │                       │               │
       │ • Format JSON         │               │
       │ • Atomic write        │               │
       │ • Retry on failure    │               │
       └───────────┬───────────┘               │
                   │                           │
                   │   CSDL File               │
                   │   (JSON)                  │
                   │                           │
                   │                           ▼
                   │               ┌───────────────────────┐
                   │               │ Read CSDL File        │
                   │               │                       │
                   │               │ • Parse JSON          │
                   │               │ • Validate data       │
                   │               │ • Retry on failure    │
                   │               └───────────┬───────────┘
                   │                           ▼
                   │               ┌───────────────────────┐
                   │               │ Map to EA Variables   │
                   │               │                       │
                   │               │ • 7 TF × 10 columns   │
                   │               │ • Store in g_ea       │
                   │               └───────────┬───────────┘
                   │                           ▼
                   │               ┌───────────────────────┐
                   │               │ FOR each TF (0-6):    │
                   │               │                       │
                   │               │ IF signal changed:    │
                   │               └───────────┬───────────┘
                   │                           ▼
                   │               ┌───────────────────────┐
                   │               │ Close Old Orders      │
                   │               │                       │
                   │               │ • Close S1/S2/S3      │
                   │               │ • Reset flags         │
                   │               └───────────┬───────────┘
                   │                           ▼
                   │               ┌───────────────────────┐
                   │               │ Open New Orders       │
                   │               │                       │
                   │               │ IF S1: ProcessS1()    │
                   │               │ IF S2: ProcessS2()    │
                   │               │ IF S3: ProcessS3()    │
                   │               └───────────┬───────────┘
                   │                           ▼
                   │               ┌───────────────────────┐
                   │               │ Process BONUS         │
                   │               │                       │
                   │               │ IF NEWS >= threshold: │
                   │               │  • Open bonus orders  │
                   │               └───────────┬───────────┘
                   │                           ▼
                   │               ┌───────────────────────┐
                   │               │ Update baseline       │
                   │               │                       │
                   │               │ • signal_old = new    │
                   │               │ • timestamp_old = new │
                   │               └───────────┬───────────┘
                   │                           │
                   └───────────────────────────┴──────────────────┐
                                               │                   │
                                               ▼                   ▼
                                   ┌───────────────────┐ ┌────────────────┐
                                   │ Risk Management   │ │ Dashboard      │
                                   │                   │ │                │
                                   │ • Stoploss check  │ │ • Show 21 pos  │
                                   │ • Takeprofit      │ │ • Show P&L     │
                                   │ • Emergency       │ │ • Alert status │
                                   └───────────────────┘ └────────────────┘
                                               │
                                               ▼
                                   ┌───────────────────────┐
                                   │   BROKER (MT4/MT5)    │
                                   │                       │
                                   │   Live Trading        │
                                   └───────────────────────┘
```

### 6.2. Sequence Diagram - Signal Processing

```
Time  SPY Bot           CSDL File         EA Bot            Broker
│
│ 1s   │
├──────┤
│      │ Calculate WT
│      │ Detect BUY signal
│      │
│      │ Write JSON ────>│
│      │                 │
│ 2s   │                 │
├──────┤                 │
│                        │ Read JSON ────> │
│                        │                 │
│                        │                 │ Signal changed?
│                        │                 │ YES
│                        │                 │
│                        │                 │ Close old SELL
│                        │                 │ orders ──────> │
│                        │                 │                │
│                        │                 │                │ Close #123
│                        │                 │                │
│                        │                 │ Open new BUY   │
│                        │                 │ orders ──────> │
│                        │                 │                │ Open #456
│                        │                 │                │
│                        │                 │ Update flags   │
│                        │                 │ signal_old=+1  │
│                        │                 │                │
│ 3s   │                 │                 │                │
├──────┤                 │                 │                │
│      │ Calculate WT    │                 │                │
│      │ Still BUY       │                 │                │
│      │                 │                 │                │
│      │ Write JSON ────>│                 │                │
│      │ (no change)     │                 │                │
│                        │                 │                │
│ 4s   │                 │                 │                │
├──────┤                 │                 │                │
│                        │ Read JSON ────> │                │
│                        │                 │                │
│                        │                 │ Signal changed?│
│                        │                 │ NO (still +1)  │
│                        │                 │                │
│                        │                 │ Skip processing│
│                        │                 │                │
...continues every second...
```

### 6.3. State Machine - EA Trading Logic

```
                    ┌──────────────────┐
                    │   IDLE STATE     │
                    │                  │
                    │ • No positions   │
                    │ • Waiting signal │
                    └────────┬─────────┘
                             │
                    Signal changed (+1 or -1)
                             │
                             ▼
                    ┌──────────────────┐
                    │  OPENING STATE   │
                    │                  │
                    │ • Close old      │
              ┌─────│ • Open new       │
              │     │ • Set flags      │
              │     └────────┬─────────┘
              │              │
              │     Order opened successfully
              │              │
              │              ▼
              │     ┌──────────────────┐
              │     │  HOLDING STATE   │
              │     │                  │
              │     │ • Monitor P&L    │
              │     │ • Check SL/TP    │
              │     │ • Update dash    │
              │     └────────┬─────────┘
              │              │
              │              ├─────────────────────┐
              │              │                     │
              │    Signal changed        Stoploss/Takeprofit hit
              │              │                     │
              │              ▼                     ▼
              │     ┌──────────────────┐  ┌──────────────────┐
              └────>│  CLOSING STATE   │  │  CLOSING STATE   │
                    │                  │  │                  │
                    │ • Close by magic │  │ • Close by risk  │
                    │ • Reset flags    │  │ • Reset flags    │
                    └────────┬─────────┘  └────────┬─────────┘
                             │                     │
                             └──────────┬──────────┘
                                        │
                              Order closed successfully
                                        │
                                        ▼
                             ┌──────────────────┐
                             │   IDLE STATE     │
                             │                  │
                             │ Wait next signal │
                             └──────────────────┘
```

---

## 7. CHI TIẾT KỸ THUẬT

### 7.1. Performance Metrics

| Metric | SPY Bot | EA Bot |
|--------|---------|--------|
| **OnTimer Frequency** | 1 second | 1 second |
| **CPU Usage** | ~2-5% (7 TF calc) | ~1-2% (read file) |
| **File I/O** | Write every second | Read every second |
| **File Size** | ~2 KB (JSON) | N/A |
| **Latency** | <50ms (WT calc) | <10ms (JSON parse) |
| **Memory** | ~5 MB | ~3 MB |

### 7.2. File System Requirements

**Folder Structure:**
```
MT4/MT5 Terminal/
└── MQL4/ or MQL5/
    └── Files/
        └── DataAutoOner/
            ├── XAUUSD.json      ← SPY writes, EA reads
            ├── EURUSD.json
            └── ... (other symbols)
```

**Permissions:**
- Read/Write for both SPY and EA
- Shared folder access
- Atomic write operations

### 7.3. Multi-Symbol Support

**MT4 Version:**
- ❌ Single symbol only
- Reason: File I/O limitations, architecture constraints

**MT5 Version:**
- ✅ Multi-symbol capable
- Architecture: `g_ea_array[10]` for up to 10 symbols
- Input: `EnableMultiSymbol = true`, `Symbols = "XAUUSD,EURUSD,GBPUSD"`
- Each symbol has independent CSDL file

### 7.4. Scalability

**Current Limits:**

| Component | Limit | Reason |
|-----------|-------|--------|
| **Timeframes** | 7 (M1-D1) | Hardcoded arrays |
| **Strategies** | 3 + 1 BONUS | Magic number design |
| **Symbols (MT4)** | 1 | Single instance |
| **Symbols (MT5)** | 10 | Array size |
| **Max Orders** | 21 per symbol | 7 TF × 3 strategies |

**Expandable:**
- Add more TF: Requires array expansion
- Add more strategies: Requires magic number redesign
- Add more symbols (MT5): Change `g_ea_array` size

### 7.5. Error Recovery

**SPY Bot Recovery:**
1. File write fails → Retry 3 times → Skip this cycle
2. WT calculation error → Use last valid signal
3. Health check stuck → Auto-reset all TF charts

**EA Bot Recovery:**
1. File read fails → Retry 3 times → Use old data
2. Invalid JSON → Skip this cycle, wait next update
3. Order send fails → Retry with error handling
4. Position close fails → Retry with price refresh

### 7.6. Testing Recommendations

**SPY Bot Testing:**
```
1. Strategy Tester (MT4)
   - Indicator mode
   - Visual mode ON
   - Check CSDL file generation

2. Live Chart Testing
   - Open 7 TF charts (M1-D1)
   - Attach SPY to any chart
   - Monitor CSDL file updates
   - Check dashboard display

3. Stress Testing
   - High volatility periods
   - News events
   - Weekend gaps
```

**EA Bot Testing:**
```
1. Strategy Tester (MT4/MT5)
   - EA mode
   - Use historical data
   - Check order execution
   - Verify P&L calculations

2. Demo Account
   - Run 24-48 hours minimum
   - Monitor all 21 orders
   - Check risk management
   - Verify BONUS logic

3. Backtesting
   - 3-6 months data
   - Compare with MT4 results
   - Optimize parameters
```

---

## 📌 PHỤ LỤC

### A. Glossary - Thuật ngữ

| Term | Tiếng Việt | Ý nghĩa |
|------|------------|---------|
| **WaveTrend (WT)** | Sóng xu hướng | Oscillator indicator, nền tảng tín hiệu |
| **SPY Bot** | Bot gián điệp | Indicator giám sát 7 TF, tính tín hiệu |
| **EA Bot** | Bot tư vấn | Expert Advisor thực thi lệnh |
| **CSDL** | Cơ sở dữ liệu | File JSON truyền dữ liệu SPY→EA |
| **NEWS CASCADE** | Tin tức phối hợp | Độ mạnh tín hiệu dựa trên alignment |
| **TF** | Timeframe | Khung thời gian (M1/M5/M15/M30/H1/H4/D1) |
| **Magic Number** | Số magic | ID duy nhất cho mỗi order |
| **S1/S2/S3** | Strategy 1/2/3 | Các chiến lược giao dịch |
| **BONUS** | Thưởng | Orders phụ khi NEWS mạnh |

### B. Configuration Examples

**SPY Bot Settings (Recommended):**
```
Timer = 1                          // 1 second refresh
Retry = 3                          // 3 retry attempts
TargetSymbol = ""                  // Empty = current chart
EnableHealthCheck = true           // Auto-reset if stuck
EnableMidnightReset = true         // Daily reset
ProcessSignalOnOddSecond = true    // Avoid conflict with EA
NewsBaseLiveDiff = 2.5             // USD threshold
NewsLiveDiffStep = 0.5             // Increment per level
```

**EA Bot Settings (Conservative):**
```
S1_HOME = true                     // Enable binary strategy
S2_TREND = true                    // Enable trend following
S3_NEWS = true                     // Enable news alignment
EnableBonusNews = true             // Enable bonus orders
UseEvenOddMode = true              // Read on even seconds
StoplossMode = LAYER2              // 2-layer protection
MaxLossPerOrder = 50               // $50 per order
EmergencyDrawdownPercent = 20      // 20% account drawdown
BonusLotMultiplier = 1.5           // 1.5x lot for bonus
MinNewsLevelBonus = 13             // Level 3+ news
```

### C. Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **SPY not writing file** | Folder permission | Check `DataAutoOner\` exists |
| **EA not reading file** | File lock conflict | Enable `UseEvenOddMode` |
| **Orders not opening** | Signal not changed | Check `HasValidS2BaseCondition()` |
| **Duplicate orders** | Timestamp not updating | Verify SPY is running |
| **BONUS not closing** | M1 not triggering | Check `tf == 0` condition |
| **High CPU usage** | Too many TF charts | Limit to 7 TF only |

---

## 🎯 KẾT LUẬN

### Ưu điểm của hệ thống

1. ✅ **Modular Design**: SPY và EA tách biệt, dễ maintain
2. ✅ **WaveTrend Foundation**: Indicator proven, reliable signals
3. ✅ **Multi-Timeframe**: 7 TF coverage, từ M1 đến D1
4. ✅ **Multi-Strategy**: 4 strategies, đa dạng cách vào lệnh
5. ✅ **Risk Management**: 3-layer protection
6. ✅ **NEWS CASCADE**: Độ mạnh tín hiệu, filter chất lượng
7. ✅ **Auto-Recovery**: Health check, auto-reset
8. ✅ **MT5 Ready**: Full conversion, multi-symbol support

### Nhược điểm và giới hạn

1. ⚠️ **File I/O Dependency**: Lỗi file = lỗi hệ thống
2. ⚠️ **1-Second Latency**: Không phù hợp scalping cực nhanh
3. ⚠️ **Single Symbol (MT4)**: Không hỗ trợ multi-symbol
4. ⚠️ **Fixed 7 TF**: Không thể thêm TF tùy chỉnh
5. ⚠️ **Complexity**: Cần hiểu rõ 2 bots mới troubleshoot tốt

### Hướng phát triển

1. 🚀 **Multi-Symbol MT4**: Port multi-symbol architecture
2. 🚀 **Additional Strategies**: S4, S5 với logic mới
3. 🚀 **Cloud Integration**: Upload CSDL to cloud, remote monitoring
4. 🚀 **Machine Learning**: ML model phân tích NEWS CASCADE
5. 🚀 **Mobile App**: Dashboard app cho iOS/Android

---

**Tác giả:** Multi-Trading-Bot-Oner V2 Team
**Liên hệ:** See project repository
**Giấy phép:** Private/Proprietary

**Cảm ơn bạn đã đọc tài liệu này!** 🙏

---

*Document Version: 1.0*
*Last Updated: 2025-11-01*
*Generated by: Claude Code Agent*
