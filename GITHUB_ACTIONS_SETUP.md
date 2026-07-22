# 🚀 GitHub Actions - Chạy Auto Poster trên GitHub

Hướng dẫn cài đặt GitHub Actions để chạy Facebook Auto Poster tự động trên GitHub.

---

## ✨ Lợi Ích

- ✅ **Không cần máy chủ riêng** - Chạy trên máy chủ GitHub miễn phí
- ✅ **Chạy 24/7** - Không cần máy tính của bạn bật
- ✅ **Tự động theo lịch** - Đặt lịch và quên đi
- ✅ **Logs chi tiết** - Xem chi tiết mỗi lần chạy
- ✅ **Miễn phí** - 2,000 phút/tháng (đủ cho hầu hết trường hợp)

---

## 📋 Yêu Cầu

1. **Tài khoản GitHub** - https://github.com
2. **Repository** - Public hoặc Private
3. **API Keys** - Zernio API Key + Facebook Account ID
4. **Unsplash Key (optional)** - Để có hình ảnh

---

## 🛠️ Bước Cài Đặt

### Bước 1: Đẩy Code lên GitHub

Nếu chưa có repository:

```bash
# Khởi tạo git
git init

# Thêm remote
git remote add origin https://github.com/username/hoa-huy-auto-poster.git

# Tạo branch main
git branch -M main

# Thêm file
git add .

# Commit
git commit -m "Initial commit: Facebook Auto Poster"

# Push lên GitHub
git push -u origin main
```

✅ Workflow file `.github/workflows/auto-post.yml` sẽ được GitHub tự động detect.

### Bước 2: Thêm Secrets vào GitHub

**Secrets** là nơi lưu API keys an toàn (không hiển thị công khai).

#### Cách Thêm Secrets:

1. **Truy cập Repository**
   - Vào https://github.com/username/repository-name
   - Hoặc `GitHub Desktop` → Repository → View on GitHub

2. **Mở Settings**
   - Nhấp vào tab **Settings** (trên cùng repository)
   
3. **Vào Secrets**
   - Left sidebar → **Secrets and variables** → **Actions**
   - Hoặc truy cập: `Settings/secrets/actions`

4. **Thêm Secrets**
   - Nhấp **New repository secret**
   - Thêm các secret sau:

| Name | Value | Từ Đâu |
|------|-------|--------|
| `ZERNIO_API_KEY` | `sk_live_xxxxx` | Zernio Dashboard → Settings → API Keys |
| `FACEBOOK_ACCOUNT_ID` | `123456789` | Zernio Dashboard → Connected Accounts |
| `UNSPLASH_ACCESS_KEY` | `xxxxx` | Unsplash Developers (optional) |

**Ví dụ thêm ZERNIO_API_KEY:**

```
Name: ZERNIO_API_KEY
Secret: sk_live_your_actual_key_here
```

Nhấp **Add secret** → Lặp lại cho 2 secret còn lại.

### Bước 3: Kiểm Tra Workflow

1. **Vào tab Actions**
   - Repository → Tab **Actions**
   
2. **Xem Workflows**
   - Left sidebar: "🌞 Hoa Huy Auto Facebook Poster"
   
3. **Chạy Thủ Công (Test)**
   - Chọn workflow
   - **Run workflow** → **Run workflow**
   - Chờ hoàn thành (2-3 phút)

4. **Kiểm Tra Logs**
   - Nhấp vào "Run" (trên cùng)
   - Xem chi tiết từng bước

---

## ⏰ Lịch Chạy (Cron Schedule)

Workflow được cấu hình chạy vào:

- **7 AM UTC+7** = 12 AM UTC (00:00 UTC)
  ```yaml
  - cron: '0 0 * * *'
  ```

- **8 PM UTC+7** = 1 PM UTC (13:00 UTC)
  ```yaml
  - cron: '0 13 * * *'
  ```

### Thay Đổi Lịch Chạy

Nếu muốn thay đổi thời gian, mở file `.github/workflows/auto-post.yml` và sửa:

```yaml
schedule:
  - cron: '0 0 * * *'      # Lúc 12 AM UTC (00:00)
  - cron: '0 13 * * *'     # Lúc 1 PM UTC (13:00)
```

**Cron Format:** `minute hour day month weekday`

**Ví dụ:**
```yaml
# 9 AM UTC+7 = 2 AM UTC
- cron: '0 2 * * *'

# 6 PM UTC+7 = 11 AM UTC
- cron: '0 11 * * *'

# Mỗi 1 giờ
- cron: '0 * * * *'

# Mỗi 30 phút
- cron: '*/30 * * * *'
```

**Công cụ:** https://crontab.guru (để kiểm tra cron expression)

---

## 📊 Giám Sát Hoạt động

### Xem Lịch Sử Chạy

1. **Repository → Actions**
2. **Chọn workflow:** "🌞 Hoa Huy Auto Facebook Poster"
3. **Xem các lần chạy** - Hiển thị tất cả các lần chạy

### Xem Chi Tiết Logs

1. **Chọn một "Run"** từ lịch sử
2. **Mở "post-to-facebook" job**
3. **Xem các steps:**
   - ✅ Checkout code
   - ✅ Setup Python
   - ✅ Install dependencies
   - ✅ Setup environment
   - ✅ Run Facebook Auto Poster
   - ✅ Upload logs

### Download Logs

1. **Artifacts** section (dưới cùng của Run)
2. **Download "auto-post-logs.zip"**
3. **Giải nén và mở `auto_post.log`**

---

## 🔔 Nhận Thông Báo

### Email Notifications (Mặc Định)

GitHub sẽ gửi email nếu workflow:
- ✅ Thất bại
- ✅ Hoàn thành sau khi thất bại

