# MT4 → MT5 CONVERSION PLAN - COMPLETE CHECKLIST

## ⚠️ NGUYÊN TẮC VÀNG

1. **KHÔNG BAO GIỜ động vào MT4 code đã ổn định**
2. **Copy toàn bộ MT4 → file MT5 mới**
3. **Convert từng function group, test từng bước**
4. **Mỗi thay đổi phải có backup + rollback plan**
5. **HỎI USER trước khi làm thay đổi quan trọng**

---

## 📋 PHASE 1: INVENTORY - KIỂM KÊ TOÀN BỘ MT4

### **1.1 ALL FUNCTIONS (47 functions total)**

#### **GROUP A: CORE UTILITIES (8 functions)**
```
✓ IsTFEnabled(int tf_index) → bool
✓ DebugPrint(string message) → void
✓ LogError(int error_code, string context, string details) → void
✓ SignalToString(int signal) → string
✓ NormalizeLotSize(double lot_size) → double
✓ StringTrim(string input_string) → string
✓ GenerateSymbolHash(string symbol) → int
✓ FormatAge(datetime timestamp) → string
```

**MT5 Changes**: ✅ NO CHANGES needed (pure logic)

---

#### **GROUP B: SYMBOL RECOGNITION (4 functions)**
```
✓ DiscoverSymbolFromChart() → string
✓ InitializeSymbolRecognition() → bool
✓ InitializeSymbolPrefix() → void
✓ BuildCSDLFilename() → void
```

**MT5 Changes**:
- ⚠️ `Symbol()` → Still works in MT5
- ⚠️ For multi-symbol: Need to pass symbol as parameter
- 🔧 **ACTION**: Add symbol parameter to all functions

---

#### **GROUP C: CSDL FILE HANDLING (4 functions)**
```
✓ ParseLoveRow(string row_data, int row_index) → bool
✓ ParseCSDLLoveJSON(string json_content) → bool
✓ TryReadFile(string filename) → bool
✓ ReadCSDLFile() → void
```

**MT5 Changes**:
- ⚠️ `FileOpen()` → Parameters changed in MT5
- ⚠️ `FILE_SHARE_READ|FILE_SHARE_WRITE` → Use `FILE_COMMON` flag
- 🔧 **ACTION**: Update FileOpen flags

**MT4**:
```mql4
int handle = FileOpen(filename, FILE_READ|FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_TXT|FILE_ANSI);
```

**MT5**:
```mql5
int handle = FileOpen(filename, FILE_READ|FILE_COMMON|FILE_TXT|FILE_ANSI);
```

---

#### **GROUP D: MAGIC NUMBER SYSTEM (2 functions)**
```
✓ GenerateSmartMagicNumber(string symbol, int tf_index, int strategy_index) → int
✓ GenerateMagicNumbers() → bool
```

**MT5 Changes**:
- ⚠️ Magic number still used, but ORDER vs POSITION system different
- 🔧 **ACTION**: For multi-symbol, add symbol hash to magic formula

**Current Formula (MT4)**:
```
magic = (symbol_hash * 1000) + (tf_index * 10) + strategy_index
```

**New Formula (MT5 multi-symbol)**:
```
magic = (symbol_hash * 100000) + (tf_index * 1000) + (strategy_index * 100) + instance_id
```

---

#### **GROUP E: LOT CALCULATION (2 functions)**
```
✓ CalculateSmartLotSize(double base_lot, int tf_index, int strategy_index) → double
✓ InitializeLotSizes() → void
```

**MT5 Changes**: ✅ NO CHANGES needed (pure math)

---

#### **GROUP F: LAYER1 THRESHOLDS (1 function)**
```
✓ InitializeLayer1Thresholds() → void
```

**MT5 Changes**: ✅ NO CHANGES needed (pure assignment)

---

#### **GROUP G: MAPPING CSDL (1 function)**
```
✓ MapCSDLToEAVariables() → void
```

**MT5 Changes**: ✅ NO CHANGES needed (pure mapping)

---

#### **GROUP H: ORDER OPERATIONS (3 functions)**
```
✓ CloseOrderSafely(int ticket, string reason) → bool
✓ OrderSendSafe(int tf, string symbol, int cmd, double lot_smart, ...) → int
✓ RestoreOrCleanupPositions() → bool
```

