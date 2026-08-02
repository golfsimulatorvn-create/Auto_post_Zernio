import requests
import schedule
import time
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

from content_generator import MIN_BODY_WORDS, generate_post, missing_brand_fields, load_brand

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

ARCHIVE_DIR = Path(__file__).parent / 'output' / 'content'

BRAND_NAME = load_brand().get('company_name') or 'SVPsolar'


class AdvancedFacebookPoster:
    def __init__(self):
        self.zernio_api_key = ZERNIO_API_KEY
        self.facebook_account_id = FACEBOOK_ACCOUNT_ID
        self.unsplash_key = UNSPLASH_ACCESS_KEY

    def fetch_image_from_unsplash(self, query):
        """Fetch image from Unsplash theo từ khóa ảnh của chủ đề"""
        if not self.unsplash_key:
            logger.warning("⚠️  UNSPLASH_ACCESS_KEY not configured. Skipping image fetch.")
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
                logger.info(f"✅ Lấy hình ảnh từ Unsplash thành công cho: {query}")
                return image_url

            logger.warning(f"⚠️  Unsplash API returned {response.status_code}: {response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi lấy hình ảnh: {str(e)}")
            return None

    def generate_post_content(self):
        """Sinh bài đăng chuẩn SEO (thân bài > 300 từ)"""
        post = generate_post()
        report = post.seo_report

        logger.info(f"📝 Chủ đề: {post.topic_id} | Từ khóa chính: {post.focus_keyword}")
        logger.info(f"📊 Số từ: {report['body_word_count']} | "
                    f"Mật độ từ khóa: {report['keyword_density_pct']}% | "
                    f"Điểm SEO: {report['score']}")

        for name, ok in report['checks'].items():
            if not ok:
                logger.warning(f"⚠️  Tiêu chí SEO chưa đạt: {name}")

        return post

    def archive_post(self, post, image_url=None):
        """Lưu lại bài đã đăng để tra cứu về sau"""
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
            logger.warning(f"⚠️  Không lưu được bản sao bài đăng: {e}")

    def _build_payload(self, content, image_url=None, image_alt=None):
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

        # Correct Zernio API format for images
        if image_url:
            item = {'type': 'image', 'url': image_url}
            if image_alt:
                item['altText'] = image_alt
            payload['mediaItems'] = [item]

        return payload

    def post_to_facebook(self, content, image_url=None, image_alt=None):
        """Post content to Facebook via Zernio API.

        Gửi kèm altText cho ảnh (tốt cho SEO và khả năng tiếp cận). Nếu Zernio
        từ chối vì không nhận trường này, gửi lại không kèm thay vì bỏ luôn bài.
        """
        headers = {
            'Authorization': f'Bearer {self.zernio_api_key}',
            'Content-Type': 'application/json'
        }
        can_retry = bool(image_url and image_alt)

        for with_alt in (True, False):
            payload = self._build_payload(
                content, image_url, image_alt if with_alt else None
            )
            try:
                logger.info("Đang gửi request tới Zernio...")
                response = requests.post(
                    f'{ZERNIO_BASE_URL}/v1/posts',
                    headers=headers,
                    json=payload,
                    timeout=15
                )
            except Exception as e:
                logger.error(f"❌ Lỗi Network/Hệ thống: {str(e)}")
                return False

            if response.status_code in [200, 201]:
                logger.info(f"✅ Đăng bài thành công!")
                logger.info(f"Content preview: {content[:80]}...")
                if image_url:
                    logger.info(f"Image kèm theo: {image_url}")
                    if with_alt:
                        logger.info(f"Alt text ảnh: {image_alt}")
                return True

            if with_alt and can_retry and response.status_code in (400, 422):
                logger.warning(f"⚠️  Zernio trả về {response.status_code} khi gửi kèm "
                               f"altText. Thử lại không kèm alt text...")
                continue

            logger.error(f"❌ Lỗi khi đăng bài: Code {response.status_code}")
            logger.error(f"Response chi tiết: {response.text}")
            return False

        return False

    def _run_post(self, with_image):
        kind = "CÓ HÌNH ẢNH" if with_image else "TEXT"
        logger.info(f"\n🔄 Đang tạo bài đăng {kind} lúc {datetime.now().strftime('%H:%M:%S')}...")
        post = self.generate_post_content()

        if post.word_count < MIN_BODY_WORDS:
            logger.error(f"❌ Bài chỉ có {post.word_count} từ, dưới ngưỡng "
                         f"{MIN_BODY_WORDS}. Bỏ qua lượt đăng này.")
            return

        image_url = self.fetch_image_from_unsplash(post.image_query) if with_image else None
        if self.post_to_facebook(post.content, image_url, post.image_alt):
            self.archive_post(post, image_url)

    def scheduled_post_with_image(self):
        """Job to generate and post content with image"""
        self._run_post(with_image=True)

    def scheduled_post(self):
        """Job to generate and post content"""
        self._run_post(with_image=False)

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
    logger.info(f"🌞 {BRAND_NAME} - Advanced Auto Facebook Poster")
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

    missing = missing_brand_fields()
    if missing:
        logger.error(f"❌ brand_config.json còn thiếu: {', '.join(missing)}.")
        logger.error("   Điền thông tin SVPsolar rồi chạy lại. "
                     "Kiểm tra bằng: python content_generator.py --check-brand")
        exit(1)

    if not UNSPLASH_ACCESS_KEY:
        logger.warning("⚠️  CẢNH BÁO: UNSPLASH_ACCESS_KEY không được cấu hình")
        logger.warning("   Bài đăng sẽ không có hình ảnh. Để sửa, lấy key từ https://unsplash.com/developers")

    # Start poster
    poster = AdvancedFacebookPoster()
    poster.schedule_jobs()
