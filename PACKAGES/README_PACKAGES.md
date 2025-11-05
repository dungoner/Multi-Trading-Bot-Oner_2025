# 📦 SYNS BOT SYSTEM - 2 PACKAGES RELEASE

## 🎯 2 LOẠI ĐÓNG GÓI SẴN SÀNG

Bạn có **2 file ZIP** để chọn:

### 📦 PACKAGE 1: **SYNS_Bot_Portable.zip** (7.5 MB)
**Code + Python Embedded - KHUYẾN NGHỊ CHO MỚI BẮT ĐẦU**

✅ Có sẵn Python portable
✅ Giải nén là chạy ngay
✅ Không cần cài Python
✅ Không cần build gì cả
✅ Windows Defender không báo virus

### 📦 PACKAGE 2: **SYNS_Bot_Source_For_EXE.zip** (104 KB)
**Source Code để Build thành .EXE**

✅ Nhẹ (chỉ code)
✅ Build thành 4 file .exe
✅ Chạy độc lập (không cần Python)
⚠️ Cần Python + PyInstaller để build
⚠️ Windows Defender có thể báo virus

---

## 📥 PACKAGE 1: SYNS_Bot_Portable.zip

### Giải nén:
```cmd
Giải nén SYNS_Bot_Portable.zip vào thư mục bất kỳ
Ví dụ: C:\SYNS_Bot\
```

### Cấu trúc sau khi giải nén:
```
C:\SYNS_Bot\
├── python\                         ← Python 3.10 Embedded
│   ├── python.exe
│   ├── python310.dll
│   ├── Scripts\
│   │   ├── pip.exe
│   │   └── flask.exe
│   └── ...
├── sync_http80_sender.py          ← Bot 0
├── sync1_sender_optimized.py      ← Bot 1
├── sync2_data_receiver.py         ← Bot 2
├── sync_server80data.py           ← Bot 3
├── bot_config.json                ← Config chung
├── START_0123_BOT.bat             ← Chạy file này
├── requirements.txt
└── README_PORTABLE_PACKAGE.md     ← Đọc hướng dẫn chi tiết
```

### Cài thư viện (LẦN ĐẦU TIÊN):

```cmd
cd C:\SYNS_Bot

REM Bước 1: Enable pip
notepad python\python310._pth
    → Xóa dấu # trước dòng: import site
    → Save và đóng

REM Bước 2: Cài pip
python\python.exe -m ensurepip

REM Bước 3: Cài thư viện
python\python.exe -m pip install -r requirements.txt
```

### Chạy Bot:

```cmd
REM Cách 1: Dùng launcher (Khuyến nghị)
START_0123_BOT.bat

REM Cách 2: Chạy trực tiếp
python\python.exe sync1_sender_optimized.py
```

**CHI TIẾT:** Đọc file `README_PORTABLE_PACKAGE.md` trong package

---

## 📥 PACKAGE 2: SYNS_Bot_Source_For_EXE.zip

### Giải nén:
```cmd
Giải nén SYNS_Bot_Source_For_EXE.zip vào thư mục bất kỳ
Ví dụ: C:\SYNS_Bot_Source\
```

### Cấu trúc sau khi giải nén:
```
C:\SYNS_Bot_Source\
├── sync_http80_sender.py
├── sync1_sender_optimized.py
├── sync2_data_receiver.py
├── sync_server80data.py
├── bot_config.json
├── build_exe.bat                  ← Chạy file này để build
├── START_0123_BOT_EXE.bat
├── requirements.txt
└── README_EXE_PACKAGE.md          ← Đọc hướng dẫn chi tiết
```

### YÊU CẦU:
- Python 3.10+ đã cài trên Windows
- PyInstaller: `pip install pyinstaller`

### Build 4 file .EXE:

```cmd
cd C:\SYNS_Bot_Source

REM Cài PyInstaller (nếu chưa có)
pip install pyinstaller

REM Build tự động (tạo 4 .exe)
build_exe.bat
```

File .exe sẽ được tạo trong thư mục `dist\`:
- `Bot0_HTTP80_Sender.exe`
- `Bot1_Sender_Optimized.exe`
- `Bot2_Data_Receiver.exe`
- `Bot3_Server_Integrated.exe`

### Tạo package EXE hoàn chỉnh:

```cmd
REM Tạo thư mục deploy
mkdir C:\SYNS_Bot_EXE

