# 🌞 Hoa Huy Green Energy - Complete Setup Guide

Hướng dẫn chi tiết cài đặt và sử dụng tất cả các tính năng của Auto Facebook Poster.

---

## 📋 Mục Lục

1. [Yêu Cầu](#yêu-cầu)
2. [Lấy API Keys](#lấy-api-keys)
3. [Cài Đặt Cơ Bản](#cài-đặt-cơ-bản)
4. [Các Phiên Bản Script](#các-phiên-bản-script)
5. [Chạy 24/7 trên Windows](#chạy-247-trên-windows)
6. [Quản Lý Dịch Vụ](#quản-lý-dịch-vụ)
7. [Tùy Chỉnh Nội Dung](#tùy-chỉnh-nội-dung)
8. [Xử Lý Lỗi](#xử-lý-lỗi)

---

## 🔧 Yêu Cầu

- ✅ **Python 3.8+** - [Tải từ python.org](https://www.python.org/downloads/)
- ✅ **Tài khoản Zernio** - [Đăng ký tại zernio.com](https://zernio.com/signup)
- ✅ **Tài khoản Facebook** có một Page được kết nối với Zernio
- ✅ **Windows 7+** (để chạy dịch vụ Windows)

---

## 🔑 Lấy API Keys

### 1️⃣ Zernio API Key

**Bước 1:** Đăng nhập vào https://zernio.com/dashboard

**Bước 2:** Vào **Settings** → **API Keys**

**Bước 3:** Tạo API key mới hoặc sao chép key hiện có

**Bước 4:** Lưu key vào file `.env` (xem bên dưới)

![Zernio API Key Location]

### 2️⃣ Facebook Account ID

**Bước 1:** Vẫn ở Zernio Dashboard

**Bước 2:** Vào mục **Connected Accounts**

**Bước 3:** Kiểm tra Account ID của Facebook Page bạn

**Bước 4:** Lưu ID vào file `.env`

### 3️⃣ Unsplash Access Key (Optional - để có hình ảnh)

**Bước 1:** Truy cập https://unsplash.com/developers

**Bước 2:** Đăng nhập hoặc tạo tài khoản

**Bước 3:** Tạo ứng dụng mới

**Bước 4:** Sao chép **Access Key**

**Bước 5:** Lưu vào file `.env`

---

## 🚀 Cài Đặt Cơ Bản

### Bước 1: Chuẩn Bị Thư Mục

```bash
# Mở PowerShell hoặc Command Prompt
# Điều hướng tới thư mục dự án
cd "D:\1. CLAUDE\HOA HUY\Hoa huy green energy"
```

### Bước 2: Tạo File `.env`

**Cách 1:** Sao chép tự động (Windows)
```bash
copy .env.example .env
```

**Cách 2:** Sao chép tự động (PowerShell)
```powershell
Copy-Item .env.example -Destination .env
```

**Cách 3:** Tạo tay
- Tạo file `notefile.txt` trong thư mục dự án
- Đổi tên thành `.env`
- Điền nội dung (xem bên dưới)

### Bước 3: Điền Thông Tin API

Mở file `.env` và điền thông tin:

```env
ZERNIO_API_KEY=sk_live_your_actual_key_here
FACEBOOK_ACCOUNT_ID=123456789
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
TIMEZONE=Asia/Ho_Chi_Minh
```

### Bước 4: Cài Đặt Thư Viện

```bash
pip install -r requirements.txt
```

Nếu có lỗi, hãy thử:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📝 Các Phiên Bản Script

### Version 1: Basic (facebook_auto_post.py)
- ✅ Đăng bài tự động vào 7 AM và 8 PM
- ✅ Nội dung mẫu cố định
- ✅ Không cần Unsplash key

**Chạy:**
```bash
python facebook_auto_post.py
```

### Version 2: Advanced (facebook_auto_post_advanced.py) ⭐ KHUYÊN DÙNG
- ✅ Đăng bài tự động vào 7 AM và 8 PM
- ✅ Tìm kiếm hình ảnh tự động từ Unsplash
- ✅ Hashtags thông minh
- ✅ Logging chi tiết
- ✅ Ghi logs vào file

**Chạy:**
```bash
python facebook_auto_post_advanced.py
```

---

## 🖥️ Chạy 24/7 trên Windows

Bạn có 2 lựa chọn:

### Lựa Chọn 1: Chạy Script Trực Tiếp (Đơn Giản)

**Bước 1:** Mở file `run_poster_service.bat` và nhấp đôi vào nó

**Bước 2:** Script sẽ:
- ✅ Kiểm tra Python
- ✅ Kiểm tra file `.env`
- ✅ Cài đặt thư viện (nếu cần)
- ✅ Bắt đầu chạy

**Bước 3:** Để chạy 24/7, bạn cần giữ cửa sổ mở

**⚠️ Nhược điểm:** Cửa sổ phải luôn mở, nếu tắt máy sẽ dừng

### Lựa Chọn 2: Cài Đặt Dịch Vụ Windows (Chuyên Nghiệp) ⭐ KHUYÊN DÙNG

**Bước 1:** Nhấp chuột phải vào `install_windows_service.bat` → **Run as administrator**

**Bước 2:** Script sẽ tự động:
- ✅ Tải NSSM (chương trình quản lý dịch vụ)
- ✅ Tạo dịch vụ Windows
- ✅ Khởi động dịch vụ

**Bước 3:** Dịch vụ sẽ:
- ✅ Chạy 24/7 ở background
- ✅ Tự động khởi động khi bắt đầu Windows
- ✅ Chạy ngay cả khi bạn không đăng nhập

**✅ Lợi ích:** 
- Chạy 24/7 ngay cả khi tắt máy
- Không cần cửa sổ lệnh mở
- Tự động khởi động lại nếu gặp lỗi

---

## 🔧 Quản Lý Dịch Vụ

Sử dụng `manage_service.bat` để quản lý dịch vụ:

### Xem Trạng Thái

Chạy `manage_service.bat` → Chọn **1** → **Enter**

Kết quả:
```
SERVICE_NAME        : HoaHuyAutoPost
DISPLAY_NAME        : HoaHuyAutoPost
        TYPE                : 10 WIN32_OWN_PROCESS
        STATE               : 4 RUNNING
        WIN32_EXIT_CODE     : 0
        SERVICE_EXIT_CODE   : 0
        CHECKPOINT          : 0x0
        WAIT_HINT           : 0x0
```

### Khởi Động Dịch Vụ

Chạy `manage_service.bat` → Chọn **2** → **Enter**

```
✅ Dịch vụ đã khởi động thành công
```

### Dừng Dịch Vụ

Chạy `manage_service.bat` → Chọn **3** → **Enter**

```
⏹️  Dừng dịch vụ...
✅ Dịch vụ đã dừng thành công
```

### Khởi Động Lại

Chạy `manage_service.bat` → Chọn **4** → **Enter**

### Xem Logs

Chạy `manage_service.bat` → Chọn **5** → **Enter**

Hiển thị 50 dòng log cuối cùng

### Xóa Dịch Vụ

Chạy `manage_service.bat` → Chọn **6** → **Enter** → **Y**

⚠️ **Lưu ý:** Nhấp chuột phải → **Run as administrator**

---

## ✨ Tùy Chỉnh Nội Dung

### Thêm Chủ Đề Mới

Mở `facebook_auto_post_advanced.py` và tìm:

```python
TOPICS = [
    "năng lượng mặt trời",
    "pin lưu trữ năng lượng",
    # Thêm chủ đề mới ở đây
]
```

Thêm dòng:
```python
    "tên chủ đề mới",
```

Và thêm chi tiết vào `CONTENT_DETAILS`:

```python
CONTENT_DETAILS = {
    "tên chủ đề mới": "Nội dung chi tiết về chủ đề này...",
}
```

### Thêm Template Nội Dung

Tìm:
```python
CONTENT_TEMPLATES = [
    "💡 Kiến thức về {topic}:...",
    # Thêm template mới
]
```

Thêm:
```python
    "🎯 {topic} - Lựa chọn tốt:\n\n{detail}\n\n{hashtags}",
```

### Thêm Hashtags

Tìm:
```python
HASHTAGS = [
    "#NăngLượngMặtTrời",
    # Thêm hashtag mới
]
```

Thêm:
```python
    "#HashtagMới",
```

### Thay Đổi Thời Gian Đăng Bài

Tìm trong `facebook_auto_post_advanced.py`:

```python
schedule.every().day.at("07:00").do(self.scheduled_post_with_image)
schedule.every().day.at("20:00").do(self.scheduled_post)
```

Sửa thành:
```python
schedule.every().day.at("09:00").do(self.scheduled_post_with_image)  # 9 AM
schedule.every().day.at("18:00").do(self.scheduled_post)             # 6 PM
```

⏰ **Định Dạng:** "HH:MM" (24 giờ)

---

## 🐛 Xử Lý Lỗi

### Lỗi: "Python không được tìm thấy"

**Nguyên Nhân:** Python chưa được cài đặt hoặc không trong PATH

**Giải Pháp:**
1. Tải Python từ https://www.python.org
2. **BẮT BUỘC:** Chọn "Add Python to PATH" khi cài đặt
3. Khởi động lại máy tính
4. Thử lại

### Lỗi: "ModuleNotFoundError: No module named 'requests'"

**Nguyên Nhân:** Thư viện chưa được cài đặt

**Giải Pháp:**
```bash
pip install -r requirements.txt
```

Nếu vẫn lỗi:
```bash
python -m pip install --upgrade pip
pip install requests schedule python-dotenv
```

### Lỗi: ".env file not found"

**Nguyên Nhân:** File `.env` không được tạo

**Giải Pháp:**
```bash
copy .env.example .env
```

Sau đó điền thông tin vào file `.env`

### Lỗi: "❌ Lỗi khi đăng bài: 401"

**Nguyên Nhân:** API Key không đúng hoặc hết hạn

**Giải Pháp:**
1. Kiểm tra Zernio API Key có chính xác không
2. Tạo API key mới từ Zernio Dashboard
3. Cập nhật vào file `.env`

### Lỗi: "❌ Lỗi khi đăng bài: 403"

**Nguyên Nhân:** Tài khoản Facebook không được kết nối

**Giải Pháp:**
1. Kiểm tra Facebook Account ID có chính xác không
2. Đảm bảo tài khoản Facebook đã được kết nối với Zernio
3. Kiểm tra quyền của Facebook Page

### Logs cho biết không có lỗi nhưng bài không được đăng

**Nguyên Nhân:** Thường là do thiếu quyền hoặc tài khoản bị khóa

**Giải Pháp:**
1. Kiểm tra logs: `auto_post.log`
2. Đăng nhập vào Facebook và kiểm tra tình trạng Page
3. Liên hệ Zernio support

### Dịch vụ Windows không khởi động

**Nguyên Nhân:** Lỗi cấu hình hoặc quyền

**Giải Pháp:**
1. Xóa dịch vụ: Chạy `manage_service.bat` → **6** → **Y**
2. Cài đặt lại: Nhấp chuột phải vào `install_windows_service.bat` → **Run as administrator**
3. Kiểm tra logs: `auto_post_stderr.log`

---

## 📊 Giám Sát Hoạt động

### Xem Logs Trong Lúc Chạy

**Windows Command Prompt:**
```bash
powershell -Command "Get-Content 'auto_post.log' -Wait -Tail 10"
```

**Hoặc dùng `manage_service.bat`:**
- Chọn **5** để xem 50 dòng log cuối cùng

### Logs chi tiết

- **auto_post.log** - Log chính của ứng dụng
- **auto_post_stdout.log** - Output chuẩn (khi chạy dịch vụ)
- **auto_post_stderr.log** - Errors (khi chạy dịch vụ)

### Theo Dõi Trên Facebook

1. Đăng nhập vào Facebook Page
2. Vào **Insights** → **Posts** để xem bài đăng
3. Kiểm tra reaction, comment, share

---

## 📞 Hỗ Trợ

- **Zernio Docs:** https://docs.zernio.com
- **Zernio Support:** https://zernio.com/support
- **Python Docs:** https://docs.python.org
- **Windows Task Scheduler:** https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page

---

## ✅ Checklist Cài Đặt Hoàn Chỉnh

- [ ] Python 3.8+ đã cài đặt và thêm vào PATH
- [ ] File `.env` đã được tạo và điền đầy đủ
- [ ] Thư viện đã được cài đặt (`pip install -r requirements.txt`)
- [ ] Zernio API Key đã được lấy và điền vào `.env`
- [ ] Facebook Account ID đã được lấy và điền vào `.env`
- [ ] Unsplash Access Key (optional) đã được lấy
- [ ] Script có thể chạy thành công (`python facebook_auto_post_advanced.py`)
- [ ] Dịch vụ Windows đã được cài đặt (nếu muốn chạy 24/7)
- [ ] Logs cho thấy "✅ Đã lên lịch đăng bài"

---

## 🎉 Hoàn Tất!

Chúc mừng! Bạn đã cài đặt thành công Auto Facebook Poster cho Hoa Huy Green Energy.

Dịch vụ sẽ:
- ✅ Tự động đăng bài vào **7 AM** (với hình ảnh)
- ✅ Tự động đăng bài vào **8 PM** (mà không hình ảnh)
- ✅ Chạy **24/7** trên background
- ✅ Tự động khởi động lại nếu gặp lỗi

**Happy Posting! 🌞📱**

---

**Phiên bản:** 2.0  
**Cập nhật lần cuối:** 2024  
**Được tạo cho:** Hoa Huy Green Energy
