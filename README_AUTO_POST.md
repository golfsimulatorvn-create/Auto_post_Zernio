# 🌞 SVPsolar - Auto Facebook Poster

Công cụ tự động tìm kiếm và đăng bài lên Facebook về năng lượng mặt trời, pin lưu trữ, và biến tần inverter.

## ✨ Tính năng

- ✅ Tự động tạo nội dung về các chủ đề năng lượng xanh
- ✅ Đăng bài tự động vào **7 AM** và **8 PM** mỗi ngày
- ✅ Tích hợp với **Zernio API** để quản lý các nền tảng xã hội
- ✅ Dễ cấu hình và mở rộng

## 📋 Yêu cầu

- Python 3.8+
- Tài khoản Zernio (https://zernio.com)
- Tài khoản Facebook Page được kết nối với Zernio
- API Key từ Zernio

## 🚀 Cách cài đặt

### 1. Clone hoặc tải file script

```bash
cd "D:\SVPsolar\Auto_post_Zernio"
```

### 2. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

### 3. Cấu hình Zernio API Key và Facebook Account ID

**Cách lấy Zernio API Key:**
1. Đăng nhập vào https://zernio.com/dashboard
2. Vào mục **Settings** → **API Keys**
3. Tạo API key mới hoặc sao chép key hiện có

**Cách lấy Facebook Account ID:**
1. Đăng nhập vào Zernio Dashboard
2. Kết nối Facebook Page của bạn (nếu chưa kết nối)
3. Xem Account ID trong mục **Connected Accounts**

### 4. Tạo file `.env`

Sao chép file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Hoặc trên Windows:

```bash
copy .env.example .env
```

### 5. Chỉnh sửa file `.env`

Mở file `.env` và điền thông tin:

```
ZERNIO_API_KEY=your_actual_api_key_here
FACEBOOK_ACCOUNT_ID=your_facebook_account_id_here
TIMEZONE=Asia/Ho_Chi_Minh
```

## ▶️ Chạy Script

```bash
python facebook_auto_post.py
```

Script sẽ:
- ✅ Kiểm tra cấu hình
- ✅ Lên lịch đăng bài vào 7 AM và 8 PM
- ✅ Chạy liên tục và chờ thời gian lên lịch

### Dừng Script

Nhấn `Ctrl + C` để dừng chương trình.

## 📅 Chạy 24/7 (Optional)

Để script chạy 24/7, bạn có thể:

### Trên Windows:

#### Cách 1: Dùng Task Scheduler
1. Mở **Task Scheduler** (Win + R → `taskschd.msc`)
2. Tạo task mới:
   - **Name:** SVPsolar Auto Post
   - **Trigger:** At startup (hoặc daily)
   - **Action:** Start a program → `C:\Python311\python.exe` (hoặc đường dẫn Python của bạn)
   - **Arguments:** `facebook_auto_post.py`
   - **Start in:** `D:\SVPsolar\Auto_post_Zernio`

#### Cách 2: Dùng NSSM (Non-Sucking Service Manager)
1. Tải NSSM: https://nssm.cc/download
2. Chạy:
```bash
nssm install SVPsolarAutoPost "C:\Python311\python.exe" "facebook_auto_post.py"
nssm start SVPsolarAutoPost
```

### Trên Linux/Mac:

Dùng Cron job:

```bash
crontab -e
```

Thêm dòng:
```
0 0 * * * cd /path/to/script && python facebook_auto_post.py
```

## 📝 Tùy chỉnh Nội dung

Toàn bộ nội dung nằm trong `content_generator.py`, không còn nằm rải rác trong
các script đăng bài. Chi tiết đầy đủ xem `SEO_CONTENT_GUIDE.md`.

### Trước tiên: điền thông tin công ty

Mở `brand_config.json` và điền tối thiểu `company_name`, `website`, `hotline`.
Script sẽ **từ chối đăng** cho tới khi điền đủ — đây là chủ ý để không đăng bài
thiếu thông tin liên hệ.

```bash
python content_generator.py --check-brand
```

Các trường tùy chọn (`service_area`, `years_experience`, `projects_completed`,
`warranty_years`, `certifications`, `partner_brands`) mỗi trường mở khóa thêm
một khối uy tín trong bài. Để trống thì khối đó bị bỏ qua, không tự điền số.

### Thêm chủ đề mới

Thêm một mục vào danh sách `TOPICS` trong `content_generator.py`. Mỗi chủ đề
cần: `focus_keyword`, `secondary_keywords`, `hooks`, `intros`, tối thiểu 5
`sections`, `closings`, `hashtags`, `image_query`, `image_alt`.

Hai nguyên tắc bắt buộc:

- Phần thân **không chứa khẳng định riêng về công ty** — mọi thông tin thương
  hiệu chỉ đến từ `brand_config.json`.
- **Không đưa số liệu tiết kiệm hay hoàn vốn cụ thể**, vì chúng phụ thuộc bức
  xạ khu vực và mức tiêu thụ của từng công trình.

Sau khi thêm, chạy kiểm tra chất lượng:

```bash
python content_generator.py --audit 100   # exit code 1 nếu có bài không đạt
```

### Xem thử trước khi đăng

```bash
python content_generator.py --list                 # liệt kê 12 chủ đề
python content_generator.py --topic chon-inverter  # xem thử một bài + báo cáo SEO
```

## 🔄 Nâng cấp - Tìm kiếm nội dung động

Hiện tại script sử dụng nội dung mẫu. Để tìm kiếm nội dung động từ web, bạn có thể thêm:

```python
from bs4 import BeautifulSoup
import requests

def fetch_dynamic_content(topic):
    # Tìm kiếm nội dung từ nguồn tin
    pass
```

Thêm `beautifulsoup4` vào `requirements.txt`:

```
beautifulsoup4==4.12.2
```

## 🐛 Xử lý lỗi

### Lỗi: "ModuleNotFoundError: No module named 'requests'"

Cài đặt lại thư viện:
```bash
pip install -r requirements.txt
```

### Lỗi: "CẢNH BÁO: Chưa cấu hình ZERNIO_API_KEY"

Kiểm tra file `.env` có tồn tại và đúng định dạng.

### Lỗi: "❌ Lỗi khi đăng bài"

Kiểm tra:
1. API Key có chính xác không?
2. Facebook Account ID có đúng không?
3. Tài khoản Facebook đã được kết nối với Zernio chưa?

## 📊 Logs và Monitoring

Script sẽ in ra logs mỗi lần đăng bài:

```
✅ [14:30:45] Đăng bài thành công!
Content: 💡 Kiến thức về năng lượng mặt trời...
```

Để lưu logs vào file, sửa đổi script:

```python
import logging

logging.basicConfig(
    filename='auto_post.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## 📞 Hỗ trợ

- Tài liệu Zernio: https://docs.zernio.com
- GitHub Issues: [Báo cáo lỗi]

## 📄 License

Dự án này là của SVPsolar.

---

**Chúc bạn thành công! 🌞**
