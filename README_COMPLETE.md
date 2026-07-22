# 🌞 Hoa Huy Green Energy - Facebook Auto Poster Complete Suite

Hệ thống tự động đăng bài lên Facebook về năng lượng mặt trời, pin lưu trữ, và biến tần inverter.

**Phiên bản:** 2.0 (Advanced)  
**Cập nhật:** 2024  
**Tác giả:** Claude Code

---

## ✨ Tính Năng

### 🎯 Tính Năng Chính
- ✅ **Tự động đăng bài** vào 7 AM và 8 PM mỗi ngày
- ✅ **Nội dung thông minh** - Tạo nội dung ngẫu nhiên từ các template
- ✅ **Hình ảnh tự động** - Tìm kiếm hình ảnh từ Unsplash
- ✅ **Hashtags thông minh** - Tự động thêm hashtags phù hợp
- ✅ **Logging chi tiết** - Ghi lại mọi hoạt động vào file log
- ✅ **Chạy 24/7** - Dịch vụ Windows background
- ✅ **Dễ cấu hình** - Chỉ cần 2 API keys

### 📱 Các Chủ Đề
- Năng lượng mặt trời
- Pin lưu trữ năng lượng
- Biến tần inverter
- Hệ thống điện mặt trời
- Năng lượng tái tạo
- Và nhiều hơn nữa...

---

## 📁 Cấu Trúc File

```
Hoa huy green energy/
├── facebook_auto_post.py              # Script cơ bản
├── facebook_auto_post_advanced.py     # Script nâng cấp ⭐ DÙNG CÁI NÀY
├── .env.example                       # Mẫu cấu hình
├── .env                               # Cấu hình thực tế (tạo từ .env.example)
├── requirements.txt                   # Thư viện cần thiết
│
├── run_poster_service.bat             # Chạy script trực tiếp
├── install_windows_service.bat        # Cài đặt dịch vụ Windows
├── manage_service.bat                 # Quản lý dịch vụ
│
├── QUICK_START.md                     # 📌 Bắt đầu nhanh (5 phút)
├── SETUP_GUIDE.md                     # Hướng dẫn chi tiết
├── README_AUTO_POST.md                # Hướng dẫn script cơ bản
├── README_COMPLETE.md                 # File này
│
└── auto_post.log                      # Logs hoạt động (tự động tạo)
```

---

## 🚀 Bắt Đầu Nhanh (5 Phút)

### 1️⃣ Chuẩn Bị
```bash
# Tạo file .env
copy .env.example .env

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2️⃣ Lấy API Keys
- **Zernio API Key:** https://zernio.com/dashboard → Settings → API Keys
- **Facebook Account ID:** Zernio Dashboard → Connected Accounts
- **Unsplash Access Key (optional):** https://unsplash.com/developers

### 3️⃣ Cấu Hình
Mở file `.env` và điền:
```env
ZERNIO_API_KEY=your_key_here
FACEBOOK_ACCOUNT_ID=your_id_here
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
```

### 4️⃣ Chạy
```bash
python facebook_auto_post_advanced.py
```

✅ Done! Bài đăng sẽ tự động được đăng lên Facebook lúc 7 AM và 8 PM.

---

## 🖥️ Chạy 24/7 trên Windows

### Cách 1: Chạy Trực Tiếp (Đơn Giản)
Nhấp đôi vào `run_poster_service.bat`

⚠️ **Nhược điểm:** Cửa sổ phải luôn mở

### Cách 2: Dịch Vụ Windows (Chuyên Nghiệp) ⭐ KHUYÊN DÙNG

**Bước 1:** Nhấp chuột phải vào `install_windows_service.bat` → **Run as administrator**

**Bước 2:** Script sẽ tự động:
- Tải NSSM
- Tạo dịch vụ Windows
- Khởi động dịch vụ

**Bước 3:** Dịch vụ sẽ chạy 24/7 ở background

### Quản Lý Dịch Vụ
Chạy `manage_service.bat` để:
- Xem trạng thái
- Khởi động / Dừng
- Khởi động lại
- Xem logs
- Xóa dịch vụ

---

## 📋 So Sánh Script

| Tính Năng | Basic | Advanced |
|-----------|-------|----------|
| Đăng bài tự động | ✅ | ✅ |
| Lên lịch 7 AM & 8 PM | ✅ | ✅ |
| Hashtags thông minh | ❌ | ✅ |
| Hình ảnh tự động | ❌ | ✅ |
| Logging chi tiết | ❌ | ✅ |
| Ghi logs vào file | ❌ | ✅ |

**Khuyến cáo:** Sử dụng **Advanced** (`facebook_auto_post_advanced.py`) để có tất cả tính năng.

---

## ⚙️ Cấu Hình Nâng Cao

### Thay Đổi Thời Gian Đăng Bài

Mở `facebook_auto_post_advanced.py` và tìm:

```python
schedule.every().day.at("07:00").do(self.scheduled_post_with_image)
schedule.every().day.at("20:00").do(self.scheduled_post)
```

Sửa thành (ví dụ: 9 AM và 6 PM):
```python
schedule.every().day.at("09:00").do(self.scheduled_post_with_image)
schedule.every().day.at("18:00").do(self.scheduled_post)
```

### Thêm Chủ Đề Mới

Tìm trong `facebook_auto_post_advanced.py`:

```python
TOPICS = [
    "năng lượng mặt trời",
    "pin lưu trữ năng lượng",
    # Thêm chủ đề mới ở đây
]
```

Thêm:
```python
    "tên chủ đề mới",
