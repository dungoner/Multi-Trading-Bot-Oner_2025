# EA LOG FORMAT DESIGN
## Thiết kế định dạng log tối ưu cho Experts tab

---

## I. MỤC TIÊU

1. **Compact**: Mỗi hành động (mở/đóng) = 1 dòng log
2. **Full info**: Đầy đủ thông tin quan trọng
3. **Easy scan**: Dễ đọc khi scan nhanh Terminal
4. **Parseable**: Có thể parse để phân tích sau này
5. **Strategy-specific**: Mỗi chiến lược hiển thị info phù hợp
6. **Consolidated**: Gộp nhiều lệnh (ví dụ: 5 BONUS) thành 1 dòng tổng kết

---

## II. LOG FORMAT SPECIFICATION

### A. OPEN ORDER FORMAT

**Template:**
```
>>> [OPEN] <Strategy> TF=<TF> | <OrderInfo> | <StrategyContext> <<<
```

**Components:**
- `>>>` và `<<<`: Markers cho OPEN
- `<Strategy>`: S1_BASIC, S1_NEWS, S2_TREND, S3_NEWS, BONUS
- `TF=<TF>`: M1, M5, M15, M30, H1, H4, D1
- `<OrderInfo>`: #ticket TYPE lot @price HOẶC count×TYPE total_lot @price_range (cho BONUS)
- `<StrategyContext>`: Thông tin đặc thù của từng strategy

### B. CLOSE ORDER FORMAT

**Template:**
```
>> [CLOSE] <Reason> TF=<TF> S=<1/2/3> | <OrderInfo> | Profit=<$value> | <Context> <<
```

**Components:**
- `>>` và `<<`: Markers cho CLOSE
- `<Reason>`: SIGNAL_CHG, L1_SL, L2_SL, TP, WEEKEND, HEALTH, BONUS_M1
- `TF=<TF>`: Timeframe
- `S=<1/2/3>`: Strategy number
- `<OrderInfo>`: #ticket TYPE lot HOẶC count orders (cho BONUS)
- `Profit=<$value>`: Tổng profit/loss
- `<Context>`: Thông tin thêm (threshold, old/new signal, etc.)

---

## III. STRATEGY-SPECIFIC FORMATS

### 1. S1_BASIC (No NEWS filter)

**OPEN:**
```
>>> [OPEN] S1_BASIC TF=<TF> | #<ticket> <BUY/SELL> <lot> @<price> | Sig=<±1> <<<
```

**Example:**
```
>>> [OPEN] S1_BASIC TF=M1 | #12345 BUY 0.05 @1.2345 | Sig=+1 <<<
>>> [OPEN] S1_BASIC TF=H1 | #12350 SELL 0.10 @1.2340 | Sig=-1 <<<
```

**CLOSE (Signal Change):**
```
>> [CLOSE] SIGNAL_CHG TF=<TF> S=1 | #<ticket> <TYPE> <lot> | Profit=$<value> | Old:<±1> New:<±1> <<
```

**Example:**
```
>> [CLOSE] SIGNAL_CHG TF=M1 S=1 | #12345 BUY 0.05 | Profit=$12.30 | Old:+1 New:-1 <<
```

---

### 2. S1_NEWS (With NEWS filter)

**OPEN:**
```
>>> [OPEN] S1_NEWS TF=<TF> | #<ticket> <BUY/SELL> <lot> @<price> | Sig=<±1> News=<±level> Filter:<ON/OFF> Dir:<REQ/ANY> <<<
```

**Fields:**
- `News=<±level>`: News level với dấu (vd: +45, -55)
- `Filter:<ON/OFF>`: News filter enabled/disabled
- `Dir:<REQ/ANY>`: S1_RequireNewsDirection = true/false

**Example:**
```
>>> [OPEN] S1_NEWS TF=M5 | #12346 BUY 0.05 @1.2350 | Sig=+1 News=+45 Filter:ON Dir:REQ <<<
>>> [OPEN] S1_NEWS TF=M15 | #12347 SELL 0.08 @1.2340 | Sig=-1 News=-38 Filter:ON Dir:ANY <<<
```

**CLOSE:**
```
>> [CLOSE] SIGNAL_CHG TF=<TF> S=1 | #<ticket> <TYPE> <lot> | Profit=$<value> | Old:<±1> New:<±1> News:<±level> <<
```

**Example:**
```
>> [CLOSE] SIGNAL_CHG TF=M5 S=1 | #12346 BUY 0.05 | Profit=$8.50 | Old:+1 New:-1 News:-40 <<
```

