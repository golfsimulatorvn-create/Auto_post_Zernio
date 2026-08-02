import requests
import schedule
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv

from content_generator import MIN_BODY_WORDS, generate_post, missing_brand_fields, load_brand

# Load environment variables
load_dotenv()

# Configuration
ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY', 'YOUR_ZERNIO_API_KEY')
ZERNIO_BASE_URL = 'https://zernio.com/api'
FACEBOOK_ACCOUNT_ID = os.getenv('FACEBOOK_ACCOUNT_ID', 'YOUR_FACEBOOK_ACCOUNT_ID')

BRAND_NAME = load_brand().get('company_name') or 'SVPsolar'

def generate_post_content() -> str:
    """Sinh bài đăng chuẩn SEO (thân bài > 300 từ)"""
    post = generate_post()
    report = post.seo_report
    print(f"📝 Chủ đề: {post.topic_id} | Từ khóa chính: {post.focus_keyword}")
    print(f"📊 Số từ: {report['body_word_count']} | "
          f"Mật độ từ khóa: {report['keyword_density_pct']}% | "
          f"Điểm SEO: {report['score']}")
    if report['body_word_count'] < MIN_BODY_WORDS:
        print(f"⚠️  Bài chỉ có {report['body_word_count']} từ, dưới ngưỡng {MIN_BODY_WORDS}.")
    return post.content

def post_to_facebook(content: str) -> bool:
    """Post content to Facebook via Zernio API"""
    try:
        headers = {
            'Authorization': f'Bearer {ZERNIO_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            'content': content,
            'publishNow': True,
            'platforms': [
                {
                    'platform': 'facebook',
                    'accountId': FACEBOOK_ACCOUNT_ID
                }
            ]
        }

        response = requests.post(
            f'{ZERNIO_BASE_URL}/v1/posts',
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code in [200, 201]:
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Đăng bài thành công!")
            print(f"Content: {content[:100]}...")
            return True
        else:
            print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Lỗi khi đăng bài: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Lỗi: {str(e)}")
        return False

def scheduled_post():
    """Job to generate and post content"""
    print(f"\n🔄 Đang tạo bài đăng lúc {datetime.now().strftime('%H:%M:%S')}...")
    content = generate_post_content()
    post_to_facebook(content)

def schedule_jobs():
    """Schedule posts at 7 AM and 8 PM"""
    schedule.every().day.at("07:00").do(scheduled_post)
    schedule.every().day.at("20:00").do(scheduled_post)

    print("✅ Đã lên lịch đăng bài vào 7 AM và 8 PM")
    print("🔄 Chương trình đang chạy... Nhấn Ctrl+C để dừng\n")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print("=" * 50)
    print(f"🌞 {BRAND_NAME} - Auto Facebook Poster")
    print("=" * 50)
    print(f"⏰ Bắt đầu lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Lên lịch: 7 AM & 8 PM mỗi ngày")
    print("=" * 50)

    # Verify configuration
    if ZERNIO_API_KEY == 'YOUR_ZERNIO_API_KEY':
        print("⚠️  CẢNH BÁO: Chưa cấu hình ZERNIO_API_KEY")
        print("Vui lòng cấu hình file .env")
        exit(1)

    if FACEBOOK_ACCOUNT_ID == 'YOUR_FACEBOOK_ACCOUNT_ID':
        print("⚠️  CẢNH BÁO: Chưa cấu hình FACEBOOK_ACCOUNT_ID")
        print("Vui lòng cấu hình file .env")
        exit(1)

    missing = missing_brand_fields()
    if missing:
        print(f"❌ brand_config.json còn thiếu: {', '.join(missing)}")
        print("Kiểm tra bằng: python content_generator.py --check-brand")
        exit(1)

    # Start scheduler
    schedule_jobs()
