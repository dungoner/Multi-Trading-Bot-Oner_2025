# STARTUP RESET AUTO-IMPLEMENTATION
## SPY Bot: Tự động reset khi MT4 khởi động (Không cần input)

---

## Date: 2025-11-02

---

## YÊU CẦU

**Vấn đề:**
- Trước đây: Input `EnableStartupReset = true` cho phép user bật/tắt
- User phải tự kiểm tra và bật tính năng này
- Đây là tính năng CƠ BẢN cần chạy TỰ ĐỘNG để hệ thống 7 TF ổn định

**Giải pháp:**
- ❌ BỎ input parameter (không cho user tắt)
- ✅ TỰ ĐỘNG chạy mỗi khi MT4 khởi động
- ✅ Chỉ chạy 1 LẦN DUY NHẤT sau 60 giây
- ✅ Xóa biến ngay sau khi reset (dọn dẹp sạch sẽ)

---

## THUẬT TOÁN MỚI

### Logic Flow:

```
MT4 KHỞI ĐỘNG
    ↓
OnInit() chạy
    ↓
Khởi tạo GlobalVariable:
    - g_flag = 1
    - g_time = TimeCurrent()
    ↓
OnTimer() chạy mỗi giây (even seconds)
    ↓
RunStartupReset() được gọi
    ↓
Kiểm tra: flag = 1 && đã qua 60s?
    ↓ YES
    Reset 7 TF files
    ↓
    Gán flag = 0
    ↓
    XÓA flag và time
    ↓
    HOÀN THÀNH
    (Lần sau không chạy nữa vì biến đã xóa)
```

### Chi tiết Implementation:

#### 1. OnInit() - Khởi tạo biến (Line 2633-2647)

```cpp
// Chỉ tạo nếu chưa có (MT4 mới khởi động)
string gv_flag = g_target_symbol + "_StartupResetFlag";
string gv_time = g_target_symbol + "_StartupResetTime";

if(!GlobalVariableCheck(gv_flag)) {
    GlobalVariableSet(gv_flag, 1);              // Gán = 1
    GlobalVariableSet(gv_time, TimeCurrent());  // Lưu timestamp
    Print("✓ StartupReset: GlobalVariable initialized");
}
```

**Điểm quan trọng:**
- Chỉ tạo nếu biến CHƯA TỒN TẠI
- Nếu indicator reload (F5) → Biến vẫn còn → Không tạo lại
- Chỉ khi MT4 restart hoàn toàn → Biến mất → Tạo mới

#### 2. RunStartupReset() - Kiểm tra và thực thi (Line 2661-2687)

```cpp
void RunStartupReset() {
    string gv_flag = g_target_symbol + "_StartupResetFlag";
    string gv_time = g_target_symbol + "_StartupResetTime";

    // Nếu biến không tồn tại → Return (đã xóa rồi)
    if(!GlobalVariableCheck(gv_flag)) return;

    double flag_value = GlobalVariableGet(gv_flag);
    datetime init_time = (datetime)GlobalVariableGet(gv_time);

    // Chỉ chạy khi: flag=1 VÀ đã qua 60s
    if(flag_value == 1 && (TimeCurrent() - init_time >= 60)) {
        Print("✓ StartupReset: 60s after MT4 start | Resetting 7 TF files...");
        SmartTFReset();  // Reset 7 TF files

        // QUAN TRỌNG: Gán = 0 và XÓA biến ngay
        GlobalVariableSet(gv_flag, 0);  // Gán = 0
        GlobalVariableDel(gv_flag);     // Xóa flag
        GlobalVariableDel(gv_time);     // Xóa time

        Print("✓ StartupReset: Completed and cleaned up");
    }
}
```

**Điểm quan trọng:**
- Gọi mỗi giây chẵn (even seconds): 0, 2, 4, 6...
- 60 lần gọi đầu: Chưa đủ 60s → Không làm gì
- Lần gọi thứ 61: Đủ 60s → Reset → Xóa biến
- Lần gọi thứ 62+: Biến không còn → Return ngay

#### 3. OnDeinit() - Dọn dẹp khi remove (Line 2929-2945)

```cpp
// Chỉ khi REASON_REMOVE (indicator bị xóa khỏi chart)
if(reason == REASON_REMOVE) {
    string gv_flag = g_target_symbol + "_StartupResetFlag";
    string gv_time = g_target_symbol + "_StartupResetTime";

    // Xóa nếu còn tồn tại
    if(GlobalVariableCheck(gv_flag)) GlobalVariableDel(gv_flag);
    if(GlobalVariableCheck(gv_time)) GlobalVariableDel(gv_time);
}
```

**Điểm quan trọng:**
- Biến đã được xóa trong RunStartupReset() (sau 60s)
- Nhưng nếu user xóa indicator TRƯỚC 60s → Dọn dẹp ở đây
- Đảm bảo không để rác trong GlobalVariables

---

## KỊCH BẢN TEST

### Kịch bản 1: MT4 khởi động bình thường

```
00:00 - MT4 start → OnInit() → Tạo biến (flag=1, time=00:00)
00:02 - Timer #1 → RunStartupReset() → Chưa đủ 60s
00:04 - Timer #2 → RunStartupReset() → Chưa đủ 60s
...
01:00 - Timer #30 → RunStartupReset() → Đủ 60s! → Reset → Xóa biến
01:02 - Timer #31 → RunStartupReset() → Biến không còn → Return
...
```

