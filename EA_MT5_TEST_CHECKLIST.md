# 📋 MT5 EA TEST CHECKLIST & DEBUG GUIDE

**File**: `_MT5_EAs_MTF ONER_V2.mq5`
**Version**: API_V2 (MT5) - Fixed OrderSend & OrderCloseTime wrappers
**Date**: 2025-11-05

---

## ✅ PRE-FLIGHT CHECKLIST (BEFORE RUNNING EA)

### 1. MT5 CONFIGURATION
- [ ] **AutoTrading enabled**: Tools → Options → Expert Advisors → "Allow algorithmic trading" ✅
- [ ] **WebRequest allowed** (if using HTTP API): Add URL to allowed list
  - Tools → Options → Expert Advisors → "Allow WebRequest for listed URL"
  - Add: `http://dungalading.duckdns.org`
- [ ] **DLL imports** (if needed): Allow DLL imports (unchecked for this EA)
- [ ] **Chart AutoTrading button**: Green (enabled) ✅

### 2. CSDL DATA FILES (LOCAL MODE)
- [ ] **Folder exists**: `[MT5_Data_Folder]/MQL5/Files/DataAutoOner2/`
- [ ] **File exists**: `DataAutoOner2/[SYMBOL]_LIVE.json`
  - Example: `DataAutoOner2/LTCUSD_LIVE.json`
  - Example: `DataAutoOner2/XAUUSD_LIVE.json`
- [ ] **File format**: Valid JSON with 7 rows × 6 columns
  ```json
  {
    "M1": [10.5, 1730800000, 1, 0.5, 5, 12],
    "M5": [10.5, 1730800000, 1, 0.5, 5, 15],
    "M15": [10.5, 1730800000, -1, 0.5, 5, -20],
    "M30": [10.5, 1730800000, 0, 0.5, 5, 0],
    "H1": [10.5, 1730800000, 1, 0.5, 5, 25],
    "H4": [10.5, 1730800000, 1, 0.5, 5, 30],
    "D1": [10.5, 1730800000, 1, 0.5, 5, 11]
  }
  ```
  - Col 1: max_loss (double)
  - Col 2: timestamp (long)
  - Col 3: signal (int: 1=BUY, -1=SELL, 0=NONE)
  - Col 4: pricediff (unused)
  - Col 5: timediff (unused)
  - Col 6: news (int: ±11-70, CASCADE news level with direction)

### 3. EA INPUT PARAMETERS
- [ ] **CSDL_Source**: Set to `FOLDER_2` (or `HTTP_API` if using remote)
- [ ] **TF toggles**: Enable at least 1 TF (recommend: M5, H1, H4)
  - `TF_M5 = true`
  - `TF_H1 = true`
  - `TF_H4 = true`
- [ ] **Strategy toggles**: Enable at least 1 strategy
  - `S1_HOME = true` (Binary/Basic strategy)
  - `S2_TREND = true` (Trend following D1)
  - `S3_NEWS = true` (News alignment)
- [ ] **Lot size**: Set reasonable lot (0.01 - 0.1 for testing)
  - `FixedLotSize = 0.01` (for testing)
- [ ] **DebugMode**: Enable for detailed logs
  - `DebugMode = true` ✅

### 4. ACCOUNT & BROKER
- [ ] **Demo account**: Use demo first (never test on live!)
- [ ] **Sufficient balance**: At least $1000 for 0.01 lot
- [ ] **Symbol available**: Check symbol name matches broker
  - Example: Broker may use `XAUUSD.xyz` instead of `XAUUSD`
  - EA auto-detects suffix (`.raw`, `.a`, `.b`, `.c`)
- [ ] **Leverage**: Check leverage is sufficient (1:100 or higher recommended)

---

## 🧪 STEP-BY-STEP TEST PROCEDURE

### TEST 1: EA INITIALIZATION (5 minutes)

**Objective**: Verify EA starts without errors

**Steps**:
1. Attach EA to chart (any timeframe, EA uses internal 7 TF logic)
2. Check "Experts" tab in Terminal for initialization log
3. Look for `[INIT]` message

