# STARTUP RESET - SIMPLIFIED LOGIC
## SPY Bot: Simple 60s check with user control

---

## Date: 2025-11-02 (Revision 2)

---

## YÊU CẦU CỦA USER

### 1. ❌ Không xóa biến
**Lý do:** Các hàm reset khác (MidnightReset, HealthCheck) cũng gọi SmartTFReset() → Nếu xóa biến → Không còn reference → Phức tạp

**Giải pháp:** Giữ GlobalVariable, chỉ dùng static bool để mark "done"

### 2. ✅ Chấp nhận reset 2 lần
**Tình huống:**
- MT4 restart → Reset lần 1 (sau 60s)
- F5 reload → Static bool mất → Reset lần 2 (sau 60s)
- MidnightReset → Reset lần 3

**Kết luận:** Chấp nhận! Không sao cả.

### 3. ✅ Logic đơn giản
- Chỉ cần 1 biến GlobalVariable (time)
- Không cần biến flag
- Không cần file
- Chỉ cần: `TimeCurrent() - init_time >= 60`

### 4. ✅ Thêm input bật/tắt
- `input bool EnableStartupReset = true`
- User có thể tắt nếu cần
- Default = true (bật)

---

## IMPLEMENTATION MỚI

### A. Input Parameter (Line 27)

```cpp
input bool EnableStartupReset = true;  // Startup reset 60s after MT4 starts
```

**Đặc điểm:**
- ✅ User có thể tắt
- ✅ Default = true (bật tự động)

---

### B. OnInit() - Lưu timestamp (Line 2640-2646)

```cpp
if(EnableStartupReset) {
    string gv_time = g_target_symbol + "_StartupInitTime";
    if(!GlobalVariableCheck(gv_time)) {
        GlobalVariableSet(gv_time, TimeCurrent());
        Print("✓ StartupReset: Initialized (will reset after 60s)");
    }
}
```

**Logic:**
- Chỉ tạo nếu biến CHƯA TỒN TẠI
- Lưu thời gian MT4 khởi động (hoặc indicator reload)
- KHÔNG XÓA biến sau reset

**Khi nào tạo biến mới:**
- MT4 restart → Biến mất → Tạo mới ✅
- F5 reload → Biến còn → KHÔNG tạo mới ❌
- Chỉ khi user xóa biến manual → Tạo mới

---

### C. RunStartupReset() - Check đơn giản (Line 2660-2685)

```cpp
void RunStartupReset() {
    if(!EnableStartupReset) return;  // Skip if disabled

    // Get timestamp
    string gv_time = g_target_symbol + "_StartupInitTime";
    if(!GlobalVariableCheck(gv_time)) return;

    // Static bool - mất khi reload
    static bool reset_done = false;

    // Simple check
    datetime init_time = (datetime)GlobalVariableGet(gv_time);
    int elapsed = TimeCurrent() - init_time;

    // Reset once per indicator session
    if(!reset_done && elapsed >= 60) {
        Print("✓ StartupReset: ", g_target_symbol, " | ", elapsed, "s after init");
        SmartTFReset();
        reset_done = true;
        // KHÔNG XÓA GlobalVariable!
    }
}
```

**Logic:**
1. Nếu tắt → Return
2. Lấy timestamp từ GlobalVariable
3. Dùng static bool để mark "done"
4. Check: `elapsed >= 60s`
5. Reset 1 lần
6. KHÔNG xóa GlobalVariable

**Static bool behavior:**
- Tồn tại trong cùng indicator session
- MẤT khi indicator reload (F5, crash, recompile)
- → Reset lại → OK (theo yêu cầu user)

---

### D. OnDeinit() - Cleanup (Line 2929-2935)

```cpp
if(reason == REASON_REMOVE) {
    string gv_time = g_target_symbol + "_StartupInitTime";
    if(GlobalVariableCheck(gv_time)) {
        GlobalVariableDel(gv_time);
        Print("✓ Cleaned up GlobalVariable for ", g_target_symbol);
    }
}
```

**Logic:**
- Chỉ xóa khi indicator bị XÓA HOÀN TOÀN (REASON_REMOVE)
- Không xóa khi reload (REASON_CHARTCHANGE, REASON_RECOMPILE)

---

## SO SÁNH TRƯỚC VÀ SAU

| Feature | Version 1 (Phức tạp) | Version 2 (Đơn giản) |
|---------|---------------------|---------------------|
| **Input parameter** | ❌ Đã xóa (auto-run) | ✅ Có (user control) |
| **GlobalVariable** | 2 biến (flag + time) | 1 biến (time) |
| **Xóa biến sau reset** | ✅ Xóa cả 2 | ❌ Không xóa |
| **Logic check** | flag==1 && elapsed>=60 | static bool + elapsed>=60 |
| **F5 reload** | Tạo biến mới → Reset lại | Biến còn, static mất → Reset lại |
| **MidnightReset** | Không reset (biến đã xóa) | Reset thêm (biến còn) |
| **Complexity** | Cao | **Thấp** ✅ |
| **User control** | Không | **Có** ✅ |

---

## WORKFLOW MỚI

### Tình huống 1: MT4 Restart

```
00:00:00 - VPS restart → MT4 start
00:00:05 - SPY Bot OnInit():
            ├─ GlobalVariable KHÔNG TỒN TẠI
            ├─ Tạo: gv_time = 00:00:05
            └─ static bool reset_done = false

00:01:05 - RunStartupReset():
            ├─ elapsed = 60s
            ├─ reset_done = false
            ├─ Reset!
            └─ reset_done = true

00:01:07 - RunStartupReset():
            └─ reset_done = true → Return (không reset nữa)

... Hệ thống chạy bình thường ...
```