---

### 3. S2_TREND (Trend Following)

**OPEN:**
```
>>> [OPEN] S2_TREND TF=<TF> | #<ticket> <BUY/SELL> <lot> @<price> | Sig=<±1> Trend:<UP/DOWN> Mode:<AUTO/FBUY/FSELL> <<<
```

**Fields:**
- `Trend:<UP/DOWN>`: Trend direction (UP=+1, DOWN=-1)
- `Mode:<AUTO/FBUY/FSELL>`: S2_TrendMode (0=AUTO D1, 1=Force BUY, 2=Force SELL)

**Example:**
```
>>> [OPEN] S2_TREND TF=M5 | #12348 BUY 0.10 @1.2345 | Sig=+1 Trend:UP Mode:AUTO <<<
>>> [OPEN] S2_TREND TF=H1 | #12349 SELL 0.15 @1.2340 | Sig=-1 Trend:DOWN Mode:AUTO <<<
>>> [OPEN] S2_TREND TF=M30 | #12351 BUY 0.12 @1.2355 | Sig=+1 Trend:UP Mode:FBUY <<<
```

**CLOSE:**
```
>> [CLOSE] SIGNAL_CHG TF=<TF> S=2 | #<ticket> <TYPE> <lot> | Profit=$<value> | Old:<±1> New:<±1> Trend:<UP/DOWN> <<
```

**Example:**
```
>> [CLOSE] SIGNAL_CHG TF=M5 S=2 | #12348 BUY 0.10 | Profit=$25.00 | Old:+1 New:-1 Trend:DOWN <<
```

---

### 4. S3_NEWS (News Alignment)

**OPEN:**
```
>>> [OPEN] S3_NEWS TF=<TF> | #<ticket> <BUY/SELL> <lot> @<price> | Sig=<±1> News=<±level><↑/↓> <<<
```

**Fields:**
- `News=<±level><↑/↓>`: News level + arrow (vd: +55↑, -48↓)

**Example:**
```
>>> [OPEN] S3_NEWS TF=M1 | #12352 BUY 0.02 @1.2350 | Sig=+1 News=+55↑ <<<
>>> [OPEN] S3_NEWS TF=M5 | #12353 SELL 0.03 @1.2345 | Sig=-1 News=-48↓ <<<
```

**CLOSE:**
```
>> [CLOSE] SIGNAL_CHG TF=<TF> S=3 | #<ticket> <TYPE> <lot> | Profit=$<value> | Old:<±1> New:<±1> News:<±level> <<
```

---

### 5. BONUS (Multiple orders)

**OPEN (Consolidated):**
```
>>> [OPEN] BONUS TF=<TF> | <count>×<BUY/SELL> Total:<total_lot> @<price> | News=<±level><↑/↓> Tickets:<t1,t2,...> <<<
```

**Fields:**
- `<count>×<TYPE>`: Số lượng × loại lệnh (vd: 5×BUY)
- `Total:<total_lot>`: Tổng lot size
- `@<price>`: Entry price (có thể là avg nếu khác nhau)
- `Tickets:<list>`: Danh sách ticket numbers

**Example:**
```
>>> [OPEN] BONUS TF=M1 | 5×BUY Total:0.10 @1.2345 | News=+65↑ Tickets:12354,12355,12356,12357,12358 <<<
>>> [OPEN] BONUS TF=M5 | 3×SELL Total:0.09 @1.2340 | News=-58↓ Tickets:12359,12360,12361 <<<
```

**CLOSE (Consolidated):**
```
>> [CLOSE] BONUS_M1 TF=<TF> | <count> orders Total:<total_lot> | Profit=$<total_value> | Closed:<count_success>/<count_total> <<
```

**Example:**
```
>> [CLOSE] BONUS_M1 TF=M1 | 5 orders Total:0.10 | Profit=$123.45 | Closed:5/5 <<
>> [CLOSE] BONUS_M1 TF=M5 | 3 orders Total:0.09 | Profit=$-15.20 | Closed:3/3 <<
```

---

## IV. CLOSE REASONS

### 1. SIGNAL_CHG (Signal Changed)

**Format:**
```
>> [CLOSE] SIGNAL_CHG TF=<TF> S=<1/2/3> | #<ticket> <TYPE> <lot> | Profit=$<value> | Old:<old_sig> New:<new_sig> <<
```