**Expected Output**:
```
[INIT] LTCUSD | SL:L1 News:7TF(M1:+12BUY) Trend:BUY | Lot:0.10-0.12 | TF:5 S:3 | Folder:DA2 Master:M5-D1 Magic:501-721
[RESTORE] Scanned 0 orders | Restored 0 flags | Cleaned 0 zombie flags
```

**Success Criteria**:
- [x] No errors in log
- [x] `[INIT]` message shows correct symbol, lot sizes, magic numbers
- [x] Timer started (check "Experts" tab for periodic activity)

**Troubleshooting**:
- ❌ `INIT_FAILED`: Check CSDL file exists and is valid JSON
- ❌ No `[INIT]` message: Check Expert Advisors allowed in MT5 settings

---

### TEST 2: CSDL FILE READING (2 minutes)

**Objective**: Verify EA reads data from CSDL file

**Steps**:
1. Wait 2-5 seconds after EA starts
2. Check "Experts" tab for `[DEBUG]` messages (if DebugMode = true)

**Expected Output** (if DebugMode = true):
```
[DEBUG] Mapped 7 TF | signal[0]=1 trend_d1=1 news[M1]=12 (split to 14 vars: 7 level + 7 dir)
[DEBUG] NEWS 14 vars: M1[12/1] M5[15/1] M15[20/-1] ...
```

**Success Criteria**:
- [x] Signal values match CSDL file
- [x] Trend D1 detected correctly
- [x] NEWS split into level + direction

**Troubleshooting**:
- ❌ No debug messages: Set `DebugMode = true` and restart EA
- ❌ Signal = 0 for all TF: CSDL file not read, check file path

---

### TEST 3: STRATEGY S2 (TREND) - SIMPLE (10 minutes)

**Objective**: Test S2 strategy (easiest to trigger)

**Setup**:
1. Enable **ONLY S2_TREND**:
   - `S1_HOME = false`
   - `S2_TREND = true`
   - `S3_NEWS = false`
2. Enable **ONLY M5 TF**:
   - `TF_M1 = false`
   - `TF_M5 = true`
   - Other TF = false
3. Set CSDL file:
   - D1 signal = 1 (BUY trend)
   - M5 signal = 1 (BUY signal)
   - M5 timestamp = current time (within 1 minute)

**Steps**:
1. Attach EA
2. Wait for OnTimer() to run (every 1 second on EVEN seconds)
3. Watch for `[OPEN]` message

**Expected Output**:
```
>>> [OPEN] S2_TREND TF=M5 | #12345678 BUY 0.01 @1850.50 | Sig=+1 Trend:UP Mode:AUTO | Timestamp:1730800000 <<<
```

**Success Criteria**:
- [x] BUY order opened with correct lot size
- [x] Magic number = [magic_numbers[1][1]] (check INIT log)
- [x] No errors

**Troubleshooting**:
- ❌ No order: Check `[DEBUG]` messages
  - Signal old != new? (Change signal in CSDL file)
  - Timestamp new > old + 15? (Update timestamp)
  - Signal = Trend D1? (Match M5 signal to D1)
- ❌ `HasValidS2BaseCondition() = false`: Signal not changed or timestamp too old

---

### TEST 4: STRATEGY S1 (BASIC) - MEDIUM (10 minutes)

**Objective**: Test S1 basic strategy

**Setup**:
1. Enable **ONLY S1_HOME**:
   - `S1_HOME = true`
   - `S2_TREND = false`
   - `S3_NEWS = false`
2. Disable NEWS filter:
   - `S1_UseNewsFilter = false`
3. Enable M5:
   - `TF_M5 = true`
4. Set CSDL file:
   - M5 signal = 1 (BUY) or -1 (SELL)
   - M5 timestamp = current time

**Expected Output**:
```
>>> [OPEN] S1_BASIC TF=M5 | #12345679 BUY 0.01 @1850.50 | Sig=1 | Timestamp:1730800000 <<<
```

**Success Criteria**:
- [x] Order opened when signal changes
- [x] Correct strategy name: S1_BASIC

---

### TEST 5: STRATEGY S3 (NEWS) - ADVANCED (15 minutes)

