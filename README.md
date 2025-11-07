# 🤖 Multi-Trading Bot System - Hướng Dẫn Đầy Đủ

**Hệ thống giao dịch tự động 7 khung thời gian (Multi-TimeFrame) cho MT4/MT5/cTrader/TradeLocker**

> 📖 **Dành cho:** Trader và developer muốn hiểu hệ thống MTF ONER
>
> 🎯 **Mục tiêu:** Giải thích rõ ràng LUỒNG → CSDL → CHỨC NĂNG trên tất cả nền tảng
>
> ✅ **Status**: Production Ready - Đã convert đầy đủ sang 4 platforms

## 🎉 HOÀN THÀNH 100% - All Platforms Ready!

| Platform | Status | Lines | Documentation |
|----------|--------|-------|---------------|
| **MT4 EA** | ✅ Complete | 2800+ | `MQL4/Experts/` |
| **MT5 EA** | ✅ Complete | 2995 | `MQL5/Experts/` |
| **cTrader cBot** | ✅ Complete | 2800+ | `cTrader/` |
| **TradeLocker Python** | ✅ Complete | 1879 | `TradeLocker/` |

### 📚 Hướng Dẫn Cài Đặt Quick Links

- **TradeLocker (Python)**:
  - [Windows VPS Installation](TradeLocker/INSTALL_WINDOWS.md)
  - [Linux VPS Installation](TradeLocker/INSTALL_LINUX.md)
  - [TradeLocker README](TradeLocker/README.md)
- **MT4/MT5**: Sao chép file `.mq4`/`.mq5` vào thư mục `Experts`
- **cTrader**: Sao chép file `.cs` vào thư mục `cBots`

---

## 📋 MỤC LỤC

