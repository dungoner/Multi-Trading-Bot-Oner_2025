# PROMPT ĐẦY ĐỦ - CONVERT MQL4 EA SANG MQL5

**CHÚ Ý: Copy toàn bộ prompt này vào NEWCHAT mới**

---

## NHIỆM VỤ

Tôi có 1 Expert Advisor MQL4 hoạt động **ỔN ĐỊNH TUYỆT ĐỐI**. Bây giờ cần convert sang MQL5 nhưng **PHẢI GIỮ NGUYÊN 100% LOGIC**.

File gốc: `MQL4/Experts/MT4_Eas_Mtf Oner_V2.mq4` (2,422 dòng)
File đích: `MQL5/Experts/_MT5_EAs_MTF_ONER_V2.mq5` (đã compile nhưng không mở được lệnh)

---

## YÊU CẦU BẮT BUỘC

### GIAI ĐOẠN A: PHÂN TÍCH & KẾ HOẠCH (Làm TRƯỚC KHI code)

**A.1: ĐỌC VÀ PHÂN TÍCH MT4 EA**

1. Đọc file MT4 EA đầy đủ
2. Liệt kê **TẤT CẢ** các functions chính:
   - File operations (FileOpen, FileReadString, etc.)
   - Trading functions (OrderSend, OrderSelect, OrderClose, etc.)
   - Position management (OrdersTotal, OrderTicket, OrderType, etc.)
   - Account functions (AccountBalance, AccountEquity, etc.)
   - Time functions (TimeToStr, TimeDayOfWeek, etc.)
   - String functions (DoubleToStr, IntegerToString, etc.)
   - Market info functions (MarketInfo, Ask, Bid, Point, Digits, etc.)
   - Object functions (ObjectCreate, ObjectFind, etc.)

3. Liệt kê **TẤT CẢ** các constants được dùng:
   - OP_BUY, OP_SELL
   - SELECT_BY_POS, SELECT_BY_TICKET
   - MODE_TRADES
   - MODE_MINLOT, MODE_MAXLOT, etc.

4. Phân tích flow logic:
   - OnInit() làm gì?
   - OnTimer() làm gì?
   - OnDeinit() làm gì?
   - Các strategy functions (S1, S2, S3)
   - Close order logic
   - Restore positions logic

**A.2: RESEARCH MQL5 API**

1. Dùng web search tìm official MQL5 documentation:
   - File operations trong MQL5
   - Trading trong MQL5 (MqlTradeRequest, MqlTradeResult)
   - Position management trong MQL5
   - Khác biệt Order vs Deal vs Position

2. Tìm hiểu CÁC VẤN ĐỀ QUAN TRỌNG:
   - Tại sao KHÔNG được tạo wrapper functions trùng tên MT5 built-ins?
   - PositionGetTicket() vs PositionSelectByTicket() - khi nào dùng?
   - result.deal vs result.order - khác biệt là gì?
   - FILE_ANSI flag - khi nào bắt buộc?
   - TimeToStr() → TimeToString() - khác biệt parameter?
   - MqlDateTime struct - cách dùng?

**A.3: TẠO BẢNG SO SÁNH CHI TIẾT**

Tạo table đầy đủ:

| MT4 Function | MT5 Equivalent | Parameters Changed? | Notes | Must Convert? |
|--------------|----------------|---------------------|-------|---------------|
| OrdersTotal() | PositionsTotal() | No | Cannot create wrapper with same name | YES |
| OrderSelect(i, SELECT_BY_POS) | PositionGetTicket(i) + PositionSelectByTicket() | Yes | 2-step process in MT5 | YES |
| OrderTicket() | PositionGetInteger(POSITION_TICKET) | Yes | After selecting position | YES |
| OrderType() | PositionGetInteger(POSITION_TYPE) | Yes | Returns POSITION_TYPE_BUY/SELL | YES |
| OrderSend(...) | OrderSend(request, result) | Yes | Use MqlTradeRequest structure | YES |
| FileOpen(...) | FileOpen(...) | No | Must add FILE_ANSI flag | YES |
| TimeToStr() | TimeToString() | No | Just rename | YES |
| ... | ... | ... | ... | ... |

