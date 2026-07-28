import requests
import schedule
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import random
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_post.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY', 'YOUR_ZERNIO_API_KEY')
ZERNIO_BASE_URL = 'https://zernio.com/api' # Updated to match 2026 Zernio Docs
FACEBOOK_ACCOUNT_ID = os.getenv('FACEBOOK_ACCOUNT_ID', 'YOUR_FACEBOOK_ACCOUNT_ID')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')  # Optional

# Topics and hashtags
TOPICS = [
    "năng lượng mặt trời",
    "pin lưu trữ năng lượng",
    "biến tần inverter",
    "hệ thống điện mặt trời",
    "năng lượng tái tạo",
    "pin năng lượng mặt trời",
    "inverter hybrid",
    "hệ thống lưu trữ năng lượng",
    "tấm pin quang điện",
    "năng lượng xanh"
]

HASHTAGS = [
    "#NăngLượngMặtTrời",
    "#GreenEnergy",
    "#HoaHuy",
    "#NăngLượngTựatạo",
    "#EnergySolution",
    "#SolarPower",
    "#PinNăngLượng",
    "#GreenTech",
    "#SustainableEnergy",
    "#EnergyStorage",
    "#InverterHybrid",
    "#NăngLượngXanh",
    "#ĐiệnMặtTrời",
    "#FutureEnergy"
]

CONTENT_TEMPLATES = [
    "💡 Kiến thức về {topic}:\n\n{detail}\n\n{hashtags}",
    "🌞 {topic} - Giải pháp năng lượng xanh:\n\n{detail}\n\n{hashtags}",
    "⚡ {topic} là gì?\n\n{detail}\n\n{hashtags}",
    "🔋 Tìm hiểu về {topic}:\n\n{detail}\n\n{hashtags}",
    "💰 Tiết kiệm tiền với {topic}:\n\n{detail}\n\n{hashtags}",
    "🌍 {topic} - Bảo vệ môi trường:\n\n{detail}\n\n{hashtags}",
    "⚙️ Cách {topic} hoạt động:\n\n{detail}\n\n{hashtags}",
    "📊 Hiệu suất {topic}:\n\n{detail}\n\n{hashtags}"
]

CONTENT_DETAILS = {
    "năng lượng mặt trời": "Năng lượng mặt trời là nguồn năng lượng sạch, tái tạo được sử dụng rộng rãi. Nó giúp giảm chi phí điện năng lên đến 70-80% mỗi tháng. Với hệ thống hiện đại, bạn có thể được độc lập năng lượng hoàn toàn.",
    "pin lưu trữ năng lượng": "Pin lưu trữ năng lượng cho phép bạn sử dụng điện từ mặt trời 24/7. Công nghệ lithium hiện đại tăng tuổi thọ pin lên 10-15 năm với hiệu suất 90-95%. Đây là giải pháp tối ưu cho năng lượng liên tục.",
    "biến tần inverter": "Biến tần inverter chuyển đổi điện một chiều (DC) từ pin thành điện xoay chiều (AC) để sử dụng các thiết bị điện gia dụng. Inverter chất lượng cao đảm bảo an toàn và hiệu suất tối đa cho hệ thống của bạn.",
    "hệ thống điện mặt trời": "Hệ thống điện mặt trời hoàn chỉnh bao gồm tấm pin, biến tần, pin lưu trữ và hệ thống điều khiển thông minh. Một hệ thống tốt có thể hoạt động hiệu quả trong 25-30 năm.",
    "năng lượng tái tạo": "Năng lượng tái tạo như mặt trời, gió giúp bảo vệ môi trường và giảm phụ thuộc vào năng lượng hóa thạch. Đây là xu hướng phát triển bền vững của tương lai.",
    "pin năng lượng mặt trời": "Pin năng lượng mặt trời hiệu suất cao, tuổi thọ lâu dài là lựa chọn tối ưu cho hệ thống năng lượng mặt trời. Công nghệ PERC hiện đại cung cấp hiệu suất lên tới 22%.",
    "inverter hybrid": "Inverter hybrid kết hợp chức năng chuyển đổi điện và quản lý pin, tối ưu hóa việc sử dụng năng lượng. Nó cho phép bạn tối đa hóa lợi ích từ năng lượng mặt trời.",
    "hệ thống lưu trữ năng lượng": "Hệ thống lưu trữ năng lượng hiện đại cho phép tiết kiệm điện và sử dụng năng lượng hiệu quả hơn. Với pin lưu trữ, bạn có thể sử dụng năng lượng mặt trời vào lúc đêm.",
    "tấm pin quang điện": "Tấm pin quang điện chuyển ánh sáng mặt trời thành điện năng một cách hiệu quả. Các tấm pin hiện đại có khả năng hoạt động tốt ngay cả khi trời u ám.",
    "năng lượng xanh": "Năng lượng xanh là năng lượng sạch, không gây ô nhiễm môi trường. Sử dụng năng lượng xanh là cách tuyệt vời để bảo vệ hành tinh của chúng ta."
}

