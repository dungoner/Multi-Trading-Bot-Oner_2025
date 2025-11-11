# 🤖 GITHUB ACTIONS - TỰ ĐỘNG ĐÓNG GÓI

## 📋 MÔ TẢ

Workflow `build-release.yml` tự động build tất cả 4 bots thành file .exe mỗi khi:
1. Push code lên nhánh `main` hoặc `master`
2. Tạo tag version mới (vd: `v2.0.0`)
3. Trigger thủ công qua GitHub UI

## 🔄 QUY TRÌNH TỰ ĐỘNG

```
Push code/Tag → GitHub Actions trigger → Build 4 bots → Upload artifacts → Create Release (nếu có tag)
```

## 🚀 CÁCH SỬ DỤNG

### **1. Build tự động khi push code:**

```bash
git add .
git commit -m "Update bots"
git push origin main
```

→ GitHub Actions sẽ tự động build và upload artifacts trong tab "Actions"

### **2. Tạo Release chính thức:**

```bash
# Tạo tag version mới
git tag v2.0.0
git push origin v2.0.0
```

→ GitHub Actions sẽ:
- Build 4 bots
- Đóng gói thành `SYNS_Bot_System_Windows.zip`
- Tạo Release mới tại: https://github.com/dungoner/Multi-Trading-Bot-Oner_2025/releases
- Users có thể download file .zip và sử dụng ngay

### **3. Trigger thủ công:**

1. Vào GitHub repository
2. Click tab **Actions**
3. Chọn workflow **Build and Release SYNS Bot System**
4. Click **Run workflow**
5. Chọn branch và click **Run workflow**

## 📦 KẾT QUẢ BUILD

### **Artifacts (mỗi lần push):**

Tại GitHub Actions → Workflow run → **Artifacts**:
- `SYNS-Bot-System-Windows.zip` (lưu 30 ngày)
- Bao gồm 4 file .exe + bot_config.json

### **Release (khi có tag):**

Tại **Releases** page:
- Title: `v2.0.0`
- File download: `SYNS_Bot_System_Windows.zip`
- Release notes tự động
- Lưu vĩnh viễn

## 🔧 YÊU CẦU

### **Repository Settings:**

Không cần setup gì thêm! Workflow sử dụng:
- `GITHUB_TOKEN` (tự động có sẵn)
- Windows runner (GitHub cung cấp)
- Python 3.11 (tự động cài)

### **Permissions:**

Nếu workflow bị lỗi "Permission denied" khi tạo Release:
1. Vào **Settings** → **Actions** → **General**
2. Tìm **Workflow permissions**
3. Chọn: **Read and write permissions**
4. Save

## 📊 THEO DÕI BUILD

### **Xem trạng thái build:**

1. Vào tab **Actions**
2. Click vào workflow run gần nhất
3. Xem từng step:
   - ✅ Build Bot 0
   - ✅ Build Bot 1
   - ✅ Build Bot 2
   - ✅ Build Bot 3
   - ✅ Upload artifacts

### **Download file .exe:**

**Từ Artifacts (mỗi build):**
1. Vào workflow run
2. Scroll xuống **Artifacts**
3. Click `SYNS-Bot-System-Windows` để download

**Từ Releases (khi có tag):**
1. Vào tab **Releases**
2. Click version mới nhất
3. Download `SYNS_Bot_System_Windows.zip`

## 🔥 TROUBLESHOOTING

### ❌ **Lỗi: "Build failed"**

**Check log:**
1. Vào workflow run bị lỗi
2. Click vào step bị lỗi (màu đỏ)
3. Đọc error message

**Nguyên nhân thường gặp:**
- Thiếu dependencies → Fix: update `build/requirements.txt`
- Syntax error trong code → Fix: test local trước khi push
- PyInstaller error → Fix: kiểm tra file `.spec`

---

### ❌ **Lỗi: "Permission denied" khi tạo Release**

**Fix:**
1. Settings → Actions → General
2. Workflow permissions → **Read and write permissions**
3. Save

---

### ❌ **File .exe không chạy được**

**Nguyên nhân:** Build trên GitHub (Windows Server 2022) có thể khác build local

**Fix:**
1. Download artifacts từ GitHub Actions
2. Test trên máy Windows 10/11
3. Nếu lỗi, build local bằng `build_all.bat` thay vì dùng GitHub Actions

---

## 🎯 SO SÁNH PHƯƠNG PHÁP

| Phương pháp | Ưu điểm | Nhược điểm |
|-------------|---------|------------|
| **Local Build** (`build_all.bat`) | Control hoàn toàn, test ngay | Phải có Python, build thủ công |
| **GitHub Actions** (workflow) | Tự động, lưu artifacts, tạo release | Phụ thuộc GitHub, chậm hơn |

**Khuyến nghị:**
- **Development:** Dùng local build (nhanh)
- **Production:** Dùng GitHub Actions (chuyên nghiệp)

---

## 📝 NOTES

- Workflow chạy trên **Windows runner** (GitHub cung cấp free)
- Build time: ~10-15 phút cho 4 bots
- Artifacts lưu 30 ngày, sau đó tự động xóa
- Releases lưu vĩnh viễn
- File .exe chỉ chạy trên Windows (không chạy Linux/Mac)

---

## ✅ CHECKLIST

Trước khi push code:

- [ ] Code đã test local
- [ ] Chạy `build_all.bat` local thành công
- [ ] Commit message rõ ràng
- [ ] (Optional) Tạo tag nếu muốn release chính thức

---

## 🆘 HỖ TRỢ

Nếu gặp vấn đề:

1. **Check workflow log:** Actions tab → Click vào run → Xem log
2. **Compare với local build:** Build local và so sánh kết quả
3. **Disable workflow tạm thời:** Xóa file `.github/workflows/build-release.yml`

---

**Made with ❤️ by ONER Trading System**
