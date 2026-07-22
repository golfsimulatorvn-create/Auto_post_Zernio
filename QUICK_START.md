# 🚀 Quick Start - Bắt Đầu Nhanh

Hướng dẫn nhanh để chạy Facebook Auto Poster trong **5 phút**.

---

## ⚡ 5 Bước Nhanh

### 1️⃣ Tạo File `.env`

Sao chép `.env.example` thành `.env`:

**Windows:**
```bash
copy .env.example .env
```

### 2️⃣ Lấy Zernio API Key

1. Đăng nhập: https://zernio.com/dashboard
2. Vào **Settings** → **API Keys**
3. Sao chép API Key

### 3️⃣ Lấy Facebook Account ID

1. Vẫn ở Zernio Dashboard
2. Vào **Connected Accounts**
3. Sao chép Account ID của Facebook Page

### 4️⃣ Điền Thông Tin

Mở file `.env` và điền:

```env
ZERNIO_API_KEY=your_key_here
FACEBOOK_ACCOUNT_ID=your_id_here
```

### 5️⃣ Cài Đặt & Chạy

```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Chạy script
python facebook_auto_post_advanced.py
```

✅ Done! Script sẽ tự động đăng bài vào **7 AM** và **8 PM**

---

## 🖥️ Chạy 24/7 (Optional)

**Windows:** Nhấp đôi vào `install_windows_service.bat` (chạy dưới quyền Admin)

Script sẽ tự động cài đặt dịch vụ Windows chạy 24/7 ở background.

---

## 📂 Các File Quan Trọng

| File | Mục Đích |
|------|---------|
| `facebook_auto_post_advanced.py` | Script chính |
| `.env` | Cấu hình API Keys |
| `requirements.txt` | Thư viện cần thiết |
| `run_poster_service.bat` | Chạy script trực tiếp |
| `install_windows_service.bat` | Cài đặt dịch vụ Windows |
| `manage_service.bat` | Quản lý dịch vụ |
| `auto_post.log` | Logs hoạt động |

---

## ❓ Xử Lý Lỗi Nhanh

| Lỗi | Giải Pháp |
|-----|---------|
| "Python not found" | Cài Python và thêm vào PATH |
| "No module named 'requests'" | `pip install -r requirements.txt` |
| ".env file not found" | `copy .env.example .env` |
| "❌ Error 401" | Kiểm tra API Key có đúng không |
| "❌ Error 403" | Kiểm tra Account ID có đúng không |

---

## 📞 Cần Trợ Giúp Thêm?

Xem file `SETUP_GUIDE.md` để có hướng dẫn chi tiết đầy đủ.

---

**Let's Go! 🌞**
