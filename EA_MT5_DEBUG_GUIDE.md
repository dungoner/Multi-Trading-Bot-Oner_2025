# 🐛 MT5 EA DEBUG GUIDE - HƯỚNG DẪN DEBUG CHI TIẾT

**File**: `_MT5_EAs_MTF ONER_V2.mq5`
**Version**: API_V2 (MT5) - Fixed
**Date**: 2025-11-05

---

## 📖 MỤC LỤC

1. [Cách đọc log MT5](#1-cách-đọc-log-mt5)
2. [Debug messages quan trọng](#2-debug-messages-quan-trọng)
3. [Flow chart logic EA](#3-flow-chart-logic-ea)
4. [Debug từng function](#4-debug-từng-function)
5. [Tools hỗ trợ debug](#5-tools-hỗ-trợ-debug)
6. [Checklist nhanh](#6-checklist-nhanh)

---

## 1. CÁCH ĐỌC LOG MT5

### Mở Experts Tab
1. **MT5 Terminal** → **Toolbox** (Alt+R)
2. Tab **Experts**
3. Kéo xuống để xem log mới nhất

### Phân loại messages

| Prefix | Ý nghĩa | Mức độ |
|--------|---------|--------|
| `[INIT]` | Khởi động EA | INFO |
| `[RESET]` | Reset flags/state | INFO |
| `[OPEN]` | Mở lệnh thành công | SUCCESS |
| `[CLOSE]` | Đóng lệnh | INFO |
| `[DEBUG]` | Chi tiết debug (chỉ khi DebugMode=true) | DEBUG |
| `[ERROR]` | Lỗi nghiêm trọng | ERROR |
| `[WARNING]` | Cảnh báo | WARNING |
| `[ORDER_FAIL]` | Lệnh thất bại | ERROR |
| `[CLOSE_FAIL]` | Đóng lệnh thất bại | ERROR |
| `[READ]` | Đọc file CSDL | DEBUG |
| `[RESTORE]` | Khôi phục flags khi restart | INFO |

---

## 2. DEBUG MESSAGES QUAN TRỌNG

### 2.1. OnInit() - Khởi động

**SUCCESS**:
```
[INIT] LTCUSD | SL:L1 News:7TF(M1:+12BUY) Trend:BUY | Lot:0.10-0.12 | TF:5 S:3 | Folder:DA2 Master:M5-D1 Magic:501-721
[RESET] All position flags (21) & state vars reset to 0
[RESTORE] Scanned 0 orders | Restored 0 flags | Cleaned 0 zombie flags
```

**FAILED**:
```
[ERROR] CODE:... CONTEXT:InitializeSymbolRecognition DETAILS:...
```
→ Symbol không hợp lệ hoặc không tồn tại

**Phân tích INIT message**:
```
[INIT] LTCUSD | SL:L1 News:7TF(M1:+12BUY) Trend:BUY | Lot:0.10-0.12 | TF:5 S:3 | Folder:DA2 Master:M5-D1 Magic:501-721
       ^^^^^^   ^^^^^ ^^^^^^^^^^^^^^^^   ^^^^^^^^^   ^^^^^^^^^^^^   ^^^^^ ^^^^  ^^^^^^^^^^^ ^^^^^^^^^ ^^^^^^^^^^^^^
       Symbol   SL    NEWS từ CSDL       TREND D1    Lot min-max    TF  Strat   CSDL folder  Mode     Magic range
```

- **SL:L1** → Stoploss mode Layer1 (max_loss from CSDL)
- **News:7TF(M1:+12BUY)** → M1 có news level 12, direction BUY
- **Trend:BUY** → D1 trend = BUY (signal D1 = 1)
- **Lot:0.10-0.12** → Min lot (M1 S1) to Max lot (D1 S3)
- **TF:5** → 5 timeframes enabled
- **S:3** → 3 strategies enabled
- **Folder:DA2** → Đang dùng DataAutoOner2
- **Magic:501-721** → Magic number range

---

### 2.2. OnTimer() - Trading Logic

**EVEN seconds (0,2,4,6,8...)**: Trading core

```
[DEBUG] Mapped 7 TF | signal[0]=1 trend_d1=1 news[M1]=12 (split to 14 vars: 7 level + 7 dir)
[DEBUG] NEWS 14 vars: M1[12/1] M5[15/1] M15[20/-1] M30[0/0] H1[25/1] H4[30/1] D1[11/1]
```
→ CSDL đã đọc thành công, signal và news được map

**ODD seconds (1,3,5,7,9...)**: Auxiliary

```
[DEBUG] SL Check: 3 positions scanned
[DEBUG] Dashboard updated
```

---

### 2.3. Strategy Processing

**S1 (HOME/BASIC)**:
```
[DEBUG] S1_NEWS: M5 NEWS=15 < Min=20, SKIP
```
→ NEWS level < threshold, không mở lệnh

```
>>> [OPEN] S1_BASIC TF=M5 | #12345678 BUY 0.10 @1850.50 | Sig=1 | Timestamp:1730800000 <<<
```
→ Thành công!

**S2 (TREND)**:
```
[DEBUG] S2_TREND: Signal=1 != Trend=0, skip
```
→ Signal không khớp Trend D1, không mở

```
>>> [OPEN] S2_TREND TF=H1 | #12345679 BUY 0.11 @1850.55 | Sig=+1 Trend:UP Mode:AUTO | Timestamp:1730800020 <<<
```
→ Thành công!

**S3 (NEWS)**:
```
[DEBUG] S3_NEWS: TF1 NEWS=18 < 20, skip
```
→ NEWS level < MinNewsLevelS3

```
>>> [OPEN] S3_NEWS TF=H4 | #12345680 SELL 0.12 @1850.45 | Sig=-1 News=-25↓ | Timestamp:1730800040 <<<
```
→ Thành công!

---

### 2.4. Close Logic

```
[CLOSE] SIGNAL_CHANGE | #12345678 closed successfully
```
→ Đóng lệnh do signal thay đổi

```
[CLOSE_FAIL] SIGNAL_CHANGE #12345678 Err:4108 (Invalid ticket) - Skip, EA continues
```
→ Ticket không tồn tại (đã đóng hoặc sai)

```
[SL_HIT] Strategy S2_M5 | #12345679 closed | Loss: -$1.05
```
→ Stoploss kích hoạt

---

### 2.5. Error Messages

**Order failed**:
```
[ORDER_FAIL] S2_M5 Err:131 (Retry 0.01 lot)
[ORDER_FAIL] S2_M5_Min Err:134 - Skip, EA continues
```
→ Lỗi 131 (lot size), thử lại 0.01 → Lỗi 134 (not enough money)

**CSDL read failed**:
```
[WARNING] All read attempts failed. Using old data.
```
→ File không đọc được, dùng data cũ

---

## 3. FLOW CHART LOGIC EA

### OnInit() Flow

```
START OnInit()
    ↓
InitializeSymbolRecognition()
    ├─ Success → Continue
    └─ Failed → INIT_FAILED
    ↓
BuildCSDLFilename() → "DataAutoOner2/LTCUSD_LIVE.json"
    ↓
ReadCSDLFile() → Parse 7 rows
    ↓
GenerateMagicNumbers() → 21 magic numbers (7 TF × 3 Strat)
    ↓
InitializeLotSizes() → 21 lot sizes
    ↓
InitializeLayer1Thresholds() → 21 SL thresholds
    ↓
MapCSDLToEAVariables() → trend_d1, news_level[7], news_direction[7]
    ↓
Reset position_flags[7][3] = 0
    ↓
RestoreOrCleanupPositions() → Scan existing orders
    ↓
EventSetTimer(1) → Start 1-second timer
    ↓
INIT SUCCESS
```

---

### OnTimer() Flow (EVEN seconds)

```
OnTimer() called every 1 second
    ↓
Check: current_second % 2 == 0? (EVEN)
    ├─ NO → Skip to ODD logic
    └─ YES → EVEN logic (TRADING CORE)
         ↓
    ReadCSDLFile() → Re-read JSON every EVEN second
         ↓
    MapCSDLToEAVariables() → Update trend_d1, news, etc.
         ↓
    FOR each TF (0-6):
         ↓
    ┌─ STEP 1: FAST CLOSE by M1 (if tf == 0)
    │   ├─ S1_CloseByM1? → CloseS1OrdersByM1()
    │   ├─ S2_CloseByM1? → CloseS2OrdersByM1()
    │   └─ EnableBonusNews? → CloseAllBonusOrders()
    │
    ├─ STEP 2: NORMAL CLOSE by TF signal
    │   └─ HasValidS2BaseCondition(tf)?
    │       ├─ YES → CloseAllStrategiesByMagicForTF(tf)
    │       └─ NO → Skip close
    │
    ├─ STEP 3: OPEN new orders (if TF enabled)
    │   └─ IsTFEnabled(tf)?
    │       ├─ YES:
    │       │   ├─ S1_HOME? → ProcessS1Strategy(tf)
    │       │   ├─ S2_TREND? → ProcessS2Strategy(tf)
    │       │   └─ S3_NEWS? → ProcessS3Strategy(tf)
    │       └─ NO → Skip
    │
    ├─ STEP 4: BONUS NEWS (if enabled)
    │   └─ ProcessBonusNews()
    │
    └─ STEP 5: Update baseline
        ├─ signal_old[tf] = csdl_rows[tf].signal
        └─ timestamp_old[tf] = csdl_rows[tf].timestamp

    END LOOP
```

---

### ProcessS2Strategy() Flow (Example)

```
ProcessS2Strategy(tf)
    ↓
Get current_signal from csdl_rows[tf].signal
    ↓
Determine trend_to_follow:
    ├─ S2_TrendMode == FOLLOW_D1? → trend_to_follow = trend_d1
    ├─ S2_TrendMode == FORCE_BUY? → trend_to_follow = 1
    └─ S2_TrendMode == FORCE_SELL? → trend_to_follow = -1
    ↓
Check: current_signal == trend_to_follow?
    ├─ NO → Print debug "skip" → RETURN
    └─ YES → Continue
         ↓
    Check: position_flags[tf][1] == 0?
         ├─ NO → Already have order → RETURN
         └─ YES → Can open
              ↓
         RefreshRates()
              ↓
         IF signal == 1:
              OrderSendSafe(tf, Symbol, OP_BUY, lot, Ask, ...)
              ├─ Success → position_flags[tf][1] = 1
              └─ Failed → position_flags[tf][1] = 0
         ELSE IF signal == -1:
              OrderSendSafe(tf, Symbol, OP_SELL, lot, Bid, ...)
              ├─ Success → position_flags[tf][1] = 1
              └─ Failed → position_flags[tf][1] = 0
```

---

### HasValidS2BaseCondition() Logic

```
HasValidS2BaseCondition(tf)
    ↓
Get signal_old, signal_new, timestamp_old, timestamp_new
    ↓
Check ALL conditions:
    ├─ signal_old != signal_new? (Signal CHANGED)
    ├─ signal_new != 0? (Not FLAT)
    ├─ timestamp_old < timestamp_new? (Timestamp UPDATED)
    └─ (timestamp_new - timestamp_old) > 15? (At least 15 seconds difference)
         ↓
    ALL TRUE → return TRUE (Can process)
    ANY FALSE → return FALSE (Skip)
```

**Why 15 seconds?**
- Prevent acting on same signal multiple times
- SPY Bot writes CSDL every ~10 seconds
- 15 seconds ensures fresh signal

---

## 4. DEBUG TỪNG FUNCTION

### 4.1. Debug ReadCSDLFile()

**Thêm debug prints** (tạm thời):

```mql5
void ReadCSDLFile() {
    Print("[DEBUG_READ] Starting ReadCSDLFile()");
    Print("[DEBUG_READ] Filename: ", g_ea.csdl_filename);

    bool success = TryReadFile(g_ea.csdl_filename, true);

    Print("[DEBUG_READ] Result: ", success ? "SUCCESS" : "FAILED");

    if(success) {
        Print("[DEBUG_READ] M1 signal: ", g_ea.csdl_rows[0].signal);
        Print("[DEBUG_READ] M1 timestamp: ", g_ea.csdl_rows[0].timestamp);
    }
}
```

**Kiểm tra**:
1. Filename đúng không?
2. File có tồn tại không? (dùng FileIsExist())
3. JSON parse thành công không?

---

### 4.2. Debug ProcessS2Strategy()

**Thêm prints**:

```mql5
void ProcessS2Strategy(int tf) {
    int current_signal = g_ea.csdl_rows[tf].signal;
    int trend_to_follow = g_ea.trend_d1; // Simplified

    Print("[DEBUG_S2] TF=", G_TF_NAMES[tf],
          " Signal=", current_signal,
          " Trend=", trend_to_follow,
          " Flag=", g_ea.position_flags[tf][1]);

    if(current_signal != trend_to_follow) {
        Print("[DEBUG_S2] SKIP: Signal != Trend");
        return;
    }

    if(g_ea.position_flags[tf][1] == 1) {
        Print("[DEBUG_S2] SKIP: Flag already 1");
        return;
    }

    Print("[DEBUG_S2] READY TO OPEN");
    // ... rest of logic
}
```

---

### 4.3. Debug OrderSendSafe()

**Check ticket return**:

```mql5
int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, lot, Ask, 3, "S2_M5", magic, clrBlue);

Print("[DEBUG_ORDER] OrderSendSafe returned: ", ticket);
Print("[DEBUG_ORDER] GetLastError: ", GetLastError());

if(ticket > 0) {
    Print("[DEBUG_ORDER] SUCCESS");
} else {
    Print("[DEBUG_ORDER] FAILED - Check Experts log for [ORDER_FAIL]");
}
```

---

## 5. TOOLS HỖ TRỢ DEBUG

### 5.1. Script tạo CSDL test file

**File**: `Create_Test_CSDL.mq5` (Script)

```mql5
//+------------------------------------------------------------------+
//| Script to create test CSDL file for EA                          |
//+------------------------------------------------------------------+
#property copyright "ONER"
#property version   "1.00"
#property script_show_inputs

input string SymbolName = "LTCUSD";  // Symbol name

void OnStart() {
    string filename = "DataAutoOner2\\" + SymbolName + "_LIVE.json";

    long current_time = TimeCurrent();

    string json = "{\n";
    json += "  \"M1\": [10.5, " + IntegerToString(current_time) + ", 1, 0.5, 5, 12],\n";
    json += "  \"M5\": [10.5, " + IntegerToString(current_time) + ", 1, 0.5, 5, 15],\n";
    json += "  \"M15\": [10.5, " + IntegerToString(current_time) + ", -1, 0.5, 5, -20],\n";
    json += "  \"M30\": [10.5, " + IntegerToString(current_time) + ", 0, 0.5, 5, 0],\n";
    json += "  \"H1\": [10.5, " + IntegerToString(current_time) + ", 1, 0.5, 5, 25],\n";
    json += "  \"H4\": [10.5, " + IntegerToString(current_time) + ", 1, 0.5, 5, 30],\n";
    json += "  \"D1\": [10.5, " + IntegerToString(current_time) + ", 1, 0.5, 5, 11]\n";
    json += "}\n";

    int handle = FileOpen(filename, FILE_WRITE|FILE_TXT|FILE_ANSI);
    if(handle != INVALID_HANDLE) {
        FileWriteString(handle, json);
        FileClose(handle);
        Print("✅ Created test file: ", filename);
        Print("Current timestamp: ", current_time);
    } else {
        Print("❌ Failed to create file: ", filename);
        Print("Error: ", GetLastError());
    }
}
```

**Cách dùng**:
1. Compile script
2. Attach to chart
3. Run → Tạo file test với timestamp hiện tại

---

### 5.2. Script kiểm tra Position Flags

**File**: `Check_Position_Flags.mq5` (Script)

```mql5
//+------------------------------------------------------------------+
//| Script to check EA's position flags                             |
//+------------------------------------------------------------------+
#property copyright "ONER"
#property version   "1.00"

// NOTE: This requires access to g_ea struct (not possible from script)
// Use this as TEMPLATE to add debug in EA code

void OnStart() {
    Print("=== POSITION FLAGS STATUS ===");

    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
    string strat_names[3] = {"S1", "S2", "S3"};

    // Example: Print from EA's OnTimer()
    /*
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            if(g_ea.position_flags[tf][s] == 1) {
                Print(tf_names[tf], "_", strat_names[s], " = 1 (Order exists)");
            }
        }
    }
    */

    Print("Total positions: ", PositionsTotal());

    for(int i = 0; i < PositionsTotal(); i++) {
        if(PositionGetTicket(i) > 0) {
            Print("Position #", i, ": ",
                  "Ticket=", PositionGetInteger(POSITION_TICKET),
                  " Magic=", PositionGetInteger(POSITION_MAGIC),
                  " Type=", PositionGetInteger(POSITION_TYPE) == 0 ? "BUY" : "SELL",
                  " Lots=", PositionGetDouble(POSITION_VOLUME),
                  " Profit=", PositionGetDouble(POSITION_PROFIT));
        }
    }
}
```

---

### 5.3. Indicator hiển thị CSDL data

**File**: `Display_CSDL_Data.mq5` (Indicator)

```mql5
//+------------------------------------------------------------------+
//| Indicator to display CSDL data on chart                         |
//+------------------------------------------------------------------+
#property copyright "ONER"
#property version   "1.00"
#property indicator_chart_window

input string SymbolName = "LTCUSD";

void OnInit() {
    // Create text labels
    for(int i = 0; i < 7; i++) {
        string name = "CSDL_" + IntegerToString(i);
        ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
        ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_TOP);
        ObjectSetInteger(0, name, OBJPROP_XDISTANCE, 10);
        ObjectSetInteger(0, name, OBJPROP_YDISTANCE, 30 + i * 20);
        ObjectSetInteger(0, name, OBJPROP_COLOR, clrWhite);
        ObjectSetString(0, name, OBJPROP_FONT, "Consolas");
        ObjectSetInteger(0, name, OBJPROP_FONTSIZE, 9);
    }
}

int OnCalculate(...) {
    // Read and display CSDL
    string filename = "DataAutoOner2\\" + SymbolName + "_LIVE.json";

    // Parse and display (simplified - need JSON parser)
    ObjectSetString(0, "CSDL_0", OBJPROP_TEXT, "CSDL Status: Reading...");

    return 0;
}
```

---

## 6. CHECKLIST NHANH

### Trước khi debug:
- [ ] DebugMode = true
- [ ] AutoTrading enabled (green button)
- [ ] EA attached to chart
- [ ] CSDL file exists and valid

### Khi không mở lệnh:
1. [ ] Check `[INIT]` thành công
2. [ ] Check CSDL đọc được (`[DEBUG] Mapped 7 TF ...`)
3. [ ] Check signal thay đổi (old != new)
4. [ ] Check timestamp fresh (> old + 15s)
5. [ ] Check strategy conditions (S2: signal=trend, S3: news>=threshold)
6. [ ] Check position_flags = 0 (chưa có lệnh)
7. [ ] Check IsTFEnabled(tf) = true

### Khi lệnh không đóng:
1. [ ] Check signal đã thay đổi trong CSDL
2. [ ] Check timestamp đã update
3. [ ] Check `HasValidS2BaseCondition()` = true
4. [ ] Check CloseByM1 settings
5. [ ] Check OnTimer() đang chạy (xem log định kỳ)

### Khi có lỗi:
1. [ ] Đọc error code
2. [ ] Tra cứu MT5 error codes: https://www.mql5.com/en/docs/constants/errorswarnings
3. [ ] Check broker requirements (lot size, margin, etc.)
4. [ ] Restart EA nếu cần

---

## 📚 REFERENCES

- **MQL5 Documentation**: https://www.mql5.com/en/docs
- **Error Codes**: https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes
- **Trade Operations**: https://www.mql5.com/en/docs/trading

---

**Last Updated**: 2025-11-05
**EA Version**: API_V2 (MT5) - Fixed OrderSend & OrderCloseTime
