# SUPER SPY BOT V2 - Multi-Timeframe Signal Monitor

## 📋 TỔNG QUAN

**File**: `Super_Spy7TF_V2.mq4`
**Phiên bản**: V2 (Refactored 2025)
**Nền tảng**: MetaTrader 4 (MQL4)
**Chức năng**: Giám sát tín hiệu WT trên 7 timeframes + Phát hiện NEWS CASCADE

---

## 🎯 CHỨC NĂNG CHÍNH

### 1. **Multi-Timeframe Monitoring (7 TF)**
- M1, M5, M15, M30, H1, H4, D1
- Đọc tín hiệu từ WallStreet CRYPTO Indicator
- Tự động tính PriceDiff (USD) và TimeDiff (phút)

### 2. **NEWS CASCADE Detection**
Phát hiện đột phá tin tức với 2 categories:

#### **Category 1: EA Trading (Score 10-70)**
- Điều kiện **CỰC KỲ NGHIÊM NGẶT** cho bot tự động
- USD thresholds: 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5
- Time check: Signal đang hình thành trong **candle hiện tại của TF cao nhất**
- Cascade validation: Kiểm tra chuỗi timestamp liên kết
- 7 levels (L1-L7):
  - L1 (M1): Score ±10
  - L2 (M5→M1): Score ±20
  - L3 (M15→M5→M1): Score ±30
  - ...
  - L7 (D1→...→M1): Score ±70

#### **Category 2: User Reference (Score 1-7)**
- Điều kiện **LINH HOẠT** cho trader tham khảo
- USD threshold: > 0 (bất kỳ chuyển động nào)
- Time check: Thời gian tươi từ M1 (2, 4, 6, 8, 10, 12, 14 phút)
- Cascade validation: Giống Category 1
- 7 levels (L1-L7): Score ±1 đến ±7

**Priority**: Category 1 check trước → Category 2 chỉ khi Category 1 = 0

### 3. **LIVE Mode (Independent)**
- Chạy độc lập mỗi **2 giây** (giây chẵn)
- Không phụ thuộc vào WT indicator
- Update NEWS real-time

### 4. **Smart Reset System**
- **Startup Reset**: 1 phút sau khi MT4 khởi động (1 lần duy nhất)
- **Midnight Reset**: 0h hàng ngày
- **Health Check**: 8h và 16h (tự động reset nếu bot bị treo)

---

## 📊 DASHBOARD (4 DÒNG)

### Layout trên chart:

```
DÒNG 1: [BTCUSD] SPY | CSDL1: Active | 7TF | USD:1.00 pip:0.00001
DÒNG 2: [M1|BUY|+2.50|5m] [M5|SELL|-1.20|10m] [M15|BUY|+3.00|15m]
DÒNG 3: [M30|NONE|+0.00|0m] [H1|BUY|+5.00|60m] [H4|SELL|-2.00|120m]
DÒNG 4: [D1|BUY|+10.00|1440m] | LIVE: 65432.50 (+3.50 USD, 8m) | NEWS:+16
                                                                    ^^^^^^^^
                                                                  MÀU VÀNG GOLD
```

**Màu sắc xen kẽ**:
- Dòng 1, 3: Trắng
- Dòng 2, 4: Xanh (DodgerBlue)
- NEWS: Vàng Gold ⭐

**Thông tin hiển thị**:
- **TF|Signal|PriceDiff|TimeDiff**: Đầy đủ cho mỗi timeframe
- **LIVE price**: Giá real-time hiện tại
- **USD diff**: Chênh lệch USD so với M1 signal
- **Time diff**: Thời gian (phút) từ M1 signal
- **NEWS**: Score CASCADE (nổi bật màu vàng)

---

## 🗂️ DATABASE STRUCTURE

### CSDL1 (Main Database) - 10 Columns

| Column | Tên | Loại | Mô tả |
|--------|-----|------|-------|
| 1 | timeframe | String | "M1", "M5", ..., "D1" |
| 2 | period | Int | 1, 5, 15, 30, 60, 240, 1440 |
| 3 | signal | Int | -1 (SELL), 0 (NONE), +1 (BUY) |
| 4 | price | Double | Giá entry |
| 5 | cross | Long | Timestamp TF trước (cross reference) |
| 6 | timestamp | Long | Timestamp signal |
| 7 | pricediff | Double | Chênh lệch giá (USD) |
| 8 | timediff | Int | Chênh lệch thời gian (phút) |
| 9 | news_result | Int | NEWS CASCADE score |
| 10 | max_loss | Double | Max loss (reserved) |

**Files**:
- `DataAutoOner/SYMBOL.json` - Main data
- `DataAutoOner/SYMBOL_LIVE.json` - Live data
- `DataAutoOner3/SYMBOL.json` - Strategy data

---

## ⚙️ PARAMETERS (Input)

