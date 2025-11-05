# 📦 SYNS Bot System - EXE PACKAGE

## 🎯 LOẠI 2: 4 File .EXE (Không cần Python, chạy ngay)

### CẤU TRÚC THƯ MỤC:

```
SYNS_Bot_EXE/
├── Bot0_HTTP80_Sender.exe          ← Bot 0 (Sender Variant)
├── Bot1_Sender_Optimized.exe       ← Bot 1 (Sender Optimized)
├── Bot2_Data_Receiver.exe          ← Bot 2 (Receiver)
├── Bot3_Server_Integrated.exe      ← Bot 3 (2-in-1)
├── bot_config.json                 ← Config chung (4 bot đọc file này)
├── START_0123_BOT_EXE.bat          ← Launcher cho .exe
└── README_EXE_PACKAGE.md
```

---

## 🔨 BƯỚC 1: BUILD 4 FILE .EXE

### Yêu cầu:
- Python 3.11+ đã cài
- PyInstaller

### Cách build:

```cmd
REM Option 1: Dùng script tự động (KHUYẾN NGHỊ)
build_exe.bat

REM Option 2: Build thủ công
pip install pyinstaller
pyinstaller --onefile --noconsole sync1_sender_optimized.py
```

File .exe sẽ được tạo trong thư mục `dist/`

---

## 📁 BƯỚC 2: TẠO PACKAGE

### Copy các file cần thiết:

```cmd
REM Tạo thư mục
mkdir SYNS_Bot_EXE
cd SYNS_Bot_EXE

REM Copy 4 file .exe từ dist/
copy ..\dist\Bot0_HTTP80_Sender.exe .
copy ..\dist\Bot1_Sender_Optimized.exe .
copy ..\dist\Bot2_Data_Receiver.exe .
copy ..\dist\Bot3_Server_Integrated.exe .

REM Copy config và launcher
copy ..\bot_config.json .
copy ..\START_0123_BOT_EXE.bat .
copy ..\README_EXE_PACKAGE.md .
```

---

## ▶️ BƯỚC 3: CHẠY BOT

### Cách 1: Dùng START_0123_BOT_EXE.bat (Khuyến nghị)

```cmd
START_0123_BOT_EXE.bat
```

Chọn bot cần chạy:
- [0] Bot 0 - SENDER (Variant)
- [1] Bot 1 - SENDER (Optimized) ← Mặc định
- [2] Bot 2 - RECEIVER
- [3] Bot 3 - INTEGRATED

### Cách 2: Double-click .exe trực tiếp

```
Bot1_Sender_Optimized.exe     ← VPS (Sender)
Bot2_Data_Receiver.exe        ← Local (Receiver)
```

---

## ⚙️ CẤU HÌNH

### File: `bot_config.json`

**QUAN TRỌNG:**
- 4 file .exe đều đọc từ `bot_config.json`
- File `bot_config.json` PHẢI nằm CÙNG THƯ MỤC với .exe

```json
{
  "mode": 1,
  "quiet_mode": true,
  "sender": {
    "vps_ip": "dungalading.duckdns.org",
    "api_port": 80,
    "dashboard_port": 9070,
    "csdl_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner3/"
  },
  "receiver": {
    "bot1_url": "http://dungalading.duckdns.org:80",
    "output_folder": "C:/PRO_ONER/MQL4/Files/DataAutoOner3/"
  }
}
```

**ĐỔI DOMAIN:**
- Không cần sửa config này!
- Chỉ cần update IP tại: https://www.duckdns.org

---

## 🚀 THỨ TỰ CHẠY

### 1. VPS (Bot 1 - Sender):
```cmd
Bot1_Sender_Optimized.exe
```
Hoặc:
```cmd
START_0123_BOT_EXE.bat → Chọn [1]
```

### 2. Máy Local (Bot 2 - Receiver):
```cmd
Bot2_Data_Receiver.exe
```
Hoặc:
```cmd
START_0123_BOT_EXE.bat → Chọn [2]
```

---

## ✅ LỢI ÍCH EXE PACKAGE

- ✅ Không cần cài Python
- ✅ Double-click chạy ngay
- ✅ Dễ deploy (copy .exe + config)
- ✅ Kích thước nhỏ (mỗi file ~15-20MB)
- ✅ Độc lập hoàn toàn

---

## ⚠️ LƯU Ý WINDOWS DEFENDER

### File .exe có thể bị Windows Defender chặn

**Nguyên nhân:** PyInstaller đóng gói Python code → Windows nghĩ là virus

**Giải pháp:**

### Option 1: Tắt tạm Windows Defender
```
Windows Security → Virus & threat protection →
Manage settings → Real-time protection → OFF
```

### Option 2: Thêm exception
```
Windows Security → Virus & threat protection →
Manage settings → Exclusions → Add or remove exclusions →
Add folder → Chọn thư mục chứa .exe
```

### Option 3: Whitelist khi Windows Defender báo
```
Khi Windows chặn:
More info → Run anyway
```

---

## 📁 ĐÓNG GÓI ĐỂ CHIA SẺ

### Nén thư mục:

```cmd
REM Dùng 7-Zip hoặc WinRAR
7z a SYNS_Bot_EXE.zip *.exe bot_config.json START_0123_BOT_EXE.bat README_EXE_PACKAGE.md
```

### Gửi cho người khác:

1. Giải nén `SYNS_Bot_EXE.zip`
2. Chỉnh `bot_config.json` (đường dẫn folder)
3. Chạy `START_0123_BOT_EXE.bat` hoặc double-click .exe

---

## ❓ TROUBLESHOOTING

### Lỗi: Windows Defender chặn .exe

→ Làm theo hướng dẫn "LƯU Ý WINDOWS DEFENDER" ở trên

### Lỗi: `bot_config.json` not found

→ File config PHẢI nằm cùng thư mục với .exe

### Lỗi: Port 80 bị chiếm

→ Right-click .exe → Run as Administrator

### .exe không chạy (không có log gì)

→ Chạy từ CMD để xem lỗi:
```cmd
Bot1_Sender_Optimized.exe
```

---

## 🔄 CẬP NHẬT PHIÊN BẢN MỚI

Khi có code mới:

```cmd
REM 1. Build lại .exe
build_exe.bat

REM 2. Copy .exe mới thay thế .exe cũ
copy dist\Bot1_Sender_Optimized.exe SYNS_Bot_EXE\

REM 3. GIỮ NGUYÊN bot_config.json (config của bạn)
```

---

## 📞 HỖ TRỢ

- File config: `bot_config.json` (phải cùng thư mục với .exe)
- Dashboard: http://localhost:9070 (khi bot đang chạy)
- Firewall: Port 80 và 9070 phải mở
