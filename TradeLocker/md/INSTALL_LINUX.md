# 🐧 Hướng Dẫn Cài Đặt TradeLocker Bot trên Linux VPS

**Dành cho người mới bắt đầu** | **Step-by-step guide for beginners**

---

## 📋 Mục Lục | Table of Contents

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cập nhật hệ thống](#2-cập-nhật-hệ-thống)
3. [Cài đặt Python](#3-cài-đặt-python)
4. [Tải source code](#4-tải-source-code)
5. [Cài đặt thư viện](#5-cài-đặt-thư-viện)
6. [Cấu hình bot](#6-cấu-hình-bot)
7. [Chạy bot lần đầu](#7-chạy-bot-lần-đầu)
8. [Chạy bot tự động với systemd](#8-chạy-bot-tự-động-với-systemd)
9. [Giám sát và troubleshooting](#9-giám-sát-và-troubleshooting)

---

## 1. Yêu Cầu Hệ Thống

### Phần cứng tối thiểu
- **CPU**: 1 core (2 cores recommended)
- **RAM**: 512MB (1GB recommended)
- **Disk**: 5GB free space
- **Network**: Stable internet connection

### Phần mềm
- **OS**: Ubuntu 20.04/22.04, Debian 10/11, CentOS 7/8, hoặc tương tự
- **Python**: 3.8+ (recommended 3.11)
- **TradeLocker Account**: Demo hoặc Live
- **SSH Access**: Để kết nối VPS

---

## 2. Cập Nhật Hệ Thống

### Bước 2.1: Kết nối SSH vào VPS

Từ máy tính local (Windows: dùng PuTTY hoặc Windows Terminal):

```bash
ssh root@YOUR_VPS_IP
# Hoặc
ssh username@YOUR_VPS_IP
```

Nhập password khi được yêu cầu.

### Bước 2.2: Cập nhật packages

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt upgrade -y
```

**CentOS/RHEL:**
```bash
sudo yum update -y
# Hoặc với CentOS 8+
sudo dnf update -y
```

Chờ 2-5 phút để hoàn tất.

---

## 3. Cài Đặt Python

### Bước 3.1: Kiểm tra Python hiện có

```bash
python3 --version
```

**Nếu hiện `Python 3.8+` → Bỏ qua bước 3.2, chuyển sang bước 3.3**

### Bước 3.2: Cài đặt Python 3.11 (nếu cần)

**Ubuntu 20.04/22.04:**
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

**Ubuntu 18.04:**
```bash
sudo apt install python3.8 python3.8-venv python3.8-dev -y
```

**Debian 11:**
```bash
sudo apt install python3 python3-venv python3-pip -y
```

**CentOS 8:**
```bash
sudo dnf install python39 python39-devel -y
```

### Bước 3.3: Cài đặt pip

```bash
# Ubuntu/Debian
sudo apt install python3-pip -y

# CentOS
sudo yum install python3-pip -y
```

### Bước 3.4: Kiểm tra cài đặt

```bash
python3 --version
pip3 --version
```

Kết quả:
```
Python 3.11.x (hoặc 3.8+)
pip 23.x.x from ...
```

✅ **Nếu cả 2 lệnh đều chạy được → Python đã cài đặt thành công!**

---

## 4. Tải Source Code

### Bước 4.1: Cài đặt Git

```bash
# Ubuntu/Debian
sudo apt install git -y

# CentOS
sudo yum install git -y
```

### Bước 4.2: Tạo thư mục làm việc

```bash
cd /opt
sudo mkdir TradingBots
sudo chown $USER:$USER TradingBots
cd TradingBots
```

**Giải thích**:
- `/opt/TradingBots` - Thư mục chuẩn cho ứng dụng
- `chown` - Cấp quyền sở hữu cho user hiện tại

### Bước 4.3: Clone repository

```bash
git clone https://github.com/dungoner/Multi-Trading-Bot-Oner_2025.git
```

Chờ tải về hoàn tất (30 giây - 2 phút).

### Bước 4.4: Di chuyển vào thư mục TradeLocker

```bash
cd Multi-Trading-Bot-Oner_2025/TradeLocker
pwd
```

Kết quả phải là: `/opt/TradingBots/Multi-Trading-Bot-Oner_2025/TradeLocker`

---

## 5. Cài Đặt Thư Viện

### Bước 5.1: Tạo virtual environment (Recommended)

```bash
python3 -m venv venv
```

**Giải thích**: Tạo môi trường Python riêng biệt, không ảnh hưởng đến system Python.

### Bước 5.2: Kích hoạt virtual environment

```bash
source venv/bin/activate
```

Sau khi chạy, terminal sẽ có tiền tố `(venv)`:

```
(venv) root@vps:/opt/TradingBots/Multi-Trading-Bot-Oner_2025/TradeLocker#
```

### Bước 5.3: Nâng cấp pip

```bash
pip install --upgrade pip
```

### Bước 5.4: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

Chờ cài đặt hoàn tất (1-2 phút).

### Bước 5.5: Kiểm tra cài đặt

```bash
pip list | grep tradelocker
pip list | grep requests
```

Kết quả phải có:
```
tradelocker    1.0.0
requests       2.31.0
```

✅ **Nếu có 2 dòng → Thư viện đã cài đặt thành công!**

---

## 6. Cấu Hình Bot

### Bước 6.1: Mở file cấu hình

```bash
nano config.json
```

**Lưu ý**:
- Có thể dùng `vi` hoặc `vim` thay cho `nano` nếu quen
- Bot sử dụng file `config.json` để cấu hình, không cần chỉnh sửa file `.py` nữa!

### Bước 6.2: Cấu hình TradeLocker credentials

Tìm và chỉnh sửa phần `"tradelocker"`:

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

### Bước 6.3: Cấu hình HTTP API (CSDL)

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

### Bước 6.4: Lưu file

Trong `nano`:
1. Nhấn `Ctrl + O` (Write Out)
2. Nhấn `Enter` để xác nhận
3. Nhấn `Ctrl + X` để thoát

---

## 7. Chạy Bot Lần Đầu

### Bước 7.1: Test chạy bot

```bash
python TradeLocker_MTF_ONER.py
```

Hoặc chạy với symbol cụ thể:

```bash
python TradeLocker_MTF_ONER.py BTCUSD
```

### Bước 7.2: Kiểm tra kết quả

Bot sẽ hiển thị:

```
==============================================================================
TradeLocker MTF ONER Bot - Multi Timeframe Expert Advisor
==============================================================================
Version: TL_V1 - Converted from MT5 EA V2
==============================================================================

2025-01-07 14:30:00 [INFO] [INIT] Connecting to TradeLocker...
2025-01-07 14:30:01 [INFO] [INIT] TradeLocker connection successful ✓
2025-01-07 14:30:01 [INFO] [INIT] Instrument ID for BTCUSD: 12345
2025-01-07 14:30:01 [INFO] [INIT] EA initialization completed ✓
2025-01-07 14:30:01 [INFO] [START] Bot started successfully ✓
2025-01-07 14:30:01 [INFO] [START] Press Ctrl+C to stop
```

✅ **Nếu thấy "Bot started successfully" → Bot đã chạy thành công!**

### Bước 7.3: Xem Dashboard

Bot sẽ hiển thị dashboard real-time:

```
================================================================================
TradeLocker MTF ONER - BTCUSD
================================================================================
Account: Balance=$10000.00 | Equity=$10000.00 | DD=0.00%
Orders: 0 | Profit=$0.00 | Loss=$0.00
--------------------------------------------------------------------------------
M5   | Sig:NONE Age:1m     | S1:□ S2:□ S3:□ | P&L:$+0.00
M15  | Sig:NONE Age:5m     | S1:□ S2:□ S3:□ | P&L:$+0.00
...
================================================================================
```

### Bước 7.4: Dừng bot

Nhấn `Ctrl + C` để dừng bot:

```
^C
2025-01-07 14:35:00 [INFO] [SIGNAL] Shutdown signal received
2025-01-07 14:35:00 [INFO] [STOP] Stopping bot...
2025-01-07 14:35:01 [INFO] [STOP] Bot stopped ✓
```

---

## 8. Chạy Bot Tự Động với systemd

### Bước 8.1: Tạo systemd service file

```bash
sudo nano /etc/systemd/system/tradelocker-bot.service
```

Gõ nội dung sau:

```ini
[Unit]
Description=TradeLocker MTF ONER Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/TradingBots/Multi-Trading-Bot-Oner_2025/TradeLocker
ExecStart=/opt/TradingBots/Multi-Trading-Bot-Oner_2025/TradeLocker/venv/bin/python TradeLocker_MTF_ONER.py BTCUSD
Restart=always
RestartSec=10
StandardOutput=append:/var/log/tradelocker-bot.log
StandardError=append:/var/log/tradelocker-bot.log

[Install]
WantedBy=multi-user.target
```

**Giải thích**:
- `User=root` - Chạy với quyền root (hoặc thay bằng user khác)
- `WorkingDirectory` - Thư mục làm việc
- `ExecStart` - Lệnh chạy bot (dùng Python trong venv)
- `Restart=always` - Tự động restart nếu bot crash
- `RestartSec=10` - Chờ 10 giây trước khi restart
- `StandardOutput/Error` - Log ra file `/var/log/tradelocker-bot.log`

Lưu file: `Ctrl + O` → Enter → `Ctrl + X`

### Bước 8.2: Reload systemd

```bash
sudo systemctl daemon-reload
```

### Bước 8.3: Enable service (tự động khởi động khi boot)

```bash
sudo systemctl enable tradelocker-bot.service
```

### Bước 8.4: Start service

```bash
sudo systemctl start tradelocker-bot.service
```

### Bước 8.5: Kiểm tra status

```bash
sudo systemctl status tradelocker-bot.service
```

Kết quả phải hiện:

```
● tradelocker-bot.service - TradeLocker MTF ONER Bot
     Loaded: loaded (/etc/systemd/system/tradelocker-bot.service; enabled)
     Active: active (running) since Mon 2025-01-07 14:30:00 UTC; 5s ago
   Main PID: 12345 (python)
      Tasks: 2 (limit: 1234)
     Memory: 50.0M
        CPU: 2.5s
     CGroup: /system.slice/tradelocker-bot.service
             └─12345 /opt/TradingBots/.../venv/bin/python TradeLocker_MTF_ONER.py BTCUSD
```

✅ **Nếu thấy "active (running)" → Service đã chạy thành công!**

### Bước 8.6: Xem log real-time

```bash
tail -f /var/log/tradelocker-bot.log
```

Nhấn `Ctrl + C` để thoát.

---

## 9. Giám Sát và Troubleshooting

### 9.1: Các lệnh quản lý service

```bash
# Xem status
sudo systemctl status tradelocker-bot

# Start service
sudo systemctl start tradelocker-bot

# Stop service
sudo systemctl stop tradelocker-bot

# Restart service
sudo systemctl restart tradelocker-bot

# Xem log (100 dòng cuối)
sudo tail -n 100 /var/log/tradelocker-bot.log

# Xem log real-time
sudo tail -f /var/log/tradelocker-bot.log

# Xem log từ systemd journal
sudo journalctl -u tradelocker-bot.service -f
```

### 9.2: Kiểm tra bot có đang chạy không

```bash
ps aux | grep TradeLocker_MTF_ONER.py
```

Kết quả phải có dòng chứa `python TradeLocker_MTF_ONER.py`

### 9.3: Lỗi thường gặp

#### Lỗi 1: "ModuleNotFoundError: No module named 'tradelocker'"

**Nguyên nhân**: Chạy Python ngoài venv hoặc chưa cài thư viện

**Giải quyết**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### Lỗi 2: "Permission denied" khi start service

**Nguyên nhân**: Thiếu quyền

**Giải quyết**:
```bash
sudo chmod +x /opt/TradingBots/Multi-Trading-Bot-Oner_2025/TradeLocker/TradeLocker_MTF_ONER.py
sudo chown -R root:root /opt/TradingBots/Multi-Trading-Bot-Oner_2025
```

#### Lỗi 3: Service restart liên tục

**Nguyên nhân**: Bot crash ngay sau khi start

**Giải quyết**:
```bash
# Xem log để biết lỗi
sudo journalctl -u tradelocker-bot.service -n 50

# Hoặc xem file log
sudo tail -n 50 /var/log/tradelocker-bot.log
```

#### Lỗi 4: "Failed to connect to TradeLocker"

**Nguyên nhân**: Sai credentials hoặc network issue

**Giải quyết**:
```bash
# Test network
ping demo.tradelocker.com

# Test HTTP API
curl http://dungalading.duckdns.org/api/csdl/BTCUSD_LIVE.json

# Kiểm tra lại config
nano TradeLocker_MTF_ONER.py
```

#### Lỗi 5: Bot không tạo lệnh

**Nguyên nhân**: CSDL data không có signal hoặc không đọc được

**Giải quyết**:
```bash
# Enable debug mode
nano TradeLocker_MTF_ONER.py
# Set: DebugMode: bool = True

# Restart service
sudo systemctl restart tradelocker-bot

# Xem log chi tiết
sudo tail -f /var/log/tradelocker-bot.log
```

### 9.4: Rotate log file (tránh log quá lớn)

Tạo file logrotate config:

```bash
sudo nano /etc/logrotate.d/tradelocker-bot
```

Nội dung:

```
/var/log/tradelocker-bot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

Lưu file và test:

```bash
sudo logrotate -f /etc/logrotate.d/tradelocker-bot
```

### 9.5: Monitor tài nguyên hệ thống

```bash
# CPU & Memory usage
top

# Tìm process python
top -p $(pgrep -f TradeLocker_MTF_ONER.py)

# Disk usage
df -h

# Network connections
netstat -tulpn | grep python
```

---

## 🔒 Bảo Mật | Security

### 10.1: Không commit credentials vào Git

```bash
# Tạo file .gitignore
echo "*.log" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore

# Đừng commit file config có password
```

### 10.2: Sử dụng environment variables (Recommended)

Tạo file `.env`:

```bash
nano .env
```

Nội dung:

```env
TL_USERNAME=your_email@example.com
TL_PASSWORD=your_secure_password
TL_SERVER=Demo
```

Cấp quyền đọc chỉ cho owner:

```bash
chmod 600 .env
```

Cập nhật code để đọc từ `.env` (cần cài `python-dotenv`):

```bash
pip install python-dotenv
```

### 10.3: Firewall

```bash
# Ubuntu/Debian
sudo ufw allow ssh
sudo ufw enable

# CentOS
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

---

## 📊 Monitoring với tmux (Tùy chọn)

### Cài đặt tmux

```bash
sudo apt install tmux -y  # Ubuntu/Debian
sudo yum install tmux -y  # CentOS
```

### Chạy bot trong tmux session

```bash
# Tạo session
tmux new -s tradelocker

# Trong session, chạy bot
cd /opt/TradingBots/Multi-Trading-Bot-Oner_2025/TradeLocker
source venv/bin/activate
python TradeLocker_MTF_ONER.py BTCUSD

# Detach session: Ctrl + B, sau đó nhấn D

# Quay lại session
tmux attach -t tradelocker

# List sessions
tmux ls

# Kill session
tmux kill-session -t tradelocker
```

---

## 📞 Hỗ Trợ | Support

### Tài liệu
- **README**: `/opt/TradingBots/Multi-Trading-Bot-Oner_2025/TradeLocker/README.md`
- **GitHub**: https://github.com/dungoner/Multi-Trading-Bot-Oner_2025

### Báo lỗi
1. Thu thập log đầy đủ: `sudo journalctl -u tradelocker-bot.service -n 200 > error.log`
2. Chụp màn hình
3. Tạo Issue trên GitHub

---

## ✅ Checklist Hoàn Thành

- [ ] Cập nhật hệ thống
- [ ] Cài đặt Python 3.8+
- [ ] Clone source code từ GitHub
- [ ] Tạo virtual environment
- [ ] Cài đặt thư viện (`pip install -r requirements.txt`)
- [ ] Cấu hình TradeLocker credentials
- [ ] Test chạy bot thủ công
- [ ] Tạo systemd service
- [ ] Enable auto-start on boot
- [ ] Kiểm tra bot chạy sau khi reboot VPS
- [ ] Thiết lập log rotation
- [ ] Bảo mật file .env

---

## 🚀 Quick Start (Tóm tắt)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python & Git
sudo apt install python3 python3-pip python3-venv git -y

# 3. Clone repo
cd /opt && sudo mkdir TradingBots && sudo chown $USER:$USER TradingBots
cd TradingBots
git clone https://github.com/dungoner/Multi-Trading-Bot-Oner_2025.git
cd Multi-Trading-Bot-Oner_2025/TradeLocker

# 4. Setup venv & install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure bot
nano TradeLocker_MTF_ONER.py
# Edit TL_Username, TL_Password, TL_Server

# 6. Test run
python TradeLocker_MTF_ONER.py BTCUSD

# 7. Setup systemd service (see section 8)
sudo nano /etc/systemd/system/tradelocker-bot.service
sudo systemctl daemon-reload
sudo systemctl enable tradelocker-bot.service
sudo systemctl start tradelocker-bot.service
sudo systemctl status tradelocker-bot.service
```

---

**Phiên bản**: TL_V1 (2025-01-07)
**Nền tảng**: Ubuntu 20.04/22.04, Debian 10/11, CentOS 7/8
**Cấp độ**: Người mới bắt đầu | Beginner-friendly

🎉 **Chúc bạn cài đặt thành công!** 🎉