**MT5 Changes**: 🔴 **CRITICAL - MAJOR CHANGES**

**MT4 Order System**:
```mql4
OrderSelect(ticket, SELECT_BY_TICKET)
OrderClose(ticket, lot, price, slippage)
OrderSend(symbol, OP_BUY, lot, price, slippage, sl, tp, comment, magic)
```

**MT5 Position System**:
```mql5
PositionSelectByTicket(ticket)
trade.PositionClose(ticket)
trade.Buy(lot, symbol, price, sl, tp, comment)
// Need CTrade object!
```

🔧 **ACTION**:
1. Replace all `OrderXXX()` with `PositionXXX()` or `CTrade` methods
2. Add `#include <Trade\Trade.mqh>` for CTrade class
3. Create global `CTrade trade;` object

---

#### **GROUP I: CLOSE STRATEGIES (2 functions)**
```
✓ CloseAllStrategiesByMagicForTF(int tf) → void
✓ CloseAllBonusOrders() → void
```

**MT5 Changes**: 🔴 **CRITICAL**
- `OrdersTotal()` → `PositionsTotal()`
- `OrderSelect(i, SELECT_BY_POS)` → `PositionGetTicket(i)` + `PositionSelectByTicket()`
- Loop logic completely different

**MT4**:
```mql4
for(int i = OrdersTotal() - 1; i >= 0; i--) {
    if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) {
        int magic = OrderMagicNumber();
        OrderClose(...);
    }
}
```

**MT5**:
```mql5
for(int i = PositionsTotal() - 1; i >= 0; i--) {
    ulong ticket = PositionGetTicket(i);
    if(PositionSelectByTicket(ticket)) {
        long magic = PositionGetInteger(POSITION_MAGIC);
        trade.PositionClose(ticket);
    }
}
```

---

#### **GROUP J: SIGNAL VALIDATION (1 function)**
```
✓ HasValidS2BaseCondition(int tf) → bool
```

**MT5 Changes**: ✅ NO CHANGES needed (pure logic)

---

#### **GROUP K: STRATEGY PROCESSING (6 functions)**
```
✓ ProcessS1BasicStrategy(int tf) → void
✓ ProcessS1NewsFilterStrategy(int tf) → void
✓ ProcessS1Strategy(int tf) → void
✓ ProcessS2Strategy(int tf) → void
✓ ProcessS3Strategy(int tf) → void
✓ ProcessBonusNews() → void
```

**MT5 Changes**:
- ✅ Logic no changes
- ⚠️ But all call `OrderSendSafe()` → Need to update that function first
- 🔧 **ACTION**: Test after OrderSendSafe converted

---

#### **GROUP L: RISK MANAGEMENT (2 functions)**
```
✓ CheckStoplossAndTakeProfit() → void
✓ CheckAllEmergencyConditions() → void
```

**MT5 Changes**: 🔴 **CRITICAL**
- Uses `OrdersTotal()`, `OrderSelect()` → Must convert to Positions API
- 🔧 **ACTION**: Same as GROUP I

---

#### **GROUP M: RESET & HEALTH (3 functions)**
```
✓ SmartTFReset() → void
✓ CheckWeekendReset() → void
✓ CheckSPYBotHealth() → void
```

**MT5 Changes**:
- ✅ Logic mostly unchanged
- ⚠️ `FileOpen()` in health check → Update flags
- 🔧 **ACTION**: Update file flags only

---

#### **GROUP N: INITIALIZATION (2 functions)**
```
✓ OnInit() → int
✓ OnDeinit(const int reason) → void
```

**MT5 Changes**:
- ⚠️ `EventSetTimer(1)` → Still works in MT5
- ⚠️ `ChartSetSymbolPeriod()` → Same in MT5
- ✅ Mostly unchanged

---

#### **GROUP O: DASHBOARD (6 functions)**
```
✓ ScanAllOrdersForDashboard(...) → void
✓ PadRight(string text, int width) → string
✓ CalculateTFPnL(int tf) → double
✓ HasBonusOrders(int tf) → bool
✓ FormatBonusStatus() → string
✓ UpdateDashboard() → void
✓ CreateOrUpdateLabel(...) → void
```

