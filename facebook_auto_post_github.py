import requests
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import logging

from content_generator import MIN_BODY_WORDS, daily_rotation_index, generate_post

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
ZERNIO_BASE_URL = 'https://zernio.com/api' # URL chuẩn của Zernio API 2026
FACEBOOK_ACCOUNT_ID = os.getenv('FACEBOOK_ACCOUNT_ID', 'YOUR_FACEBOOK_ACCOUNT_ID')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')  # Optional

ARCHIVE_DIR = Path(__file__).parent / 'output' / 'content'


class AdvancedFacebookPoster:
    def __init__(self):
        self.zernio_api_key = ZERNIO_API_KEY
        self.facebook_account_id = FACEBOOK_ACCOUNT_ID
        self.unsplash_key = UNSPLASH_ACCESS_KEY

    def fetch_image_from_unsplash(self, query):
        """Lấy hình ảnh từ Unsplash theo từ khóa ảnh của chủ đề"""
        if not self.unsplash_key:
            logger.warning("⚠️ UNSPLASH_ACCESS_KEY không tồn tại. Bỏ qua lấy ảnh.")
            return None

        try:
            params = {
                'query': query,
                'orientation': 'landscape',
                'client_id': self.unsplash_key
            }
            response = requests.get(
                "https://api.unsplash.com/photos/random",
                params=params,
                timeout=10,
            )
            if response.status_code == 200:
                image_url = response.json().get('urls', {}).get('regular')
                logger.info(f"✅ Lấy hình ảnh từ Unsplash thành công: {query}")
                return image_url

            logger.warning(f"⚠️ Unsplash API lỗi {response.status_code}: {response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi lấy hình ảnh: {str(e)}")
            return None

    def generate_post_content(self):
        """Sinh bài đăng chuẩn SEO (thân bài > 300 từ)

        Runner của GitHub Actions không giữ lại file lịch sử giữa các lần chạy,
        nên chủ đề được xoay vòng theo ngày + ca đăng để không bị lặp.
        """
        post = generate_post(rotation_index=daily_rotation_index())
        report = post.seo_report

        logger.info(f"📝 Chủ đề: {post.topic_id} | Từ khóa chính: {post.focus_keyword}")
        logger.info(f"📊 Số từ: {report['body_word_count']} | "
                    f"Mật độ từ khóa: {report['keyword_density_pct']}% | "
                    f"Điểm SEO: {report['score']}")

        for name, ok in report['checks'].items():
            if not ok:
                logger.warning(f"⚠️ Tiêu chí SEO chưa đạt: {name}")

        return post

    def archive_post(self, post, image_url=None):
        """Lưu lại bài đã đăng để tra cứu và tránh trùng lặp về sau"""
        try:
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime('%Y-%m-%d-%H%M')
            path = ARCHIVE_DIR / f"{stamp}-{post.topic_id}.md"
            report = post.seo_report
            path.write_text(
                f"# {post.topic_id} — {stamp}\n\n"
                f"- Từ khóa chính: {post.focus_keyword}\n"
                f"- Số từ thân bài: {report['body_word_count']}\n"
                f"- Mật độ từ khóa: {report['keyword_density_pct']}%\n"
                f"- Điểm SEO: {report['score']}\n"
                f"- Ảnh: {image_url or '(không có)'}\n"
                f"- Alt text ảnh (SEO): {post.image_alt}\n\n"
                f"---\n\n{post.content}\n",
                encoding='utf-8',
            )
            logger.info(f"💾 Đã lưu bài đăng: {path.name}")
        except OSError as e:
            logger.warning(f"⚠️ Không lưu được bản sao bài đăng: {e}")

    def post_to_facebook(self, content, image_url=None):
        """Gửi API đăng bài qua Zernio"""
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

            # Khắc phục lỗi không hiện ảnh: Dùng mảng mediaItems theo docs Zernio
            if image_url:
                payload['mediaItems'] = [
                    {
                        'type': 'image',
                        'url': image_url
                    }
                ]

            logger.info("Đang gửi request tới Zernio...")
            response = requests.post(
                f'{ZERNIO_BASE_URL}/v1/posts',
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code in [200, 201]:
                logger.info(f"✅ Đăng bài thành công!")
                if image_url:
                    logger.info(f"Có kèm ảnh: {image_url}")
                return True
            else:
                logger.error(f"❌ Lỗi khi đăng bài: Code {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Lỗi Network: {str(e)}")
            return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🌞 Hoa Huy Green Energy - GitHub Actions Auto Poster")
    logger.info("=" * 60)

    # Kiểm tra biến môi trường
    if ZERNIO_API_KEY == 'YOUR_ZERNIO_API_KEY' or not ZERNIO_API_KEY:
        logger.error("❌ Lỗi: Chưa cấu hình ZERNIO_API_KEY.")
        exit(1)
    if FACEBOOK_ACCOUNT_ID == 'YOUR_FACEBOOK_ACCOUNT_ID' or not FACEBOOK_ACCOUNT_ID:
        logger.error("❌ Lỗi: Chưa cấu hình FACEBOOK_ACCOUNT_ID.")
        exit(1)

    poster = AdvancedFacebookPoster()

    # Lấy giờ UTC hiện tại từ GitHub Actions Server
    current_utc_hour = datetime.now(timezone.utc).hour
    logger.info(f"⏰ Giờ chạy máy chủ (UTC): {current_utc_hour}h")

    post = poster.generate_post_content()

    # Chặn đăng nếu bài không đạt độ dài tối thiểu
    if post.word_count < MIN_BODY_WORDS:
        logger.error(f"❌ Bài chỉ có {post.word_count} từ, dưới ngưỡng "
                     f"{MIN_BODY_WORDS}. Hủy đăng.")
        exit(1)

    # GitHub Action chạy lúc 0:00 UTC (7h sáng VN) => Đăng kèm ảnh
    # GitHub Action chạy lúc 13:00 UTC (8h tối VN) => Đăng text không ảnh
    if current_utc_hour < 10:
        logger.info("🌅 Chạy ca SÁNG (kèm hình ảnh)...")
        image_url = poster.fetch_image_from_unsplash(post.image_query)
    else:
        logger.info("🌃 Chạy ca TỐI (chỉ có text)...")
        image_url = None

    if poster.post_to_facebook(post.content, image_url):
        poster.archive_post(post, image_url)

    logger.info("✅ Hoàn tất quy trình GitHub Actions!")
