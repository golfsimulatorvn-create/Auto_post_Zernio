"""
SPV Solar - Fully Automated Content Workflow

This script orchestrates the entire content pipeline:
1. Searches for recent news about the energy sector in Vietnam.
2. Uses an AI (Gemini) to suggest relevant post topics based on the news.
3. Selects the best topic.
4. Uses an AI (Gemini) to write a full Facebook post for that topic.
5. Fetches a relevant image from Unsplash.
6. Posts the content and image to a Facebook Page via the Zernio API.
7. Schedules itself to run at predefined times.
"""
import logging
import os
import random
from dotenv import load_dotenv

# --- Local Imports ---
# Bộ module AI (content/) là tùy chọn và chưa có sẵn trong repo. Khi thiếu,
# script chuyển sang bộ sinh nội dung chuẩn SEO offline thay vì crash khi import.
try:
    from content.ai_writer import write_post_content
    from content.topic_suggester import suggest_topics_from_news
    from content.ai_image_generator import generate_image_for_post

    AI_PIPELINE_AVAILABLE = True
except ImportError:
    AI_PIPELINE_AVAILABLE = False

from content_generator import MIN_BODY_WORDS, generate_post

# --- Setup ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("auto_post_full_auto.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# --- Configuration ---
ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY")
FACEBOOK_ACCOUNT_ID = os.getenv("FACEBOOK_ACCOUNT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ZERNIO_BASE_URL = "https://zernio.com/api"


def search_recent_news(queries: list[str]) -> list[dict]:
    """
    Placeholder for a function that searches for recent news.
    In a real scenario, this would use a Google Search API or similar.
    """
    logger.info("Đang tìm kiếm tin tức với các từ khóa: %s", queries)
    # This is mock data. Replace with a real search API call.
    # For example, using the `google-search-results` library:
    # from serpapi import GoogleSearch
    # search = GoogleSearch({"q": queries[0], "api_key": "..."})
    # results = search.get_dict()
    # return [{"title": r["title"], "link": r["link"]} for r in results.get("organic_results", [])]
    return [
        {
            "title": "Giá điện có thể tăng trong quý 3, doanh nghiệp lo chi phí sản xuất",
            "link": "https://vnexpress.net/gia-dien-co-the-tang-trong-quy-3-4758392.html",
        },
        {
            "title": "Việt Nam đặt mục tiêu 50% tòa nhà công sở dùng điện mặt trời mái nhà",
            "link": "https://solarpower.vn/viet-nam-dat-muc-tieu-50-toa-nha-cong-so-dung-dien-mat-troi-mai-nha/",
        },
        {
            "title": "Xu hướng sử dụng pin lưu trữ ESS cho hộ gia đình tại các thành phố lớn",
            "link": "https://www.pv-magazine-vietnam.com/2026/07/10/xu-huong-su-dung-pin-luu-tru-ess-cho-ho-gia-dinh/",
        },
    ]


def post_to_facebook(content: str, image_url: str | None = None) -> bool:
    """Posts content to Facebook via the Zernio API."""
    import requests

    logger.info("Chuẩn bị đăng bài lên Facebook...")
    payload = {
        "content": content,
        "publishNow": True,
        "platforms": [{"platform": "facebook", "accountId": FACEBOOK_ACCOUNT_ID}],
    }
    if image_url:
        # Zernio nhận ảnh qua mảng mediaItems, không phải trường "image"
        payload["mediaItems"] = [{"type": "image", "url": image_url}]

    try:
        response = requests.post(
            f"{ZERNIO_BASE_URL}/v1/posts",
            headers={
                "Authorization": f"Bearer {ZERNIO_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        if response.status_code in [200, 201]:
            logger.info("✅ Đăng bài thành công! Nội dung: %s...", content[:100])
            return True
        logger.error("Lỗi đăng bài: %s — %s", response.status_code, response.text)
        return False
    except Exception as e:
        logger.error("Lỗi kết nối đến Zernio: %s", e)
        return False


def run_seo_fallback_post() -> None:
    """Đăng bài bằng bộ sinh nội dung chuẩn SEO khi pipeline AI chưa sẵn sàng."""
    logger.info("ℹ️  Chưa có module AI (content/). Dùng bộ sinh nội dung chuẩn SEO.")
    post = generate_post()
    report = post.seo_report
    logger.info(
        "📊 Chủ đề: %s | Số từ: %s | Mật độ từ khóa: %s%% | Điểm SEO: %s",
        post.topic_id, report["body_word_count"],
        report["keyword_density_pct"], report["score"],
    )
    if post.word_count < MIN_BODY_WORDS:
        logger.error("❌ Bài chỉ có %s từ, dưới ngưỡng %s. Hủy đăng.",
                     post.word_count, MIN_BODY_WORDS)
        return
    post_to_facebook(post.content)


def run_fully_automated_post():
    """The main function that orchestrates the entire automated workflow."""
    logger.info("🚀 Bắt đầu quy trình đăng bài hoàn toàn tự động...")

    if not AI_PIPELINE_AVAILABLE:
        run_seo_fallback_post()
        return

    # 1. Search for news
    news_items = search_recent_news(
        ["chính sách điện mặt trời việt nam", "giá điện EVN", "pin lưu trữ ESS"]
    )

    # 2. Suggest topics
    suggested_topics = suggest_topics_from_news(GEMINI_API_KEY, news_items)
    if not suggested_topics:
        logger.error("❌ AI không đề xuất được chủ đề nào. Dừng quy trình.")
        return

    # 3. Select the "hottest" topic
    try:
        # Sắp xếp các chủ đề theo 'hotness_score' giảm dần và chọn cái đầu tiên
        suggested_topics.sort(key=lambda x: x.get("hotness_score", 0), reverse=True)
        topic_to_write = suggested_topics[0]
    except (IndexError, TypeError):
        logger.warning("⚠️ Không thể xác định chủ đề hot nhất, chọn ngẫu nhiên.")
        topic_to_write = random.choice(suggested_topics) if suggested_topics else None

    if not topic_to_write:
        logger.error("❌ Không chọn được chủ đề nào để viết. Dừng lại.")
        return

    logger.info("💡 AI đã chọn chủ đề: '%s'", topic_to_write["topic_title"])

    # 4. Write content
    post_content = write_post_content(topic_to_write, GEMINI_API_KEY)
    if "fallback" in post_content:  # Simple check if fallback was used
        logger.warning("⚠️ AI không viết được bài, đã sử dụng nội dung thay thế.")

    # 5. Generate a unique image for the post
    image_url = generate_image_for_post(topic_to_write)

    # 6. Post to Facebook
    post_to_facebook(post_content, image_url)
    logger.info("✅ Quy trình hoàn tất.")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("SPV Solar - Fully Automated Content Workflow")
    logger.info("=" * 60)

    required = [ZERNIO_API_KEY, FACEBOOK_ACCOUNT_ID]
    if AI_PIPELINE_AVAILABLE:
        required.append(GEMINI_API_KEY)

    if not all(required):
        logger.critical("Lỗi: Vui lòng kiểm tra các biến môi trường ZERNIO_API_KEY, FACEBOOK_ACCOUNT_ID, và GEMINI_API_KEY trong file .env")
    else:
        # Khi chạy trên GitHub Actions, script sẽ được gọi trực tiếp
        # và chạy hàm này một lần rồi kết thúc.
        run_fully_automated_post()