class AdvancedFacebookPoster:
    def __init__(self):
        self.zernio_api_key = ZERNIO_API_KEY
        self.facebook_account_id = FACEBOOK_ACCOUNT_ID
        self.unsplash_key = UNSPLASH_ACCESS_KEY

    def get_random_hashtags(self, count=5):
        """Get random hashtags"""
        selected = random.sample(HASHTAGS, min(count, len(HASHTAGS)))
        return " ".join(selected)

    def fetch_image_from_unsplash(self, topic):
        """Fetch image from Unsplash"""
        if not self.unsplash_key:
            logger.warning("⚠️  UNSPLASH_ACCESS_KEY not configured. Skipping image fetch.")
            return None

        try:
            url = "https://api.unsplash.com/photos/random"
            # Translating topic to English roughly for better Unsplash results
            search_query = "solar panel" 
            if "pin" in topic or "lưu trữ" in topic: search_query = "battery storage"
            if "xanh" in topic or "tái tạo" in topic: search_query = "green energy"
            
            params = {
                'query': search_query,
                'orientation': 'landscape',
                'client_id': self.unsplash_key # Corrected Unsplash auth param
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get('urls', {}).get('regular')
                logger.info(f"✅ Lấy hình ảnh từ Unsplash thành công cho: {topic}")
                return image_url
            else:
                logger.warning(f"⚠️  Unsplash API returned {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi lấy hình ảnh: {str(e)}")
            return None

    def generate_post_content(self):
        """Generate random content from templates and topics"""
        topic = random.choice(TOPICS)
        template = random.choice(CONTENT_TEMPLATES)
        detail = CONTENT_DETAILS.get(topic, "Tìm hiểu thêm về công nghệ năng lượng mặt trời hiện đại.")
        hashtags = self.get_random_hashtags()

        content = template.format(topic=topic, detail=detail, hashtags=hashtags)
        return content, topic

    def post_to_facebook(self, content, image_url=None):
        """Post content to Facebook via Zernio API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.zernio_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'content': content,
                'publishNow': True,
                'platforms': [
                    {
                        'platform': 'facebook',
                        'accountId': self.facebook_account_id
                    }
                ]
            }

            # ==========================================
            # THE FIX: Correct Zernio API format for images
            # ==========================================
            if image_url:
                payload['mediaItems'] = [
                    {
                        'type': 'image',
                        'url': image_url
                    }
                ]
            # ==========================================

            logger.info("Đang gửi request tới Zernio...")
            response = requests.post(
                f'{ZERNIO_BASE_URL}/v1/posts',
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code in [200, 201]:
                logger.info(f"✅ Đăng bài thành công!")
                logger.info(f"Content preview: {content[:80]}...")
                if image_url:
                    logger.info(f"Image kèm theo: {image_url}")
                return True
            else:
                logger.error(f"❌ Lỗi khi đăng bài: Code {response.status_code}")
                logger.error(f"Response chi tiết: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Lỗi Network/Hệ thống: {str(e)}")
            return False

    def scheduled_post_with_image(self):
        """Job to generate and post content with image"""
        logger.info(f"\n🔄 Đang tạo bài đăng CÓ HÌNH ẢNH lúc {datetime.now().strftime('%H:%M:%S')}...")
        content, topic = self.generate_post_content()

        # Try to fetch image
        image_url = self.fetch_image_from_unsplash(topic)

        self.post_to_facebook(content, image_url)

    def scheduled_post(self):
        """Job to generate and post content"""
        logger.info(f"\n🔄 Đang tạo bài đăng TEXT lúc {datetime.now().strftime('%H:%M:%S')}...")
        content, topic = self.generate_post_content()
        self.post_to_facebook(content)

    def schedule_jobs(self):
        """Schedule posts at 7 AM and 8 PM"""
        schedule.every().day.at("07:00").do(self.scheduled_post_with_image)
        schedule.every().day.at("20:00").do(self.scheduled_post)

        logger.info("✅ Đã lên lịch đăng bài vào 7:00 (có hình ảnh) và 20:00 (chỉ text)")
        logger.info("🔄 Chương trình đang chạy... Nhấn Ctrl+C để dừng\n")
        
        # Uncomment this line if you want to test run immediately upon starting
        # self.scheduled_post_with_image() 

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🌞 Hoa Huy Green Energy - Advanced Auto Facebook Poster")
    logger.info("=" * 60)
    logger.info(f"⏰ Bắt đầu lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Verify configuration
    if ZERNIO_API_KEY == 'YOUR_ZERNIO_API_KEY' or not ZERNIO_API_KEY:
        logger.error("❌ Lỗi: Chưa cấu hình ZERNIO_API_KEY.")
        exit(1)

    if FACEBOOK_ACCOUNT_ID == 'YOUR_FACEBOOK_ACCOUNT_ID' or not FACEBOOK_ACCOUNT_ID:
        logger.error("❌ Lỗi: Chưa cấu hình FACEBOOK_ACCOUNT_ID.")
        exit(1)

    if not UNSPLASH_ACCESS_KEY:
        logger.warning("⚠️  CẢNH BÁO: UNSPLASH_ACCESS_KEY không được cấu hình")
        logger.warning("   Bài đăng sẽ không có hình ảnh. Để sửa, lấy key từ https://unsplash.com/developers")

    # Start poster
    poster = AdvancedFacebookPoster()
    poster.schedule_jobs()