**Example:**
```
>> [CLOSE] SIGNAL_CHG TF=M1 S=1 | #12345 BUY 0.05 | Profit=$12.30 | Old:+1 New:-1 <<
>> [CLOSE] SIGNAL_CHG TF=M5 S=2 | #12348 SELL 0.10 | Profit=$-8.50 | Old:-1 New:+1 <<
```

---

### 2. L1_SL (Layer 1 Stoploss - Max Loss)

**Format:**
```
>> [CLOSE] L1_SL TF=<TF> S=<1/2/3> | #<ticket> <TYPE> <lot> | Loss=$<value> | Threshold=$<value> <<
```

**Example:**
```
>> [CLOSE] L1_SL TF=M5 S=2 | #12346 BUY 0.10 | Loss=$-50.00 | Threshold=$-45.00 <<
>> [CLOSE] L1_SL TF=H1 S=1 | #12350 SELL 0.15 | Loss=$-120.00 | Threshold=$-100.00 <<
```

---

### 3. L2_SL (Layer 2 Stoploss - Margin Emergency)

**Format:**
```
>> [CLOSE] L2_SL TF=<TF> S=<1/2/3> | #<ticket> <TYPE> <lot> | Loss=$<value> | Threshold=$<value> Margin=$<margin> <<
```

**Example:**
```
>> [CLOSE] L2_SL TF=M1 S=3 | #12352 BUY 0.02 | Loss=$-200.00 | Threshold=$-180.00 Margin=$360.00 <<
```

---

### 4. TP (Take Profit)

**Format:**
```
>> [CLOSE] TP TF=<TF> S=<1/2/3> | #<ticket> <TYPE> <lot> | Profit=$<value> | Threshold=$<tp_value> Mult=<multiplier> <<
```

**Example:**
```
>> [CLOSE] TP TF=H1 S=3 | #12347 BUY 0.02 | Profit=$150.00 | Threshold=$120.00 Mult=3.0 <<
>> [CLOSE] TP TF=M30 S=1 | #12355 SELL 0.08 | Profit=$85.00 | Threshold=$70.00 Mult=2.5 <<
```

---

### 5. WEEKEND (Weekend Reset)

**Format:**
```
>> [CLOSE] WEEKEND | All positions closed | Total: <count> orders Profit=$<total> | Sat 00:03 Reset <<
```

**Example:**
```
>> [CLOSE] WEEKEND | All positions closed | Total: 12 orders Profit=$256.80 | Sat 00:03 Reset <<
```

---

### 6. HEALTH (Health Check - SPY Bot Frozen)

**Format:**
```
>> [CLOSE] HEALTH | SPY frozen <hours>h<mins>m | Total: <count> orders Profit=$<total> | Reset triggered <<
```

**Example:**
```
>> [CLOSE] HEALTH | SPY frozen 3h15m | Total: 8 orders Profit=$-45.20 | Reset triggered <<
```

---

## V. CODE MODIFICATION LOCATIONS

### A. OPEN ORDER LOGS

#### 1. ProcessS1BasicStrategy() - Lines 903-933
**Current:**
```cpp
DebugPrint("[S1_BASIC_" + tf_names[tf] + "] BUY #" + IntegerToString(ticket));
```

**New:**
```cpp
Print(">>> [OPEN] S1_BASIC TF=", tf_names[tf], " | #", ticket, " BUY ",
      DoubleToStr(g_ea.lot_sizes[tf][0], 2), " @", DoubleToStr(Ask, Digits),
      " | Sig=+1 <<<");
```

#### 2. ProcessS1NewsFilterStrategy() - Lines 938-991
**Current:**
```cpp
DebugPrint("[S1_NEWS_" + tf_names[tf] + "] BUY #" + IntegerToString(ticket) +
           " (NEWS=" + IntegerToString(tf_news) + ")");
```

**New:**
```cpp
string filter_str = S1_UseNewsFilter ? "ON" : "OFF";
string dir_str = S1_RequireNewsDirection ? "REQ" : "ANY";
Print(">>> [OPEN] S1_NEWS TF=", tf_names[tf], " | #", ticket, " BUY ",
      DoubleToStr(g_ea.lot_sizes[tf][0], 2), " @", DoubleToStr(Ask, Digits),
      " | Sig=+1 News=", tf_news > 0 ? "+" : "", tf_news,
      " Filter:", filter_str, " Dir:", dir_str, " <<<");
```

