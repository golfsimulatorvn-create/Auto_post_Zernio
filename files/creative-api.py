#!/usr/bin/env python3
"""
creative-api.py
----------------
Pipeline tạo ảnh sản phẩm bằng Gemini API (model gemini-3.1-flash-image,
tên thân quen "Nano Banana").

Cách dùng:
    python3 creative-api.py [product] [platform] [prompt] [filename?]

Ví dụ:
    python3 creative-api.py HHXM6025A2 fb \
        "product-hero photo of HHXM6025A2 lithium battery pack, studio \
         lighting, premium lithium battery, clean tech aesthetic, \
         photorealistic, 4k"

    # Chỉ định rõ file ảnh gốc khi thư mục có nhiều ảnh:
    python3 creative-api.py HHXM6025A2 fb "..." z7983693533546_....jpg

Pipeline:
    1. Nhận 3-4 tham số: product, platform, prompt, [filename ảnh gốc]
    2. Load GEMINI_API_KEY từ .env
    3. Tìm ảnh gốc trong Products/[product]/ (bỏ qua bản vẽ kỹ thuật/
       video), mã hóa base64 — Gemini nhận ảnh input trực tiếp, không cần
       upload lên dịch vụ trung gian
    4. Gọi POST https://generativelanguage.googleapis.com/v1beta/interactions
       với model gemini-3.1-flash-image, input gồm text prompt + ảnh gốc
    5. Giải mã ảnh kết quả (base64) và lưu về
       output/images/[product]-[fb|ig]-[YYYY-MM-DD]-01.png

Yêu cầu:
    pip install requests python-dotenv
"""

import base64
import json
import mimetypes
import os
import sys
from datetime import date
from pathlib import Path

import requests

# Console Windows (cp1252) không encode được emoji/dấu tiếng Việt mặc định
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


# ---------------------------------------------------------------------------
# Cấu hình đường dẫn
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
PRODUCTS_DIR = PROJECT_ROOT / "Products"
OUTPUT_IMAGES_DIR = PROJECT_ROOT / "output" / "images"

GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image"

VALID_PLATFORMS = {"fb", "ig"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
EXCLUDE_KEYWORDS = ("drawing",)  # bản vẽ kỹ thuật, không dùng làm ảnh gốc


# ---------------------------------------------------------------------------
# Bước 2: Load API key từ .env
# ---------------------------------------------------------------------------
def load_api_key() -> str:
    if load_dotenv is not None and ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)
    else:
        # Fallback: tự đọc .env nếu chưa cài python-dotenv
        if ENV_PATH.exists():
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

    gemini_key = os.environ.get("GEMINI_API_KEY")

    if not gemini_key:
        raise RuntimeError(
            f"Thiếu biến môi trường GEMINI_API_KEY trong .env. "
            f"Vui lòng thêm vào file {ENV_PATH} (lấy key tại "
            f"https://aistudio.google.com/apikey)"
        )

    return gemini_key


# ---------------------------------------------------------------------------
# Bước 3: Tìm ảnh gốc trong Products/[product]/ và mã hóa base64
# ---------------------------------------------------------------------------
def resolve_source_image(product: str, filename: str | None = None) -> Path:
    product_dir = PRODUCTS_DIR / product

    if not product_dir.is_dir():
        raise FileNotFoundError(
            f"Không tìm thấy thư mục ảnh gốc: {product_dir}. "
            f"Hãy đặt ảnh sản phẩm tại Products/{product}/"
        )

    if filename:
        image_path = product_dir / filename
        if not image_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {image_path}")
        return image_path

    candidates = sorted(
        p for p in product_dir.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
        and not any(kw in p.name.lower() for kw in EXCLUDE_KEYWORDS)
    )

    if not candidates:
        raise FileNotFoundError(
            f"Không tìm thấy ảnh sản phẩm hợp lệ trong {product_dir} "
            f"(loại trừ bản vẽ kỹ thuật/video). Hãy thêm ảnh .jpg/.png."
        )

    if len(candidates) > 1:
        print(
            f"⚠️  Có {len(candidates)} ảnh trong {product_dir}, dùng ảnh đầu "
            f"tiên: {candidates[0].name}. Kiểm tra lại các ảnh cùng thư mục "
            f"có đúng là cùng một mã sản phẩm không — truyền tên file cụ "
            f"thể làm tham số thứ 4 nếu muốn chọn ảnh khác."
        )

    return candidates[0]


def load_source_image(product: str, filename: str | None = None) -> tuple[str, str]:
    image_path = resolve_source_image(product, filename)
    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    image_b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    print(f"📷 Dùng ảnh gốc: {image_path}")
    return image_b64, mime_type


# ---------------------------------------------------------------------------
# Bước 4: Gọi Gemini API để sinh ảnh
# ---------------------------------------------------------------------------
def generate_image(api_key: str, prompt: str, image_b64: str, image_mime_type: str) -> bytes:
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": GEMINI_IMAGE_MODEL,
        "input": [
            {"type": "text", "text": prompt},
            {"type": "image", "mime_type": image_mime_type, "data": image_b64},
        ],
    }

    print(f"🎨 Đang gọi Gemini API ({GEMINI_IMAGE_MODEL})...")
    response = requests.post(GEMINI_INTERACTIONS_URL, headers=headers, json=payload, timeout=180)
    response.raise_for_status()
    result = response.json()

    output_image = result.get("output_image")
    if not output_image or not output_image.get("data"):
        raise RuntimeError(f"Phản hồi API không chứa ảnh hợp lệ: {result}")

    print("✅ Ảnh đã sinh xong.")
    return base64.b64decode(output_image["data"])


# ---------------------------------------------------------------------------
# Bước 5: Lưu ảnh kết quả
# ---------------------------------------------------------------------------
def build_output_path(product: str, platform: str) -> Path:
    today = date.today().isoformat()
    filename = f"{product}-{platform}-{today}-01.png"
    return OUTPUT_IMAGES_DIR / filename


def save_image(content: bytes, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(content)
    print(f"💾 Đã lưu ảnh tại: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) not in (4, 5):
        print(__doc__)
        sys.exit(1)

    product, platform, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
    source_filename = sys.argv[4] if len(sys.argv) == 5 else None

    if platform not in VALID_PLATFORMS:
        print(f"❌ platform không hợp lệ: '{platform}'. Chỉ chấp nhận: fb, ig")
        sys.exit(1)

    try:
        api_key = load_api_key()
        image_b64, image_mime_type = load_source_image(product, source_filename)
        image_content = generate_image(api_key, prompt, image_b64, image_mime_type)
        output_path = build_output_path(product, platform)
        save_image(image_content, output_path)

        print("\n🎉 Hoàn tất!")
        print(f"   Product : {product}")
        print(f"   Platform: {platform}")
        print(f"   Output  : {output_path}")

    except (RuntimeError, FileNotFoundError, requests.RequestException) as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
