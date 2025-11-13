# 🍷 Wine Installation Guide - Chạy MT4 Windows trên Linux

> **Hướng dẫn cài đặt Wine và setup MT4 từ A-Z cho người mới**
>
> **Wine = Windows compatibility layer cho Linux**

---

## 📋 MỤC LỤC

1. [Wine Là Gì?](#1-wine-là-gì)
2. [Cách Wine Hoạt Động](#2-cách-wine-hoạt-động)
3. [Cài Đặt Wine - Ubuntu/Debian](#3-cài-đặt-wine---ubuntudebian)
4. [Cài Đặt Wine - CentOS/RHEL](#4-cài-đặt-wine---centosrhel)
5. [Cài Đặt Wine - Oracle Linux ARM64](#5-cài-đặt-wine---oracle-linux-arm64)
6. [Verify Wine Installation](#6-verify-wine-installation)
7. [Cài MT4 Qua Wine](#7-cài-mt4-qua-wine)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. WINE LÀ GÌ?

### 🍷 Định Nghĩa

**Wine** = **W**ine **I**s **N**ot an **E**mulator

```
┌─────────────────────────────────────────────────────────┐
│  Wine KHÔNG phải emulator (máy ảo)                      │
│  Wine là COMPATIBILITY LAYER (lớp tương thích)          │
│                                                         │
│  → Dịch Windows API calls → Linux API calls            │
│  → KHÔNG chạy Windows OS bên trong                     │
│  → Nhẹ hơn Virtual Machine rất nhiều                   │
└─────────────────────────────────────────────────────────┘
```

### 📊 So Sánh: Wine vs Virtual Machine

| Aspect | Wine | Virtual Machine (VirtualBox/VMware) |
|--------|------|-------------------------------------|
| **Cơ chế** | Translate API calls | Chạy Windows OS đầy đủ |
| **RAM usage** | ~100-200 MB | ~2-4 GB |
| **CPU overhead** | 5-10% | 20-40% |
| **Setup time** | 5 phút | 30-60 phút |
| **Performance** | 90-95% native | 60-80% native |
| **Disk space** | ~500 MB | ~20-40 GB |

**Verdict**: Wine nhẹ hơn và nhanh hơn rất nhiều!

---

## 2. CÁCH WINE HOẠT ĐỘNG

### 🔄 Quy Trình Dịch API

```
┌──────────────────────────────────────────────────────────────┐
│  WINDOWS APP (MT4.exe)                                       │
│  ↓                                                           │
│  Calls Windows API: CreateFile("data.txt")                  │
│  ↓                                                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  WINE TRANSLATION LAYER                            │     │
│  │  ↓                                                 │     │
│  │  Wine intercepts: CreateFile()                    │     │
│  │  ↓                                                 │     │
│  │  Wine translates to: open() (Linux syscall)      │     │
│  │  ↓                                                 │     │
│  │  Returns result back to MT4.exe                   │     │
│  └────────────────────────────────────────────────────┘     │
│  ↓                                                           │
│  LINUX KERNEL                                                │
│  ↓                                                           │
│  File created: ~/.wine/drive_c/data.txt                     │
└──────────────────────────────────────────────────────────────┘
```

### 📁 Virtual C:\ Drive

Wine tạo "fake C:\" drive trong Linux:

```
Windows path (MT4 thấy):
  C:\Program Files\MetaTrader 4\terminal.exe

Linux path (thực tế):
  ~/.wine/drive_c/Program Files/MetaTrader 4/terminal.exe
```

**MT4 không biết nó đang chạy trên Linux!**

---

## 3. CÀI ĐẶT WINE - UBUNTU/DEBIAN

### 🐧 Ubuntu 22.04 LTS (Recommended)

#### Step 1: Enable 32-bit Architecture

**Lý do**: MT4 có cả phiên bản 32-bit, cần hỗ trợ cả 2 arch

```bash
sudo dpkg --add-architecture i386
```

#### Step 2: Add WineHQ Repository

**Lý do**: Wine trong Ubuntu repo cũ, dùng WineHQ để có bản mới nhất

```bash
# Download và add GPG key
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key \
  https://dl.winehq.org/wine-builds/winehq.key
```

#### Step 3: Add Repository Source

**Ubuntu 22.04 (Jammy)**:
```bash
sudo wget -NP /etc/apt/sources.list.d/ \
  https://dl.winehq.org/wine-builds/ubuntu/dists/jammy/winehq-jammy.sources
```

**Ubuntu 20.04 (Focal)**:
```bash
sudo wget -NP /etc/apt/sources.list.d/ \
  https://dl.winehq.org/wine-builds/ubuntu/dists/focal/winehq-focal.sources
```

**Ubuntu 18.04 (Bionic)**:
```bash
sudo wget -NP /etc/apt/sources.list.d/ \
  https://dl.winehq.org/wine-builds/ubuntu/dists/bionic/winehq-bionic.sources
```

#### Step 4: Update Package List

```bash
sudo apt update
```

**Expected output**:
```
Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
Get:2 https://dl.winehq.org/wine-builds/ubuntu jammy InRelease [4,324 B]
...
Reading package lists... Done
```

#### Step 5: Install Wine Stable

```bash
sudo apt install --install-recommends winehq-stable -y
```

**Installation size**: ~500 MB

**Time**: 2-5 phút (tùy internet speed)

**Expected output**:
```
The following NEW packages will be installed:
  winehq-stable wine-stable wine-stable-amd64 wine-stable-i386
...
Setting up winehq-stable (9.0~jammy-1) ...
```

#### Step 6: Verify Installation

```bash
wine --version
```

**Expected output**:
```
wine-9.0
```

✅ **Thành công!** Wine đã cài xong.

---

### 🐧 Debian 11 (Bullseye)

#### Quick Install:

```bash
# Enable 32-bit
sudo dpkg --add-architecture i386

# Add WineHQ repository
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key \
  https://dl.winehq.org/wine-builds/winehq.key

# Add source (Debian 11)
echo "deb [signed-by=/etc/apt/keyrings/winehq-archive.key] \
  https://dl.winehq.org/wine-builds/debian/ bullseye main" | \
  sudo tee /etc/apt/sources.list.d/winehq.list

# Update & Install
sudo apt update
sudo apt install --install-recommends winehq-stable -y

# Verify
wine --version
```

---

### 🐧 Linux Mint 21

**Lưu ý**: Mint 21 based on Ubuntu 22.04

```bash
# Same as Ubuntu 22.04
sudo dpkg --add-architecture i386
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key \
  https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ \
  https://dl.winehq.org/wine-builds/ubuntu/dists/jammy/winehq-jammy.sources
sudo apt update
sudo apt install --install-recommends winehq-stable -y
wine --version
```

---

## 4. CÀI ĐẶT WINE - CENTOS/RHEL

### 🎩 CentOS 7

```bash
# Enable EPEL repository
sudo yum install epel-release -y

# Install Wine
sudo yum install wine -y

# Verify
wine --version
```

**Lưu ý**: CentOS 7 Wine version cũ (wine-1.x hoặc 2.x)

---

### 🎩 CentOS 8 / Rocky Linux 8

```bash
# Enable EPEL
sudo dnf install epel-release -y

# Install Wine
sudo dnf install wine -y

# Verify
wine --version
```

---

### 🎩 RHEL 8 / AlmaLinux 8

```bash
# Enable CodeReady Builder
sudo subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms

# Install EPEL
sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y

# Install Wine
sudo dnf install wine -y

# Verify
wine --version
```

---

## 5. CÀI ĐẶT WINE - ORACLE LINUX ARM64

### ⚠️ Oracle ARM64 - Vấn Đề Đặc Biệt

**Oracle Free Tier** = ARM64 (Ampere A1), **KHÔNG phải x86_64**

```
┌────────────────────────────────────────────────────────┐
│  Wine trên ARM64 = CHỈ hỗ trợ ARM Windows apps        │
│                                                        │
│  MT4 = x86_64 Windows app                             │
│  → Cần thêm Box64 (x86_64 emulator)                  │
└────────────────────────────────────────────────────────┘
```

### 🔧 Cài Box64 + Wine trên ARM64

#### Step 1: Install Dependencies

```bash
sudo apt update
sudo apt install -y git build-essential cmake python3
```

#### Step 2: Clone Box64

```bash
cd ~
git clone https://github.com/ptitSeb/box64
cd box64
```

#### Step 3: Build Box64

```bash
mkdir build
cd build
cmake .. -DARM_DYNAREC=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j$(nproc)
sudo make install
```

**Time**: 10-15 phút

#### Step 4: Verify Box64

```bash
box64 --version
```

**Expected output**:
```
Box64 v0.2.8 (built on ...)
```

#### Step 5: Install Wine x86_64

**Method 1: Download pre-built Wine**

```bash
# Download Wine x86_64 build
cd ~
wget https://github.com/Kron4ek/Wine-Builds/releases/download/9.0/wine-9.0-amd64.tar.xz

# Extract
tar -xf wine-9.0-amd64.tar.xz

# Move to /opt
sudo mv wine-9.0-amd64 /opt/wine

# Create symlink
sudo ln -s /opt/wine/bin/wine /usr/local/bin/wine-x64
```

#### Step 6: Run Wine via Box64

```bash
# Test
box64 /opt/wine/bin/wine --version
```

**Expected output**:
```
wine-9.0
```

#### Step 7: Create Wrapper Script

```bash
sudo nano /usr/local/bin/wine
```

**Content**:
```bash
#!/bin/bash
box64 /opt/wine/bin/wine "$@"
```

**Make executable**:
```bash
sudo chmod +x /usr/local/bin/wine
```

#### Step 8: Verify

```bash
wine --version
```

**Expected output**:
```
wine-9.0
```

✅ **Done!** Wine x86_64 via Box64 on ARM64

---

## 6. VERIFY WINE INSTALLATION

### ✅ Test 1: Version Check

```bash
wine --version
```

**Expected**: `wine-9.0` hoặc mới hơn

---

### ✅ Test 2: Run Simple Windows App

```bash
wine notepad
```

**Expected**: Notepad window mở ra (hoặc error nếu chưa có X display)

**Nếu lỗi "Error: no display specified"**:
```bash
# Cài Xvfb (virtual display)
sudo apt install xvfb -y

# Start Xvfb
Xvfb :99 -screen 0 1024x768x24 &

# Set DISPLAY
export DISPLAY=:99

# Test lại
wine notepad
```

---

### ✅ Test 3: Check Wine Prefix

```bash
ls ~/.wine/drive_c/
```

**Expected output**:
```
Program Files/
Program Files (x86)/
users/
windows/
```

✅ **Wine prefix created successfully!**

---

## 7. CÀI MT4 QUA WINE

### 📥 Download MT4 Installer

**Option 1: From broker** (Recommended)

Ví dụ FundedFolk:
```bash
wget https://fundedfolk.com/download/fundedfolk-mt4.exe
```

**Option 2: From MetaQuotes**

```bash
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt4/mt4setup.exe
```

---

### 🚀 Install MT4

#### Method 1: Silent Install (No GUI)

```bash
wine mt4setup.exe /auto
```

**Expected output**:
```
Installer starting...
Extracting files...
Installing MetaTrader 4...
Installation completed successfully
```

**Time**: 2-3 phút

---

#### Method 2: Interactive Install (với GUI)

**Cần X display** (VNC hoặc local desktop)

```bash
wine mt4setup.exe
```

**Steps**:
1. Click "Next"
2. Accept License
3. Choose install path (default: C:\Program Files\MetaTrader 4)
4. Click "Install"
5. Wait 2-3 phút
6. Click "Finish"

---

### 📂 Verify MT4 Installation

```bash
ls ~/.wine/drive_c/Program\ Files/MetaTrader\ 4/
```

**Expected output**:
```
terminal.exe
metaeditor.exe
MQL4/
experts/
indicators/
scripts/
...
```

✅ **MT4 installed!**

---

### 🎯 Run MT4

```bash
wine ~/.wine/drive_c/Program\ Files/MetaTrader\ 4/terminal.exe
```

**Nếu không có GUI** (headless server):
```bash
# Start Xvfb first
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Run MT4
wine ~/.wine/drive_c/Program\ Files/MetaTrader\ 4/terminal.exe &
```

**Nếu muốn xem GUI từ xa**:
```bash
# Install VNC server
sudo apt install tigervnc-standalone-server -y

# Start VNC
vncserver :1 -geometry 1280x720 -depth 24

# Connect từ local: VNC Viewer → vps_ip:5901
```

---

## 8. TROUBLESHOOTING

### ❌ Problem 1: Wine command not found

**Error**:
```
bash: wine: command not found
```

**Solution**:
```bash
# Check if installed
dpkg -l | grep wine

# If not, install again
sudo apt install --install-recommends winehq-stable -y

# Add to PATH (if needed)
echo 'export PATH="/opt/wine-stable/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### ❌ Problem 2: 32-bit architecture not enabled

**Error**:
```
The following packages have unmet dependencies:
 winehq-stable : Depends: wine-stable (= 9.0~jammy-1)
E: Unable to correct problems, you have held broken packages.
```

**Solution**:
```bash
# Enable 32-bit
sudo dpkg --add-architecture i386
sudo apt update

# Install again
sudo apt install --install-recommends winehq-stable -y
```

---

### ❌ Problem 3: Wine crashes immediately

**Error**:
```
wine: Unhandled page fault on read access to 0x00000000 at address ...
```

**Solution**:
```bash
# Remove old Wine prefix
rm -rf ~/.wine

# Recreate
wineboot --init

# Test
wine notepad
```

---

### ❌ Problem 4: MT4 installer không chạy

**Error**:
```
fixme:ntdll:NtQuerySystemInformation info_class SYSTEM_PERFORMANCE_INFORMATION
err:module:import_dll Library MSVCP140.dll ...
```

**Solution**:
```bash
# Install Visual C++ Runtime via winetricks
sudo apt install winetricks -y

# Install MSVCP140
winetricks vcrun2015

# Try installer again
wine mt4setup.exe /auto
```

---

### ❌ Problem 5: Box64 build fails on ARM64

**Error**:
```
CMake Error: Could not find CMAKE_ROOT
```

**Solution**:
```bash
# Update CMake
sudo apt remove cmake -y
sudo apt install cmake -y

# Or install from snap
sudo snap install cmake --classic

# Try build again
cd ~/box64/build
cmake .. -DARM_DYNAREC=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j$(nproc)
```

---

### ❌ Problem 6: Wine performance very slow

**Symptoms**: MT4 mất 10-20 giây để mở

**Solutions**:

**1. Disable Wine debugging**:
```bash
export WINEDEBUG=-all
wine mt4.exe
```

**2. Add to ~/.bashrc**:
```bash
echo 'export WINEDEBUG=-all' >> ~/.bashrc
source ~/.bashrc
```

**3. Use Windows 10 mode**:
```bash
winecfg
# Applications tab → Windows Version → Windows 10
```

---

### ❌ Problem 7: Graphics artifacts / black screen

**Symptoms**: MT4 window đen hoặc chart không hiển thị

**Solutions**:

**1. Try different graphics backend**:
```bash
# OpenGL (default)
wine mt4.exe

# GDI (fallback)
WINEDLLOVERRIDES="d3d11=;dxgi=" wine mt4.exe
```

**2. Disable font smoothing**:
```bash
winetricks settings fontsmooth=disable
```

**3. Try software rendering**:
```bash
LIBGL_ALWAYS_SOFTWARE=1 wine mt4.exe
```

---

## 📊 WINE VERSIONS COMPARISON

| Version | Release | MT4 Compatibility | Recommended |
|---------|---------|-------------------|-------------|
| Wine 9.0 | 2024-01 | ⭐⭐⭐⭐⭐ Excellent | ✅ Yes |
| Wine 8.0 | 2023-01 | ⭐⭐⭐⭐ Good | ✅ Yes |
| Wine 7.0 | 2022-01 | ⭐⭐⭐⭐ Good | ⚠️ OK |
| Wine 6.0 | 2021-01 | ⭐⭐⭐ Fair | ❌ No |
| Wine 5.0 | 2020-01 | ⭐⭐ Poor | ❌ No |

**Recommendation**: Dùng Wine 8.0+ (stable nhất với MT4)

---

## 🎯 QUICK REFERENCE

### Ubuntu 22.04 - 1 Lệnh

```bash
sudo dpkg --add-architecture i386 && \
sudo mkdir -pm755 /etc/apt/keyrings && \
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/jammy/winehq-jammy.sources && \
sudo apt update && \
sudo apt install --install-recommends winehq-stable -y && \
wine --version
```

---

### Oracle ARM64 - Full Script

```bash
#!/bin/bash
# Install Box64 + Wine on ARM64

# Dependencies
sudo apt update
sudo apt install -y git build-essential cmake

# Clone Box64
cd ~
git clone https://github.com/ptitSeb/box64
cd box64

# Build
mkdir build && cd build
cmake .. -DARM_DYNAREC=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j$(nproc)
sudo make install

# Download Wine x64
cd ~
wget https://github.com/Kron4ek/Wine-Builds/releases/download/9.0/wine-9.0-amd64.tar.xz
tar -xf wine-9.0-amd64.tar.xz
sudo mv wine-9.0-amd64 /opt/wine

# Create wrapper
echo '#!/bin/bash' | sudo tee /usr/local/bin/wine
echo 'box64 /opt/wine/bin/wine "$@"' | sudo tee -a /usr/local/bin/wine
sudo chmod +x /usr/local/bin/wine

# Verify
wine --version
```

---

### Test MT4 Installation

```bash
#!/bin/bash
# Test MT4 installation

# 1. Download MT4
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt4/mt4setup.exe

# 2. Install
wine mt4setup.exe /auto

# 3. Verify
ls ~/.wine/drive_c/Program\ Files/MetaTrader\ 4/terminal.exe

# 4. Run
export WINEDEBUG=-all
wine ~/.wine/drive_c/Program\ Files/MetaTrader\ 4/terminal.exe &

echo "✅ MT4 running on Wine!"
```

---

## 📚 TÀI LIỆU THAM KHẢO

**Official Wine**:
- Website: https://www.winehq.org/
- Documentation: https://wiki.winehq.org/
- Downloads: https://dl.winehq.org/

**Box64 (ARM64)**:
- GitHub: https://github.com/ptitSeb/box64
- Wiki: https://github.com/ptitSeb/box64/wiki

**MT4 on Wine**:
- MQL5 Article: https://www.mql5.com/en/articles/1358
- MetaTrader Linux Help: https://www.metatrader4.com/en/trading-platform/help/userguide/install_linux

---

## ✅ CHECKLIST

- [ ] Wine version ≥ 8.0 installed
- [ ] 32-bit architecture enabled (i386)
- [ ] Wine prefix created (~/.wine/)
- [ ] MT4 installer downloaded
- [ ] MT4 installed successfully
- [ ] MT4 terminal.exe runs
- [ ] (Optional) Xvfb installed for headless
- [ ] (Optional) VNC server for remote GUI
- [ ] (Optional) winetricks installed
- [ ] (ARM64 only) Box64 installed

---

**Version**: 1.0
**Date**: 2025-01-13
**Platform**: Linux (Ubuntu/Debian/CentOS/Oracle ARM64)
**Status**: Production-Ready Guide

🍷 **Wine - Chạy MT4 Windows trên Linux dễ dàng!** 🍷