#### 3. ProcessS2Strategy() - Lines 1005-1056
**Current:**
```cpp
DebugPrint("[S2_" + tf_names[tf] + "] Opened #" + IntegerToString(ticket) + " BUY " + DoubleToStr(g_ea.lot_sizes[tf][1], 2));
```

**New:**
```cpp
string trend_str = trend_to_follow == 1 ? "UP" : "DOWN";
string mode_str = (S2_TrendMode == 0) ? "AUTO" : (S2_TrendMode == 1) ? "FBUY" : "FSELL";
Print(">>> [OPEN] S2_TREND TF=", tf_names[tf], " | #", ticket, " BUY ",
      DoubleToStr(g_ea.lot_sizes[tf][1], 2), " @", DoubleToStr(Ask, Digits),
      " | Sig=+1 Trend:", trend_str, " Mode:", mode_str, " <<<");
```

#### 4. ProcessS3Strategy() - Lines 1060-1108
**Current:**
```cpp
DebugPrint("[S3_" + tf_names[tf] + "] Opened #" + IntegerToString(ticket) + " BUY " + DoubleToStr(g_ea.lot_sizes[tf][2], 2));
```

**New:**
```cpp
string arrow = (tf_news > 0) ? "↑" : "↓";
Print(">>> [OPEN] S3_NEWS TF=", tf_names[tf], " | #", ticket, " BUY ",
      DoubleToStr(g_ea.lot_sizes[tf][2], 2), " @", DoubleToStr(Ask, Digits),
      " | Sig=+1 News=", tf_news > 0 ? "+" : "", tf_news, arrow, " <<<");
```

#### 5. ProcessBonusNews() - Lines 1112-1152
**Current:** (Logs each order individually)
```cpp
DebugPrint("[BONUS_" + tf_names[tf] + "] Opened #" + IntegerToString(ticket) + " BUY " + DoubleToStr(g_ea.lot_sizes[tf][2], 2));
```

**New:** (Consolidate into single log after loop)
```cpp
// After loop completes, log consolidated:
if(opened_count > 0) {
    Print(">>> [OPEN] BONUS TF=", tf_names[tf], " | ", opened_count, "×",
          news_direction == 1 ? "BUY" : "SELL", " Total:",
          DoubleToStr(opened_count * g_ea.lot_sizes[tf][2], 2), " @",
          DoubleToStr(news_direction == 1 ? Ask : Bid, Digits),
          " | News=", tf_news > 0 ? "+" : "", tf_news,
          news_direction == 1 ? "↑" : "↓", " Tickets:", ticket_list, " <<<");
}
```

### B. CLOSE ORDER LOGS

#### 1. CloseOrderSafely() - Line 241
**Current:**
```cpp
DebugPrint("[CLOSE] " + reason + " #" + IntegerToString(ticket));
```

**Problem:** Thiếu thông tin (TF, Strategy, Profit, Context)

**Solution:** Không sửa ở đây, sửa ở nơi GỌI CloseOrderSafely() để truyền đủ info

#### 2. CheckStoplossAndTakeProfit() - Lines 1229, 1253
**Current Layer1/Layer2:**
```cpp
Print("[", mode_name, "] ", strategy_names[s], "_", tf_names[tf],
      " #", ticket, " Loss=$", DoubleToStr(profit, 2),
      " Threshold=$", DoubleToStr(sl_threshold, 2));
```

**New:**
```cpp
Print(">> [CLOSE] ", mode_name == "LAYER1_SL" ? "L1_SL" : "L2_SL",
      " TF=", tf_names[tf], " S=", (s+1),
      " | #", ticket, " ", OrderType() == OP_BUY ? "BUY" : "SELL", " ",
      DoubleToStr(OrderLots(), 2),
      " | Loss=$", DoubleToStr(profit, 2),
      " | Threshold=$", DoubleToStr(sl_threshold, 2),
      mode_name == "LAYER2_SL" ? " Margin=$" + DoubleToStr(margin_usd, 2) : "",
      " <<");
```

**Current Take Profit:**
```cpp
Print("[TAKE_PROFIT] ", strategy_names[s], "_", tf_names[tf],
      " #", ticket, " Profit=$", DoubleToStr(profit, 2),
      " Threshold=$", DoubleToStr(tp_threshold, 2),
      " (Multiplier=", DoubleToStr(TakeProfit_Multiplier, 2), ")");
```