### Cấu Hình Notifications

1. **GitHub Settings** (cá nhân)
   - Avatar → **Settings** → **Notifications**
2. **Chọn cách nhận thông báo:**
   - Email
   - Web
   - Mobile app

---

## 🐛 Xử Lý Lỗi

### Workflow Không Chạy

**Nguyên nhân có thể:**
- [ ] Workflow file không trong `.github/workflows/`
- [ ] Tên file không đúng (phải là `.yml` hoặc `.yaml`)
- [ ] YAML syntax sai (kiểm tra indentation)

**Giải pháp:**
1. Kiểm tra file path: `.github/workflows/auto-post.yml`
2. Kiểm tra YAML syntax (sử dụng https://www.yamllint.com)
3. Push code lên GitHub lại

### Workflow Chạy Nhưng Fail

**Kiểm tra Logs:**
1. **Actions** → **Chọn Run** → **post-to-facebook**
2. **Xem chi tiết lỗi**

**Lỗi Phổ Biến:**

| Lỗi | Giải Pháp |
|-----|---------|
| `ModuleNotFoundError` | Kiểm tra `requirements.txt` |
| `API Key not found` | Kiểm tra Secrets có được thêm không |
| `401 Unauthorized` | API Key sai hoặc hết hạn |
| `403 Forbidden` | Account ID sai hoặc Facebook Page chưa kết nối |
| `Timeout` | Script mất quá lâu, tăng timeout (hiện là 10 phút) |

### Không Có Logs File

Nếu không thấy `auto-post-logs` artifact:
- Script chạy quá nhanh (logs chưa được upload)
- Hoặc script crash ngay đầu

**Giải pháp:** Xem console output từng step.

---

## 📈 Mẹo & Tối Ưu

### 1. Giảm Thời Gian Chạy

Thêm `cache: 'pip'` trong Python setup (đã có sẵn):
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'  # ← Caching pip
```

### 2. Tùy Chỉnh Thời Gian Chạy

Nếu muốn chạy vào các thời gian khác nhau:
```yaml
schedule:
  - cron: '0 0 * * *'      # 7 AM UTC+7 (Thứ 2-7)
  - cron: '0 13 * * *'     # 8 PM UTC+7
  - cron: '0 6 * * 0'      # 1 PM UTC+7 vào Chủ Nhật
```

### 3. Thêm Log Chi Tiết

Mở `.github/workflows/auto-post.yml` và thêm:
```yaml
- name: 🐛 Debug
  if: failure()
  run: |
    echo "=== Python Version ==="
    python --version
    echo "=== Installed Packages ==="
    pip list
    echo "=== Environment ==="
    env | grep -E "ZERNIO|FACEBOOK"
```

### 4. Chạy Hàng Tuần

Nếu muốn chạy ít thường xuyên hơn:
```yaml
schedule:
  # Chỉ 2 lần mỗi tuần (Thứ 3 & Thứ 7)
  - cron: '0 0 * * 3'   # Thứ 4
  - cron: '0 13 * * 0'  # Chủ Nhật
```

---

## 🔐 Bảo Mật

### ✅ Secrets Được Bảo Vệ

- API keys được mã hóa
- Không hiển thị trong logs
- Chỉ được sử dụng bởi các workflows
- Có thể xóa/cập nhật bất kỳ lúc nào

### ❌ Không Làm

- ❌ Không hardcode API keys vào code
- ❌ Không commit `.env` file
- ❌ Không chia sẻ secrets với người khác
- ❌ Không push code với API keys

### ✅ Các Biện Pháp An Toàn

1. **Thêm `.env` vào `.gitignore`:**
   ```
   .env
   .env.local
   *.log
   ```

2. **Rotate API Keys thường xuyên:**
   - Zernio: Tạo key mới, xóa key cũ
   - Unsplash: Thay đổi key mỗi 3 tháng

3. **Kiểm tra Workflow Logs:**
   - Đảm bảo API keys không xuất hiện
   - GitHub sẽ tự động mask secrets

---

## 📚 Tài Liệu Thêm

- **GitHub Actions:** https://docs.github.com/en/actions
- **Scheduling Workflows:** https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#on-schedule
- **Secrets Management:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Cron Schedule:** https://crontab.guru

---

## ✅ Checklist Cài Đặt

- [ ] Repository đã có code trên GitHub
- [ ] Workflow file `.github/workflows/auto-post.yml` đã được push
- [ ] `ZERNIO_API_KEY` secret đã được thêm
- [ ] `FACEBOOK_ACCOUNT_ID` secret đã được thêm
- [ ] `UNSPLASH_ACCESS_KEY` secret đã được thêm (optional)
- [ ] Workflow đã được test thủ công (workflow_dispatch)
- [ ] Logs không có lỗi
- [ ] Bài đăng xuất hiện trên Facebook

---

## 🎉 Hoàn Tất!

Chúc mừng! GitHub Actions đã được cài đặt thành công.

### Tiếp Theo:
1. ✅ GitHub sẽ tự động chạy workflow vào **7 AM & 8 PM UTC+7**
2. ✅ Kiểm tra **Actions** tab để xem logs
3. ✅ Kiểm tra Facebook Page để xem bài đăng
4. ✅ Tùy chỉnh lịch chạy nếu cần

### Lợi Ích:
- ✅ Không cần máy chủ riêng
- ✅ Không cần máy tính luôn bật
- ✅ Chạy tự động mỗi ngày
- ✅ Logs chi tiết
- ✅ Miễn phí (2,000 phút/tháng)

**Happy Automation! 🚀**

---

**GitHub Actions - Auto Posting Made Easy**
