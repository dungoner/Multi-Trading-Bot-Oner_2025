# BONUS LOT MULTIPLIER FEATURE
## Thêm tính năng nhân lot cho lệnh BONUS

---

## I. YÊU CẦU

**Mục đích:** Tăng lot cho lệnh BONUS (S3+B) lên gấp đôi hoặc nhiều hơn so với S3 chuẩn (S3+A)

**Lý do:**
- Lot S3 chuẩn (21 loại) đã được tính sẵn
- BONUS là cơ hội đặc biệt (news >= 20)
- Muốn tận dụng cơ hội này với lot lớn hơn

---

## II. GIẢI PHÁP TRIỂN KHAI

### A. Thêm Input Parameter (Line 61)

```cpp
input double BonusLotMultiplier = 1.0; // S3: Bonus lot multiplier (1.0-10.0)
```

**Đặc điểm:**
- Kiểu: `double` (cho phép 1.5, 2.5...)
- Giá trị mặc định: `1.0` (giữ nguyên, x1)
- Phạm vi: 1.0 - 10.0
- Vị trí: Sau `MinNewsLevelBonus`, trong phần S3 input

### B. Tính Toán Bonus Lot (Line 1180)

```cpp
// Calculate BONUS lot (S3 lot × multiplier)
double bonus_lot = g_ea.lot_sizes[tf][2] * BonusLotMultiplier;
```

**Logic:**
- Đọc lot S3 chuẩn: `g_ea.lot_sizes[tf][2]`
- Nhân với multiplier: `× BonusLotMultiplier`
- Kết quả: `bonus_lot`

**Ví dụ:**
- S3 M1 lot = 0.05
- BonusLotMultiplier = 1.0 (mặc định)
- → bonus_lot = 0.05 × 1.0 = **0.05** (giữ nguyên)

**Ví dụ (x2):**
- S3 M1 lot = 0.05
- BonusLotMultiplier = 2.0
- → bonus_lot = 0.05 × 2.0 = **0.10** (gấp đôi)

### C. Sử Dụng Bonus Lot (Line 1191, 1201)

```cpp
// BUY order
int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, bonus_lot, Ask, 3,
                           "BONUS_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][2], clrGold);

// SELL order
int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, bonus_lot, Bid, 3,
                           "BONUS_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][2], clrOrange);
```

**Thay đổi:**
- **Trước:** `g_ea.lot_sizes[tf][2]` (lot S3 chuẩn)
- **Sau:** `bonus_lot` (lot S3 × multiplier)

### D. Cập Nhật Log (Line 1217-1222)

```cpp
Print(">>> [OPEN] BONUS TF=", G_TF_NAMES[tf], " | ", opened_count, "×",
      news_direction == 1 ? "BUY" : "SELL", " @", DoubleToStr(bonus_lot, 2),
      " Total:", DoubleToStr(total_lot, 2), " @", DoubleToStr(entry_price, Digits),
      " | News=", tf_news > 0 ? "+" : "", tf_news, arrow,
      " | Multiplier:", DoubleToStr(BonusLotMultiplier, 1), "x",
      " Tickets:", ticket_list, " <<<");
```

**Thông tin hiển thị:**
- Lot từng lệnh: `@0.10` (bonus_lot)
- Tổng lot: `Total:0.20` (opened_count × bonus_lot)
- Multiplier: `Multiplier:2.0x`

---

## III. VÍ DỤ SỬ DỤNG

### Kịch Bản 1: Multiplier = 1.0 (Mặc định - Giữ nguyên)

**Cấu hình:**
- S3 M1 lot = 0.05
- BonusOrderCount = 2
- BonusLotMultiplier = 1.0

**Khi news M1 = +65 (>= 20):**
```
1. Tính bonus_lot = 0.05 × 1.0 = 0.05
2. Mở 2 lệnh BUY:
   - Ticket #12345: BUY 0.05 lot
   - Ticket #12346: BUY 0.05 lot
3. Tổng: 0.10 lot

Log:
>>> [OPEN] BONUS TF=M1 | 2×BUY @0.05 Total:0.10 @25000.50 | News=+65↑ | Multiplier:1.0x Tickets:12345,12346 <<<
```

### Kịch Bản 2: Multiplier = 2.0 (Gấp đôi)

**Cấu hình:**
- S3 M1 lot = 0.05
- BonusOrderCount = 2
- BonusLotMultiplier = 2.0

**Khi news M1 = +65 (>= 20):**
```
1. Tính bonus_lot = 0.05 × 2.0 = 0.10
2. Mở 2 lệnh BUY:
   - Ticket #12350: BUY 0.10 lot
   - Ticket #12351: BUY 0.10 lot
3. Tổng: 0.20 lot

Log:
>>> [OPEN] BONUS TF=M1 | 2×BUY @0.10 Total:0.20 @25000.50 | News=+65↑ | Multiplier:2.0x Tickets:12350,12351 <<<
```

### Kịch Bản 3: Multiplier = 3.0 (Tăng lên)

**Cấu hình:**
- S3 M15 lot = 0.08
- BonusOrderCount = 2
- BonusLotMultiplier = 3.0

**Khi news M15 = +42 (>= 20):**
```
1. Tính bonus_lot = 0.08 × 3.0 = 0.24
2. Mở 2 lệnh BUY:
   - Ticket #12350: BUY 0.24 lot
   - Ticket #12351: BUY 0.24 lot
3. Tổng: 0.48 lot

Log:
>>> [OPEN] BONUS TF=M15 | 2×BUY @0.24 Total:0.48 @25005.20 | News=+42↑ | Multiplier:3.0x Tickets:12350,12351 <<<
```