```mql4
// Basic
input int    Timer = 1;                    // Timer interval (giây)
input int    Retry = 3;                    // Retry attempts
input string TargetSymbol = "";            // Symbol (rỗng = chart hiện tại)
input string DataFolder = "DataAutoOner\\";

// Reset System
input bool   EnableHealthCheck = true;     // Health check 8h & 16h
input bool   EnableMidnightReset = true;   // Reset 0h hàng ngày
input bool   EnableStartupReset = true;    // Reset 1 phút sau MT4 start

// Signal Processing
input bool   ProcessSignalOnOddSecond = true;  // Xử lý giây lẻ (tránh conflict)

// NEWS CASCADE
input double NewsBaseLiveDiff = 2.5;       // L1 threshold (USD)
input double NewsLiveDiffStep = 0.5;       // Tăng mỗi level (+0.5 USD)
input int    NewsBaseTimeMinutes = 2;      // Category 2 base (2 phút)
input bool   EnableCategoryEA = true;      // Enable Category 1
input bool   EnableCategoryUser = true;    // Enable Category 2
```

---

## 🔧 CÀI ĐẶT

### Bước 1: Copy file
```
MQL4/Indicators/Super_Spy7TF_V2.mq4
```

### Bước 2: Compile trong MetaEditor
- Mở MetaEditor (F4)
- Compile file (F7)
- Không có lỗi → OK

### Bước 3: Attach vào chart
1. Mở chart symbol (BTCUSD, XAUUSD, etc.)
2. Insert → Indicators → Custom → Super_Spy7TF_V2
3. Cấu hình parameters (hoặc để default)
4. OK

### Bước 4: Requirement
**QUAN TRỌNG**: Cần có **7 charts cùng symbol** (M1, M5, M15, M30, H1, H4, D1) với:
- WallStreet CRYPTO Indicator đã chạy
- GlobalVariables có sẵn tín hiệu

---

## 📈 TIMING SCHEDULE

```
Giây 0 (CHẴN):  UpdateLiveNEWS() + Reset checks + Dashboard update
Giây 1 (LẺ):    ProcessAllSignals() (7 TF)
Giây 2 (CHẴN):  UpdateLiveNEWS() + Reset checks + Dashboard update
Giây 3 (LẺ):    ProcessAllSignals() (7 TF)
...
```

**Tại sao giây lẻ/chẵn?**
- **Giây lẻ**: Process WT signals (tránh conflict với WT indicator chạy giây chẵn)
- **Giây chẵn**: NEWS + Dashboard + Maintenance

---

## 🚨 LOGS & ALERTS

### Terminal Logs (Expert Tab)

**NEWS Detection** (L3+ only):
```
2025.10.30 14:35:22 | NEWS XAUUSD L3: BUY | Score:30
2025.10.30 15:20:45 | NEWS BTCUSD L5: SELL | Score:-50
```

**Reset Logs**:
```
StartupReset: XAUUSD | 1 min after MT4 start
MidnightReset: XAUUSD | New day started
HealthCheck: XAUUSD STUCK | Auto-reset triggered
SmartTFReset: XAUUSD | 7 charts reset
```

**Alert** (khi bot treo):
```
Bot SPY stuck - Auto reset!
```

---

## 🔍 TROUBLESHOOTING

### Bot không detect signals?
1. Kiểm tra WallStreet Indicator đã chạy chưa
2. Check GlobalVariables: `Tools → Global Variables`
3. Verify 7 charts cùng symbol đã mở

### Dashboard không hiện?
1. Check Objects: `Ctrl+B` → Tìm "SPY_Dashboard_*"
2. Dashboard ở Y=120px (có thể bị che bởi indicator khác)
3. Thử zoom out chart

### NEWS không trigger?
1. **Category 1**: Cần USD breakthrough lớn (≥$2.5) + cascade alignment + signal đang forming
2. **Category 2**: Cần cascade alignment + trong time window
3. Check log terminal xem có detect không

### Bot bị treo?
- Health Check tự động reset lúc 8h/16h nếu phát hiện treo
- Hoặc manual restart indicator

---

## 💾 SYMBOL ISOLATION

**Multi-bot safe**: Chạy nhiều bot cùng lúc không conflict

### GlobalVariables (Symbol-specific):
```
XAUUSD_StartupResetDone
XAUUSD_StartupInitTime
XAUUSD_M1_SignalType1
XAUUSD_M1_LastSignalTime
... (7 TFs × 2 = 14 variables)
```

### Files (Symbol-specific):
```
DataAutoOner/XAUUSD.json
DataAutoOner/BTCUSD.json
DataAutoOner/GBPUSD.json
```

**Kết quả**: 3 bot trên 3 symbols hoạt động độc lập 100%

---

## 📚 ALGORITHM DETAILS