1. [TỔNG QUAN - 3 BOT LÀ GÌ?](#1-tổng-quan---3-bot-là-gì)
2. [BOT 1: WT (7 BỘ) - TẠO TÍN HIỆU GỐC](#2-bot-1-wt-7-bộ---tạo-tín-hiệu-gốc)
3. [BOT 2: SPY (1 BỘ) - TỔNG HỢP VÀ TÍNH NEWS](#3-bot-2-spy-1-bộ---tổng-hợp-và-tính-news)
4. [BOT 3: EA (1 BỘ) - GIAO DỊCH TỰ ĐỘNG](#4-bot-3-ea-1-bộ---giao-dịch-tự-động)
5. [CẤU TRÚC CSDL - DỮ LIỆU TRUNG TÂM](#5-cấu-trúc-csdl---dữ-liệu-trung-tâm)
6. [LUỒNG HOÀN CHỈNH - TỪ ĐẦU ĐẾN CUỐI](#6-luồng-hoàn-chỉnh---từ-đầu-đến-cuối)
7. [CRITICAL BUG ĐÃ SỬA](#7-critical-bug-đã-sửa)

---

## 1. TỔNG QUAN - 3 BOT LÀ GÌ?

### 🎯 Hệ thống gồm 3 loại bot chạy trên MT4:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MT4 PLATFORM (1 SYMBOL)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 7 CHARTS BẮT BUỘC (M1, M5, M15, M30, H1, H4, D1)           │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       ┌──────────┐  │
│  │ M1 Chart │  │ M5 Chart │  │M15 Chart │  ...  │ D1 Chart │  │
│  │          │  │          │  │          │       │          │  │
│  │ + WT Bot │  │ + WT Bot │  │ + WT Bot │       │ + WT Bot │  │
│  │ + EA Bot │  │          │  │          │       │ + SPY Bot│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       └────┬─────┘  │
│       │             │              │                  │        │
│       │             │              │                  │        │
│       └─────────────┴──────────────┴──────────────────┘        │
│                     │                                           │
│                     ▼                                           │
│            ┌──────────────────┐                                │
│            │  BOT SPY (D1)    │ ← Thu thập 7 TF                │
│            │  Đọc + Ghi file  │                                │
│            └────────┬─────────┘                                │
│                     │                                           │
│                     ▼                                           │
│              ┌─────────────┐                                   │
│              │ JSON Files  │ ← 7 rows × 6 columns              │
│              │ (CSDL 7x6)  │                                   │
│              └──────┬──────┘                                   │
│                     │                                           │
│                     ▼                                           │
│            ┌──────────────────┐                                │
│            │  BOT EA (M1)     │ ← Đọc file và giao dịch        │
│            │  Đọc + Mở lệnh   │                                │
│            └──────────────────┘                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📝 Giải thích đơn giản:

1. **7 BOT WT** (WaveTrend) - mỗi khung thời gian 1 bot
   - Nhiệm vụ: Phân tích giá → tạo tín hiệu BUY/SELL
   - Ghi kết quả: Vào Global Variables (bộ nhớ MT4)

2. **1 BOT SPY** (Surveillance) - chạy trên D1
   - Nhiệm vụ: Thu thập 7 tín hiệu → tính NEWS CASCADE → ghi file
   - Đọc từ: Global Variables (7 bot WT)
   - Ghi vào: File JSON (3 folder)

3. **1 BOT EA** (Expert Advisor) - chạy trên M1
   - Nhiệm vụ: Đọc file → mở lệnh tự động → quản lý rủi ro
   - Đọc từ: File JSON (SPY ghi)
   - Kết quả: Tối đa 21 lệnh (7 TF × 3 strategies) + BONUS

---

## 2. BOT 1: WT (7 BỘ) - TẠO TÍN HIỆU GỐC

### 📍 Vị trí:
- **7 chart riêng:** M1, M5, M15, M30, H1, H4, D1
- **Mỗi chart 1 bot WT** (indicator tự động)

### 🎯 Nhiệm vụ:

**TẠO TÍN HIỆU GIAO DỊCH TỪ WAVE TREND ALGORITHM**

### 🔧 Làm gì?

1. **Phân tích giá:**
   - Theo dõi biến động giá trên khung thời gian của mình
   - VD: Bot WT trên M1 → phân tích nến M1

2. **Chạy thuật toán Wave Trend:**
   - Tính toán các chỉ báo kỹ thuật
   - Phát hiện xu hướng tăng/giảm

3. **Tạo tín hiệu:**
   - `+1` = Tín hiệu MUA (BUY)
   - `-1` = Tín hiệu BÁN (SELL)
   - `0` = Không có tín hiệu (NONE)

### 💾 Ghi kết quả ở đâu?

**Vào Global Variables của MT4:**

```
Tên biến: {SYMBOL}_{TF}_SignalType1
VD: 
- BTCUSD_M1_SignalType1 = 1
- BTCUSD_M5_SignalType1 = -1
- BTCUSD_M15_SignalType1 = 0
```

### ❓ Vì sao cần 7 bot riêng?

**TRẢ LỜI:** Mỗi khung thời gian có đặc điểm khác nhau:
- **M1:** Nhanh, thay đổi liên tục (cho scalping)
- **H4:** Chậm, ổn định hơn (cho swing trading)
- **D1:** Rất chậm, xu hướng dài hạn (cho trend following)

→ Không thể 1 bot xử lý được cả 7 khung!

### ✅ Kết quả:

**Sau khi chạy → có 7 tín hiệu độc lập trong Global Variables**

Các bot khác (SPY) sẽ đọc từ đây.

---

## 3. BOT 2: SPY (1 BỘ) - TỔNG HỢP VÀ TÍNH NEWS

### 📍 Vị trí:
- **Chart D1** (1 bot duy nhất cho mỗi symbol)

### 🎯 Nhiệm vụ:

**THU THẬP 7 TÍN HIỆU + TÍNH NEWS CASCADE → GHI FILE**

SPY chia làm **2 PHẦN:**

---

### 📊 PHẦN A: THU THẬP TÍN HIỆU GỐC

#### Làm gì?

1. **Đọc Global Variables từ 7 bot WT:**
   ```
   M1_signal  = 1
   M5_signal  = 1
   M15_signal = 0
   M30_signal = -1
   H1_signal  = -1
   H4_signal  = 1
   D1_signal  = 1
   ```

2. **Tính toán thêm:**
   - `PriceDiff (USD)`: Chênh lệch giá so với lần trước
     - VD: Lần trước M1 = 50000, bây giờ = 50002.5 → +2.5 USD
   
   - `TimeDiff (phút)`: Thời gian từ tín hiệu trước
     - VD: Tín hiệu cũ lúc 10:00, mới lúc 10:05 → 5 phút
   
   - `MaxLoss`: Lỗ tối đa cho 1 LOT
     - Dùng để tính stoploss sau này

#### Kết quả?

**Có 7 rows dữ liệu cơ bản:**

| TF  | Signal | Price   | Timestamp | PriceDiff | TimeDiff | MaxLoss |
|-----|--------|---------|-----------|-----------|----------|---------|
| M1  | +1     | 50002.5 | 17306...  | +2.5      | 5        | -0.50   |
| M5  | +1     | 50001.0 | 17306...  | +1.2      | 15       | -0.75   |
| ... | ...    | ...     | ...       | ...       | ...      | ...     |

---

### 🔥 PHẦN B: TÍNH NEWS CASCADE (QUAN TRỌNG!)

#### NEWS CASCADE là gì?

**PHÁT HIỆN "TIN TỨC LỚN" KHI GIÁ ĐỘT BIẾN**

Khi có tin tức quan trọng → giá tăng/giảm đột ngột → đây là cơ hội giao dịch!

#### Tính toán như thế nào?

**BƯỚC 1: Lấy tín hiệu M1 mới nhất**
```
M1_signal = +1 (BUY)
M1_price  = 50000.0
M1_time   = 10:00:00
```

**BƯỚC 2: Lấy giá LIVE hiện tại**
```
Current_price = 50003.0
Current_time  = 10:00:30 (30 giây sau)
```

**BƯỚC 3: Tính độ đột biến**
```
live_diff = |50003.0 - 50000.0| = 3.0 USD
```

**BƯỚC 4: So sánh với 7 ngưỡng CASCADE**

#### 7 CẤP ĐỘ NEWS (2 Categories):

**CATEGORY 1 - EA TRADING (Điểm 10-70):**

| Level | Điều kiện TF          | Ngưỡng USD | Điểm NEWS |
|-------|-----------------------|------------|-----------|
| L1    | M1 đủ                 | > 2.5      | ±10       |
| L2    | M5→M1 cascade         | > 3.0      | ±20       |
| L3    | M15→M5→M1 cascade     | > 3.5      | ±30       |
| L4    | M30→M15→M5→M1         | > 4.0      | ±40       |
| L5    | H1→M30→M15→M5→M1      | > 4.5      | ±50       |
| L6    | H4→H1→M30→M15→M5→M1   | > 5.0      | ±60       |
| L7    | D1→H4→...→M1 (cả 7)   | > 5.5      | ±70       |

**CATEGORY 2 - SPECIAL (Điểm 1-7):**
- Tương tự nhưng ngưỡng riêng
- Dùng để tham khảo

**VÍ DỤ TÍNH TOÁN:**

```
M1:  live_diff = 3.0 > 2.5 ✓ → NEWS[M1]  = +10
M5:  M5→M1 chưa cascade    → NEWS[M5]  = 0
M15: Chưa đủ điều kiện     → NEWS[M15] = 0
M30: Chưa đủ điều kiện     → NEWS[M30] = 0
H1:  Chưa đủ điều kiện     → NEWS[H1]  = 0
H4:  Chưa đủ điều kiện     → NEWS[H4]  = 0
D1:  Chưa đủ điều kiện     → NEWS[D1]  = 0
```

#### Vì sao cần NEWS?

**PHÁT HIỆN CƠ HỘI LỚN!**

- Tin tức → giá biến động mạnh → lợi nhuận cao
- Càng nhiều TF cascade → tin càng mạnh → điểm càng cao
- EA dùng NEWS để mở lệnh BONUS (tăng volume)

---

### 📁 PHẦN C: GHI FILE CSDL

#### SPY ghi 3 file đồng thời:

```
DataAutoOner/SYMBOL_LIVE.json   ← Folder 1
DataAutoOner2/SYMBOL_LIVE.json  ← Folder 2 (EA đọc chính)
DataAutoOner3/SYMBOL_LIVE.json  ← Folder 3 (dự phòng)
```

**Tại sao 3 file?**
- Tránh file bị lock khi EA đang đọc
- Tăng reliability (nếu 1 file lỗi, còn 2 file khác)

#### Cấu trúc file JSON (7 rows × 6 columns):

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
    "signal": 1,
    "pricediff": 1.20,
    "timediff": 15,
    "news": -20
  },
  ... (5 rows nữa cho M15, M30, H1, H4, D1)
]
```

#### Ý nghĩa 6 cột:

| Cột | Ý nghĩa | EA dùng để? |
|-----|---------|-------------|
| `max_loss` | Lỗ tối đa 1 LOT | Tính stoploss |
| `timestamp` | Thời gian tín hiệu | Kiểm tra tín hiệu mới |
| **`signal`** | **Tín hiệu (±1, 0)** | **Quyết định BUY/SELL** |
| `pricediff` | Chênh lệch giá USD | Tham khảo |
| `timediff` | Thời gian từ tín hiệu trước | Tham khảo |
| **`news`** | **Điểm NEWS CASCADE** | **Mở lệnh BONUS** |

#### Khi nào SPY ghi file?

**MỖI 2 GIÂY:**
- Quét 7 TF
- Cập nhật NEWS
- Ghi lại 3 file

---

## 4. BOT 3: EA (1 BỘ) - GIAO DỊCH TỰ ĐỘNG

### 📍 Vị trí:
- **Chart M1** (1 bot duy nhất cho mỗi symbol)

### 🎯 Nhiệm vụ:

**ĐỌC FILE CSDL → GIAO DỊCH 7 TF × 3 STRATEGIES + BONUS**

---

### ⏱️ LUỒNG CHÍNH (Mỗi 2 giây)

```
┌──────────────────────────────────────────────────────────────┐
│ GIÂY CHẴN (0,2,4,6...): TRADING CORE                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ [1] ĐỌC FILE CSDL                                           │
│     ReadCSDLFile()                                           │
│     ├─ Thử đọc Folder 2 (ưu tiên)                           │
│     ├─ Nếu fail → thử Folder 1                              │
│     ├─ Nếu fail → thử Folder 3                              │
│     └─ Lưu vào g_ea.csdl_rows[7]                           │
│                                                              │
│ [2] TÁCH NEWS THÀNH 14 BIẾN                                 │
│     MapNewsTo14Variables()                                   │
│     ├─ g_ea.news_level[tf] = MathAbs(news)                 │
│     └─ g_ea.news_direction[tf] = sign(news)                │
│                                                              │
│     VD: news = +30                                           │
│         → level[tf] = 30 (mức độ)                          │
│         → direction[tf] = +1 (BUY)                         │
│                                                              │
│ [3] QUÉT 7 TF (M1→D1):                                      │
│     │                                                        │
│     ├─ [A] ĐÓNG LỆNH NHANH (chỉ M1):                        │
│     │   if(tf == M1 && M1_đảo_chiều):                      │
│     │   ├─ CloseS1OrdersByM1()                             │
│     │   ├─ CloseS2OrdersByM1()                             │
│     │   └─ CloseAllBonusOrders()                           │
│     │                                                        │
│     ├─ [B] ĐÓNG LỆNH BÌNH THƯỜNG (theo TF):                 │
│     │   if(TF_đảo_chiều):                                  │
│     │   └─ CloseOrdersForTF(tf)                            │
│     │                                                        │
│     └─ [C] MỞ LỆNH MỚI (3 strategies):                      │
│         ├─ ProcessS1Strategy(tf)  ← HOME/Binary            │
│         ├─ ProcessS2Strategy(tf)  ← TREND                  │
│         └─ ProcessS3Strategy(tf)  ← NEWS                   │
│                                                              │
│ [4] MỞ LỆNH BONUS                                           │
│     ProcessBonusNews()                                       │
│     └─ Quét 7 TF, mở thêm lệnh nếu NEWS cao               │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ GIÂY LẺ (1,3,5,7...): AUXILIARY                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ [1] CheckStoplossAndTakeProfit()                            │
│     └─ Đóng lệnh lỗ quá ngưỡng                              │
│                                                              │
│ [2] UpdateDashboard()                                        │
│     └─ Hiển thị bảng điều khiển                             │
│                                                              │
│ [3] CheckEmergencyConditions()                              │
│     └─ Đóng tất cả nếu DD > ngưỡng                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

### 🎯 3 CHIẾN LƯỢC GIAO DỊCH

#### Strategy 1: S1_HOME (Binary)

**Đọc từ:** Cột `signal`

**Điều kiện mở:**
- Signal hiện tại ≠ 0 (có tín hiệu BUY hoặc SELL)
- Signal cũ = 0 (trước đó không có tín hiệu)
- Timestamp thay đổi (tín hiệu mới)

**Điều kiện đóng:**
- **Nếu S1_CloseByM1 = true:** Đóng khi **M1** đảo chiều (nhanh)
- **Nếu S1_CloseByM1 = false:** Đóng khi **TF của nó** đảo chiều

**Đặc điểm:**
- Giao dịch ngắn hạn (binary options style)
- Chờ tín hiệu từ 0 → ±1 (cửa vào tốt nhất)
- Lot size nhỏ (risk thấp)

**VÍ DỤ:**
```
TF = M15
signal_cũ = 0
signal_mới = +1

→ MỞ lệnh S1_M15 BUY
```

---

#### Strategy 2: S2_TREND (Trend Following)

**Đọc từ:** Cột `signal` + Trend D1

**Điều kiện mở:**
- Signal hiện tại ≠ 0
- Signal thay đổi (≠ signal cũ)
- **Signal CÙNG CHIỀU với D1**
- Timestamp thay đổi

**Điều kiện đóng:**
- **Nếu S2_CloseByM1 = true:** Đóng khi **M1** đảo chiều
- **Nếu S2_CloseByM1 = false:** Đóng khi **TF của nó** đảo chiều

**Đặc điểm:**
- Theo xu hướng chính (D1)
- Chỉ vào lệnh khi TF nhỏ cùng chiều D1
- Lot size trung bình

**VÍ DỤ:**
```
D1_signal = +1 (BUY trend)
M5_signal = +1

→ MỞ lệnh S2_M5 BUY (cùng chiều!)

Nếu M5_signal = -1
→ BỎ QUA (ngược chiều D1)
```

---

#### Strategy 3: S3_NEWS (News Trading)

**Đọc từ:** Cột `news` (đã tách thành 14 biến)

**Điều kiện mở:**
- Signal hiện tại ≠ 0
- `news_level[tf]` ≥ MinNewsLevel (mặc định 20)
- `news_direction[tf]` = signal (cùng chiều)
- Timestamp thay đổi

**Điều kiện đóng:**
- **Luôn luôn:** Đóng khi **TF của nó** đảo chiều

**Đặc điểm:**
- Chỉ giao dịch khi có "tin tức"
- News càng mạnh → cơ hội càng lớn
- Lot size lớn (risk cao, reward cao)

**VÍ DỤ:**
```
TF = M1
signal = +1
news_level[0] = 30
news_direction[0] = +1

→ MỞ lệnh S3_M1 BUY
```

---

### 🎁 BONUS STRATEGY (Bổ sung)

**KHÔNG PHẢI STRATEGY RIÊNG!**
- Dùng chung **MAGIC với S3**
- 1 magic có thể có **nhiều lệnh**

**Điều kiện mở:**
```
FOR mỗi TF (0→6):
  if(news_level[tf] >= MinNewsLevelBonus &&
     news_level[tf] != 1 &&      // Loại bỏ cấp yếu
     news_level[tf] != 10 &&     // Loại bỏ cấp yếu
     news_direction[tf] != 0)

  → Mở BonusOrderCount lệnh (mặc định 2)
  → Lot = S3_lot × BonusLotMultiplier
  → Magic = g_ea.magic_numbers[tf][2] (GIỐNG S3)
```

**Điều kiện đóng:**
```
Khi M1 đảo chiều → CloseAllBonusOrders()
→ Đóng TẤT CẢ lệnh có magic = S3 (bao gồm cả BONUS)
```

**Đặc điểm:**
- Giao dịch cực ngắn (chỉ theo M1)
- Mở nhiều lệnh cùng lúc (2-5 lệnh/TF)
- Chốt lời nhanh theo M1

**VÍ DỤ:**
```
TF = H1
news_level[4] = 50 (rất mạnh!)
news_direction[4] = +1

→ Mở 2 lệnh BONUS_H1 BUY
→ Magic = 5878 (GIỐNG S3_H1)

Khi M1 đảo chiều:
→ Đóng cả 2 lệnh BONUS
→ Đóng luôn lệnh S3_H1 (cùng magic)
```

---

### 📊 DASHBOARD (Bảng điều khiển)

**15 dòng hiển thị trên chart:**

```
[BTCUSD] DA2 | 7TFx3S | D1:^ | $5000 DD:2.5% | 3/21
---------------------------------------------
TF    Sig   S1     S2     S3     P&L      News   Bonus
---------------------------------------------
M1    ^     1|0.10 -      -      +15.50   +30    2|0.10
M5    ^     -      -      -      +0.00    -20    -
M15   -     -      -      -      +0.00    0      -
M30   -     -      1|0.30 -      +25.00   +40    1|0.15
H1    ^     -      -      1|0.40 +50.00   0      -
H4    -     -      -      -      +0.00    0      -
D1    ^     -      1|0.50 -      +80.00   +50    3|0.25
---------------------------------------------
BONUS: M1,M30,D1 | Active | Last:12:34:56
NET:$170.50 | S1:2x$40 | S2:3x$105 | S3:1x$50 | 9/21
Exness | Lev:1:500 | 2s
```

**Giải thích:**

| Cột | Ý nghĩa |
|-----|---------|
| TF | Khung thời gian |
| Sig | Tín hiệu hiện tại (^ = BUY, v = SELL, - = NONE) |
| S1 | Lệnh S1: `số_lệnh\|lot` (VD: 1\|0.10 = 1 lệnh 0.10 lot) |
| S2 | Lệnh S2 |
| S3 | Lệnh S3 |
| P&L | Lãi/lỗ của TF này |
| News | Điểm NEWS (±10-70) |
| Bonus | Lệnh BONUS: `số_lệnh\|tổng_lot` |

**Dòng BONUS:**
- Hiển thị TF nào đang có lệnh BONUS
- Status: Active/Inactive
- Last: Thời gian mở lệnh BONUS cuối

**Dòng NET:**
- Tổng lãi/lỗ: $170.50
- Phân tích theo strategy: S1 2 lệnh lãi $40...
- 9/21: 9 lệnh đang mở / 21 lệnh tối đa

---

## 5. CẤU TRÚC CSDL - DỮ LIỆU TRUNG TÂM

### 📁 File CSDL: `SYMBOL_LIVE.json`

**Định dạng:** JSON Array (7 rows)

**Cấu trúc:** 7 TF × 6 columns

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
  ... (6 rows nữa)
]
```

### 📋 Ý nghĩa từng cột:

| # | Cột | Kiểu | Giá trị | SPY làm gì? | EA làm gì? |
|---|-----|------|---------|-------------|------------|
| 1 | `max_loss` | double | -0.50, -1.00... | Tính từ CSDL | Dùng tính stoploss |
| 2 | `timestamp` | long | 1730620800 | Lấy từ WT | So sánh tín hiệu mới |
| 3 | **`signal`** | **int** | **±1, 0** | **Đọc WT** | **S1+S2 đọc** |
| 4 | `pricediff` | double | ±2.50 | Tính giá mới - cũ | Tham khảo |
| 5 | `timediff` | int | 5 (phút) | Tính time mới - cũ | Tham khảo |
| 6 | **`news`** | **int** | **±10-70** | **SPY TÍNH** | **S3 đọc** |

### 🔑 2 CỘT QUAN TRỌNG NHẤT:

**CỘT 3: `signal` (Tín hiệu gốc)**
- Nguồn: 7 bot WT
- Giá trị: -1 (SELL), 0 (NONE), 1 (BUY)
- S1 + S2 dùng cột này

**CỘT 6: `news` (NEWS CASCADE)**
- Nguồn: SPY tính toán
- Giá trị: 0, ±10-70 (Category 1), ±1-7 (Category 2)
- S3 + BONUS dùng cột này

---

## 6. LUỒNG HOÀN CHỈNH - TỪ ĐẦU ĐẾN CUỐI

### ⏱️ Timeline chi tiết (1 chu kỳ 2 giây):

```
═══════════════════════════════════════════════════════════════
GIÂY 0.0: 7 BOT WT
═══════════════════════════════════════════════════════════════
M1_WT:  Phân tích nến → signal = +1 → Ghi GlobalVariable
M5_WT:  Phân tích nến → signal = +1 → Ghi GlobalVariable
M15_WT: Phân tích nến → signal = 0  → Ghi GlobalVariable
...
D1_WT:  Phân tích nến → signal = +1 → Ghi GlobalVariable

───────────────────────────────────────────────────────────────
GIÂY 0.5: BOT SPY (D1)
───────────────────────────────────────────────────────────────
[1] Đọc 7 GlobalVariables:
    M1_signal  = +1
    M5_signal  = +1
    M15_signal = 0
    ...

[2] Tính PriceDiff, TimeDiff, MaxLoss

[3] TÍNH NEWS CASCADE:
    M1_price_cũ  = 50000.0
    M1_price_live = 50003.0
    live_diff = 3.0 USD
    
    L1: 3.0 > 2.5 ✓ → news[M1] = +10
    L2: M5→M1 chưa cascade → news[M5] = 0
    ...

[4] GHI 3 FILE JSON:
    DataAutoOner/BTCUSD_LIVE.json
    DataAutoOner2/BTCUSD_LIVE.json
    DataAutoOner3/BTCUSD_LIVE.json

═══════════════════════════════════════════════════════════════
GIÂY 1.0: BOT EA (M1)
═══════════════════════════════════════════════════════════════
[1] ĐỌC FILE:
    ReadCSDLFile()
    → Đọc DataAutoOner2/BTCUSD_LIVE.json
    → Parse JSON thành 7 rows

[2] TÁCH NEWS:
    Row 0: news = +10
    → news_level[0] = 10
    → news_direction[0] = +1

[3] KIỂM TRA SIGNAL THAY ĐỔI:
    TF = M1 (0)
    signal_cũ = 0
    signal_mới = +1
    → CÓ THAY ĐỔI!

[4] MỞ LỆNH S1:
    ProcessS1Strategy(0)
    → Signal = +1
    → OrderSend(BUY, 0.11 lot)
    → Ticket #12345

[5] MỞ LỆNH S2:
    ProcessS2Strategy(0)
    → Signal = +1
    → Trend D1 = +1 (KHỚP!)
    → OrderSend(BUY, 0.12 lot)
    → Ticket #12346

[6] KIỂM TRA S3:
    ProcessS3Strategy(0)
    → news_level[0] = 10
    → 10 < 20 (MinNewsLevel)
    → BỎ QUA (NEWS quá yếu)

[7] KIỂM TRA BONUS:
    ProcessBonusNews()
    → news_level[0] = 10
    → 10 < 20 (MinNewsLevelBonus)
    → BỎ QUA

───────────────────────────────────────────────────────────────
GIÂY 2.0: SPY CẬP NHẬT NEWS
───────────────────────────────────────────────────────────────
DetectCASCADE_New()
→ Tính lại NEWS cho 7 TF
→ Ghi lại 3 file

───────────────────────────────────────────────────────────────
GIÂY 3.0: EA KIỂM TRA STOPLOSS + DASHBOARD
───────────────────────────────────────────────────────────────
CheckStoplossAndTakeProfit()
→ Quét tất cả lệnh
→ Nếu lỗ > threshold → đóng

UpdateDashboard()
→ Cập nhật bảng điều khiển

═══════════════════════════════════════════════════════════════
... LẶP LẠI MỖI 2 GIÂY
═══════════════════════════════════════════════════════════════
```

---

## 7. CRITICAL BUG ĐÃ SỬA

### ⚠️ BUG NGHIÊM TRỌNG: NEWS không bao giờ được parse!

**Ngày phát hiện:** 2025-01-03

**Vấn đề:**

Cột `news` là cột CUỐI CÙNG trong JSON:
```json
{"max_loss":0.5,"timestamp":1730620800,"signal":1,"pricediff":2.5,"timediff":5,"news":30}
```

**Code CŨ (SAI):**
```cpp
int end_pos = (comma > 0 && comma < bracket) ? comma : bracket;
if(end_pos > 0) {
    news = StringToInteger(...);
}
```

**Tại sao SAI:**
1. NEWS là cột cuối → **KHÔNG có dấu phẩy sau**
2. `StringFind(temp, ",")` = `-1` (không tìm thấy)
3. `StringFind(temp, "}")` có thể = `-1` hoặc sai vị trí
4. → `end_pos = -1`
5. → `if(end_pos > 0)` = **FALSE**
6. → **KHÔNG BAO GIỜ CHẠY VÀO ĐOẠN PARSE!**

**Hậu quả:**
- NEWS luôn = 0
- S3 strategy **KHÔNG BAO GIỜ CHẠY** (vì NEWS = 0 < 20)
- BONUS strategy **KHÔNG BAO GIỜ CHẠY** (vì NEWS = 0 < 20)
- Dashboard hiển thị đúng... giá trị sai (0)

**Code MỚI (ĐÚNG):**
```cpp
int end_pos = StringLen(temp);  // Mặc định = độ dài string
if(comma > 0 && bracket > 0) {
    end_pos = (comma < bracket) ? comma : bracket;
} else if(bracket > 0) {
    end_pos = bracket;
}
// Luôn có end_pos > 0 → luôn parse được!
```

**Cách phát hiện:**
- So sánh code EA với code SPY
- SPY parse đúng → EA học theo
- **Thank you for the hint!** 🙏

**File đã sửa:**
- MT4: `MQL4/Experts/MT4_Eas_Smf_Oner_V2.mq4` (commit a7eb5bd)
- MT5: `MQL5/Experts/MT5_EAs_MTF_ONER_V2.mq5` (commit 2497bcb)

---

## 📝 TÓM TẮT NHANH

### Hệ thống làm gì?

1. **7 BOT WT** → Tạo tín hiệu BUY/SELL
2. **BOT SPY** → Thu thập tín hiệu + Tính NEWS → Ghi file
3. **BOT EA** → Đọc file → Mở lệnh tự động

### Dữ liệu chảy như thế nào?

```
WT → GlobalVariable → SPY → JSON File → EA → Lệnh giao dịch
```

### 2 cột quan trọng nhất trong CSDL?

1. **`signal`** (±1, 0) → S1 + S2 đọc
2. **`news`** (±10-70) → S3 + BONUS đọc

### 3 strategies + 1 BONUS là gì?

1. **S1:** Tín hiệu từ 0 → ±1 (binary)
2. **S2:** Tín hiệu cùng chiều D1 (trend)
3. **S3:** Tín hiệu + NEWS mạnh (news trading)
4. **BONUS:** Nhiều lệnh khi NEWS cực mạnh (volume boost)

### Tối đa bao nhiêu lệnh?

**21 lệnh cơ bản:**
- 7 TF × 3 strategies = 21

**+ BONUS:**
- Mỗi TF có thể thêm 2-5 lệnh
- Tổng cộng: ~40-50 lệnh cùng lúc

---

**📅 Cập nhật:** 2025-01-03  
**📧 Support:** Check code comments for details  
**🔧 Version:** 2.0 (After NEWS bug fix)
