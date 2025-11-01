# PROMPT: Review EA System và Thiết kế Log Format

## YÊU CẦU CHÍNH:

Đọc lại toàn bộ 2 session gần nhất để hiểu đầy đủ EA trading system, sau đó thực hiện thiết kế lại Experts tab log format.

---

## BƯỚC 1: ĐỌC VÀ HIỂU EA SYSTEM

### A. Cấu trúc EA (7 TF × 3 Strategies = 21 orders)

Đọc code `MQL4/Experts/Eas_Smf_Oner_V2.mq4` để hiểu:

1. **7 Timeframes:**
   - M1, M5, M15, M30, H1, H4, D1
   - Mỗi TF có thể bật/tắt riêng (TF_M1, TF_M5, ...)

2. **3 Strategies:**
   - S1_HOME (Binary/Home signal)
   - S2_TREND (Follow D1 trend)
   - S3_NEWS (High impact news)
   - Mỗi strategy có thể bật/tắt riêng

3. **Data source:**
   - SPY Bot (Super_Spy7TF_V2.mq4) tạo CSDL files
   - Folder: DataAutoOner2/
   - Format: LTCUSD_M1_Love.csv, LTCUSD_M5_Love.csv, ...

4. **CSDL File Structure:** (6 columns)
   - Col 1: max_loss (per 1 LOT)
   - Col 2: timestamp
   - Col 3: signal (1=BUY, -1=SELL, 0=NONE)
   - Col 4: pricediff (unused)
   - Col 5: timediff (unused)
   - Col 6: news (CASCADE ±11-16)

### B. Order Management

**Magic Number System:**
- Base: 1000000 + (LTCUSD hash)
- Each TF+Strategy có magic riêng
- Example: M1_S1 = base + 0*3 + 0 = 1234567

**Lot Size Calculation:**
- Dùng CalculateSmartLotSize()
- Base: FixedLotSize (input parameter)
- Adjust theo TF và Strategy

**Open Order Logic:**
- Check signal thay đổi từ CSDL
- Check TF enabled
- Check Strategy enabled
- Check conditions (news filter, trend direction, etc.)
- Close old order (if exists)
- Open new order

**Close Order Logic:**
- Signal reversal (CSDL thay đổi)
- Stoploss (Layer1: max_loss × lot, Layer2: margin/divisor)
- Take profit (optional)
- Weekend reset
- Health check (SPY bot frozen)

---

## BƯỚC 2: THIẾT KẾ LOG FORMAT

### YÊU CẦU:

Thiết kế lại 2 dòng log cho Experts tab khi EA đóng/mở lệnh:

**CLOSE ORDER FORMAT:**
```
->>- [CLOSE] <Reason> | TF=<M1/M5/...> S=<1/2/3> | Ticket=#<number> Type=<BUY/SELL> Lot=<0.01> | Profit=$<123.45> | <Additional Info>
```

**OPEN ORDER FORMAT:**
```
->>>- [OPEN] <Reason> | TF=<M1/M5/...> S=<1/2/3> | Ticket=#<number> Type=<BUY/SELL> Lot=<0.01> Price=<1.2345> | <Additional Info>
```

### CẦN HIỂN THỊ:

**Cho MỖI STRATEGY:**
- S1_HOME: Signal, News level (nếu dùng filter), News direction
- S2_TREND: Signal, Trend direction (D1), Mode (auto/force BUY/SELL)
- S3_NEWS: Signal, News level, News direction, Bonus count (nếu có)

**Cho CLOSE:**
- Reason: SIGNAL_CHANGE / LAYER1_SL / LAYER2_SL / TAKE_PROFIT / WEEKEND_RESET / HEALTH_CHECK
- Profit/Loss amount
- SL threshold (nếu có)

**Cho OPEN:**
- Entry price
- Expected lot size
- Current signal value
- Relevant conditions met

---

## BƯỚC 3: TÌM CODE LOCATIONS

Tìm trong EA các hàm liên quan đến log:

1. **Open order logs:**
   - ProcessS1BasicStrategy()
   - ProcessS1NewsFilterStrategy()
   - ProcessS2Strategy()
   - ProcessS3Strategy()
   - ProcessBonusNews()

2. **Close order logs:**
   - CheckStoplossAndTakeProfit()
   - CloseAllStrategiesByMagicForTF()
   - ProcessWeekendReset()
   - CheckHealthAndResetIfNeeded()

---

## BƯỚC 4: THIẾT KẾ CỤ THỂ

Tạo format cụ thể cho TỪNG TRƯỜNG HỢP:

### Example CLOSE logs:

```
->>- [CLOSE] SIGNAL_CHANGE | TF=M1 S=1 | #12345 SELL 0.05 | Profit=$12.30 | Old:SELL New:BUY News:45
->>- [CLOSE] LAYER1_SL | TF=M5 S=2 | #12346 BUY 0.10 | Loss=$-50.00 | Threshold=$-45.00 Trend:UP
->>- [CLOSE] TAKE_PROFIT | TF=H1 S=3 | #12347 BUY 0.02 | Profit=$150.00 | TP_Threshold=$120.00 Multiplier:3.0
```

### Example OPEN logs:

```
->>>- [OPEN] SIGNAL_NEW | TF=M1 S=1 | #12348 BUY 0.05 @1.2345 | Signal:BUY News:35 Filter:ON
->>>- [OPEN] TREND_FOLLOW | TF=M5 S=2 | #12349 SELL 0.10 @1.2340 | Signal:SELL Trend:DOWN Mode:AUTO
->>>- [OPEN] NEWS_HIGH | TF=H1 S=3 | #12350 BUY 0.02 @1.2350 | Signal:BUY News:55↑ Bonus:2
```

---

## OUTPUT YÊU CẦU:

1. **Document thiết kế:** Chi tiết format cho từng loại log
2. **Code locations:** Liệt kê các hàm cần sửa
3. **Implementation plan:** Các bước implement cụ thể
4. **Example outputs:** Ít nhất 10 ví dụ log cho các tình huống khác nhau

---

## LƯU Ý:

- Log phải COMPACT (1 dòng) nhưng ĐẦY ĐỦ thông tin
- Dễ đọc khi scan nhanh trong Terminal
- Có thể parse được (nếu cần analyze sau này)
- Không quá dài (< 200 chars/line)