**New:**
```cpp
Print(">> [CLOSE] TP TF=", tf_names[tf], " S=", (s+1),
      " | #", ticket, " ", OrderType() == OP_BUY ? "BUY" : "SELL", " ",
      DoubleToStr(OrderLots(), 2),
      " | Profit=$", DoubleToStr(profit, 2),
      " | Threshold=$", DoubleToStr(tp_threshold, 2),
      " Mult=", DoubleToStr(TakeProfit_Multiplier, 2), " <<");
```

#### 3. CloseAllBonusOrders() - Lines 1154-1178
**Current:** Calls CloseOrderSafely() individually for each order

**New:** Collect tickets, profit, then log consolidated:
```cpp
if(closed_count > 0) {
    Print(">> [CLOSE] BONUS_M1 TF=", tf_names[tf],
          " | ", closed_count, " orders Total:", DoubleToStr(total_lot, 2),
          " | Profit=$", DoubleToStr(total_profit, 2),
          " | Closed:", closed_count, "/", closed_count, " <<");
}
```

#### 4. Signal Change Close (Multiple locations)
**Location:** Inside each strategy's main loop before opening new order

**Current:** Implied via CloseOrderSafely()

**New:** Need to pass more context to close function, or log separately:
```cpp
// Example in ProcessS1Strategy() before opening new order:
if(g_ea.position_flags[tf][0] == 1) {
    // Find and close old order
    for(int i = OrdersTotal() - 1; i >= 0; i--) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES) &&
           OrderSymbol() == Symbol() &&
           OrderMagicNumber() == g_ea.magic_numbers[tf][0]) {

            double old_profit = OrderProfit() + OrderSwap() + OrderCommission();
            int old_type = OrderType();
            double old_lot = OrderLots();
            int old_ticket = OrderTicket();

            if(CloseOrderSafely(old_ticket, "SIGNAL_CHG")) {
                Print(">> [CLOSE] SIGNAL_CHG TF=", tf_names[tf], " S=1",
                      " | #", old_ticket, " ", old_type == OP_BUY ? "BUY" : "SELL", " ",
                      DoubleToStr(old_lot, 2),
                      " | Profit=$", DoubleToStr(old_profit, 2),
                      " | Old:", signal_old, " New:", current_signal, " <<");
                g_ea.position_flags[tf][0] = 0;
            }
        }
    }
}
```

---

## VI. IMPLEMENTATION PLAN

### Phase 1: Modify OPEN logs (Simple, no logic change)
1. ProcessS1BasicStrategy() - 2 locations (BUY, SELL)
2. ProcessS1NewsFilterStrategy() - 2 locations (BUY, SELL)
3. ProcessS2Strategy() - 2 locations (BUY, SELL)
4. ProcessS3Strategy() - 2 locations (BUY, SELL)
5. ProcessBonusNews() - Consolidate loop

### Phase 2: Modify CLOSE logs (More complex)
1. CheckStoplossAndTakeProfit() - 3 sections (L1_SL, L2_SL, TP)
2. CloseAllBonusOrders() - Consolidate close
3. Add SIGNAL_CHG logs in each strategy before opening new order

### Phase 3: Test & Verify
1. Test each strategy individually
2. Test bonus orders (multiple)
3. Test close reasons (SL, TP, signal change)
4. Verify log length < 200 chars

---

## VII. EXAMPLE OUTPUT (10+ scenarios)

### Scenario 1: S1_BASIC opens BUY, then signal reverses
```
>>> [OPEN] S1_BASIC TF=M1 | #12345 BUY 0.05 @1.23450 | Sig=+1 <<<
>> [CLOSE] SIGNAL_CHG TF=M1 S=1 | #12345 BUY 0.05 | Profit=$12.30 | Old:+1 New:-1 <<
>>> [OPEN] S1_BASIC TF=M1 | #12346 SELL 0.05 @1.23420 | Sig=-1 <<<
```

### Scenario 2: S1_NEWS with filter, high news, profit target hit
```
>>> [OPEN] S1_NEWS TF=M5 | #12347 BUY 0.08 @1.23500 | Sig=+1 News=+45 Filter:ON Dir:REQ <<<
>> [CLOSE] TP TF=M5 S=1 | #12347 BUY 0.08 | Profit=$85.00 | Threshold=$70.00 Mult=2.5 <<
```

### Scenario 3: S2_TREND follows D1, hit Layer1 stoploss
```
>>> [OPEN] S2_TREND TF=H1 | #12348 BUY 0.15 @1.23600 | Sig=+1 Trend:UP Mode:AUTO <<<
>> [CLOSE] L1_SL TF=H1 S=2 | #12348 BUY 0.15 | Loss=$-120.00 | Threshold=$-100.00 <<
```