### PriceDiff Normalization (USD)
Tất cả symbols normalize về **GOLD standard**:
```mql4
double GetUSDValue(string symbol, double price_diff) {
    double gold_point = 0.01;  // XAUUSD standard point
    double symbol_point = MarketInfo(symbol, MODE_POINT);
    double pip_value = MarketInfo(symbol, MODE_TICKVALUE);

    if(symbol_point <= 0 || pip_value <= 0) return 0.0;

    double price_in_pips = price_diff / symbol_point;
    double usd_value = price_in_pips * pip_value;
    double normalized = usd_value * (gold_point / symbol_point);

    return MathAbs(normalized);
}
```

### CASCADE Validation Logic

**Category 1** (EA - Strict):
```mql4
// L3 example: M15→M5→M1
if(m15_signal != 0 && m5_signal != 0 && m1_signal != 0 &&
   m1_signal == m5_signal && m5_signal == m15_signal) {  // Same direction

    if(m15_cross == m5_time && m5_cross == m1_time) {  // Cascade linkage

        if(live_usd_diff > 3.5 &&  // USD threshold
           IsWithinOneCandle(2, m15_time)) {  // M15 signal forming in M15 candle

            result = m15_signal * 30;  // Score ±30
        }
    }
}
```

**Category 2** (User - Relaxed):
```mql4
// L3 example: Same cascade but different time check
if(/* same cascade validation */) {
    int l3_time_limit = 3 * NewsBaseTimeMinutes * 60;  // 3 × 2 × 60 = 360s = 6min

    if(live_usd_diff > 0 &&  // Any USD movement
       live_time_diff < l3_time_limit) {  // Within 6 minutes from M1

        result = m15_signal * 3;  // Score ±3
    }
}
```

---

## 📝 VERSION HISTORY

### V2 (2025) - Major Refactor
- ✅ NEWS CASCADE với 2 categories
- ✅ LIVE mode độc lập
- ✅ Dashboard 4 dòng với NEWS highlight vàng
- ✅ Smart reset system (3 loại)
- ✅ Symbol isolation (multi-bot safe)
- ✅ Clean logging
- ✅ PriceDiff USD normalization

### Key Commits:
- `c3e7d78`: Fix CASCADE candle checks (critical bug)
- `87cae01`: Optimize logs
- `e05bee0`: Add timestamp to NEWS log
- `0a56173`: Dashboard redesign
- `da0c23a`: LIVE format fix
- `ccbbf77`: NEWS gold color at end

---

## 🎯 BEST PRACTICES

### Khi chạy Production:
1. ✅ Enable tất cả reset systems
2. ✅ Để Timer = 1 (optimal)
3. ✅ ProcessSignalOnOddSecond = true (tránh conflict)
4. ✅ Mở đủ 7 charts cho mỗi symbol
5. ✅ Monitor logs định kỳ

### Khi test NEWS:
1. Theo dõi lịch tin tức (NFP, FOMC, CPI)
2. Chạy bot trước 5 phút
3. Check log sau tin 15-30 phút
4. Verify cascade alignment trong file JSON

### Performance:
- RAM: ~10-20MB per symbol
- CPU: Minimal (chỉ 1-2% spike mỗi giây)
- Disk: ~50KB per symbol (JSON files)

---

## 🔗 LINKS & RESOURCES

- **GitHub**: [Multi-Trading-Bot-Oner_2025](https://github.com/dungoner/Multi-Trading-Bot-Oner_2025)
- **Branch**: `claude/bot-spy-v2-ok`
- **Indicator**: WallStreet CRYPTO Indicator by FXautomater

---

## 👨‍💻 DEVELOPER NOTES

### Code Structure:
```
Section 1:  User Inputs (37 lines)
Section 2:  Data Structures (3 structs)
Section 3:  Core Functions (Signal processing)
Section 4:  News CASCADE Detection
Section 5:  Dashboard (PrintDashboard)
Section 6:  Reset System (3 functions)
Section 7:  Timer & Main Loop (OnTimer)
Section 8:  Cleanup (OnDeinit)
```

### Important Functions:
- `ProcessSignalForTF()`: Process 1 TF signal
- `DetectCASCADE_New()`: NEWS detection logic
- `UpdateLiveNEWS()`: Live NEWS update
- `PrintDashboard()`: Dashboard rendering
- `SmartTFReset()`: Reset all charts

---

## ⚠️ DISCLAIMER

Bot này là **CÔNG CỤ HỖ TRỢ PHÂN TÍCH**, không phải tư vấn tài chính.

- Luôn test trên demo account trước
- Verify signals thủ công trước khi trade
- Risk management là trách nhiệm trader
- Past performance không đảm bảo tương lai

---

**Last Updated**: 2025-10-30
**Author**: Dungoner Team
**Generated with**: Claude Code 🤖
