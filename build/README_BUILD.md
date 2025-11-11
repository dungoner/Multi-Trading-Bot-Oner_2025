# 🎁 HƯỚNG DẪN ĐÓNG GÓI SYNS BOT SYSTEM

**Chuyển Python scripts thành file .exe chạy độc lập (không cần cài Python)**

---

## 📋 MỤC LỤC

1. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
2. [Cài đặt công cụ](#cài-đặt-công-cụ)
3. [Đóng gói tự động](#đóng-gói-tự-động-1-click)
4. [Đóng gói thủ công](#đóng-gói-thủ-công)
5. [Sử dụng file .exe](#sử-dụng-file-exe)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ YÊU CẦU HỆ THỐNG

### **Developer (máy build):**
- Windows 10/11
- Python 3.7+ (download: https://www.python.org/downloads/)
- 5GB disk space trống (cho build artifacts)

### **End User (máy chạy .exe):**
- Windows 10/11
- **KHÔNG CẦN** cài Python!
- Chỉ cần copy file .exe và chạy

---

## 🔧 CÀI ĐẶT CÔNG CỤ

### **Bước 1: Cài Python**

1. Download Python từ https://www.python.org/downloads/
2. **QUAN TRỌNG:** Check ☑️ "Add Python to PATH" khi cài
3. Verify:
   ```cmd
   python --version
   ```
   → Phải hiện: `Python 3.x.x`

### **Bước 2: Cài PyInstaller**

Mở CMD trong folder `build/`:
```cmd
cd build
pip install -r requirements.txt
```

**Verify:**
```cmd
pyinstaller --version
```
→ Phải hiện: `6.x.x`

---

## 🚀 ĐÓNG GÓI TỰ ĐỘNG (1-CLICK)

### **Cách 1: Double-click (Đơn giản nhất)**

1. Mở folder `build/`
2. **Double-click** file `build_all.bat`
3. Đợi 5-10 phút (tùy máy)
4. Xong! Check folder `dist/`

### **Cách 2: Command Line**

```cmd
cd build
build_all.bat
```

### **Cách 3: GitHub Actions (Tự động trên cloud)**

**Yêu cầu:** Code đã push lên GitHub

**Build tự động mỗi khi push:**
```bash
git add .
git commit -m "Update bots"
git push origin main
```

**Tạo Release chính thức:**
```bash
git tag v2.0.0
git push origin v2.0.0
```

**Download file .exe:**
1. Vào GitHub repository → Tab **Actions**
2. Click vào workflow run mới nhất
3. Scroll xuống **Artifacts** → Download `SYNS-Bot-System-Windows.zip`
4. Hoặc vào tab **Releases** nếu đã tạo tag

**Chi tiết:** Xem `.github/workflows/README.md`

### **Kết quả:**

Folder `dist/` sẽ chứa:
```
dist/
├── SYNS_Bot0_Sender_Full.exe       (~50MB)
├── SYNS_Bot1_Sender_Optimized.exe  (~50MB)
├── SYNS_Bot2_Receiver.exe          (~50MB)
├── SYNS_Bot3_All_In_One.exe        (~50MB)
└── bot_config.json                 (~2KB)
```

---

## 🛠️ ĐÓNG GÓI THỦ CÔNG

### **Build từng bot riêng:**

```cmd
cd build

# Bot 0
pyinstaller --clean --noconfirm build_bot0.spec

# Bot 1
pyinstaller --clean --noconfirm build_bot1.spec

# Bot 2
pyinstaller --clean --noconfirm build_bot2.spec

# Bot 3
pyinstaller --clean --noconfirm build_bot3.spec
```

### **Tùy chỉnh build (nâng cao):**

**1. Thêm icon:**

Sửa file `.spec`, dòng `icon=None`:
```python
icon='../assets/bot.ico'  # Path to your .ico file
```

**2. Giảm file size:**

Sửa file `.spec`:
```python
upx=True,              # Enable UPX compression
upx_exclude=[],        # Don't exclude any files from UPX
strip=True,            # Strip debug symbols
```

**3. Hide console window:**

Sửa file `.spec`:
```python
console=False,  # No console window (for GUI apps)
```

---

## 💻 SỬ DỤNG FILE .EXE

### **Bước 1: Copy files**

Copy toàn bộ folder `dist/` sang máy cần chạy:
```
C:\SYNS_Bot\
├── SYNS_Bot0_Sender_Full.exe
├── SYNS_Bot1_Sender_Optimized.exe
├── SYNS_Bot2_Receiver.exe
├── SYNS_Bot3_All_In_One.exe
└── bot_config.json
```

### **Bước 2: Chỉnh config**

Sửa `bot_config.json` theo nhu cầu:
```json
{
  "mode": 0,
  "sender": {
    "api_port": 80,
    "dashboard_port": 9070,
    "csdl_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner3/",
    "polling_interval": 1
  }
}
```

### **Bước 3: Chạy bot**

**Double-click** file .exe tương ứng:
- `SYNS_Bot0_Sender_Full.exe` → Bot 0
- `SYNS_Bot1_Sender_Optimized.exe` → Bot 1
- `SYNS_Bot2_Receiver.exe` → Bot 2
- `SYNS_Bot3_All_In_One.exe` → Bot 3

**Hoặc qua CMD:**
```cmd
cd C:\SYNS_Bot
SYNS_Bot1_Sender_Optimized.exe
```

---

## 🔥 TROUBLESHOOTING

### ❌ **Lỗi: "Python not found"**

**Nguyên nhân:** Python chưa cài hoặc không có trong PATH

**Fix:**
1. Cài Python từ https://www.python.org/downloads/
2. **PHẢI CHECK** ☑️ "Add Python to PATH" khi cài
3. Restart CMD và thử lại

---

### ❌ **Lỗi: "PyInstaller not found"**

**Nguyên nhân:** Chưa cài PyInstaller

**Fix:**
```cmd
pip install pyinstaller
```

---

### ❌ **Lỗi: "Failed to execute script"**

**Nguyên nhân:** File .exe thiếu dependencies

**Fix:**
1. Mở file `.spec` tương ứng
2. Thêm vào `hiddenimports`:
   ```python
   hiddenimports=[
       'flask',
       'flask_cors',
       'requests',
       # Add missing module here
   ],
   ```
3. Build lại

---

### ❌ **Lỗi: "Access denied Port 80"**

**Nguyên nhân:** Port 80 requires Admin quyền

**Fix:**
- **Right-click** file .exe → "Run as Administrator"

---

### ❌ **File .exe bị antivirus chặn**

**Nguyên nhân:** Antivirus nghi ngờ file .exe do PyInstaller packing

**Fix:**
1. Add exception trong antivirus cho folder `C:\SYNS_Bot\`
2. Hoặc disable antivirus tạm thời khi chạy
3. (Tốt nhất) Code signing certificate (bỏ qua nếu không cần)

---

### ❌ **File size quá lớn (>100MB)**

**Nguyên nhân:** PyInstaller bundle toàn bộ Python runtime

**Fix:**
1. Enable UPX compression trong file `.spec`
2. Exclude unused modules
3. (Nâng cao) Dùng `--onefile` flag

---

## 📊 SO SÁNH PHƯƠNG PHÁP ĐÓNG GÓI

| Phương pháp | Build location | File size | Speed | Yêu cầu |
|-------------|----------------|-----------|-------|---------|
| **build_all.bat (Local)** | Local PC | ~50MB/bot | Fast (5-10 min) | Python, PyInstaller |
| **GitHub Actions (Cloud)** | GitHub Server | ~50MB/bot | Medium (10-15 min) | GitHub repo only |
| **PyInstaller + NSIS** | Local PC | ~200MB | Medium | Installer chuyên nghiệp |
| **Python Embedded** | Local PC | ~30MB/bot | Slow | Phức tạp, không recommend |

**Khuyến nghị:**
- **Development/Testing:** Dùng `build_all.bat` (local build - nhanh)
- **Production/Release:** Dùng GitHub Actions (tự động, chuyên nghiệp)

---

## 🎯 BEST PRACTICES

### **1. Test trước khi deploy:**

```cmd
# Test local
cd dist
SYNS_Bot1_Sender_Optimized.exe

# Check console output
# Kiểm tra Port 80 và 9070
```

### **2. Backup config:**

Luôn backup `bot_config.json` trước khi update:
```cmd
copy bot_config.json bot_config.json.backup
```

### **3. Version control:**

Đặt tên file theo version:
```
SYNS_Bot1_Sender_Optimized_v2.0.exe
```

### **4. Clean build:**

Nếu build lỗi, xóa cache và build lại:
```cmd
rmdir /s /q dist
rmdir /s /q build_temp
build_all.bat
```

---

## 🚀 DEPLOYMENT

### **Deploy lên VPS:**

**Option 1: Copy qua Remote Desktop**
1. Connect RDP to VPS
2. Copy folder `dist/` vào `C:\SYNS_Bot\`
3. Run .exe

**Option 2: Upload qua FileZilla/WinSCP**
1. Connect SFTP to VPS
2. Upload folder `dist/`
3. Run .exe qua RDP

**Option 3: Google Drive/Dropbox**
1. Zip folder `dist/` → `SYNS_Bot_v2.0.zip`
2. Upload lên Drive/Dropbox
3. Download trên VPS và unzip

---

## 📝 NOTES

- File .exe chỉ chạy trên **Windows** (không chạy trên Linux/Mac)
- Mỗi lần sửa code Python, phải **build lại** .exe
- File .exe bao gồm **toàn bộ Python runtime** → không cần cài Python
- Antivirus có thể false positive → add exception

---

## ✅ CHECKLIST

Trước khi deploy:

- [ ] Build thành công (no errors)
- [ ] Test local (chạy được)
- [ ] Check ports (80, 9070 open)
- [ ] Config đúng (paths, IPs)
- [ ] Backup config cũ
- [ ] Antivirus exception added

---

## 🆘 HỖ TRỢ

Nếu gặp vấn đề:

1. **Check log:** Console output khi chạy .exe
2. **Check config:** `bot_config.json` syntax
3. **Check ports:** `netstat -an | findstr :80`
4. **Re-build:** Clean build và thử lại

---

**Made with ❤️ by ONER Trading System**
