# PROMPT CHO NEWCHAT SESSION MỚI

## BỐI CẢNH
Session trước đã ĐỌC code nhưng HIỂU SAI hệ thống và viết README.md SAI BÉT.
Session mới cần làm lại từ đầu với phương pháp ĐÚNG.

---

## BƯỚC 1: HIỂU TOÀN BỘ HỆ THỐNG

### YÊU CẦU:
Đọc toàn bộ code của 2 bot để hiểu THẬT SỰ hệ thống, KHÔNG ĐOÁN, KHÔNG SUY LUẬN.

### CÁC FILE CẦN ĐỌC (THEO THỨ TỰ):

1. **File SPY Bot:** `MQL4/Indicators/Super_Spy7TF_V2.mq4` (2946 dòng)
   - Đọc TOÀN BỘ từ đầu đến cuối
   - Chú ý: Cấu trúc struct, các hàm chính, cách ghi CSDL

2. **File EA Auto:** `MQL4/Experts/Eas_Smf_Oner_V2.mq4` (2050 dòng)
   - Đọc TOÀN BỘ từ đầu đến cuối
   - Chú ý: Cách đọc CSDL, 3 strategies S1/S2/S3

3. **File README cũ (nếu còn):** Để tham khảo cấu trúc cũ (dễ hiểu hơn)

### SAU KHI ĐỌC, TRẢ LỜI CÁC CÂU HỎI SAU:

#### Câu hỏi 1: Cấu trúc CSDL
**Q1.1:** CSDL có bao nhiêu cột? Liệt kê TẤT CẢ 10 cột với tên và mô tả ngắn.

**Q1.2:** "CSDL có 10 cột chia làm 2 phần" - 2 phần này là gì? Giải thích rõ ràng:
- Phần 1: Cột nào đến cột nào? Dùng để làm gì?
- Phần 2: Cột nào đến cột nào? Dùng để làm gì?

**Q1.3:** Tín hiệu GỐC là gì? Đến từ đâu? Ghi vào cột nào?

#### Câu hỏi 2: SPY Bot
**Q2.1:** SPY Bot có BẤO NHIÊU phần xử lý? (Không đoán, dựa vào code)

**Q2.2:** Mỗi phần xử lý cái gì? Ghi vào cột nào trong CSDL?

**Q2.3:** Hàm nào ghi CSDL? Tần suất ghi là bao nhiêu?

#### Câu hỏi 3: EA Auto
**Q3.1:** EA Auto đọc từ file CSDL nào? (CSDL1 hay CSDL2? Folder nào?)

**Q3.2:** S1, S2, S3 mỗi strategy đọc CỘT NÀO trong CSDL? Liệt kê cụ thể:
- S1 đọc: cột ?
- S2 đọc: cột ?
- S3 đọc: cột ?

**Q3.3:** Có phải S1+S2 cùng đọc 1 cột, S3 đọc cột khác không? Nếu đúng, giải thích tại sao.

#### Câu hỏi 4: Luồng dữ liệu
**Q4.1:** Vẽ sơ đồ luồng dữ liệu HOÀN CHỈNH từ WallStreet EA → SPY Bot → CSDL → EA Auto, bao gồm:
- Tất cả các cột được ghi/đọc
- Thời điểm ghi/đọc
- Các hàm liên quan

**Q4.2:** "MỐC NỐI" giữa 2 bot là gì? Có mấy mốc nối? Mỗi mốc nối là cột nào?

---

## BƯỚC 2: TÌM HIỂU VẤN ĐỀ CỤ THỂ

### BỐI CẢNH VẤN ĐỀ:
User phát hiện: NEWS hiển thị trên Dashboard của SPY Bot KHÁC với NEWS trên Dashboard của EA Auto, mặc dù cả 2 đều đọc từ cùng CSDL.

### YÊU CẦU:

**Q5.1: Phân tích Dashboard SPY Bot**
- File code: `Super_Spy7TF_V2.mq4`
- Tìm hàm `PrintDashboard()` hoặc tương tự
- NEWS hiển thị lấy từ BIẾN NÀO? (dòng code cụ thể)
- Biến đó được CẬP NHẬT Ở ĐÂU? KHI NÀO?

**Q5.2: Phân tích Dashboard EA Auto**
- File code: `Eas_Smf_Oner_V2.mq4`
- Tìm hàm `UpdateDashboard()` hoặc tương tự
- NEWS hiển thị lấy từ BIẾN NÀO? (dòng code cụ thể)
- Biến đó được LOAD TỪ ĐÂU? KHI NÀO?

**Q5.3: So sánh 2 dashboard**
Tạo bảng so sánh:

| Điểm | SPY Dashboard | EA Dashboard |
|------|---------------|--------------|
| NEWS lấy từ biến | ? | ? |
| Biến được update ở hàm | ? | ? |
| Tần suất update | ? | ? |
| Nguồn dữ liệu gốc | ? | ? |

**Q5.4: Tìm nguyên nhân gốc rễ**
- Tại sao 2 dashboard hiển thị NEWS KHÁC NHAU?
- CSDL1 và CSDL2 có ĐỒNG NHẤT không? (kiểm tra code ghi file)
- EA đọc CSDL có đúng cột không?
- Có phải EA đọc từ file CŨ/CACHE không?
- Có phải timing issue (SPY ghi giây chẵn, EA đọc giây lẻ)?

**Q5.5: Đề xuất giải pháp**
- Vấn đề nằm ở đâu? (SPY ghi sai, EA đọc sai, hay file sync sai?)
- Cần sửa ở file nào, hàm nào, dòng nào?

---

## LƯU Ý QUAN TRỌNG CHO NEWCHAT SESSION:

1. **KHÔNG ĐOÁN:** Mọi câu trả lời phải dựa vào CODE THỰC TẾ, kèm số dòng cụ thể
2. **ĐỌC KỸ:** Đọc toàn bộ code, không skip
3. **KIỂM TRA KỸ:** So sánh CSDL1 vs CSDL2, SPY ghi vs EA đọc
4. **TÌM GỐC RỄ:** Không chỉ nói "khác nhau", mà phải tìm TẠI SAO khác nhau
5. **CODE REFERENCE:** Mỗi câu trả lời phải có tên file + số dòng

---

## OUTPUT MONG MUỐN:

Sau khi hoàn thành 2 bước, tạo 1 báo cáo gồm:

1. **Phần 1: Trả lời đầy đủ câu hỏi Q1.1 → Q4.2**
2. **Phần 2: Phân tích vấn đề NEWS Dashboard (Q5.1 → Q5.5)**
3. **Phần 3: Đề xuất sửa README.md ĐÚNG** (chỉ sau khi đã hiểu rõ hệ thống)

---

## KẾT QUẢ MONG ĐỢI:

- Newchat session hiểu ĐÚNG về cấu trúc 10 cột và 2 phần
- Tìm ra nguyên nhân tại sao NEWS dashboard khác nhau
- Viết được README.md ĐÚNG dựa trên sự hiểu biết THẬT

---

**CHÚ Ý:** Session trước đã SAI vì không đọc kỹ code và ĐOÁN. Session mới phải đọc TỪNG DÒNG CODE và TRẢ LỜI CỤ THỂ.
