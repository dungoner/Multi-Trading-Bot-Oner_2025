# 🔧 SYNS Bot System - TẠO FILE SETUP.EXE INSTALLER

## 🎯 TẠO INSTALLER NHƯ PHẦN MỀM CHUYÊN NGHIỆP

Thay vì file .zip, bạn có thể tạo file **SETUP.EXE** installer chuyên nghiệp với:
- ✅ Giao diện wizard đẹp mắt
- ✅ Tự động cài đặt thư viện Python
- ✅ Tạo shortcuts Start Menu + Desktop
- ✅ Uninstaller tự động
- ✅ Như cài phần mềm thật!

---

## 📋 YÊU CẦU

### Download Inno Setup (FREE):

**Tải về:** https://jrsoftware.org/isdl.php

Chọn: **Inno Setup 6.x** (mới nhất)

**Cài đặt:** Chạy file `innosetup-6.x.x.exe` và làm theo wizard

---

## 🔨 TẠO 2 LOẠI SETUP

### ✅ SETUP 1: Portable Python Package

**File:** `setup_portable.iss`

**Bao gồm:**
- Python 3.10 Embedded
- 4 Bot .py files
- bot_config.json
- Auto-install Flask, Requests, Flask-CORS

**Output:** `SYNS_Bot_Portable_Setup.exe` (~7.5 MB)

---

### ✅ SETUP 2: EXE Package

**File:** `setup_exe.iss`

**Bao gồm:**
- 4 Bot .exe files (đã build)
- bot_config.json
- Launcher

**Output:** `SYNS_Bot_EXE_Setup.exe` (~15-20 MB)

---

## 🚀 CÁCH TẠO SETUP 1 (Portable)

### Bước 1: Chuẩn bị files

```
SYNS_Bot_PY/
├── python/           ← Phải có thư mục này (Python Embedded)
├── *.py              ← 4 bot files
├── bot_config.json
├── START_0123_BOT.bat
└── setup_portable.iss  ← Script Inno Setup
```

### Bước 2: Compile

**Cách 1: Dùng GUI**
1. Mở **Inno Setup Compiler**
2. File → Open → Chọn `setup_portable.iss`
3. Build → Compile (hoặc Ctrl+F9)
4. Đợi compile xong

**Cách 2: Dùng Command Line**
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_portable.iss
```

### Bước 3: Kết quả

File output: `PACKAGES\SYNS_Bot_Portable_Setup.exe`

---

## 🚀 CÁCH TẠO SETUP 2 (EXE)

### Bước 1: Build .exe files trước

```cmd
REM Phải build 4 .exe trước!
build_exe.bat
```

Files trong `dist/`:
- Bot0_HTTP80_Sender.exe
- Bot1_Sender_Optimized.exe
- Bot2_Data_Receiver.exe
- Bot3_Server_Integrated.exe

### Bước 2: Compile Installer

**Cách 1: GUI**
1. Mở **Inno Setup Compiler**
2. File → Open → Chọn `setup_exe.iss`
3. Build → Compile

**Cách 2: Command Line**
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_exe.iss
```

### Bước 3: Kết quả

File output: `PACKAGES\SYNS_Bot_EXE_Setup.exe`

---

## 📦 CÁCH DÙNG SETUP.EXE

### Người dùng nhận file SETUP.exe:

1. **Double-click** `SYNS_Bot_Portable_Setup.exe` hoặc `SYNS_Bot_EXE_Setup.exe`
2. Làm theo wizard:
   - Chọn thư mục cài đặt
   - Chọn tạo shortcuts
   - Next → Next → Install
3. **Tự động cài đặt:**
   - Copy files vào thư mục
   - Cài thư viện Python (nếu Portable)
   - Tạo shortcuts Start Menu
   - Tạo Desktop icon (nếu chọn)
4. **Finish** → Chạy ngay!

---

## 🎯 TÍNH NĂNG INSTALLER