```

Và thêm chi tiết:
```python
CONTENT_DETAILS = {
    "tên chủ đề mới": "Nội dung chi tiết...",
}
```

### Thêm Hashtags

Tìm:
```python
HASHTAGS = [
    "#NăngLượngMặtTrời",
]
```

Thêm:
```python
    "#HashtagMới",
```

---

## 🐛 Xử Lý Lỗi

### "Python not found"
```
❌ Cài đặt Python từ https://www.python.org
❌ Chọn "Add Python to PATH" khi cài
❌ Khởi động lại máy
```

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install -r requirements.txt
```

### ".env file not found"
```bash
copy .env.example .env
# Sau đó điền thông tin vào .env
```

### "❌ Error 401 - Unauthorized"
```
❌ API Key không đúng
❌ Kiểm tra key từ Zernio Dashboard
❌ Cập nhật vào file .env
```

### "❌ Error 403 - Forbidden"
```
❌ Account ID không đúng hoặc Facebook Page chưa kết nối
❌ Kiểm tra Account ID từ Zernio Dashboard
❌ Đảm bảo Facebook Page đã được kết nối với Zernio
```

### "Dịch vụ Windows không khởi động"
```
1. Xóa dịch vụ: manage_service.bat → 6 → Y
2. Cài đặt lại: install_windows_service.bat (Run as Admin)
3. Kiểm tra logs: auto_post_stderr.log
```

Xem file `SETUP_GUIDE.md` để có hướng dẫn chi tiết hơn.

---

## 📊 Giám Sát Hoạt động

### Xem Logs Thời Thực
```bash
powershell -Command "Get-Content 'auto_post.log' -Wait -Tail 10"
```

### Files Logs
- `auto_post.log` - Log chính của ứng dụng
- `auto_post_stdout.log` - Output (khi chạy dịch vụ)
- `auto_post_stderr.log` - Errors (khi chạy dịch vụ)

### Theo Dõi trên Facebook
1. Đăng nhập Facebook Page
2. Vào **Insights** → **Posts**
3. Kiểm tra reaction, comment, share

---

## 🎓 Học Thêm

### Tài Liệu Zernio
- 📖 API Docs: https://docs.zernio.com
- 🏠 Website: https://zernio.com
- 💬 Support: https://zernio.com/support

### Python & Scheduling
- 📖 Schedule Library: https://schedule.readthedocs.io
- 📖 Python Docs: https://docs.python.org
- 📖 Requests Library: https://requests.readthedocs.io

### Windows
- 📖 Windows Task Scheduler: https://docs.microsoft.com/en-us/windows/win32/taskschd/
- 📖 NSSM (Service Manager): https://nssm.cc

---

## 📞 Hỗ Trợ & Giúp Đỡ

| Vấn Đề | Giải Pháp |
|--------|---------|
| Cài đặt nhanh | Xem `QUICK_START.md` |
| Hướng dẫn chi tiết | Xem `SETUP_GUIDE.md` |
| Script cơ bản | Xem `README_AUTO_POST.md` |
| Lỗi Zernio | Kiểm tra https://docs.zernio.com |
| Lỗi Python | Kiểm tra https://docs.python.org |

---

## ✅ Checklist Cài Đặt Hoàn Chỉnh

- [ ] Python 3.8+ đã cài đặt
- [ ] File `.env` đã tạo và điền thông tin
- [ ] Thư viện đã cài (`pip install -r requirements.txt`)
- [ ] Zernio API Key lấy được
- [ ] Facebook Account ID lấy được
- [ ] Script chạy thành công (test 1-2 lần)
- [ ] Dịch vụ Windows cài đặt (nếu muốn chạy 24/7)
- [ ] Logs cho thấy "✅ Đã lên lịch đăng bài"

---

## 📈 Những Tính Năng Tương Lai (v3.0)

- [ ] AI generate nội dung tự động
- [ ] Đăng bài với multiple images
- [ ] Hỗ trợ Instagram, Twitter, LinkedIn
- [ ] Scheduling lên lịch tuần
- [ ] Analytics dashboard
- [ ] Web UI quản lý

---

## 📄 License

Dự án này được phát triển cho **Hoa Huy Green Energy**.

---

## 🎉 Hoàn Tất!

Chúc mừng! Bạn đã cài đặt thành công **Facebook Auto Poster** cho Hoa Huy Green Energy.

### Tiếp Theo:
1. ✅ Cấu hình API keys
2. ✅ Chạy script test
3. ✅ Cài dịch vụ Windows (nếu cần)
4. ✅ Theo dõi logs
5. ✅ Tùy chỉnh nội dung

### Các Links Quan Trọng:
- 📌 **Quick Start:** `QUICK_START.md`
- 📋 **Chi Tiết:** `SETUP_GUIDE.md`
- 🚀 **Script Advanced:** `facebook_auto_post_advanced.py`

**Happy Posting! 🌞📱**

---

**Made with ❤️ for Hoa Huy Green Energy**