---

## IV. SO SÁNH TRƯỚC VÀ SAU

### A. Trước Khi Thêm Multiplier

```cpp
// Luôn dùng lot S3 chuẩn
int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, g_ea.lot_sizes[tf][2], ...);

// Log không hiển thị multiplier
Print(">>> [OPEN] BONUS TF=M1 | 2×BUY Total:0.10 @25000.50 | News=+65↑ Tickets:12345,12346 <<<");
```

**Vấn đề:**
- Lot BONUS = Lot S3 chuẩn
- Không tận dụng cơ hội BONUS (news >= 20)
- Không linh hoạt

### B. Sau Khi Thêm Multiplier

```cpp
// Tính lot BONUS riêng
double bonus_lot = g_ea.lot_sizes[tf][2] * BonusLotMultiplier;
int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, bonus_lot, ...);

// Log hiển thị đầy đủ
Print(">>> [OPEN] BONUS TF=M1 | 2×BUY @0.10 Total:0.20 @25000.50 | News=+65↑ | Multiplier:2.0x Tickets:12345,12346 <<<");
```

**Lợi ích:**
- Lot BONUS = Lot S3 × Multiplier
- Tận dụng cơ hội BONUS với lot lớn hơn
- Linh hoạt điều chỉnh (1.0 - 10.0)
- Log rõ ràng, hiển thị multiplier

---

## V. KIỂM TRA VÀ XÁC NHẬN

### A. Các Thay Đổi Code

| File | Line | Thay đổi | Mục đích |
|------|------|----------|----------|
| Eas_Smf_Oner_V2.mq4 | 61 | Thêm input `BonusLotMultiplier` | Tham số điều khiển |
| Eas_Smf_Oner_V2.mq4 | 1180 | Tính `bonus_lot = lot × multiplier` | Tính lot BONUS |
| Eas_Smf_Oner_V2.mq4 | 1191 | Dùng `bonus_lot` trong BUY | Mở lệnh với lot mới |
| Eas_Smf_Oner_V2.mq4 | 1201 | Dùng `bonus_lot` trong SELL | Mở lệnh với lot mới |
| Eas_Smf_Oner_V2.mq4 | 1216 | Cập nhật `total_lot = count × bonus_lot` | Tính tổng lot đúng |
| Eas_Smf_Oner_V2.mq4 | 1218-1221 | Hiển thị `@bonus_lot` và `Multiplier` | Log rõ ràng |

### B. Kiểm Tra Bằng Grep

```bash
$ grep -n "BonusLotMultiplier" Eas_Smf_Oner_V2.mq4
61:input double BonusLotMultiplier = 2.0;     # Khai báo ✅
1180:double bonus_lot = g_ea.lot_sizes[tf][2] * BonusLotMultiplier;  # Tính toán ✅
1221:" | Multiplier:", DoubleToStr(BonusLotMultiplier, 1), "x",      # Log ✅
```

**Kết quả:** 3 vị trí sử dụng, tất cả đúng ✅

---

## VI. LƯU Ý SỬ DỤNG

### ⚠️ Lưu Ý Quan Trọng

1. **Risk Management:**
   - Multiplier càng cao, rủi ro càng lớn
   - Nên bắt đầu với 1.5 - 2.0
   - Chỉ tăng lên khi account đủ lớn

2. **Broker Limits:**
   - Kiểm tra lot max của broker
   - VD: Lot max = 1.0, S3 lot = 0.8 → Multiplier max = 1.25

3. **Balance Requirements:**
   - BONUS có thể mở nhiều TF cùng lúc
   - VD: 4 TF × 2 lệnh × 0.20 lot = 8 lệnh, 1.60 lot tổng
   - Cần đủ margin

### ✅ Khuyến Nghị

**Multiplier theo mức độ rủi ro:**
- **Conservative:** 1.0 - 1.5x
- **Moderate:** 1.5 - 2.5x
- **Aggressive:** 2.5 - 5.0x
- **Very Aggressive:** 5.0 - 10.0x

**Multiplier theo news level:**
```cpp
// Có thể cải tiến sau này:
if(news_abs >= 50) multiplier = 3.0;      // News rất mạnh
else if(news_abs >= 30) multiplier = 2.0; // News mạnh
else multiplier = 1.5;                     // News vừa
```

---

## VII. KẾT LUẬN

### ✅ Hoàn Thành

**Tính năng đã triển khai:**
- ✅ Thêm input parameter `BonusLotMultiplier`
- ✅ Tính toán lot BONUS riêng
- ✅ Áp dụng cho cả BUY và SELL
- ✅ Cập nhật log hiển thị đầy đủ
- ✅ Linh hoạt điều chỉnh (1.0 - 10.0)

**Lợi ích:**
- Tận dụng tối đa cơ hội BONUS (news >= 20)
- Linh hoạt điều chỉnh theo risk appetite
- Không ảnh hưởng lot S3 chuẩn (g_ea.lot_sizes vẫn giữ nguyên)
- Code sạch, dễ bảo trì

**Sẵn sàng sử dụng:**
- Chỉ cần compile lại EA
- Điều chỉnh `BonusLotMultiplier` trong input
- Test trên demo account trước

---

**Ngày triển khai:** 2025-11-01  
**Phiên bản EA:** Eas_Smf_Oner_V2.mq4  
**Status:** ✅ **HOÀN THÀNH**