**MT5 Changes**: 🔴 **CRITICAL**
- `ScanAllOrdersForDashboard()` uses `OrdersTotal()` → Must convert
- `ObjectCreate()` → Signature changed in MT5
- 🔧 **ACTION**: Update to MT5 object functions

**MT4**:
```mql4
ObjectCreate(name, OBJ_LABEL, 0, 0, 0);
ObjectSet(name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
```

**MT5**:
```mql5
ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
```

---

#### **GROUP P: TIMER (1 function)**
```
✓ OnTimer() → void
```

**MT5 Changes**:
- ✅ Structure unchanged
- ⚠️ All called functions must be converted first
- 🔧 **ACTION**: Test last after all functions converted

---

## 📊 SUMMARY OF CHANGES

| Group | Functions | MT5 Impact | Priority |
|-------|-----------|------------|----------|
| **A: Utilities** | 8 | ✅ No change | LOW |
| **B: Symbol** | 4 | ⚠️ Add symbol param for multi-symbol | MEDIUM |
| **C: CSDL** | 4 | ⚠️ FileOpen flags | LOW |
| **D: Magic** | 2 | ⚠️ Formula for multi-symbol | MEDIUM |
| **E: Lot** | 2 | ✅ No change | LOW |
| **F: Layer1** | 1 | ✅ No change | LOW |
| **G: Mapping** | 1 | ✅ No change | LOW |
| **H: Orders** | 3 | 🔴 **CRITICAL** - Order→Position API | **HIGH** |
| **I: Close** | 2 | 🔴 **CRITICAL** - Order→Position API | **HIGH** |
| **J: Validation** | 1 | ✅ No change | LOW |
| **K: Strategy** | 6 | ⚠️ Depends on H | MEDIUM |
| **L: Risk** | 2 | 🔴 **CRITICAL** - Order→Position API | **HIGH** |
| **M: Reset** | 3 | ⚠️ FileOpen flags | LOW |
| **N: Init** | 2 | ✅ Mostly unchanged | LOW |
| **O: Dashboard** | 7 | 🔴 **CRITICAL** - Order→Position + Objects | **HIGH** |
| **P: Timer** | 1 | ⚠️ Test last | LOW |

**TOTAL**: 47 functions
- ✅ **No change**: 18 functions (38%)
- ⚠️ **Minor changes**: 13 functions (28%)
- 🔴 **Critical changes**: 16 functions (34%)

---

## 🏗️ PHASE 2: MULTI-SYMBOL ARCHITECTURE

### **2.1 CURRENT MT4 STRUCTURE (Single Symbol)**

```mql4
struct EASymbolData {
    string symbol;              // Current symbol
    CSDLRow csdl_rows[7];      // 7 TF data
    int signal_old[7];
    // ... all EA state
};

EASymbolData g_ea;  // Global single instance
```

### **2.2 NEW MT5 STRUCTURE (Multi-Symbol)**

```mql5
struct EASymbolData {
    string symbol;              // Symbol for THIS instance
    CSDLRow csdl_rows[7];
    int signal_old[7];
    // ... same fields

    // NEW: Symbol-specific magic numbers
    int magic_numbers[7][3];    // Recalculated per symbol

    // NEW: Symbol-specific CSDL filename
    string csdl_filename;       // e.g., "LOVE_XAUUSD.json"
};

// Global array of EA instances
#define MAX_SYMBOLS 10
EASymbolData g_ea_array[MAX_SYMBOLS];
int g_ea_count = 0;  // Number of active symbols

// Add symbol to array
bool AddSymbol(string symbol) {
    if(g_ea_count >= MAX_SYMBOLS) return false;

    g_ea_array[g_ea_count].symbol = symbol;
    g_ea_array[g_ea_count].csdl_filename = "LOVE_" + symbol + ".json";

    // Generate magic numbers for this symbol
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea_array[g_ea_count].magic_numbers[tf][s] =
                GenerateSmartMagicNumber(symbol, tf, s);
        }
    }

    g_ea_count++;
    return true;
}
```

### **2.3 OnTimer() MULTI-SYMBOL LOOP**

