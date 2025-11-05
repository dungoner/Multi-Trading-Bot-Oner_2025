# 📦 SYNS Bot System - PORTABLE PYTHON PACKAGE

## 🎯 LOẠI 1: Code + Embedded Python (Không cần cài Python)

### CẤU TRÚC THƯ MỤC:

```
SYNS_Bot_Package/
├── python/                          ← Embedded Python (portable)
│   ├── python.exe
│   ├── python311.dll
│   ├── Lib/
│   └── ...
├── sync_http80_sender.py           ← Bot 0
├── sync1_sender_optimized.py       ← Bot 1
├── sync2_data_receiver.py          ← Bot 2
├── sync_server80data.py            ← Bot 3
├── bot_config.json                 ← Config chung (4 bot đọc file này)
├── START_0123_BOT.bat              ← Launcher chính
├── requirements.txt
└── README_PORTABLE_PACKAGE.md
```

---

## 📥 BƯỚC 1: TẢI PYTHON EMBEDDED

### Option A: Tải từ Python.org (KHUYẾN NGHỊ)

1. Truy cập: https://www.python.org/downloads/windows/
2. Tìm **Python 3.11.x** → Download **Windows embeddable package (64-bit)**
3. File tải về: `python-3.11.x-embed-amd64.zip`
4. Giải nén vào thư mục `python/`

### Option B: Tải trực tiếp (nhanh)

```cmd
REM Download Python 3.11.9 Embedded
curl -o python-embed.zip https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip

REM Extract
powershell -command "Expand-Archive -Path python-embed.zip -DestinationPath python"
```

---

## 🔧 BƯỚC 2: CÀI ĐẶT THƯ VIỆN

### 2.1. Enable pip trong Python Embedded

Mở file `python\python311._pth` và xóa dấu `#` trước dòng:

```
# Trước:
#import site

# Sau:
import site
```

### 2.2. Tải get-pip.py

```cmd
cd python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python.exe get-pip.py
```

### 2.3. Cài đặt thư viện

```cmd
cd ..
python\python.exe -m pip install -r requirements.txt
```

Hoặc cài thủ công:

```cmd
python\python.exe -m pip install Flask==3.0.0
python\python.exe -m pip install flask-cors==4.0.0
python\python.exe -m pip install requests==2.31.0
```

---

## ▶️ BƯỚC 3: CHẠY BOT

### Cách 1: Dùng START_0123_BOT.bat (Khuyến nghị)

```cmd
START_0123_BOT.bat
```

Chọn bot cần chạy:
- [0] Bot 0 - SENDER (Variant)
- [1] Bot 1 - SENDER (Optimized) ← Mặc định
- [2] Bot 2 - RECEIVER
- [3] Bot 3 - INTEGRATED

### Cách 2: Chạy trực tiếp

```cmd
REM Bot 1 (VPS - Sender)
python\python.exe sync1_sender_optimized.py

REM Bot 2 (Local - Receiver)
python\python.exe sync2_data_receiver.py
```

---

## ⚙️ CẤU HÌNH

### File: `bot_config.json`

**QUAN TRỌNG:** 4 bot đều đọc từ file `bot_config.json` này!

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

### VPS (Bot 1):
```cmd
START_0123_BOT.bat
→ Chọn [1] Bot 1
```

### Máy Local (Bot 2):
```cmd
START_0123_BOT.bat
→ Chọn [2] Bot 2
```

---

## ✅ LỢI ÍCH PORTABLE PACKAGE

- ✅ Không cần cài Python vào Windows
- ✅ Không xung đột với Python đã cài
- ✅ Dễ backup (copy toàn bộ thư mục)
- ✅ Dễ debug (thấy code .py)
- ✅ Windows Defender không báo virus
- ✅ Chạy được trên máy không có quyền admin

---

## 📁 ĐÓNG GÓI ĐỂ CHIA SẺ

### Nén thư mục (sau khi cài xong thư viện):

```cmd
REM Dùng 7-Zip hoặc WinRAR
7z a SYNS_Bot_Portable.zip python *.py *.bat *.json *.txt *.md
```

### Gửi cho người khác:

1. Giải nén `SYNS_Bot_Portable.zip`
2. Chỉnh `bot_config.json` (đường dẫn folder)
3. Chạy `START_0123_BOT.bat`

---

## ❓ TROUBLESHOOTING

### Lỗi: `python\python.exe` not found

→ Chưa tải Python Embedded. Làm lại BƯỚC 1.

### Lỗi: `No module named 'flask'`

→ Chưa cài thư viện. Làm lại BƯỚC 2.

### Lỗi: Port 80 bị chiếm

→ Chạy với quyền Administrator (right-click .bat → Run as Administrator)

---

## 📞 HỖ TRỢ

- File config: `bot_config.json`
- Log: Xem trong terminal khi chạy bot
- Dashboard: http://localhost:9070 (khi bot đang chạy)