**Objective**: Test S3 news alignment strategy

**Setup**:
1. Enable **ONLY S3_NEWS**:
   - `S1_HOME = false`
   - `S2_TREND = false`
   - `S3_NEWS = true`
2. Set news threshold:
   - `MinNewsLevelS3 = 20`
3. Set CSDL file:
   - M5 signal = 1
   - M5 news = +25 (BUY direction, level 25)
   - M5 timestamp = current time

**Expected Output**:
```
>>> [OPEN] S3_NEWS TF=M5 | #12345680 BUY 0.01 @1850.50 | Sig=+1 News=+25↑ | Timestamp:1730800000 <<<
```

**Success Criteria**:
- [x] Order opened when NEWS >= threshold
- [x] Signal matches NEWS direction
- [x] Arrow (↑/↓) shows direction

---

### TEST 6: CLOSE ORDERS (10 minutes)

**Objective**: Test order closing logic

**Setup**:
1. Have 1 open S2 order (from TEST 3)
2. Change CSDL file:
   - M5 signal: 1 → -1 (or -1 → 1)
   - M5 timestamp: Update to current time + 20 seconds

**Expected Output**:
```
[CLOSE] Strategy changed | #12345678 closed
```

**Success Criteria**:
- [x] Order closed when signal changes
- [x] Position flag reset to 0

---

### TEST 7: STOPLOSS & TAKEPROFIT (Optional, 20 minutes)

**Objective**: Test SL/TP logic

**Setup**:
1. Enable stoploss:
   - `StoplossMode = LAYER1_MAXLOSS`
2. Set max_loss in CSDL: `10.0` (means $10 per lot)
3. Open 1 order with 0.1 lot
4. Let order run into loss > $1.0 (10 × 0.1)

**Expected Output**:
```
[SL_HIT] Strategy S2_M5 | #12345678 closed | Loss: -$1.05
```

**Success Criteria**:
- [x] Order closed when loss > threshold
- [x] Position flag reset

---

### TEST 8: MULTI-TIMEFRAME (Advanced, 30 minutes)

**Objective**: Test multiple TF and strategies simultaneously

**Setup**:
1. Enable all strategies:
   - `S1_HOME = true`
   - `S2_TREND = true`
   - `S3_NEWS = true`
2. Enable multiple TF:
   - `TF_M5 = true`
   - `TF_H1 = true`
   - `TF_H4 = true`
3. Set CSDL file with different signals per TF

**Expected Output**:
```
>>> [OPEN] S1_BASIC TF=M5 | #... BUY ...
>>> [OPEN] S2_TREND TF=H1 | #... BUY ...
>>> [OPEN] S3_NEWS TF=H4 | #... SELL ...
```

**Success Criteria**:
- [x] Each TF opens independently
- [x] Each strategy opens independently
- [x] No conflicts between orders
- [x] Total orders ≤ 21 (7 TF × 3 strategies)

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue 1: EA doesn't open any orders

**Symptoms**: No `[OPEN]` messages, no orders in Terminal

**Debug Steps**:
1. Check `DebugMode = true`
2. Look for `[DEBUG]` messages showing why skip:
   ```
   [DEBUG] S2_TREND: Signal=1 != Trend=0, skip
   [DEBUG] S3_NEWS: TF0 NEWS=15 < 20, skip
   ```
3. Common causes:
   - Signal old = Signal new (no change)
   - Timestamp too old (< 15 seconds since last)
   - Strategy conditions not met (S2: signal != trend, S3: news < threshold)
   - Position flag already = 1 (order already open)

**Solutions**:
- Update CSDL file with NEW signal and FRESH timestamp
- Check strategy-specific conditions
- Restart EA to reset position flags

---

### Issue 2: EA opens orders but doesn't close them

**Symptoms**: Orders remain open when signal changes

**Debug Steps**:
1. Check close mode settings:
   - `S1_CloseByM1 = true` → S1 closes by M1 signal
   - `S2_CloseByM1 = false` → S2 closes by own TF signal
2. Check `HasValidS2BaseCondition()`:
   - Signal must CHANGE (old != new)
   - Timestamp must be FRESH (new > old + 15)

