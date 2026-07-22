import requests
import schedule
import time
from datetime import datetime
import json
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY', 'YOUR_ZERNIO_API_KEY')
ZERNIO_BASE_URL = 'https://api.zernio.com'
FACEBOOK_ACCOUNT_ID = os.getenv('FACEBOOK_ACCOUNT_ID', 'YOUR_FACEBOOK_ACCOUNT_ID')

# Topics for content generation
TOPICS = [
    "năng lượng mặt trời",
    "pin lưu trữ năng lượng",
    "biến tần inverter",
    "hệ thống điện mặt trời",
    "năng lượng tái tạo",
    "pin năng lượng mặt trời",
    "inverter hybrid",
    "hệ thống lưu trữ năng lượng"
]

# Sample content templates
CONTENT_TEMPLATES = [
    "💡 Kiến thức về {topic}:\n\n{detail}\n\n#NăngLượngMặtTrời #GreenEnergy #HoaHuy",
    "🌞 {topic} - Giải pháp năng lượng xanh:\n\n{detail}\n\n#NăngLượngTựatạo #EnergySolution",
    "⚡ {topic} là gì?\n\n{detail}\n\n#HoaHuyGreenEnergy #SolarPower",
    "🔋 Tìm hiểu về {topic}:\n\n{detail}\n\n#PinNăngLượng #GreenTech"
]

# Sample details for each topic
CONTENT_DETAILS = {
    "năng lượng mặt trời": "Năng lượng mặt trời là nguồn năng lượng sạch, tái tạo được sử dụng rộng rãi. Nó giúp giảm chi phí điện năng lên đến 70-80% mỗi tháng.",
    "pin lưu trữ năng lượng": "Pin lưu trữ năng lượng cho phép bạn sử dụng điện từ mặt trời 24/7. Công nghệ hiện đại tăng tuổi thọ pin lên 10-15 năm.",
    "biến tần inverter": "Biến tần inverter chuyển đổi điện một chiều (DC) từ pin thành điện xoay chiều (AC) để sử dụng các thiết bị điện gia dụng.",
    "hệ thống điện mặt trời": "Hệ thống điện mặt trời hoàn chỉnh bao gồm tấm pin, biến tần, pin lưu trữ và hệ thống điều khiển thông minh.",
    "năng lượng tái tạo": "Năng lượng tái tạo như mặt trời, gió giúp bảo vệ môi trường và giảm phụ thuộc vào năng lượng hóa thạch.",
    "pin năng lượng mặt trời": "Pin năng lượng mặt trời hiệu suất cao, tuổi thọ lâu dài là lựa chọn tối ưu cho hệ thống năng lượng mặt trời.",
    "inverter hybrid": "Inverter hybrid kết hợp chức năng chuyển đổi điện và quản lý pin, tối ưu hóa việc sử dụng năng lượng.",
    "hệ thống lưu trữ năng lượng": "Hệ thống lưu trữ năng lượng hiện đại cho phép tiết kiệm điện và sử dụng năng lượng hiệu quả hơn."
}

def generate_post_content() -> str:
    """Generate random content from templates and topics"""
    import random

    topic = random.choice(TOPICS)
    template = random.choice(CONTENT_TEMPLATES)
    detail = CONTENT_DETAILS.get(topic, "Tìm hiểu thêm về công nghệ năng lượng mặt trời hiện đại.")

    content = template.format(topic=topic, detail=detail)
    return content

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
    print("🌞 Hoa Huy Green Energy - Auto Facebook Poster")
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

    # Start scheduler
    schedule_jobs()