### SETUP 1 (Portable):
✅ Cài Python Embedded
✅ Enable pip tự động
✅ Cài Flask, Requests, Flask-CORS
✅ Tạo shortcuts Start Menu:
   - SYNS Bot Launcher
   - Bot 1 - Sender (VPS)
   - Bot 2 - Receiver (Local)
   - Bot 3 - Integrated
   - Open Config File
   - Uninstall
✅ Desktop shortcut (tùy chọn)
✅ Hướng dẫn sau khi cài

### SETUP 2 (EXE):
✅ Cài 4 .exe files
✅ Tạo shortcuts Start Menu
✅ Desktop shortcut (tùy chọn)
✅ Cảnh báo Windows Defender
✅ Uninstaller

---

## 🔧 CHỈNH SỬA INSTALLER

### Thay đổi thông tin ứng dụng:

Mở file `.iss` và sửa:

```pascal
#define MyAppName "SYNS Bot System - Portable"
#define MyAppVersion "1.0"              ← Đổi version
#define MyAppPublisher "SYNS Trading"   ← Đổi tên công ty
#define MyAppURL "http://dungalading.duckdns.org"
```

### Thay đổi thư mục cài mặc định:

```pascal
DefaultDirName={autopf}\SYNS_Bot_Portable  ← Đổi tên thư mục
```

### Thêm/bớt files:

```pascal
[Files]
Source: "file_moi.py"; DestDir: "{app}"; Flags: ignoreversion
```

### Thêm shortcuts:

```pascal
[Icons]
Name: "{group}\Ten_Shortcut"; Filename: "{app}\file.exe"
```

---

## 📊 SO SÁNH 3 PHƯƠNG THỨC

| Phương thức | Kích thước | Cài đặt | Chuyên nghiệp | Dễ dùng |
|-------------|-----------|---------|---------------|---------|
| **.ZIP** | Nhỏ | Giải nén thủ công | ⭐ | ⭐⭐ |
| **SETUP.EXE (Portable)** | 7.5 MB | Tự động | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **SETUP.EXE (EXE)** | 15-20 MB | Tự động | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## ⚠️ LƯU Ý

### Windows Defender:

**SETUP.EXE (Portable):**
- ✅ Thường không bị chặn (chỉ có Python + code)

**SETUP.EXE (EXE):**
- ⚠️ Có thể bị chặn (chứa .exe files từ PyInstaller)
- Giải pháp: Code signing certificate (tốn phí) hoặc hướng dẫn user add exception

### Code Signing (Nâng cao):

Để không bị Windows chặn, mua certificate:
- **DigiCert, Sectigo, GlobalSign:** ~$200-500/năm
- Ký setup.exe bằng `signtool.exe`
- Windows sẽ tin tưởng installer

---

## 🎯 BUILD TẤT CẢ SETUP FILES

### Script tự động (tạo file `build_all_setups.bat`):

```batch
@echo off
echo Building all SETUP.EXE files...

echo.
echo [1/3] Building EXE files with PyInstaller...
call build_exe.bat

echo.
echo [2/3] Compiling Portable Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_portable.iss

echo.
echo [3/3] Compiling EXE Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_exe.iss

echo.
echo ============================================
echo ALL SETUP FILES CREATED!
echo ============================================
echo.
echo Output files:
echo   PACKAGES\SYNS_Bot_Portable_Setup.exe
echo   PACKAGES\SYNS_Bot_EXE_Setup.exe
echo.
pause
```

Chạy: `build_all_setups.bat`

---

## 📥 DOWNLOAD INNO SETUP

**Official Website:** https://jrsoftware.org/isinfo.php

**Direct Download:** https://jrsoftware.org/download.php/is.exe

**Documentation:** https://jrsoftware.org/ishelp/

---

## 🎉 KẾT QUẢ

Sau khi compile, bạn có:

✅ **SYNS_Bot_Portable_Setup.exe** - Installer như phần mềm thật!
✅ **SYNS_Bot_EXE_Setup.exe** - Installer cho .exe version!

Người dùng chỉ cần:
1. Download file SETUP.exe
2. Double-click
3. Next → Next → Install
4. Done!

**CHUYÊN NGHIỆP 100%!** 🚀