**Solutions**:
- Update CSDL with opposite signal + fresh timestamp
- Check OnTimer() is running (look for periodic debug messages)
- Check OrderClose() errors in log

---

### Issue 3: Error 130 (Invalid stops)

**Symptoms**: `[ORDER_FAIL] ... Err:130`

**Cause**: SL/TP too close to current price

**Solution**:
- EA uses SL=0, TP=0 by default (no stops on order open)
- Check broker's minimum stop distance
- Stoploss managed by EA logic, not broker stops

---

### Issue 4: Error 131 (Invalid volume)

**Symptoms**: `[ORDER_FAIL] ... Err:131`

**Cause**: Lot size too small/large for broker

**Solutions**:
- Check `SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN)` → Usually 0.01
- Check `SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX)` → Usually 100
- Set `FixedLotSize` within broker limits
- EA has fallback: Retries with 0.01 lot if volume error

---

### Issue 5: Error 134 (Not enough money)

**Symptoms**: `[ORDER_FAIL] ... Err:134`

**Cause**: Insufficient account balance

**Solutions**:
- Increase demo account balance
- Reduce `FixedLotSize` to 0.01
- Check margin requirement: `MarketInfo(Symbol(), MODE_MARGINREQUIRED)`

---

### Issue 6: CSDL file not found

**Symptoms**: `[WARNING] All read attempts failed. Using old data.`

**Cause**: File path incorrect or file doesn't exist

**Solutions**:
1. Check file path:
   - FOLDER_2 = `MQL5/Files/DataAutoOner2/[SYMBOL]_LIVE.json`
2. Check symbol name:
   - EA auto-detects: `LTCUSDC` → `LTCUSD`
   - Check `[INIT]` log for detected symbol name
3. Create file manually:
   - Copy template from section 2 above
   - Save as UTF-8 JSON

---

## 📊 EXPECTED BEHAVIOR SUMMARY

| Condition | S1 (HOME) | S2 (TREND) | S3 (NEWS) |
|-----------|-----------|------------|-----------|
| **Open when** | Signal = ±1 | Signal = Trend D1 | Signal = News dir AND News ≥ threshold |
| **Close when** | Signal changes (or M1 if enabled) | Signal changes (or M1 if enabled) | Signal changes |
| **News filter** | Optional (S1_UseNewsFilter) | None | Required |
| **Lot size** | lot_sizes[tf][0] | lot_sizes[tf][1] | lot_sizes[tf][2] |
| **Magic number** | magic_numbers[tf][0] | magic_numbers[tf][1] | magic_numbers[tf][2] |

---

## 🎯 SUCCESS CRITERIA FOR FULL TEST

EA is working correctly if:
- [x] OnInit() completes without errors
- [x] CSDL file is read every EVEN second (or HTTP API)
- [x] At least 1 strategy opens orders when conditions met
- [x] Orders close when signal changes
- [x] Stoploss activates when loss exceeds threshold
- [x] No errors or crashes during 1 hour run
- [x] Dashboard shows correct info (if ShowDashboard = true)
- [x] Multiple TF/strategies work independently

---

## 📝 NOTES

1. **Timer runs every 1 second**: OnTimer() executes every second
   - EVEN seconds (0,2,4...): Trading logic (read CSDL, open/close orders)
   - ODD seconds (1,3,5...): Auxiliary (SL/TP check, dashboard, health check)

2. **Position flags prevent duplicate orders**: Each [TF][Strategy] has a flag
   - Flag = 0: No order open → Can open
   - Flag = 1: Order already open → Skip

3. **Magic numbers are unique**: Each [TF][Strategy] has unique magic
   - Format: `500 + (tf × 30) + (strat × 10)`
   - Example: M5 (tf=1) S2 (strat=1) → 500 + 30 + 10 = 540

4. **Timestamp check prevents stale signals**:
   - New timestamp must be > old timestamp + 15 seconds
   - Prevents acting on same signal multiple times

---

**Last Updated**: 2025-11-05
**EA Version**: API_V2 (MT5) - Fixed OrderSend & OrderCloseTime wrappers