### Scenario 4: S2_TREND forced BUY mode
```
>>> [OPEN] S2_TREND TF=M30 | #12349 BUY 0.12 @1.23550 | Sig=+1 Trend:UP Mode:FBUY <<<
```

### Scenario 5: S3_NEWS high impact, signal change close
```
>>> [OPEN] S3_NEWS TF=M1 | #12350 BUY 0.02 @1.23480 | Sig=+1 News=+55↑ <<<
>> [CLOSE] SIGNAL_CHG TF=M1 S=3 | #12350 BUY 0.02 | Profit=$8.50 | Old:+1 New:-1 <<
```

### Scenario 6: BONUS 5 orders opened, all closed when M1 signal comes
```
>>> [OPEN] BONUS TF=M1 | 5×BUY Total:0.10 @1.23500 | News=+65↑ Tickets:12351,12352,12353,12354,12355 <<<
>> [CLOSE] BONUS_M1 TF=M1 | 5 orders Total:0.10 | Profit=$123.45 | Closed:5/5 <<
```

### Scenario 7: BONUS 3 SELL orders, negative news
```
>>> [OPEN] BONUS TF=M5 | 3×SELL Total:0.09 @1.23400 | News=-58↓ Tickets:12356,12357,12358 <<<
>> [CLOSE] BONUS_M1 TF=M5 | 3 orders Total:0.09 | Profit=$-15.20 | Closed:3/3 <<
```

### Scenario 8: Layer2 emergency stoploss (margin crisis)
```
>>> [OPEN] S3_NEWS TF=M1 | #12359 BUY 0.02 @1.23550 | Sig=+1 News=+48↑ <<<
>> [CLOSE] L2_SL TF=M1 S=3 | #12359 BUY 0.02 | Loss=$-200.00 | Threshold=$-180.00 Margin=$360.00 <<
```

### Scenario 9: Weekend reset (12 orders closed)
```
>> [CLOSE] WEEKEND | All positions closed | Total: 12 orders Profit=$256.80 | Sat 00:03 Reset <<
```

### Scenario 10: Health check reset (SPY frozen 3h15m)
```
>> [CLOSE] HEALTH | SPY frozen 3h15m | Total: 8 orders Profit=$-45.20 | Reset triggered <<
```

### Scenario 11: Multiple strategies on same TF
```
>>> [OPEN] S1_BASIC TF=M5 | #12360 BUY 0.05 @1.23500 | Sig=+1 <<<
>>> [OPEN] S2_TREND TF=M5 | #12361 BUY 0.10 @1.23505 | Sig=+1 Trend:UP Mode:AUTO <<<
>>> [OPEN] S3_NEWS TF=M5 | #12362 BUY 0.03 @1.23510 | Sig=+1 News=+42↑ <<<
```

### Scenario 12: Failed order (not logged as OPEN, only error)
```
[ORDER_FAIL] S1_M1 Err:134 (Retry 0.01 lot)
>>> [OPEN] S1_BASIC TF=M1 | #12363 BUY 0.01 @1.23500 | Sig=+1 <<<
```

---

## VIII. NOTES & CONSTRAINTS

1. **Log length:** Tất cả logs < 200 chars để fit trong Terminal width
2. **Parsing:** Có thể parse bằng regex pattern: `^(>>>|>>).*(<<<<|<<)$`
3. **Timestamp:** MT4 tự động thêm timestamp vào mỗi Print(), không cần manual
4. **DebugMode:** Chỉ OPEN/CLOSE logs luôn hiển thị, debug logs chỉ khi DebugMode=true
5. **Error logs:** Giữ nguyên format hiện tại `[ORDER_FAIL]`, `[CLOSE_FAIL]`
6. **Ticket list:** Nếu quá dài (>10 orders) có thể truncate: `Tickets:123,124,...,132 (10 total)`

---

## IX. VARIABLES TO TRACK (For BONUS consolidation)

**In ProcessBonusNews():**
```cpp
int opened_count = 0;
string ticket_list = "";
double total_lot = 0;
```

**In CloseAllBonusOrders():**
```cpp
int closed_count = 0;
double total_profit = 0;
double total_lot = 0;
```

---

## X. ROLLBACK PLAN

Nếu log mới gây issue, có thể rollback về commit hiện tại:
```
git log --oneline -5
git reset --hard <commit_hash>
```

Current clean state: commit `33f5a28`

---

**END OF DESIGN DOCUMENT**
