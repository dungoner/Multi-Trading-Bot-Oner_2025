# 🪟 Hướng Dẫn Cài Đặt TradeLocker Bot trên Windows VPS

**Dành cho người mới bắt đầu** | **Step-by-step guide for beginners**

---

## 📋 Mục Lục | Table of Contents

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cài đặt Python](#2-cài-đặt-python)
3. [Tải source code](#3-tải-source-code)
4. [Cài đặt thư viện](#4-cài-đặt-thư-viện)
5. [Cấu hình bot](#5-cấu-hình-bot)
6. [Chạy bot lần đầu](#6-chạy-bot-lần-đầu)
7. [Chạy bot tự động](#7-chạy-bot-tự-động)
8. [Giám sát và troubleshooting](#8-giám-sát-và-troubleshooting)

---

## 1. Yêu Cầu Hệ Thống

### Phần cứng tối thiểu
- **CPU**: 1 core (2 cores recommended)
- **RAM**: 1GB (2GB recommended)
- **Disk**: 10GB free space
- **Network**: Stable internet connection

### Phần mềm
- **OS**: Windows Server 2016/2019/2022 hoặc Windows 10/11
- **Python**: 3.8 trở lên (recommended 3.11)
- **TradeLocker Account**: Demo hoặc Live

---

## 2. Cài Đặt Python

### Bước 2.1: Tải Python

1. Mở trình duyệt, truy cập: https://www.python.org/downloads/
2. Click nút **"Download Python 3.11.x"** (phiên bản mới nhất)
3. Chờ file `.exe` tải về (khoảng 25MB)

### Bước 2.2: Cài đặt Python

1. **Chạy file cài đặt** (ví dụ: `python-3.11.7-amd64.exe`)
2. ⚠️ **QUAN TRỌNG**: Check vào ô **"Add Python 3.11 to PATH"** (ở dưới cùng)
3. Click **"Install Now"**
4. Chờ cài đặt hoàn tất (2-3 phút)
5. Click **"Close"**

### Bước 2.3: Kiểm tra Python đã cài đặt

1. Nhấn `Win + R`, gõ `cmd`, nhấn Enter
2. Trong Command Prompt, gõ:
   ```cmd
   python --version
   ```
3. Kết quả phải hiện: `Python 3.11.x` (hoặc tương tự)
4. Kiểm tra pip:
   ```cmd
   pip --version
   ```
5. Kết quả phải hiện: `pip 23.x.x from ...`

✅ **Nếu cả 2 lệnh đều chạy được → Python đã cài đặt thành công!**

---

## 3. Tải Source Code

### Phương án A: Tải từ GitHub (Recommended)

#### Bước 3.1: Cài đặt Git cho Windows

1. Truy cập: https://git-scm.com/download/win
2. Tải file **"64-bit Git for Windows Setup"**
3. Chạy file cài đặt, click **"Next"** hết (giữ mặc định)
4. Click **"Install"** và chờ hoàn tất

#### Bước 3.2: Clone repository

1. Mở Command Prompt (`Win + R` → gõ `cmd` → Enter)
2. Di chuyển đến thư mục muốn lưu bot:
   ```cmd
   cd C:\
   mkdir TradingBots
   cd TradingBots
   ```
3. Clone repository:
   ```cmd
   git clone https://github.com/dungoner/Multi-Trading-Bot-Oner_2025.git
   ```
4. Chờ tải về hoàn tất (30 giây - 2 phút tùy mạng)
5. Di chuyển vào thư mục TradeLocker:
   ```cmd
   cd Multi-Trading-Bot-Oner_2025\TradeLocker
   ```

### Phương án B: Tải file ZIP (Dễ hơn cho người mới)

1. Truy cập: https://github.com/dungoner/Multi-Trading-Bot-Oner_2025
2. Click nút xanh **"Code"** → Click **"Download ZIP"**
3. Giải nén file ZIP vào `C:\TradingBots\`
4. Mở Command Prompt:
   ```cmd
   cd C:\TradingBots\Multi-Trading-Bot-Oner_2025\TradeLocker
   ```

---

## 4. Cài Đặt Thư Viện

### Bước 4.1: Cài đặt dependencies

Trong Command Prompt (đang ở thư mục `TradeLocker`):

```cmd
pip install -r requirements.txt
```

**Giải thích**: Lệnh này cài đặt tất cả thư viện cần thiết:
- `tradelocker` - TradeLocker API library
- `requests` - HTTP requests cho CSDL data

Chờ cài đặt hoàn tất (1-2 phút).

### Bước 4.2: Kiểm tra cài đặt thành công

```cmd
pip list | findstr tradelocker
pip list | findstr requests
```

Kết quả phải hiện 2 dòng chứa `tradelocker` và `requests`.

✅ **Nếu có 2 dòng → Thư viện đã cài đặt thành công!**

---

## 5. Cấu Hình Bot

### Bước 5.1: Mở file cấu hình

1. Mở **Notepad** hoặc **Notepad++** (recommended)
2. Mở file: `C:\TradingBots\Multi-Trading-Bot-Oner_2025\TradeLocker\config.json`

⚠️ **Lưu ý**: Bot sử dụng file `config.json` để cấu hình, không cần chỉnh sửa file `.py` nữa!

### Bước 5.2: Cấu hình TradeLocker credentials

Tìm và thay đổi phần `"tradelocker"`:

```json
"tradelocker": {
  "_comment": "TradeLocker Account Credentials",
  "environment": "https://demo.tradelocker.com",
  "username": "your_email@example.com",        ← Thay bằng email của bạn
  "password": "YOUR_PASSWORD",                 ← Thay bằng password của bạn
  "server": "Demo"                             ← Thay bằng tên server
}
```

**Ví dụ cấu hình DEMO:**

```json
"tradelocker": {
  "_comment": "TradeLocker Account Credentials",
  "environment": "https://demo.tradelocker.com",
  "username": "john.trader@gmail.com",
  "password": "MySecurePass123",
  "server": "Demo"
}
```

### Bước 5.3: Cấu hình HTTP API (CSDL Data Source)

Tìm và kiểm tra phần `"csdl"`:

```json
"csdl": {
  "_comment": "CSDL Data Source: FOLDER_1, FOLDER_2, FOLDER_3, or HTTP_API",
  "source": "HTTP_API",
  "HTTP_Server_IP": "dungalading.duckdns.org",
  "HTTP_API_Key": "",
  "EnableSymbolNormalization": false
}
```

⚠️ **Lưu ý**: Nếu bạn có VPS riêng chạy SPY Bot, thay đổi `HTTP_Server_IP` thành IP/domain của bạn.

### Bước 5.4: Cấu hình Trading Settings (Tùy chọn)

**Bật/tắt Timeframes:**

```json
"timeframes": {
  "_comment": "Enable/Disable Timeframes (true/false)",
  "M1": false,   ← M1 (không khuyến nghị)
  "M5": true,    ← M5 ✓ Bật
  "M15": true,   ← M15 ✓ Bật
  "M30": true,   ← M30 ✓ Bật
  "H1": true,    ← H1 ✓ Bật
  "H4": true,    ← H4 ✓ Bật
  "D1": false    ← D1 (không khuyến nghị)
}
```

**Bật/tắt Strategies:**

```json
"strategies": {
  "_comment": "Enable/Disable Strategies (true/false)",
  "S1_HOME": true,   ← S1: Binary/News
  "S2_TREND": true,  ← S2: Trend D1
  "S3_NEWS": true    ← S3: News Alignment
}
```

**Risk Management:**

```json
"risk": {
  "_comment": "Risk Management Settings",
  "FixedLotSize": 0.1,        ← Lot size (0.01-1.0)
  "MaxLoss_Fallback": -1000.0 ← Max loss fallback ($USD)
}
```

### Bước 5.5: Lưu file

Nhấn `Ctrl + S` để lưu file.

---

## 6. Chạy Bot Lần Đầu

### Bước 6.1: Test chạy bot

1. Mở Command Prompt
2. Di chuyển đến thư mục TradeLocker:
   ```cmd
   cd C:\TradingBots\Multi-Trading-Bot-Oner_2025\TradeLocker
   ```
3. Chạy bot với symbol mặc định (BTCUSD):
   ```cmd
   python TradeLocker_MTF_ONER.py
   ```

### Bước 6.2: Kiểm tra kết quả

Bot sẽ hiển thị:

```
==============================================================================
TradeLocker MTF ONER Bot - Multi Timeframe Expert Advisor
Bot EA nhiều khung thời gian cho TradeLocker
==============================================================================
Version: TL_V1 - Converted from MT5 EA V2
Logic: 100% identical to MT5 EA - NO CHANGES
==============================================================================

2025-01-07 14:30:00 [INFO] [INIT] Connecting to TradeLocker...
2025-01-07 14:30:01 [INFO] [INIT] TradeLocker connection successful ✓
2025-01-07 14:30:01 [INFO] [INIT] Instrument ID for BTCUSD: 12345
2025-01-07 14:30:01 [INFO] [INIT] BTCUSD CRYPTO | Broker:TradeLocker/Demo | Leverage:TL:100 ✓
2025-01-07 14:30:01 [INFO] [INIT] EA initialization completed ✓
2025-01-07 14:30:01 [INFO] [START] Bot started successfully ✓
2025-01-07 14:30:01 [INFO] [START] Press Ctrl+C to stop
```

✅ **Nếu thấy "Bot started successfully" → Bot đã chạy thành công!**

### Bước 6.3: Xem Dashboard (Real-time)

Bot sẽ hiển thị dashboard mỗi giây (nếu `ShowDashboard = True`):

```
================================================================================
TradeLocker MTF ONER - BTCUSD
================================================================================
Account: Balance=$10000.00 | Equity=$10000.00 | DD=0.00%
Orders: 0 | Profit=$0.00 | Loss=$0.00
--------------------------------------------------------------------------------
M5   | Sig:NONE Age:1m     | S1:□ S2:□ S3:□ | P&L:$+0.00
M15  | Sig:NONE Age:5m     | S1:□ S2:□ S3:□ | P&L:$+0.00
M30  | Sig:NONE Age:10m    | S1:□ S2:□ S3:□ | P&L:$+0.00
H1   | Sig:NONE Age:30m    | S1:□ S2:□ S3:□ | P&L:$+0.00
H4   | Sig:NONE Age:2h     | S1:□ S2:□ S3:□ | P&L:$+0.00
--------------------------------------------------------------------------------
BONUS: None | IDLE | Last:14:30:05
================================================================================
```

### Bước 6.4: Dừng bot

Nhấn `Ctrl + C` trong Command Prompt để dừng bot:

```
^C
2025-01-07 14:35:00 [INFO]
[SIGNAL] Shutdown signal received
2025-01-07 14:35:00 [INFO] [STOP] Stopping bot...
2025-01-07 14:35:01 [INFO] [STOP] Bot stopped ✓
```

---

## 7. Chạy Bot Tự Động

### Phương án A: Sử dụng Task Scheduler (Recommended)

#### Bước 7.1: Tạo file batch script

1. Mở Notepad
2. Gõ nội dung sau:

```batch
@echo off
cd C:\TradingBots\Multi-Trading-Bot-Oner_2025\TradeLocker
python TradeLocker_MTF_ONER.py BTCUSD >> logs\bot_%date:~-4,4%-%date:~-10,2%-%date:~-7,2%.log 2>&1
```

3. Lưu với tên: `C:\TradingBots\start_tradelocker_bot.bat`
4. Chọn **"All Files"** trong Save as type

#### Bước 7.2: Tạo Task Scheduler

1. Nhấn `Win + R`, gõ `taskschd.msc`, nhấn Enter
2. Click **"Create Basic Task"** (bên phải)
3. Name: `TradeLocker Bot - BTCUSD`
4. Trigger: **"When the computer starts"**
5. Action: **"Start a program"**
6. Program/script: `C:\TradingBots\start_tradelocker_bot.bat`
7. Click **"Finish"**

#### Bước 7.3: Cấu hình Task để chạy khi khởi động

1. Trong Task Scheduler, tìm task vừa tạo
2. Right-click → **Properties**
3. Tab **"General"**:
   - Check **"Run whether user is logged on or not"**
   - Check **"Run with highest privileges"**
4. Tab **"Conditions"**:
   - Uncheck **"Start the task only if the computer is on AC power"**
5. Tab **"Settings"**:
   - Check **"Allow task to be run on demand"**
   - Check **"If the task fails, restart every"** → 1 minute
6. Click **"OK"**

#### Bước 7.4: Test Task

1. Right-click task → **"Run"**
2. Mở Task Manager (`Ctrl + Shift + Esc`)
3. Tab **"Details"** → Tìm `python.exe`
4. Nếu thấy `python.exe` đang chạy → Task hoạt động!

### Phương án B: Chạy trong background với pythonw

Tạo file `start_bot_background.bat`:

```batch
@echo off
cd C:\TradingBots\Multi-Trading-Bot-Oner_2025\TradeLocker
start /B pythonw TradeLocker_MTF_ONER.py BTCUSD
```

Chạy file này để bot chạy ngầm (không hiện cửa sổ).

---

## 8. Giám Sát và Troubleshooting

### 8.1: Xem log file

Nếu bot chạy bằng Task Scheduler, log được lưu tại:

```
C:\TradingBots\Multi-Trading-Bot-Oner_2025\TradeLocker\logs\bot_2025-01-07.log
```

Mở bằng Notepad để xem:

```cmd
notepad C:\TradingBots\Multi-Trading-Bot-Oner_2025\TradeLocker\logs\bot_2025-01-07.log
```

### 8.2: Lỗi thường gặp

#### Lỗi 1: "TradeLocker library not installed"

**Nguyên nhân**: Chưa cài đặt thư viện `tradelocker`

**Giải quyết**:
```cmd
pip install tradelocker requests
```

#### Lỗi 2: "Failed to connect to TradeLocker"

**Nguyên nhân**: Sai username/password hoặc server name

**Giải quyết**:
1. Kiểm tra lại `TL_Username`, `TL_Password`, `TL_Server` trong file config
2. Đảm bảo đăng nhập được vào TradeLocker web
3. Thử với Demo account trước khi dùng Live

#### Lỗi 3: "Cannot find instrument ID for symbol"

**Nguyên nhân**: Symbol không tồn tại hoặc sai tên

**Giải quyết**:
1. Kiểm tra symbol name (ví dụ: `BTCUSD`, `EURUSD`, `XAUUSD`)
2. Thử symbol khác: `python TradeLocker_MTF_ONER.py EURUSD`
3. Nếu vẫn lỗi, set `EnableSymbolNormalization: bool = True` trong config

#### Lỗi 4: "HTTP_ERROR: Server returned status code 404"

**Nguyên nhân**: CSDL API không hoạt động hoặc sai IP

**Giải quyết**:
1. Kiểm tra `HTTP_Server_IP` trong config
2. Test API bằng browser: `http://dungalading.duckdns.org/api/csdl/BTCUSD_LIVE.json`
3. Nếu API không hoạt động, liên hệ admin VPS

#### Lỗi 5: Bot tự tắt sau vài giây

**Nguyên nhân**: Crash do lỗi code hoặc network

**Giải quyết**:
1. Xem log file để biết nguyên nhân
2. Chạy bot với debug mode: Set `DebugMode: bool = True` trong config
3. Báo lỗi với log đầy đủ

### 8.3: Kiểm tra bot có đang chạy không

**Cách 1**: Task Manager
1. Nhấn `Ctrl + Shift + Esc`
2. Tab **"Details"**
3. Tìm `python.exe` hoặc `pythonw.exe`

**Cách 2**: Command Prompt
```cmd
tasklist | findstr python
```

Kết quả phải có: `python.exe` hoặc `pythonw.exe`

### 8.4: Dừng bot đang chạy

**Cách 1**: Task Manager
1. Tìm `python.exe` trong tab **"Details"**
2. Right-click → **"End task"**

**Cách 2**: Command Prompt
```cmd
taskkill /F /IM python.exe
```

---

## 📞 Hỗ Trợ | Support

### Tài liệu
- **README**: `C:\TradingBots\Multi-Trading-Bot-Oner_2025\TradeLocker\README.md`
- **GitHub**: https://github.com/dungoner/Multi-Trading-Bot-Oner_2025

### Báo lỗi
1. Tạo file log đầy đủ
2. Chụp màn hình lỗi
3. Tạo Issue trên GitHub

---

## ✅ Checklist Hoàn Thành

- [ ] Cài đặt Python 3.8+ (check PATH)
- [ ] Tải source code từ GitHub
- [ ] Cài đặt thư viện (`pip install -r requirements.txt`)
- [ ] Cấu hình TradeLocker credentials
- [ ] Test chạy bot lần đầu
- [ ] Thiết lập Task Scheduler (auto-start)
- [ ] Kiểm tra bot chạy sau khi restart VPS
- [ ] Xem và hiểu log file

---

**Phiên bản**: TL_V1 (2025-01-07)
**Nền tảng**: Windows Server 2016+ / Windows 10/11
**Cấp độ**: Người mới bắt đầu | Beginner-friendly

🎉 **Chúc bạn cài đặt thành công!** 🎉