```mql5
void OnTimer() {
    datetime current_time = TimeCurrent();
    int current_second = TimeSeconds(current_time);

    if(current_time == g_last_timer_run) return;
    g_last_timer_run = current_time;

    //=============================================================================
    // PROCESS EACH SYMBOL INDEPENDENTLY
    //=============================================================================
    for(int ea_index = 0; ea_index < g_ea_count; ea_index++) {

        EASymbolData& ea = g_ea_array[ea_index];  // Reference to current EA
        string symbol = ea.symbol;

        // EVEN seconds: Trading logic for THIS symbol
        if(!UseEvenOddMode || (current_second % 2 == 0)) {

            // Read CSDL for THIS symbol
            ReadCSDLFile(ea);  // Pass ea instance
            MapCSDLToEAVariables(ea);

            // Process 7 TF for THIS symbol
            for(int tf = 0; tf < 7; tf++) {
                if(HasValidS2BaseCondition(ea, tf)) {

                    if(tf == 0 && EnableBonusNews) {
                        CloseAllBonusOrders(ea, symbol);
                    }

                    CloseAllStrategiesByMagicForTF(ea, tf, symbol);

                    if(IsTFEnabled(tf)) {
                        if(S1_HOME) ProcessS1Strategy(ea, tf, symbol);
                        if(S2_TREND) ProcessS2Strategy(ea, tf, symbol);
                        if(S3_NEWS) ProcessS3Strategy(ea, tf, symbol);
                    }

                    if(EnableBonusNews) {
                        ProcessBonusNews(ea, symbol);
                    }

                    ea.signal_old[tf] = ea.csdl_rows[tf].signal;
                    ea.timestamp_old[tf] = ea.csdl_rows[tf].timestamp;
                }
            }
        }

        // ODD seconds: Auxiliary for THIS symbol
        if(!UseEvenOddMode || (current_second % 2 != 0)) {
            CheckStoplossAndTakeProfit(ea, symbol);
            UpdateDashboard(ea, symbol, ea_index);  // Dashboard with index
        }
    }
}
```

### **2.4 INPUT PARAMETERS FOR MULTI-SYMBOL**

```mql5
input string Symbols = "XAUUSD,EURUSD,GBPUSD";  // Comma-separated symbols
input bool EnableMultiSymbol = true;            // Enable multi-symbol mode

int OnInit() {
    if(EnableMultiSymbol) {
        // Parse symbols from input
        string symbols_array[];
        int count = StringSplit(Symbols, ',', symbols_array);

        for(int i = 0; i < count && i < MAX_SYMBOLS; i++) {
            string symbol = StringTrim(symbols_array[i]);
            if(!AddSymbol(symbol)) {
                Print("ERROR: Cannot add symbol ", symbol);
                return INIT_FAILED;
            }
            Print("✓ Added symbol: ", symbol);
        }
    } else {
        // Single symbol mode (backward compatible)
        AddSymbol(Symbol());
    }

    EventSetTimer(1);
    return INIT_SUCCEEDED;
}
```

---

## 🧪 PHASE 3: TEST PLAN

### **3.1 UNIT TESTS (Per Function Group)**

```
□ Test Group H (Orders) - OrderSendSafe, CloseOrderSafely
  ├─ Test open BUY position
  ├─ Test open SELL position
  ├─ Test close position by ticket
  └─ Compare with MT4 behavior

□ Test Group I (Close) - CloseAllStrategiesByMagicForTF
  ├─ Open 3 positions with different magic
  ├─ Call CloseAllStrategiesByMagicForTF
  └─ Verify correct magic closed

□ Test Group O (Dashboard) - Object creation
  ├─ Create label objects
  ├─ Verify display on chart
  └─ Update text dynamically
```

### **3.2 INTEGRATION TESTS**

```
□ Test single symbol mode
  ├─ Place EA on XAUUSD chart
  ├─ Verify all 7 TF work
  └─ Compare results with MT4

□ Test multi-symbol mode
  ├─ Configure Symbols = "XAUUSD,EURUSD"
  ├─ Verify CSDL read for both symbols
  ├─ Verify magic numbers unique per symbol
  ├─ Verify positions tracked separately
  └─ Dashboard shows both symbols
```

### **3.3 STRESS TESTS**

```
□ Test with 5 symbols simultaneously
□ Test signal changes across all TF at once
□ Test order spam prevention
□ Test memory usage vs MT4
```