**QUAN TRỌNG:** Liệt kê **TẤT CẢ** functions, KHÔNG BỎ SÓT!

**A.4: XÁC ĐỊNH CÁI GÌ CẦN CONVERT, CÁI GÌ KHÔNG**

**CẦN CONVERT:**
- File operations: Thêm FILE_ANSI flag
- Trading functions: Dùng MqlTradeRequest + MqlTradeResult
- Position management: Dùng PositionGetTicket() + PositionSelect()
- String functions: TimeToStr → TimeToString, DoubleToStr → DoubleToString
- Time functions: TimeDayOfWeek(dt) → MqlDateTime.day_of_week
- Constants: Phải define lại (OP_BUY, OP_SELL, etc.)

**KHÔNG CẦN CONVERT (giữ nguyên):**
- Toàn bộ LOGIC business (S1, S2, S3 strategies)
- Toàn bộ CALCULATION (lot sizes, magic numbers, thresholds)
- Toàn bộ DATA STRUCTURES (structs, arrays)
- Toàn bộ FLOW CONTROL (if/else, for loops, conditions)

**A.5: TẠO CONVERSION PLAN CHI TIẾT**

Viết plan từng bước:

**Step 1:** Đọc MT4 EA lines 1-500, liệt kê functions cần convert
**Step 2:** Đọc MT4 EA lines 501-1000, tiếp tục liệt kê
**Step 3:** ...
**Step N:** Hoàn thành full inventory

Sau đó:

**Step N+1:** Convert file operations
**Step N+2:** Convert trading functions
**Step N+3:** Convert position management
**Step N+4:** Convert utility functions
**Step N+5:** Test compile
**Step N+6:** Add debug logs
**Step N+7:** Test trên chart

**A.6: TRÌNH BÀY PLAN CHO USER APPROVAL**

Trước khi code BẤT KỲ điều gì, trình bày:
1. Full list functions cần convert
2. Conversion table
3. Step-by-step plan
4. Estimated changes

Hỏi user: "Bạn có đồng ý với plan này không?"

---

### GIAI ĐOẠN B: THỰC HIỆN CONVERSION (Chỉ sau khi A hoàn thành)

**B.1: CÁC NGUYÊN TẮC BẮT BUỘC**

1. **KHÔNG BAO GIỜ** tạo wrapper functions trùng tên MT5 built-ins:
   ```mql5
   // ❌ WRONG - Cannot do this!
   int OrdersTotal() {
       return PositionsTotal();
   }

   // ✅ CORRECT - Use different name or modify code directly
   // Option 1: Different name
   int MT4_OrdersTotal() {
       return PositionsTotal();
   }

   // Option 2: Replace directly in code
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   ```

2. **LUÔN LUÔN** select position đúng cách:
   ```mql5
   // ✅ CORRECT MT5 way
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
       ulong ticket = PositionGetTicket(i);  // Get ticket + auto select
       if(ticket == 0) continue;

       // Optionally re-select for fresh data
       if(!PositionSelectByTicket(ticket)) continue;

       // Now can get properties
       long type = PositionGetInteger(POSITION_TYPE);
       double volume = PositionGetDouble(POSITION_VOLUME);
   }
   ```

3. **LUÔN LUÔN** check OrderSend() result đúng:
   ```mql5
   MqlTradeRequest request = {};
   MqlTradeResult result = {};

   // Fill request...

   if(!OrderSend(request, result)) {
       Print("OrderSend failed: ", GetLastError());
       return -1;
   }

   if(result.retcode != TRADE_RETCODE_DONE) {
       Print("Trade failed, retcode: ", result.retcode);
       return -1;
   }

   // Success - use result.deal for market orders
   return (int)result.deal;
   ```

4. **LUÔN LUÔN** thêm FILE_ANSI flag khi đọc text files:
   ```mql5
   int flags = FILE_READ | FILE_TXT | FILE_ANSI | FILE_SHARE_READ | FILE_SHARE_WRITE;
   int handle = FileOpen(filename, flags);
   ```