### Tình huống 2: F5 Reload (Trong 60s đầu)

```
00:00:05 - OnInit() → Tạo gv_time = 00:00:05
00:00:30 - User nhấn F5
00:00:31 - OnInit() lại:
            ├─ gv_time ĐÃ CÓ (= 00:00:05)
            └─ Không tạo mới
            ├─ static bool reset_done = false (mới)

00:01:05 - RunStartupReset():
            ├─ elapsed = 60s (từ 00:00:05)
            ├─ Reset!
            └─ reset_done = true

Kết quả: Vẫn reset ĐÚNG 60s kể từ MT4 start (không phải 60s từ F5)
```

### Tình huống 3: F5 Reload (Sau 60s)

```
00:00:05 - OnInit() → Tạo gv_time = 00:00:05
00:01:05 - Reset lần 1 → reset_done = true
00:05:00 - User nhấn F5
00:05:01 - OnInit() lại:
            ├─ gv_time ĐÃ CÓ (= 00:00:05)
            └─ Không tạo mới
            ├─ static bool reset_done = false (MỚI - bị reset!)

00:05:02 - RunStartupReset():
            ├─ elapsed = 297s (>60s)
            ├─ reset_done = false
            ├─ Reset lần 2!
            └─ reset_done = true

Kết quả: Reset lại sau F5 → Đúng yêu cầu user (chấp nhận)
```

### Tình huống 4: MidnightReset

```
00:00:05 - OnInit() → gv_time = 00:00:05
00:01:05 - StartupReset chạy → reset_done = true
...
23:59:59 - (23 giờ sau)
00:00:00 - MidnightReset() chạy:
            └─ SmartTFReset() (độc lập, không check gv_time)

Kết quả: Reset thêm lần nữa → OK (theo yêu cầu user)
```

---

## ƯU ĐIỂM

1. **✅ Đơn giản:** Chỉ 1 biến GlobalVariable, logic rõ ràng
2. **✅ User control:** Có thể bật/tắt bằng input
3. **✅ Không conflict:** MidnightReset reset thêm → OK
4. **✅ F5 safe:** Reset lại sau F5 → Chấp nhận
5. **✅ Multi-symbol:** Mỗi symbol có biến riêng
6. **✅ Cleanup:** Xóa biến khi remove indicator

---

## HẠN CHẾ (CHẤP NHẬN)

1. **⚠️ F5 reload → Reset lại:**
   - Sau 60s: F5 → Reset lần 2
   - User nói: "Chấp nhận, không sao" ✅

2. **⚠️ MidnightReset → Reset thêm:**
   - 0h đêm → Reset lần 3
   - User nói: "Chấp nhận, không sao" ✅

3. **⚠️ HealthCheck → Reset thêm:**
   - 8h, 16h → Có thể reset thêm
   - User nói: "Chấp nhận, không sao" ✅

---

## TEST SCENARIOS

### Test 1: MT4 Restart
- ✅ VPS restart → MT4 start
- ✅ Sau 60s → Reset
- ✅ Không reset nữa

### Test 2: F5 Reload Trước 60s
- ✅ OnInit() → gv_time = T0
- ✅ F5 at T0+30s
- ✅ OnInit() lại → gv_time vẫn = T0
- ✅ Sau 60s từ T0 → Reset

### Test 3: F5 Reload Sau 60s
- ✅ Reset lần 1 at T0+60s
- ✅ F5 at T0+120s
- ✅ Static bool mất → Reset lần 2

### Test 4: Tắt EnableStartupReset
- ✅ Input = false
- ✅ Không reset

### Test 5: Nhiều Symbol
- ✅ BTCUSD: gv_time riêng
- ✅ LTCUSD: gv_time riêng
- ✅ Không conflict

---

## FILES MODIFIED

1. **MQL4/Indicators/Super_Spy7TF_V2.mq4**
   - Line 27: Thêm `input bool EnableStartupReset = true`
   - Line 2640-2646: OnInit() - Lưu timestamp (đơn giản)
   - Line 2660-2685: RunStartupReset() - Static bool + 60s check
   - Line 2929-2935: OnDeinit() - Cleanup 1 biến

---

## COMMIT MESSAGE

```
feat: Simplify StartupReset with static bool (user feedback)

CHANGES:
- Add input EnableStartupReset = true (user control)
- OnInit(): Save timestamp only (no flag variable)
- RunStartupReset(): Static bool + simple 60s check
- DON'T delete GlobalVariable (other resets need it)
- OnDeinit(): Cleanup simplified (1 variable only)

LOGIC:
- Static bool = false initially
- After 60s: Reset once → Static bool = true
- F5 reload: Static bool lost → Reset again → OK (accepted by user)
- MidnightReset: Reset again → OK (accepted by user)

USER FEEDBACK:
1. Don't delete variable (other resets use it)
2. Accept 2-3 resets (F5, MidnightReset)
3. Simple logic (no complex flag)
4. Add input toggle (default = true)

STATUS: Simplified and ready for testing
```

---

## KẾT LUẬN

✅ **LOGIC ĐƠN GIẢN HƠN NHIỀU**

**So với version 1:**
- Ít biến hơn (1 vs 2)
- Ít logic hơn (static bool vs flag check + delete)
- User control (có input)
- Chấp nhận reset nhiều lần (không sao)

**Status:** ✅ Ready for commit

---

**Implementation Date:** 2025-11-02 (Revision 2)
**Based on:** User feedback
**Simplified by:** Claude Code