---

## 📝 PHASE 4: CONVERSION STEPS (DETAILED)

### **STEP 1: Create MT5 file (NO conversion yet)**
```bash
cp MQL4/Experts/EAs_MTF_ONER_V2_MT4.mq4 MQL5/Experts/EAs_MTF_ONER_V2_MT5.mq5
```
✅ Just copy, commit, no changes

---

### **STEP 2: Add MT5 headers**
```mql5
#property strict
#include <Trade\Trade.mqh>

CTrade trade;  // Global trade object
```
✅ Compile to check syntax, commit

---

### **STEP 3: Convert Group H (Orders) - CRITICAL**
```
□ Replace OrderSend with trade.Buy() / trade.Sell()
□ Replace OrderClose with trade.PositionClose()
□ Test with dummy positions
□ ❓ ASK USER to review before commit
```

---

### **STEP 4: Convert Group I (Close strategies)**
```
□ Replace OrdersTotal() with PositionsTotal()
□ Replace OrderSelect() with PositionSelectByTicket()
□ Test CloseAllStrategiesByMagicForTF
□ Test CloseAllBonusOrders
□ ❓ ASK USER to review before commit
```

---

### **STEP 5: Convert Group O (Dashboard)**
```
□ Replace ObjectCreate() signature
□ Replace ObjectSet() with ObjectSetInteger()
□ Test dashboard display
□ ❓ ASK USER to review before commit
```

---

### **STEP 6: Add Multi-Symbol support**
```
□ Create g_ea_array[]
□ Modify OnTimer() to loop through symbols
□ Add symbol parameter to all functions
□ Test with 1 symbol first
□ Test with 2 symbols
□ ❓ ASK USER to review before commit
```

---

### **STEP 7: Final integration test**
```
□ Test all strategies (S1, S2, S3, BONUS)
□ Test close logic (M1 trigger)
□ Test dashboard
□ Compare results with MT4
□ ❓ ASK USER final approval
```

---

## ⚠️ ROLLBACK PLAN

```
IF ANY STEP FAILS:
├─ git checkout previous commit
├─ Analyze what went wrong
├─ ❓ ASK USER before retry
└─ Document the issue
```

---

## ✅ SUCCESS CRITERIA

```
✓ MT5 EA compiles without errors
✓ All 47 functions work correctly
✓ Single symbol mode = same results as MT4
✓ Multi-symbol mode works for 3+ symbols
✓ Magic numbers unique per symbol
✓ Dashboard shows all symbols
✓ No spam orders
✓ Performance comparable to MT4
```

---

## 🎯 TIMELINE ESTIMATE

```
Phase 1: Inventory & Planning    - 2 hours (DONE - this document)
Phase 2: Architecture Design     - 1 hour (DONE - this document)
Phase 3: Test Plan               - 1 hour (DONE - this document)
Phase 4: Conversion (7 steps)    - 10-15 hours (with testing)
Phase 5: Final testing           - 3-5 hours
---
TOTAL: 17-24 hours of careful, systematic work
```

---

## 🙋 QUESTIONS FOR USER

Trước khi bắt đầu convert, tôi cần bạn xác nhận:

1. **Multi-symbol approach đúng không?**
   - Input: `Symbols = "XAUUSD,EURUSD,GBPUSD"`
   - Array: `g_ea_array[MAX_SYMBOLS]`
   - Loop qua từng symbol trong OnTimer()

2. **Có muốn backward compatibility không?**
   - `EnableMultiSymbol = false` → Chạy 1 symbol như MT4
   - `EnableMultiSymbol = true` → Chạy nhiều symbol

3. **Dashboard hiển thị thế nào?**
   - Option A: Tất cả symbols trên 1 dashboard (dài)
   - Option B: Mỗi symbol 1 dashboard riêng (nhiều dashboard)

4. **CSDL filename convention?**
   - `LOVE_XAUUSD.json`, `LOVE_EURUSD.json` đúng không?

5. **Có muốn tôi làm STEP BY STEP và hỏi review mỗi step không?**

---

**❓ BẠN MUỐN TÔI BẮT ĐẦU KHÔNG? HAY CẦN CHỈNH SỬA PLAN NÀY TRƯỚC?**