**B.2: CONVERSION THỨ TỰ**

Làm theo thứ tự này, KHÔNG bỏ qua bước nào:

1. **Constants & Defines** (top of file)
2. **File operations functions**
3. **Trading wrapper functions**
4. **Position management wrappers**
5. **Utility functions** (Time, String conversions)
6. **Main logic** (OnInit, OnTimer, OnDeinit)
7. **Strategy functions** (giữ nguyên logic, chỉ đổi API calls)

**B.3: TESTING**

Sau MỖI bước conversion:
1. Compile - phải 0 errors
2. Nếu có errors - đọc kỹ error message
3. Fix errors trước khi tiếp tục
4. KHÔNG làm quá nhiều changes cùng lúc

**B.4: DEBUG LOGS**

Thêm logs vào các vị trí QUAN TRỌNG:
- ReadCSDLFile() - biết có đọc được file không
- OnTimer() - biết data có load không
- ProcessS1Strategy() - biết có vào logic không
- OrderSendSafe() - biết lệnh có gửi không

---

## THÔNG TIN VỀ EA

**Chức năng chính:**
- Đọc signals từ file CSDL (7 timeframes)
- 3 strategies: S1 (Binary), S2 (Trend), S3 (News)
- Mở/đóng orders tự động
- Multi-timeframe (M1, M5, M15, M30, H1, H4, D1)
- Quản lý 21 orders (7 TF × 3 strategies)

**Files quan trọng:**
- MT4 working version: `MQL4/Experts/MT4_Eas_Mtf Oner_V2.mq4`
- MT5 current (broken): `MQL5/Experts/_MT5_EAs_MTF_ONER_V2.mq5`
- CSDL file: `DataAutoOner2/LTCUSD.txt`

**Test environment:**
- Symbol: LTCUSD
- Timeframe: M1 (user luôn test trên M1)
- Broker: MT5 account

---

## LƯU Ý QUAN TRỌNG

1. **MT4 EA là CHUẨN** - giữ nguyên logic 100%
2. **CHỈ đổi API calls** - không đổi logic
3. **KHÔNG bỏ qua GIAI ĐOẠN A** - phải phân tích trước
4. **Liệt kê đầy đủ** - không được sót function nào
5. **Test từng bước** - không làm quá nhiều cùng lúc
6. **Thêm logs** - để debug khi cần

---

## CÁC LỖI THƯỜNG GẶP (Tránh những lỗi này!)

1. ❌ Tạo wrapper `int OrdersTotal()` - conflict với MT5 built-in
2. ❌ Dùng `PositionGetSymbol(i)` để select position - không select!
3. ❌ Check `OrderSend()` return true là đủ - phải check `result.retcode`!
4. ❌ Dùng `result.order` cho market orders - phải dùng `result.deal`!
5. ❌ Quên `FILE_ANSI` flag - file đọc bị gibberish
6. ❌ Quên `request.type_filling` - trade sẽ fail

---

## YÊU CẦU ĐẦU RA

1. **GIAI ĐOẠN A:** Full analysis report với:
   - Complete function inventory
   - Conversion table
   - Detailed plan
   - Ước tính changes

2. **GIAI ĐOẠN B:** Working MT5 EA:
   - Compile 0 errors, 0 warnings
   - Mở được lệnh trên LTCUSD
   - Logic giống 100% MT4
   - Có debug logs

3. **Test reports:**
   - Compile log
   - Runtime logs (with DebugMode=true)
   - Order execution confirmation

---

## BẮT ĐẦU

Hãy bắt đầu với **GIAI ĐOẠN A.1: ĐỌC VÀ PHÂN TÍCH MT4 EA**.

Đọc file `MQL4/Experts/MT4_Eas_Mtf Oner_V2.mq4` và liệt kê **TẤT CẢ** functions được sử dụng. Chia thành các categories:
- File operations
- Trading functions
- Position management
- Account functions
- Time functions
- String functions
- Market info
- Object functions
- Constants

**KHÔNG được bỏ qua bước này!** Phải hoàn thành full inventory trước khi làm gì khác.