**Kết quả:** Reset thành công, biến đã xóa

### Kịch bản 2: Indicator reload (F5) trong 60s đầu

```
00:00 - MT4 start → OnInit() → Tạo biến (flag=1, time=00:00)
00:20 - User nhấn F5 → OnInit() → Biến đã có → Không tạo lại
00:40 - Timer → RunStartupReset() → Kiểm tra time=00:00 → Chưa đủ 60s
01:00 - Timer → RunStartupReset() → Đủ 60s! → Reset → Xóa biến
```

**Kết quả:** Vẫn reset đúng sau 60s kể từ lúc MT4 start (không phải lúc F5)

### Kịch bản 3: User xóa indicator trước 60s

```
00:00 - MT4 start → OnInit() → Tạo biến (flag=1, time=00:00)
00:30 - User xóa indicator → OnDeinit(REASON_REMOVE) → Xóa biến
```

**Kết quả:** Biến được dọn dẹp, không để rác

### Kịch bản 4: MT4 restart sau khi đã reset

```
DAY 1:
00:00 - MT4 start → OnInit() → Tạo biến (flag=1, time=00:00)
01:00 - Timer → Reset → Xóa biến
... MT4 chạy cả ngày, biến đã xóa ...

DAY 2:
MT4 restart
00:00 - MT4 start → OnInit() → Biến không còn → Tạo biến mới (flag=1, time=00:00)
01:00 - Timer → Reset → Xóa biến
```

**Kết quả:** Reset lại sau mỗi lần MT4 restart

---

## FILES MODIFIED

1. **MQL4/Indicators/Super_Spy7TF_V2.mq4**
   - ❌ Removed: `input bool EnableStartupReset = true;` (Line 27)
   - ✅ Added: GlobalVariable initialization in OnInit() (Line 2633-2647)
   - ✅ Modified: RunStartupReset() - Auto-run with cleanup (Line 2661-2687)
   - ✅ Modified: OnDeinit() - Update variable names (Line 2933-2945)

---

## SO SÁNH TRƯỚC VÀ SAU

### TRƯỚC (Old Implementation):

| Feature | Status |
|---------|--------|
| **Input parameter** | ✅ `EnableStartupReset = true` (user có thể tắt) |
| **Khởi tạo biến** | ❌ Trong RunStartupReset() (chậm trễ) |
| **Biến sử dụng** | `gv_done` (0/1), `gv_init_time` |
| **Sau khi reset** | ❌ Chỉ gán `gv_done = 1`, KHÔNG xóa biến |
| **Cleanup** | ✅ Trong OnDeinit(REASON_REMOVE) |
| **Vấn đề** | User có thể tắt → Hệ thống không ổn định |

### SAU (New Implementation):

| Feature | Status |
|---------|--------|
| **Input parameter** | ❌ Đã xóa (không cho user tắt) |
| **Khởi tạo biến** | ✅ Trong OnInit() (nhanh, chính xác) |
| **Biến sử dụng** | `gv_flag` (0/1), `gv_time` |
| **Sau khi reset** | ✅ Gán `gv_flag = 0` VÀ XÓA cả 2 biến ngay |
| **Cleanup** | ✅ Trong OnDeinit(REASON_REMOVE) + sau reset |
| **Ưu điểm** | TỰ ĐỘNG chạy, không phụ thuộc user |

---

## ƯU ĐIỂM

1. **Tự động 100%:** Không cần user bật/tắt
2. **Chạy 1 lần duy nhất:** Không lặp lại trong cùng session
3. **Dọn dẹp sạch sẽ:** Xóa biến ngay sau khi dùng xong
4. **An toàn:** Vẫn cleanup trong OnDeinit() nếu indicator bị xóa sớm
5. **Không conflict:** Dùng symbol-specific variable names
6. **Đúng timing:** 60s là đủ để MT4 khởi động ổn định

---

## LƯU Ý KHI DEPLOY

1. **Compile:** Kiểm tra không có syntax error
2. **Test trên Demo:**
   - MT4 restart → Đợi 60s → Check log
   - F5 reload → Đợi 60s → Check log
   - Xóa indicator trước 60s → Check GlobalVariables
3. **Monitor Log:**
   ```
   ✓ StartupReset: GlobalVariable initialized
   ✓ StartupReset: 60s after MT4 start | Resetting 7 TF files...
   ✓ StartupReset: Completed and cleaned up
   ```
4. **Check Files:** 7 TF files (M1-D1) được reset về 0

---

## ROLLBACK

Nếu có vấn đề, rollback về commit trước:

```bash
git log --oneline -5
git reset --hard <previous_commit_hash>
```

---

## KẾT LUẬN

✅ **HOÀN THÀNH:** Tính năng StartupReset đã được chuyển từ "optional" sang "auto-mandatory"

**Lợi ích:**
- Hệ thống 7 TF luôn được reset khi MT4 khởi động
- Không phụ thuộc vào user (tránh quên bật)
- Code sạch hơn, logic rõ ràng hơn
- Dọn dẹp biến tự động (không để rác)

**Status:** ✅ Ready for testing

---

**Implementation Date:** 2025-11-02
**Modified By:** Claude Code
**File Version:** Super_Spy7TF_V2.mq4