REM Copy 4 .exe
copy dist\*.exe C:\SYNS_Bot_EXE\

REM Copy config và launcher
copy bot_config.json C:\SYNS_Bot_EXE\
copy START_0123_BOT_EXE.bat C:\SYNS_Bot_EXE\
```

### Chạy:

```cmd
cd C:\SYNS_Bot_EXE
START_0123_BOT_EXE.bat
```

**CHI TIẾT:** Đọc file `README_EXE_PACKAGE.md` trong package

---

## ⚙️ CẤU HÌNH - bot_config.json

**QUAN TRỌNG:** File `bot_config.json` ở trong cả 2 package

```json
{
  "sender": {
    "vps_ip": "dungalading.duckdns.org",
    "csdl_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner3/"
  },
  "receiver": {
    "bot1_url": "http://dungalading.duckdns.org:80",
    "output_folder": "C:/PRO_ONER/MQL4/Files/DataAutoOner3/"
  }
}
```

**Chỉnh lại đường dẫn folder cho phù hợp với máy của bạn!**

---

## 🚀 THỨ TỰ CHẠY BOT

### VPS (Bot 1 - Sender):
1. Giải nén package
2. Cài thư viện (nếu dùng Portable) hoặc Build .exe
3. Chạy Bot 1:
   ```cmd
   START_0123_BOT.bat → Chọn [1]
   ```

### Máy Local (Bot 2 - Receiver):
1. Giải nén package
2. Cài thư viện (nếu dùng Portable) hoặc Build .exe
3. **ĐỢI Bot 1 chạy xong trước**
4. Chạy Bot 2:
   ```cmd
   START_0123_BOT.bat → Chọn [2]
   ```

---

## 📊 SO SÁNH 2 PACKAGE

| Tính năng | PACKAGE 1 (Portable) | PACKAGE 2 (EXE) |
|-----------|---------------------|-----------------|
| Kích thước | 7.5 MB | 104 KB (source) / ~60 MB (sau build) |
| Cần cài Python? | ❌ Không | ✅ Có (để build) |
| Cần build? | ❌ Không | ✅ Có (chạy build_exe.bat) |
| Chạy ngay? | ✅ Có (sau cài thư viện) | ❌ Không (phải build trước) |
| Windows Defender | ✅ Không báo | ⚠️ Có thể báo virus |
| Dễ debug | ✅ Có (thấy code .py) | ❌ Khó (đã compile) |
| Khuyến nghị | 🌟 Người mới | ⭐ Người có kinh nghiệm |

---

## ❓ NÊN CHỌN PACKAGE NÀO?

### Chọn PACKAGE 1 (Portable) nếu:
- ✅ Muốn chạy ngay, không muốn build
- ✅ Không có Python trên máy
- ✅ Muốn xem code dễ dàng
- ✅ Không muốn Windows Defender chặn

### Chọn PACKAGE 2 (EXE) nếu:
- ✅ Đã có Python trên máy
- ✅ Muốn file .exe độc lập
- ✅ Biết cách xử lý Windows Defender
- ✅ Muốn deploy nhanh (chỉ copy .exe)

---

## 🔄 CẬP NHẬT IP VPS

Khi đổi IP VPS:

1. Vào: https://www.duckdns.org
2. Update: `dungalading.duckdns.org` → IP mới
3. **XONG!**

❌ KHÔNG cần sửa code
❌ KHÔNG cần sửa config
❌ KHÔNG cần rebuild .exe

---

## 🆘 HỖ TRỢ

### PACKAGE 1 (Portable):
- Đọc: `README_PORTABLE_PACKAGE.md`
- Lỗi thư viện → Chạy lại: `python\python.exe -m pip install -r requirements.txt`
- Lỗi port 80 → Run as Administrator

### PACKAGE 2 (EXE):
- Đọc: `README_EXE_PACKAGE.md`
- Build lỗi → Kiểm tra Python và PyInstaller đã cài chưa
- Windows Defender chặn → Thêm exception

---

## 📞 LIÊN HỆ

- Dashboard khi bot chạy: http://localhost:9070
- Config file: `bot_config.json`
- Domain management: https://www.duckdns.org

---

**🎉 CHÚC BẠN SỬ DỤNG THÀNH CÔNG! 🎉**
