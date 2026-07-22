import requests
import logging
import os
from dotenv import load_dotenv
import random

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
ZERNIO_BASE_URL = 'https://api.zernio.com'
FACEBOOK_ACCOUNT_ID = os.getenv('FACEBOOK_ACCOUNT_ID', 'YOUR_FACEBOOK_ACCOUNT_ID')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')

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
]

CONTENT_TEMPLATES = [
    "💡 Kiến thức về {topic}:\n\n{detail}\n\n{hashtags}",
    "🌞 {topic} - Giải pháp năng lượng xanh:\n\n{detail}\n\n{hashtags}",
    "⚡ {topic} là gì?\n\n{detail}\n\n{hashtags}",
    "🔋 Tìm hiểu về {topic}:\n\n{detail}\n\n{hashtags}",
    "💰 Tiết kiệm tiền với {topic}:\n\n{detail}\n\n{hashtags}",
]

CONTENT_DETAILS = {
    "năng lượng mặt trời": "Năng lượng mặt trời là nguồn năng lượng sạch, tái tạo được sử dụng rộng rãi. Nó giúp giảm chi phí điện năng lên đến 70-80% mỗi tháng.",
    "pin lưu trữ năng lượng": "Pin lưu trữ năng lượng cho phép bạn sử dụng điện từ mặt trời 24/7. Công nghệ lithium hiện đại tăng tuổi thọ pin lên 10-15 năm.",
    "biến tần inverter": "Biến tần inverter chuyển đổi điện một chiều (DC) từ pin thành điện xoay chiều (AC) để sử dụng các thiết bị điện gia dụng.",
    "hệ thống điện mặt trời": "Hệ thống điện mặt trời hoàn chỉnh bao gồm tấm pin, biến tần, pin lưu trữ và hệ thống điều khiển thông minh.",
    "năng lượng tái tạo": "Năng lượng tái tạo như mặt trời, gió giúp bảo vệ môi trường và giảm phụ thuộc vào năng lượng hóa thạch.",
    "pin năng lượng mặt trời": "Pin năng lượng mặt trời hiệu suất cao, tuổi thọ lâu dài là lựa chọn tối ưu cho hệ thống năng lượng mặt trời.",
    "inverter hybrid": "Inverter hybrid kết hợp chức năng chuyển đổi điện và quản lý pin, tối ưu hóa việc sử dụng năng lượng.",
    "hệ thống lưu trữ năng lượng": "Hệ thống lưu trữ năng lượng hiện đại cho phép tiết kiệm điện và sử dụng năng lượng hiệu quả hơn.",
    "tấm pin quang điện": "Tấm pin quang điện chuyển ánh sáng mặt trời thành điện năng một cách hiệu quả.",
    "năng lượng xanh": "Năng lượng xanh là năng lượng sạch, không gây ô nhiễm môi trường.",
}

class GitHubActionsPoster:
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
            params = {
                'query': topic,
                'orientation': 'portrait',
                'access_key': self.unsplash_key
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get('urls', {}).get('regular')
                logger.info(f"✅ Lấy hình ảnh từ Unsplash: {topic}")
                return image_url
            else:
                logger.warning(f"⚠️  Unsplash API returned {response.status_code}")
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

            if image_url:
                payload['image'] = image_url

            response = requests.post(
                f'{ZERNIO_BASE_URL}/v1/posts',
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.info(f"✅ Đăng bài thành công!")
                logger.info(f"Content preview: {content[:80]}...")
                if image_url:
                    logger.info(f"Image: {image_url[:50]}...")
                return True
            else:
                logger.error(f"❌ Lỗi khi đăng bài: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Lỗi: {str(e)}")
            return False

    def post_once_with_image(self):
        """Post content once with image"""
        logger.info("🔄 Đang tạo bài đăng...")
        content, topic = self.generate_post_content()
        image_url = self.fetch_image_from_unsplash(topic)
        self.post_to_facebook(content, image_url)

    def post_once_without_image(self):
        """Post content once without image"""
        logger.info("🔄 Đang tạo bài đăng...")
        content, topic = self.generate_post_content()
        self.post_to_facebook(content)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🌞 Hoa Huy Green Energy - GitHub Actions Auto Poster")
    logger.info("=" * 60)

    # Verify configuration
    if ZERNIO_API_KEY == 'YOUR_ZERNIO_API_KEY':
        logger.error("❌ Lỗi: Chưa cấu hình ZERNIO_API_KEY trong secrets")
        exit(1)

    if FACEBOOK_ACCOUNT_ID == 'YOUR_FACEBOOK_ACCOUNT_ID':
        logger.error("❌ Lỗi: Chưa cấu hình FACEBOOK_ACCOUNT_ID trong secrets")
        exit(1)

    # Determine which post type based on environment or random
    import sys
    from datetime import datetime

    # 7 AM (00:00 UTC) → với hình ảnh
    # 8 PM (13:00 UTC) → không hình ảnh
    current_hour = datetime.utcnow().hour

    poster = GitHubActionsPoster()

    if current_hour == 0:
        # 7 AM UTC+7 (00:00 UTC)
        logger.info("⏰ Lúc 7 AM - Đăng bài với hình ảnh")
        poster.post_once_with_image()
    else:
        # 8 PM UTC+7 (13:00 UTC) hoặc test run
        logger.info("⏰ Lúc 8 PM hoặc test - Đăng bài")
        poster.post_once_without_image()

    logger.info("=" * 60)
    logger.info("✅ Script hoàn tất")
    logger.info("=" * 60)
