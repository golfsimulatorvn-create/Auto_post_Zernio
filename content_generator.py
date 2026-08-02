"""
Bộ sinh nội dung chuẩn SEO cho SVPsolar — lĩnh vực điện mặt trời.

Nguyên tắc thiết kế:
- Mỗi bài đăng có phần thân >= 300 từ (không tính hashtag).
- Cấu trúc chuẩn SEO: hook chứa từ khóa chính trong ~125 ký tự đầu, mở bài,
  3 phần thân có tiêu đề phụ, khối uy tín (E-E-A-T), phần kết, CTA, hashtag.
- **Không bịa số liệu.** Phần thân chỉ chứa kiến thức kỹ thuật điện mặt trời
  mang tính phổ quát, không khẳng định gì riêng về công ty. Mọi thông tin
  thương hiệu (tên, hotline, website, số năm kinh nghiệm, chứng nhận...) đều
  lấy từ brand_config.json — trường nào bỏ trống thì phần nội dung tương ứng
  bị bỏ qua, không có giá trị mặc định tự chế.
- Các con số tiết kiệm/hoàn vốn/sản lượng phụ thuộc bức xạ khu vực, hướng mái
  và mức tiêu thụ, nên nội dung luôn dẫn về "cần khảo sát thực tế" thay vì đưa
  ra con số cụ thể.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MIN_BODY_WORDS = 300

BASE_DIR = Path(__file__).parent
HISTORY_FILE = BASE_DIR / "output" / "post_history.json"
BRAND_CONFIG_FILE = BASE_DIR / "brand_config.json"
HISTORY_SIZE = 40

BRAND_HASHTAGS = ["#SVPsolar", "#DienMatTroi", "#NangLuongMatTroi"]

# Trường bắt buộc phải có thì mới được phép đăng bài
REQUIRED_BRAND_FIELDS = ["company_name", "website", "hotline"]

# Nhãn hiển thị khi trường còn trống — cố tình để dễ thấy trong bản xem thử
FIELD_PLACEHOLDERS = {
    "company_name": "«TÊN CÔNG TY»",
    "website": "«WEBSITE»",
    "hotline": "«HOTLINE»",
}


# --- Nạp và kiểm tra cấu hình thương hiệu -----------------------------------
def load_brand(path: Path | None = None) -> dict:
    """Đọc brand_config.json. Thiếu file thì trả về cấu hình rỗng."""
    path = path or BRAND_CONFIG_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return {k: v for k, v in data.items() if not k.startswith("_")}


def missing_brand_fields(brand: dict | None = None) -> list[str]:
    """Danh sách trường bắt buộc còn trống."""
    brand = load_brand() if brand is None else brand
    return [f for f in REQUIRED_BRAND_FIELDS if not str(brand.get(f, "")).strip()]


def brand_is_ready(brand: dict | None = None) -> bool:
    return not missing_brand_fields(brand)


def _has(brand: dict, *fields: str) -> bool:
    """Kiểm tra các trường tùy chọn đã được điền hay chưa."""
    for f in fields:
        value = brand.get(f)
        if isinstance(value, list):
            if not value:
                return False
        elif not str(value or "").strip():
            return False
    return True


def _fill(text: str, brand: dict) -> str:
    """Thay các token thương hiệu bằng giá trị thật (hoặc nhãn còn trống)."""
    values = {
        "company": brand.get("company_name") or FIELD_PLACEHOLDERS["company_name"],
        "website": brand.get("website") or FIELD_PLACEHOLDERS["website"],
        "hotline": brand.get("hotline") or FIELD_PLACEHOLDERS["hotline"],
        "sales": brand.get("sales_contact") or brand.get("hotline")
                 or FIELD_PLACEHOLDERS["hotline"],
        "area": brand.get("service_area", ""),
        "years": str(brand.get("years_experience", "")),
        "projects": str(brand.get("projects_completed", "")),
        "warranty": str(brand.get("warranty_years", "")),
        "certs": ", ".join(brand.get("certifications", []) or []),
        "brands": ", ".join(brand.get("partner_brands", []) or []),
    }
    for token, value in values.items():
        text = text.replace("{" + token + "}", value)
    return text


def contact_line(brand: dict) -> str:
    parts = [brand.get("hotline") or FIELD_PLACEHOLDERS["hotline"]]
    if brand.get("email"):
        parts.append(brand["email"])
    parts.append(brand.get("website") or FIELD_PLACEHOLDERS["website"])
    return " | ".join(parts)


# --- Khối uy tín (E-E-A-T) --------------------------------------------------
# `requires` là các trường tùy chọn bắt buộc phải có thì khối mới được dùng.
# Khối đầu tiên chỉ cần company_name nên luôn khả dụng.
PROOF_TEMPLATES = [
    {
        "title": "Khảo sát trước, báo giá sau",
        "requires": [],
        "body": "Một hệ điện mặt trời chỉ hiệu quả khi được thiết kế theo đúng mái và "
                "đúng mức tiêu thụ của từng công trình. Vì vậy quy trình chuẩn của "
                "{company} là khảo sát hiện trạng trước — đo diện tích và hướng mái, "
                "đánh giá kết cấu chịu lực, ghi nhận bóng che theo giờ trong ngày và "
                "đối chiếu hóa đơn điện thực tế — rồi mới đưa ra phương án công suất và "
                "báo giá. Cách làm này tránh tình trạng lắp thừa công suất gây lãng phí "
                "hoặc lắp thiếu khiến hệ không đáp ứng đủ nhu cầu.",
    },
    {
        "title": "Kinh nghiệm triển khai thực tế",
        "requires": ["years_experience", "projects_completed"],
        "body": "{company} đã có {years} năm hoạt động trong lĩnh vực điện mặt trời, với "
                "{projects} công trình đã bàn giao. Kinh nghiệm tích lũy qua nhiều dạng "
                "mái và nhiều mức công suất khác nhau là thứ tạo ra khác biệt ở khâu xử "
                "lý chi tiết: cách đi dây, cách bố trí chuỗi tấm pin để hạn chế ảnh hưởng "
                "của bóng che, và cách xử lý chống thấm tại các điểm bắt giá đỡ — những "
                "việc quyết định độ bền của cả hệ thống về sau.",
    },
    {
        "title": "Phạm vi thi công và hỗ trợ tại chỗ",
        "requires": ["service_area"],
        "body": "{company} triển khai thi công tại {area}. Với điện mặt trời, khả năng hỗ "
                "trợ tại chỗ quan trọng hơn nhiều người nghĩ: hệ thống vận hành ngoài "
                "trời suốt 20 năm trở lên, nên khi cần kiểm tra inverter, siết lại đầu "
                "nối hay xử lý cảnh báo lỗi, đơn vị thi công ở gần sẽ phản hồi nhanh hơn "
                "hẳn so với nhà cung cấp ở xa hoặc bán hàng qua trung gian.",
    },
    {
        "title": "Thiết bị và tiêu chuẩn áp dụng",
        "requires": ["certifications"],
        "body": "Hệ thống do {company} lắp đặt áp dụng các tiêu chuẩn: {certs}. Với chủ "
                "đầu tư, tiêu chuẩn và chứng nhận là cách kiểm chứng chất lượng khách "
                "quan thay vì chỉ dựa vào lời giới thiệu — đặc biệt quan trọng với thiết "
                "bị phải phơi nắng mưa liên tục trong hàng chục năm và đấu nối trực tiếp "
                "vào hệ điện của công trình.",
    },
    {
        "title": "Thiết bị từ các hãng có bảo hành chính hãng",
        "requires": ["partner_brands"],
        "body": "{company} sử dụng thiết bị từ các thương hiệu: {brands}. Điều đáng quan "
                "tâm với tấm pin và inverter không chỉ là thông số lúc mới lắp, mà là "
                "chính sách bảo hành có thực hiện được hay không sau nhiều năm. Thiết bị "
                "có kênh bảo hành chính hãng rõ ràng giúp chủ đầu tư tránh rủi ro khi cần "
                "thay thế linh kiện ở giai đoạn giữa vòng đời hệ thống.",
    },
    {
        "title": "Bảo hành và đồng hành sau nghiệm thu",
        "requires": ["warranty_years"],
        "body": "Hệ thống do {company} lắp đặt được bảo hành {warranty} năm. Điện mặt "
                "trời là khoản đầu tư dài hạn, nên phần việc sau nghiệm thu — kiểm tra "
                "định kỳ, theo dõi sản lượng, xử lý khi có cảnh báo — mới là thứ quyết "
                "định hệ thống có đạt hiệu quả như kỳ vọng trong suốt vòng đời hay không.",
    },
]

CTA_TEMPLATES = [
    "Anh/chị muốn biết mái nhà mình lắp được công suất bao nhiêu? Liên hệ {company} để "
    "được khảo sát và tư vấn theo hiện trạng thực tế: {contact}.",
    "Cần báo giá cụ thể cho công trình của mình? Gửi hóa đơn tiền điện gần nhất và thông "
    "tin mái cho đội kỹ thuật {company}: {contact}. Phương án sẽ được tính theo mức tiêu "
    "thụ thật thay vì áp một cấu hình có sẵn.",
    "Anh/chị đang phân vân giữa các phương án đã nhận báo giá? Liên hệ {company} qua "
    "{contact} để được phân tích ưu nhược điểm từng cấu hình theo điều kiện công trình "
    "của mình.",
]


# --- Dữ liệu chủ đề ---------------------------------------------------------
# Phần thân cố tình KHÔNG chứa khẳng định riêng về công ty — chỉ là kiến thức
# kỹ thuật điện mặt trời phổ quát. Thông tin thương hiệu nằm ở khối uy tín và CTA.
TOPICS: list[dict] = [
    {
        "id": "dien-mat-troi-ap-mai",
        "focus_keyword": "điện mặt trời áp mái",
        "secondary_keywords": ["hóa đơn tiền điện", "công suất hệ thống",
                               "khảo sát mái", "tự tiêu thụ"],
        "image_query": "rooftop solar panels residential house",
        "image_alt": "Hệ thống điện mặt trời áp mái lắp đặt cho nhà ở dân dụng",
        "hooks": [
            "Điện mặt trời áp mái: lắp bao nhiêu kW là đủ cho gia đình mình?",
            "Điện mặt trời áp mái — những gì cần biết trước khi xuống tiền.",
            "Điện mặt trời áp mái cho nhà ở: bắt đầu từ hóa đơn tiền điện, không phải từ báo giá.",
        ],
        "intros": [
            "Câu hỏi đầu tiên của hầu hết gia đình khi tìm hiểu điện mặt trời áp mái là "
            "\"lắp bao nhiêu kW\". Nhưng đó lại là câu hỏi nên trả lời sau cùng. Công suất "
            "phù hợp phụ thuộc vào mức tiêu thụ thật, diện tích và hướng mái, cùng thói "
            "quen dùng điện trong ngày của gia đình. Dưới đây là những yếu tố cần nắm "
            "trước khi so sánh các báo giá.",
            "Điện mặt trời áp mái không còn xa lạ, nhưng chênh lệch giữa các báo giá vẫn "
            "khiến nhiều gia đình bối rối. Phần lớn khác biệt nằm ở những thứ không hiện "
            "trên tờ báo giá: chất lượng inverter, cách thiết kế chuỗi tấm pin và cách xử "
            "lý chống thấm khi thi công. Bài viết này giúp anh/chị biết cần hỏi gì.",
        ],
        "sections": [
            ("Hệ thống hoạt động thế nào",
             "Tấm pin đặt trên mái hấp thụ ánh sáng và tạo ra dòng điện một chiều. "
             "Inverter chuyển dòng điện đó thành điện xoay chiều để dùng cho các thiết "
             "bị trong nhà. Lượng điện tạo ra sẽ ưu tiên cấp cho tải đang hoạt động; "
             "phần dư có thể phát lên lưới hoặc nạp vào pin lưu trữ nếu hệ thống có "
             "trang bị. Hiểu đúng thứ tự này giúp anh/chị hình dung được vì sao thói "
             "quen dùng điện ban ngày lại ảnh hưởng lớn đến hiệu quả đầu tư."),
            ("Bắt đầu từ hóa đơn tiền điện",
             "Cách xác định công suất hợp lý là đi từ hóa đơn tiền điện của vài tháng "
             "gần nhất, kết hợp với biểu đồ sử dụng trong ngày. Gia đình có người ở nhà "
             "ban ngày, dùng điều hòa hoặc máy lạnh vào giờ nắng, sẽ tận dụng được "
             "nhiều điện tự sản xuất hơn so với gia đình chỉ sinh hoạt vào buổi tối. "
             "Cùng một công suất lắp đặt, hiệu quả thực tế của hai trường hợp này khác "
             "nhau đáng kể."),
            ("Mái nhà thế nào thì lắp được",
             "Ba yếu tố cần đánh giá: diện tích khả dụng, hướng và độ dốc mái, và kết "
             "cấu chịu lực. Ở Việt Nam, mái hướng nam thường nhận được bức xạ tốt nhất "
             "trong ngày, nhưng mái hướng đông hoặc tây vẫn khai thác được với sản lượng "
             "thấp hơn. Mái tôn, mái ngói hay mái bằng đều có giải pháp giá đỡ riêng — "
             "điều quan trọng là kết cấu phải chịu được tải trọng tăng thêm và các điểm "
             "bắt vít phải được xử lý chống thấm đúng cách."),
            ("Bóng che — yếu tố hay bị bỏ qua",
             "Một tán cây, bồn nước hay nhà bên cạnh cao hơn đều có thể che nắng một "
             "phần mái vào những giờ nhất định. Với tấm pin nối chuỗi, bóng che lên một "
             "tấm có thể kéo giảm sản lượng của cả chuỗi. Đây là lý do khảo sát cần ghi "
             "nhận bóng che theo giờ trong ngày, chứ không chỉ nhìn mái một lần. Khi "
             "không tránh được bóng che, có thể xử lý bằng cách chia chuỗi hợp lý hoặc "
             "dùng thiết bị tối ưu cho từng tấm."),
            ("Những chi phí cần tính đủ",
             "Ngoài tấm pin và inverter, chi phí trọn gói còn gồm khung giá đỡ, dây dẫn "
             "và tủ điện DC/AC, thiết bị bảo vệ, nhân công thi công và phần hoàn thiện "
             "chống thấm. Khi so sánh các báo giá, nên yêu cầu liệt kê rõ từng hạng mục "
             "thay vì chỉ nhìn tổng tiền — chênh lệch thường nằm ở chất lượng những "
             "hạng mục ít được nhắc tới này, và chính chúng ảnh hưởng đến độ bền của hệ "
             "thống về lâu dài."),
        ],
        "closings": [
            "Tóm lại, hiệu quả của điện mặt trời áp mái được quyết định từ khâu khảo sát "
            "mái và đọc hóa đơn tiền điện, chứ không phải từ việc chọn công suất hệ thống "
            "lớn nhất trong khả năng. Tỷ lệ tự tiêu thụ càng cao thì khoản đầu tư càng "
            "phát huy giá trị.",
            "Nói ngắn gọn, trước khi chốt điện mặt trời áp mái, hãy có trong tay ba thứ: "
            "hóa đơn tiền điện vài tháng gần nhất, kết quả khảo sát mái, và tỷ lệ tự tiêu "
            "thụ ước tính. Công suất hệ thống nên là kết luận rút ra từ ba dữ liệu đó.",
        ],
        "hashtags": ["#DienMatTroiApMai", "#DienNangLuongMatTroi", "#TietKiemDien", "#SolarVietNam"],
    },
    {
        "id": "dien-mat-troi-doanh-nghiep",
        "focus_keyword": "điện mặt trời cho doanh nghiệp",
        "secondary_keywords": ["nhà xưởng", "giờ cao điểm", "chi phí sản xuất", "mái tôn"],
        "image_query": "solar panels factory warehouse roof industrial",
        "image_alt": "Hệ thống điện mặt trời lắp trên mái nhà xưởng công nghiệp",
        "hooks": [
            "Điện mặt trời cho doanh nghiệp: mái nhà xưởng đang bỏ không là tài sản chưa khai thác.",
            "Điện mặt trời cho doanh nghiệp — vì sao nhà xưởng là nơi hiệu quả nhất?",
            "Điện mặt trời cho doanh nghiệp: cắt chi phí điện mà không đổi dây chuyền.",
        ],
        "intros": [
            "Với nhà xưởng và cơ sở sản xuất, điện là chi phí đầu vào cố định và thường "
            "chiếm tỷ trọng đáng kể trong giá thành. Điện mặt trời cho doanh nghiệp hấp "
            "dẫn ở chỗ tận dụng được thứ sẵn có mà không phải động đến dây chuyền: diện "
            "tích mái xưởng thường rất lớn và hầu như không dùng vào việc gì khác.",
            "Điện mặt trời cho doanh nghiệp có một lợi thế mà hệ dân dụng không có: giờ "
            "sản xuất trùng gần như hoàn toàn với giờ nắng. Điều đó có nghĩa phần lớn "
            "điện tạo ra được dùng ngay tại chỗ thay vì phải phát lên lưới — yếu tố quyết "
            "định hiệu quả của cả khoản đầu tư.",
        ],
        "sections": [
            ("Giờ sản xuất trùng giờ nắng",
             "Đây là điểm khác biệt căn bản so với hệ gia đình. Nhà xưởng vận hành ban "
             "ngày, đúng khung giờ hệ thống phát điện mạnh nhất, nên tỷ lệ tự tiêu thụ "
             "thường rất cao. Điện sản xuất ra được dùng ngay cho máy móc, hệ thống làm "
             "mát và chiếu sáng, thay vì phải phát lên lưới. Với cơ sở hoạt động cả tuần, "
             "mức độ trùng khớp này càng lớn."),
            ("Dịch tải khỏi khung giờ giá cao",
             "Nhiều cơ sở sản xuất áp dụng biểu giá điện theo khung giờ, trong đó khung "
             "cao điểm có đơn giá cao hơn hẳn. Vì hệ điện mặt trời phát mạnh vào ban "
             "ngày, một phần đáng kể sản lượng rơi vào khung giờ có giá điện cao. Mức "
             "tiết kiệm cụ thể phụ thuộc vào biểu giá đang áp dụng và biểu đồ phụ tải "
             "của từng nhà máy, nên cần lấy số liệu thực tế để tính thay vì áp một tỷ lệ "
             "chung."),
            ("Mái tôn nhà xưởng và bài toán kết cấu",
             "Mái tôn nhịp lớn của nhà xưởng rất phù hợp để lắp đặt, nhưng cần đánh giá "
             "kỹ khả năng chịu tải bổ sung của hệ kèo và xà gồ, cũng như tình trạng tôn "
             "hiện tại. Nếu mái đã cũ và dự kiến phải thay trong vài năm tới, nên cân "
             "nhắc thay tôn trước khi lắp — vì tháo dỡ và lắp lại toàn bộ hệ thống sau "
             "này tốn kém hơn nhiều so với xử lý ngay từ đầu."),
            ("Giảm nhiệt cho nhà xưởng",
             "Một lợi ích ít được nhắc tới: lớp tấm pin che phủ mái giúp giảm bức xạ "
             "trực tiếp lên tôn, nhờ đó nhiệt độ bên trong xưởng thường dễ chịu hơn. Với "
             "các cơ sở đang phải chạy quạt công nghiệp hoặc hệ thống làm mát liên tục, "
             "đây là hiệu quả cộng thêm bên cạnh phần điện tiết kiệm được, dù mức độ cụ "
             "thể còn tùy thuộc kết cấu mái và điều kiện thông gió."),
            ("Đấu nối và vận hành song song với lưới",
             "Hệ thống cho doanh nghiệp cần được thiết kế để vận hành an toàn song song "
             "với nguồn lưới hiện có, bao gồm thiết bị bảo vệ, chống dòng ngược nếu cần, "
             "và phương án ngắt khi lưới mất điện để đảm bảo an toàn cho người sửa chữa. "
             "Đây là phần kỹ thuật cần đơn vị thi công có kinh nghiệm, vì liên quan trực "
             "tiếp đến an toàn vận hành của cả cơ sở."),
        ],
        "closings": [
            "Tóm lại, điện mặt trời cho doanh nghiệp phát huy hiệu quả cao nhất ở nhà "
            "xưởng có mái tôn diện tích lớn và hoạt động ban ngày, nơi phần lớn sản lượng "
            "rơi vào giờ cao điểm và được dùng ngay tại chỗ, qua đó giảm trực tiếp chi phí "
            "sản xuất.",
            "Nói ngắn gọn, để đánh giá điện mặt trời cho doanh nghiệp, cần ba dữ liệu: "
            "biểu đồ phụ tải theo giờ cao điểm, hiện trạng kết cấu mái tôn, và chi phí "
            "điện đang chiếm bao nhiêu trong giá thành sản xuất.",
        ],
        "hashtags": ["#DienMatTroiCongNghiep", "#NhaXuong", "#TietKiemChiPhi", "#SolarB2B"],
    },
    {
        "id": "he-thong-hybrid",
        "focus_keyword": "hệ thống điện mặt trời hybrid",
        "secondary_keywords": ["pin lưu trữ", "mất điện", "inverter hybrid", "tự tiêu thụ"],
        "image_query": "hybrid solar inverter battery storage home",
        "image_alt": "Hệ thống điện mặt trời hybrid kết hợp pin lưu trữ và inverter hybrid",
        "hooks": [
            "Hệ thống điện mặt trời hybrid: vẫn có điện dùng khi lưới mất.",
            "Hệ thống điện mặt trời hybrid — giải bài toán điện chỉ có ban ngày.",
            "Hệ thống điện mặt trời hybrid có đáng đầu tư thêm so với hòa lưới thường?",
        ],
        "intros": [
            "Hệ hòa lưới thông thường có một hạn chế nhiều người chỉ nhận ra sau khi "
            "lắp: khi lưới mất điện, hệ thống cũng ngừng hoạt động, dù trời đang nắng. "
            "Đó là quy định an toàn bắt buộc. Hệ thống điện mặt trời hybrid ra đời để xử "
            "lý đúng vấn đề này, bằng cách kết hợp thêm pin lưu trữ.",
            "Điện mặt trời phát mạnh vào ban ngày, trong khi nhiều gia đình lại tiêu thụ "
            "nhiều nhất vào buổi tối. Hệ thống điện mặt trời hybrid lấp khoảng trống đó: "
            "tích phần điện dư ban ngày để dùng vào buổi tối, đồng thời giữ được nguồn "
            "khi lưới gặp sự cố.",
        ],
        "sections": [
            ("Khác biệt so với hệ hòa lưới thường",
             "Hệ hòa lưới thường chỉ có tấm pin và inverter, điện dư phát lên lưới và "
             "khi lưới mất thì hệ ngừng. Hệ hybrid bổ sung pin lưu trữ cùng inverter có "
             "khả năng quản lý cả ba nguồn: tấm pin, pin lưu trữ và lưới điện. Nhờ đó hệ "
             "có thể tự động chuyển đổi giữa các nguồn theo thứ tự ưu tiên đã cài đặt, "
             "thay vì phụ thuộc hoàn toàn vào lưới."),
            ("Duy trì nguồn khi mất điện",
             "Đây là giá trị rõ rệt nhất với khu vực hay mất điện. Khi lưới gặp sự cố, "
             "hệ hybrid chuyển sang cấp điện từ pin lưu trữ cho các tải đã được chỉ định "
             "từ trước. Cần lưu ý: thông thường không phải toàn bộ tải trong nhà đều "
             "được duy trì, mà chỉ nhóm tải ưu tiên được đấu riêng — vì vậy việc xác "
             "định thiết bị nào thật sự cần chạy khi mất điện nên được bàn ngay từ khâu "
             "thiết kế."),
            ("Tăng tỷ lệ tự tiêu thụ",
             "Ngoài chức năng dự phòng, pin lưu trữ giúp nâng tỷ lệ tự tiêu thụ — tức "
             "phần điện tự sản xuất được dùng cho chính nhu cầu của mình thay vì phát "
             "lên lưới. Với gia đình sinh hoạt chủ yếu vào buổi tối, đây là cách để "
             "khoản đầu tư phát huy giá trị thay vì chỉ tận dụng được vài giờ ban ngày. "
             "Mức cải thiện cụ thể phụ thuộc dung lượng pin và thói quen dùng điện."),
            ("Chọn dung lượng pin lưu trữ",
             "Nguyên tắc là đi từ lượng điện cần dùng trong khoảng thời gian muốn chủ "
             "động, chứ không phải chọn dung lượng lớn nhất có thể mua. Cần liệt kê các "
             "thiết bị ưu tiên, công suất và số giờ dự kiến chạy, từ đó suy ra dung "
             "lượng cần thiết. Chọn dư gây đội chi phí không cần thiết, chọn thiếu thì "
             "không đủ dùng đúng lúc cần nhất."),
            ("Chi phí tăng thêm và điều cần cân nhắc",
             "Hệ hybrid có chi phí cao hơn hệ hòa lưới thường do phải bổ sung pin lưu "
             "trữ và inverter loại phù hợp. Quyết định nên dựa trên tần suất mất điện "
             "thực tế ở khu vực và mức độ thiệt hại khi mất điện — với hộ gia đình thông "
             "thường thì đó là bất tiện, nhưng với cơ sở kinh doanh có kho lạnh hay thiết "
             "bị không được phép dừng thì bài toán hoàn toàn khác."),
        ],
        "closings": [
            "Tóm lại, hệ thống điện mặt trời hybrid đáng cân nhắc khi anh/chị cần duy trì "
            "nguồn lúc mất điện hoặc muốn nâng tỷ lệ tự tiêu thụ. Dung lượng pin lưu trữ "
            "nên tính từ nhóm tải ưu tiên, và inverter hybrid cần chọn đúng loại ngay từ "
            "đầu để tránh phải thay sau này.",
            "Nói ngắn gọn, giá trị của hệ thống điện mặt trời hybrid nằm ở hai chỗ: giữ "
            "được điện khi mất điện, và dùng được phần điện ban ngày vào buổi tối. Cả hai "
            "đều phụ thuộc vào việc chọn đúng dung lượng pin lưu trữ và inverter hybrid "
            "phù hợp với mức tự tiêu thụ mong muốn.",
        ],
        "hashtags": ["#DienMatTroiHybrid", "#PinLuuTru", "#BackupDien", "#SolarStorage"],
    },
    {
        "id": "chon-tam-pin",
        "focus_keyword": "tấm pin năng lượng mặt trời",
        "secondary_keywords": ["hiệu suất tấm pin", "bảo hành", "suy hao", "diện tích mái"],
        "image_query": "solar panel close up photovoltaic module",
        "image_alt": "Cận cảnh tấm pin năng lượng mặt trời lắp trên hệ thống điện mặt trời",
        "hooks": [
            "Tấm pin năng lượng mặt trời: nhìn vào đâu ngoài con số Wp?",
            "Tấm pin năng lượng mặt trời — hiệu suất cao có luôn đáng tiền hơn?",
            "Chọn tấm pin năng lượng mặt trời: ba thông số quan trọng hơn giá.",
        ],
        "intros": [
            "Khi so sánh báo giá, tấm pin năng lượng mặt trời thường được rút gọn thành "
            "một con số công suất. Nhưng hai tấm cùng công suất vẫn có thể khác nhau về "
            "diện tích chiếm chỗ, tốc độ suy hao theo năm và điều kiện bảo hành. Đây là "
            "những yếu tố ảnh hưởng đến sản lượng thu được trong suốt vòng đời hệ thống.",
            "Tấm pin là hạng mục chiếm tỷ trọng lớn trong chi phí và cũng là thứ sẽ nằm "
            "trên mái hàng chục năm. Hiểu vài thông số cơ bản của tấm pin năng lượng mặt "
            "trời sẽ giúp anh/chị đặt đúng câu hỏi khi so sánh giữa các nhà cung cấp, "
            "thay vì chỉ nhìn vào tổng giá.",
        ],
        "sections": [
            ("Công suất và hiệu suất khác nhau thế nào",
             "Công suất cho biết tấm pin tạo ra bao nhiêu điện trong điều kiện thử "
             "nghiệm chuẩn. Hiệu suất cho biết tấm chuyển đổi được bao nhiêu phần năng "
             "lượng ánh sáng chiếu tới. Hai tấm cùng công suất nhưng hiệu suất khác nhau "
             "sẽ chiếm diện tích khác nhau — tấm hiệu suất cao hơn cần ít diện tích hơn "
             "cho cùng một sản lượng. Điều này chỉ thực sự quan trọng khi diện tích mái "
             "bị giới hạn."),
            ("Khi nào nên trả thêm cho hiệu suất cao",
             "Nếu mái rộng và còn dư chỗ, tấm hiệu suất trung bình với giá tốt hơn "
             "thường là lựa chọn hợp lý — cứ lắp thêm tấm là bù được sản lượng. Ngược "
             "lại, khi diện tích mái hạn chế mà nhu cầu điện lớn, tấm hiệu suất cao giúp "
             "khai thác tối đa phần mái sẵn có. Nói cách khác, hiệu suất là câu chuyện "
             "của diện tích, không phải câu chuyện của chất lượng."),
            ("Suy hao theo thời gian",
             "Tấm pin giảm dần khả năng phát điện qua các năm, và nhà sản xuất thường "
             "công bố mức suy hao cam kết cùng công suất còn lại sau một số năm nhất "
             "định. Đây là thông số đáng đọc kỹ khi so sánh, vì nó quyết định sản lượng "
             "ở nửa sau vòng đời hệ thống. Nên yêu cầu nhà cung cấp đưa ra tài liệu kỹ "
             "thuật chính thức của hãng thay vì chỉ nghe giới thiệu miệng."),
            ("Hai loại bảo hành cần phân biệt",
             "Tấm pin thường có hai loại bảo hành riêng biệt: bảo hành sản phẩm cho lỗi "
             "vật lý và lỗi sản xuất, và bảo hành hiệu suất cam kết công suất còn lại "
             "theo thời gian. Hai mốc thời gian này khác nhau và không thay thế cho "
             "nhau. Khi so sánh, cần đối chiếu cả hai, đồng thời hỏi rõ đơn vị nào đứng "
             "ra thực hiện bảo hành và thủ tục ra sao."),
            ("Điều kiện vận hành thực tế tại Việt Nam",
             "Thông số công bố được đo trong điều kiện thử nghiệm chuẩn, còn thực tế "
             "tấm pin làm việc dưới nhiệt độ cao, độ ẩm lớn và bụi bám. Nhiệt độ cao làm "
             "giảm hiệu suất phát điện, nên thiết kế cần đảm bảo khoảng hở thông gió "
             "phía sau tấm. Đây là chi tiết thi công ảnh hưởng trực tiếp đến sản lượng "
             "nhưng thường không xuất hiện trên báo giá."),
        ],
        "closings": [
            "Tóm lại, chọn tấm pin năng lượng mặt trời nên cân giữa hiệu suất tấm pin, "
            "mức suy hao cam kết và điều kiện bảo hành — trong đó hiệu suất chủ yếu quan "
            "trọng khi diện tích mái bị giới hạn.",
            "Nói ngắn gọn, đừng chọn tấm pin năng lượng mặt trời chỉ theo giá trên mỗi Wp. "
            "Hãy đối chiếu thêm mức suy hao theo năm, cả hai loại bảo hành, và xem diện "
            "tích mái có buộc anh/chị phải ưu tiên hiệu suất tấm pin hay không.",
        ],
        "hashtags": ["#TamPinMatTroi", "#PinMatTroi", "#SolarPanel", "#CongNgheSolar"],
    },
    {
        "id": "chon-inverter",
        "focus_keyword": "inverter điện mặt trời",
        "secondary_keywords": ["biến tần", "hiệu suất chuyển đổi", "bảo hành", "giám sát"],
        "image_query": "solar inverter installation wall",
        "image_alt": "Inverter điện mặt trời lắp đặt trong hệ thống năng lượng mặt trời",
        "hooks": [
            "Inverter điện mặt trời: bộ phận hay hỏng nhất, nhưng hay bị chọn qua loa nhất.",
            "Inverter điện mặt trời — vì sao đây là nơi không nên tiết kiệm?",
            "Inverter điện mặt trời: chọn loại nào cho mái nhà mình?",
        ],
        "intros": [
            "Tấm pin thường được bảo hành hiệu suất tới vài chục năm, còn inverter điện "
            "mặt trời thì có vòng đời ngắn hơn đáng kể và là thiết bị làm việc liên tục "
            "mỗi ngày. Đây cũng là hạng mục quyết định phần lớn trải nghiệm vận hành: từ "
            "hiệu suất chuyển đổi cho tới khả năng theo dõi sản lượng.",
            "Nếu tấm pin là phần dễ thấy nhất của hệ thống thì inverter điện mặt trời là "
            "phần quyết định nhiều nhất tới sản lượng thực tế. Hiểu các loại inverter và "
            "điểm mạnh của từng loại sẽ giúp anh/chị chọn đúng theo đặc điểm mái nhà "
            "mình, thay vì chọn theo thương hiệu nghe quen.",
        ],
        "sections": [
            ("Nhiệm vụ của inverter trong hệ thống",
             "Tấm pin tạo ra dòng điện một chiều, còn thiết bị trong nhà dùng điện xoay "
             "chiều. Inverter đảm nhiệm việc chuyển đổi này, đồng thời điều chỉnh để lấy "
             "được nhiều công suất nhất có thể từ dàn pin trong từng điều kiện nắng. "
             "Ngoài ra inverter còn xử lý phần bảo vệ và ghi nhận dữ liệu vận hành, nên "
             "chất lượng của nó ảnh hưởng đến cả sản lượng lẫn độ an toàn."),
            ("Inverter chuỗi — lựa chọn phổ biến",
             "Loại này đấu nhiều tấm pin thành chuỗi và đưa về một thiết bị trung tâm. "
             "Ưu điểm là chi phí hợp lý, lắp đặt và bảo trì đơn giản vì chỉ có một thiết "
             "bị chính cần theo dõi. Hạn chế là khi một tấm trong chuỗi bị che nắng hoặc "
             "suy giảm, sản lượng của cả chuỗi bị kéo theo. Phù hợp với mái thông thoáng, "
             "ít bóng che và hướng mái đồng nhất."),
            ("Micro inverter và bộ tối ưu công suất",
             "Hai giải pháp này xử lý bài toán bóng che bằng cách quản lý công suất ở "
             "cấp từng tấm thay vì cả chuỗi. Nhờ đó một tấm bị che không kéo giảm các "
             "tấm còn lại, đồng thời cho phép theo dõi tình trạng từng tấm. Đổi lại, chi "
             "phí đầu tư cao hơn và số thiết bị trên mái nhiều hơn. Đáng cân nhắc với "
             "mái phức tạp, nhiều hướng hoặc không tránh được bóng che."),
            ("Inverter hybrid khi có pin lưu trữ",
             "Nếu có kế hoạch lắp pin lưu trữ, dù là ngay bây giờ hay vài năm tới, thì "
             "loại inverter cần được tính từ đầu. Inverter hybrid quản lý được cả tấm "
             "pin, pin lưu trữ và lưới điện. Chọn sai loại ngay từ đầu đồng nghĩa với "
             "việc phải thay thiết bị khi muốn bổ sung pin về sau — khoản phát sinh hoàn "
             "toàn tránh được nếu bàn kỹ ở khâu thiết kế."),
            ("Bảo hành và khả năng giám sát",
             "Vì inverter là thiết bị điện tử làm việc liên tục, chính sách bảo hành và "
             "khả năng hỗ trợ kỹ thuật tại chỗ quan trọng không kém thông số. Nên hỏi rõ "
             "thời hạn bảo hành, đơn vị thực hiện và thời gian xử lý khi có sự cố. Ngoài "
             "ra, hầu hết inverter hiện nay đều có ứng dụng theo dõi sản lượng — tính "
             "năng giúp phát hiện sớm khi hệ thống hoạt động bất thường."),
        ],
        "closings": [
            "Tóm lại, chọn inverter điện mặt trời nên căn cứ vào đặc điểm mái: mái thoáng "
            "và đồng hướng thì biến tần chuỗi là đủ, mái nhiều bóng che hoặc nhiều hướng "
            "thì nên cân nhắc giải pháp tối ưu theo từng tấm. Hiệu suất chuyển đổi, bảo "
            "hành và khả năng giám sát là ba thứ cần đối chiếu.",
            "Nói ngắn gọn, đừng chọn inverter điện mặt trời chỉ theo giá. Loại biến tần "
            "phải khớp với đặc điểm mái, phải tính trước khả năng lắp pin lưu trữ, và "
            "phải rõ ràng về bảo hành cùng khả năng giám sát từ xa.",
        ],
        "hashtags": ["#Inverter", "#BienTan", "#DienMatTroi", "#SolarInverter"],
    },
    {
        "id": "pin-luu-tru-solar",
        "focus_keyword": "pin lưu trữ điện mặt trời",
        "secondary_keywords": ["dung lượng kWh", "LiFePO4", "tự tiêu thụ", "tuổi thọ pin"],
        "image_query": "home battery energy storage system wall mounted",
        "image_alt": "Pin lưu trữ điện mặt trời lắp đặt cho hệ thống năng lượng mặt trời gia đình",
        "hooks": [
            "Pin lưu trữ điện mặt trời: có nên đầu tư thêm, hay để dành tiền lắp nhiều tấm hơn?",
            "Pin lưu trữ điện mặt trời — cần bao nhiêu kWh là đủ?",
            "Pin lưu trữ điện mặt trời: dùng điện ban ngày vào buổi tối.",
        ],
        "intros": [
            "Câu hỏi thường gặp sau khi lắp điện mặt trời là có nên bổ sung pin lưu trữ "
            "điện mặt trời hay không. Câu trả lời phụ thuộc vào hai thứ rất cụ thể: khu "
            "vực có hay mất điện không, và gia đình dùng điện nhiều vào ban ngày hay buổi "
            "tối. Cùng một khoản tiền, hai trường hợp này cho hiệu quả khác hẳn nhau.",
            "Pin lưu trữ điện mặt trời giải quyết độ lệch giữa lúc hệ thống phát điện và "
            "lúc gia đình cần dùng. Nhưng đây cũng là hạng mục làm tăng đáng kể chi phí "
            "đầu tư, nên cần được tính toán theo nhu cầu thật thay vì lắp cho đủ bộ.",
        ],
        "sections": [
            ("Vấn đề mà pin lưu trữ giải quyết",
             "Hệ điện mặt trời phát mạnh nhất vào giữa trưa, trong khi nhiều gia đình "
             "tiêu thụ nhiều nhất vào buổi tối khi cả nhà về. Không có pin, phần điện dư "
             "ban ngày sẽ phát lên lưới, còn buổi tối vẫn phải mua điện. Pin lưu trữ giữ "
             "lại phần dư đó để dùng vào khung giờ cần thiết, qua đó nâng tỷ lệ tự tiêu "
             "thụ của cả hệ thống."),
            ("Tính dung lượng theo nhu cầu thật",
             "Cách làm đúng là liệt kê các thiết bị cần chạy, công suất từng thiết bị và "
             "số giờ dự kiến sử dụng, từ đó suy ra lượng điện cần lưu trữ. Nên tính riêng "
             "cho hai kịch bản: dùng hằng ngày để dịch điện sang buổi tối, và dùng dự "
             "phòng khi mất điện. Hai kịch bản này cho ra con số khác nhau, và việc chọn "
             "kịch bản nào là quyết định của chủ nhà chứ không phải của người bán."),
            ("Vì sao LiFePO4 phổ biến cho hệ dân dụng",
             "Trong các loại pin lithium, LiFePO4 được ưa dùng cho hệ lưu trữ tại nhà "
             "nhờ độ ổn định nhiệt tốt và tuổi thọ chu kỳ cao. Với thiết bị đặt trong "
             "hoặc sát khu vực sinh hoạt, độ an toàn là tiêu chí được đặt lên trước hiệu "
             "năng. Đây cũng là lý do loại pin này dần thay thế các giải pháp ắc quy "
             "truyền thống trong hệ điện mặt trời gia đình."),
            ("Tuổi thọ tính theo chu kỳ, không theo năm",
             "Pin lưu trữ thường được công bố tuổi thọ theo số chu kỳ sạc/xả kèm mức "
             "dung lượng còn lại, chứ không đơn thuần theo số năm. Điều đó có nghĩa cách "
             "sử dụng ảnh hưởng trực tiếp đến độ bền: pin xả cạn hằng ngày sẽ hao mòn "
             "nhanh hơn pin chỉ dùng ở mức vừa phải. Khi so sánh sản phẩm, nên đối chiếu "
             "cả số chu kỳ và điều kiện kèm theo trong cam kết bảo hành."),
            ("Tương thích với hệ thống hiện có",
             "Nếu bổ sung pin cho hệ đã lắp sẵn, cần kiểm tra inverter hiện tại có hỗ trợ "
             "kết nối pin hay không. Nhiều hệ hòa lưới thông thường không có sẵn khả năng "
             "này và sẽ phải thay inverter — khoản phát sinh không nhỏ. Đây là lý do nên "
             "bàn về kế hoạch lắp pin ngay từ khi thiết kế hệ thống ban đầu, kể cả khi "
             "chưa lắp ngay."),
        ],
        "closings": [
            "Tóm lại, pin lưu trữ điện mặt trời đáng đầu tư khi anh/chị cần dự phòng lúc "
            "mất điện hoặc muốn nâng tỷ lệ tự tiêu thụ. Dung lượng kWh nên tính từ nhóm "
            "thiết bị ưu tiên, và LiFePO4 là lựa chọn phổ biến cho hệ dân dụng nhờ độ an "
            "toàn cùng tuổi thọ pin tốt.",
            "Nói ngắn gọn, trước khi chốt pin lưu trữ điện mặt trời, hãy trả lời hai câu: "
            "cần chạy những thiết bị nào và trong bao lâu. Từ đó mới ra được dung lượng "
            "kWh hợp lý, thay vì chọn theo gói có sẵn.",
        ],
        "hashtags": ["#PinLuuTru", "#LuuTruDienMatTroi", "#LiFePO4", "#SolarBattery"],
    },
    {
        "id": "bai-toan-hoan-von",
        "focus_keyword": "chi phí lắp điện mặt trời",
        "secondary_keywords": ["hoàn vốn", "hóa đơn tiền điện", "tự tiêu thụ", "báo giá"],
        "image_query": "solar panels installation house calculation",
        "image_alt": "Tính toán chi phí đầu tư và hiệu quả hệ thống điện mặt trời",
        "hooks": [
            "Chi phí lắp điện mặt trời: vì sao các báo giá chênh nhau nhiều đến vậy?",
            "Chi phí lắp điện mặt trời và bài toán hoàn vốn — tính thế nào cho đúng?",
            "Chi phí lắp điện mặt trời: đọc báo giá theo hạng mục, đừng nhìn tổng tiền.",
        ],
        "intros": [
            "Khi nhận vài báo giá cho cùng một công suất, nhiều chủ nhà bối rối vì mức "
            "chênh lệch khá lớn. Chi phí lắp điện mặt trời không chỉ gồm tấm pin và "
            "inverter, mà còn nhiều hạng mục ít được nhắc tới nhưng ảnh hưởng trực tiếp "
            "đến độ bền hệ thống. Bài viết này giúp anh/chị đọc báo giá có cơ sở hơn.",
            "Thời gian hoàn vốn của điện mặt trời phụ thuộc vào quá nhiều biến số để có "
            "một con số chung cho mọi công trình. Thay vì tin vào một mốc thời gian được "
            "đưa ra sẵn, anh/chị nên nắm cách tính để tự kiểm chứng dựa trên chi phí lắp "
            "điện mặt trời và mức tiêu thụ thật của gia đình mình.",
        ],
        "sections": [
            ("Các hạng mục tạo nên báo giá",
             "Một báo giá đầy đủ gồm: tấm pin, inverter, khung giá đỡ, dây dẫn DC và AC, "
             "tủ điện cùng thiết bị bảo vệ, hệ thống tiếp địa và chống sét, nhân công thi "
             "công, và phần hoàn thiện chống thấm. Khi hai báo giá chênh nhau, nguyên "
             "nhân thường nằm ở nhóm hạng mục phía sau chứ không phải ở tấm pin. Nên yêu "
             "cầu bóc tách chi tiết để so sánh đúng thứ cần so sánh."),
            ("Cách tính hoàn vốn cho đúng",
             "Công thức cơ bản là lấy tổng chi phí đầu tư chia cho khoản tiết kiệm mỗi "
             "năm. Phần khó nằm ở vế thứ hai: khoản tiết kiệm phụ thuộc vào sản lượng "
             "thực tế của hệ, tỷ lệ tự tiêu thụ và đơn giá điện đang áp dụng. Vì cả ba "
             "yếu tố này khác nhau theo từng công trình, con số hoàn vốn chỉ đáng tin khi "
             "được tính từ dữ liệu thật của chính gia đình anh/chị."),
            ("Tỷ lệ tự tiêu thụ ảnh hưởng lớn nhất",
             "Cùng một hệ thống, gia đình dùng nhiều điện ban ngày sẽ có hiệu quả kinh tế "
             "tốt hơn hẳn gia đình chỉ sinh hoạt buổi tối, vì điện tự sản xuất được dùng "
             "trực tiếp thay vì phát lên lưới. Đây là lý do việc khảo sát thói quen dùng "
             "điện quan trọng ngang với khảo sát mái, và cũng là lý do không nên áp một "
             "tỷ lệ hoàn vốn chung cho mọi khách hàng."),
            ("Biểu giá điện bậc thang",
             "Với hộ gia đình áp dụng biểu giá bậc thang, phần điện tiêu thụ ở bậc cao có "
             "đơn giá cao hơn nhiều so với bậc thấp. Điện mặt trời cắt vào phần tiêu thụ "
             "ở bậc trên cùng trước, nên gia đình đang dùng nhiều điện thường thấy hiệu "
             "quả rõ rệt hơn. Đây cũng là lý do hóa đơn tiền điện hiện tại là dữ liệu đầu "
             "vào quan trọng khi tính toán phương án."),
            ("Chi phí trong vòng đời hệ thống",
             "Ngoài đầu tư ban đầu, nên tính thêm chi phí vận hành: vệ sinh tấm pin định "
             "kỳ, kiểm tra hệ thống, và khả năng phải thay inverter ở giữa vòng đời do "
             "thiết bị này có tuổi thọ ngắn hơn tấm pin. Đưa các khoản đó vào ngay từ đầu "
             "sẽ cho bức tranh sát thực tế hơn, thay vì chỉ so sánh giá lắp đặt ban đầu "
             "giữa các nhà cung cấp."),
        ],
        "closings": [
            "Tóm lại, để đánh giá chi phí lắp điện mặt trời, hãy yêu cầu báo giá bóc tách "
            "theo hạng mục và tự tính hoàn vốn dựa trên hóa đơn tiền điện cùng tỷ lệ tự "
            "tiêu thụ của chính gia đình mình, thay vì dựa vào con số chung.",
            "Nói ngắn gọn, chi phí lắp điện mặt trời chỉ có ý nghĩa khi đặt cạnh sản lượng "
            "và mức tự tiêu thụ thực tế. Một báo giá rẻ hơn nhưng cắt bớt hạng mục bảo vệ "
            "và chống thấm thường đắt hơn về lâu dài — hãy so sánh trên hóa đơn tiền điện "
            "tiết kiệm được, không chỉ trên tổng tiền đầu tư.",
        ],
        "hashtags": ["#ChiPhiDienMatTroi", "#HoanVon", "#BaoGiaSolar", "#DauTuSolar"],
    },
    {
        "id": "khao-sat-thiet-ke",
        "focus_keyword": "khảo sát thiết kế hệ thống điện mặt trời",
        "secondary_keywords": ["hướng mái", "bóng che", "kết cấu mái", "tải tiêu thụ"],
        "image_query": "engineer surveying roof solar installation",
        "image_alt": "Kỹ thuật viên khảo sát mái trước khi thiết kế hệ thống điện mặt trời",
        "hooks": [
            "Khảo sát thiết kế hệ thống điện mặt trời: bước quyết định nhưng hay bị làm qua loa.",
            "Khảo sát thiết kế hệ thống điện mặt trời — báo giá qua điện thoại có đáng tin?",
            "Khảo sát thiết kế hệ thống điện mặt trời: cần đo và ghi nhận những gì?",
        ],
        "intros": [
            "Một báo giá đưa ra chỉ sau vài câu hỏi qua điện thoại thường là dấu hiệu "
            "đáng lưu ý. Khảo sát thiết kế hệ thống điện mặt trời là bước quyết định "
            "công suất, cách bố trí và cả độ bền của công trình. Bỏ qua bước này đồng "
            "nghĩa với việc chấp nhận rủi ro lắp sai ngay từ đầu.",
            "Cùng một mái nhà, hai đơn vị khảo sát kỹ và khảo sát qua loa sẽ cho ra hai "
            "phương án rất khác nhau. Bài viết này liệt kê những gì một buổi khảo sát "
            "thiết kế hệ thống điện mặt trời cần ghi nhận, để anh/chị biết mình đang được "
            "tư vấn nghiêm túc hay chỉ được chào bán một gói có sẵn.",
        ],
        "sections": [
            ("Đo đạc mái và xác định diện tích khả dụng",
             "Không phải toàn bộ diện tích mái đều lắp được. Cần trừ đi khu vực có vật "
             "cản như bồn nước, ống thông gió, cửa mái, cùng khoảng cách an toàn ở rìa "
             "mái và lối đi phục vụ bảo trì sau này. Diện tích khả dụng thực tế thường "
             "nhỏ hơn diện tích mái khá nhiều, và đây là con số quyết định công suất tối "
             "đa có thể lắp."),
            ("Hướng mái và độ dốc",
             "Hướng và độ dốc quyết định lượng bức xạ mà dàn pin nhận được trong ngày. "
             "Ở Việt Nam, mái hướng nam thường cho sản lượng tốt nhất, nhưng mái hướng "
             "đông hoặc tây vẫn khai thác được. Với mái nhiều hướng khác nhau, cách chia "
             "chuỗi và lựa chọn thiết bị cần được tính riêng cho từng mặt mái, thay vì áp "
             "chung một cấu hình cho toàn bộ hệ thống."),
            ("Ghi nhận bóng che theo giờ",
             "Bóng che là yếu tố dễ bị bỏ qua nhất vì nó thay đổi theo giờ và theo mùa. "
             "Một tán cây không che gì lúc 10 giờ sáng có thể phủ nửa mái vào buổi chiều. "
             "Khảo sát nghiêm túc cần ghi nhận nguồn bóng che và khoảng thời gian ảnh "
             "hưởng, từ đó quyết định cách chia chuỗi hoặc có cần thiết bị tối ưu theo "
             "từng tấm hay không."),
            ("Đánh giá kết cấu chịu lực",
             "Hệ thống làm tăng tải trọng thường xuyên lên mái, đồng thời chịu thêm tải "
             "gió. Cần đánh giá tình trạng kèo, xà gồ và vật liệu lợp hiện tại. Nếu mái "
             "đã xuống cấp hoặc dự kiến thay trong vài năm tới, nên xử lý trước khi lắp "
             "— vì việc tháo dỡ và lắp lại toàn bộ hệ thống về sau tốn kém hơn nhiều so "
             "với làm gọn ngay từ đầu."),
            ("Phân tích tải tiêu thụ",
             "Song song với khảo sát mái là phân tích tải tiêu thụ: hóa đơn điện các "
             "tháng gần nhất, các thiết bị công suất lớn và khung giờ hoạt động. Dữ liệu "
             "này quyết định công suất hợp lý và tỷ lệ tự tiêu thụ dự kiến. Thiếu bước "
             "này, phương án đưa ra chỉ dựa trên diện tích mái, dễ dẫn đến lắp thừa so "
             "với nhu cầu thật của gia đình."),
        ],
        "closings": [
            "Tóm lại, một buổi khảo sát thiết kế hệ thống điện mặt trời nghiêm túc phải "
            "ghi nhận đủ bốn thứ: diện tích khả dụng, hướng mái và độ dốc, bóng che theo "
            "giờ, và kết cấu mái — cộng với phân tích tải tiêu thụ từ hóa đơn thật.",
            "Nói ngắn gọn, nếu một đơn vị báo giá mà chưa từng lên mái đo đạc, chưa hỏi "
            "về bóng che và chưa xem hóa đơn điện, thì đó chưa phải là khảo sát thiết kế "
            "hệ thống điện mặt trời — mới chỉ là chào bán một gói thiết bị.",
        ],
        "hashtags": ["#KhaoSatSolar", "#ThietKeHeThong", "#DienMatTroi", "#TuVanSolar"],
    },
    {
        "id": "thi-cong-an-toan",
        "focus_keyword": "thi công lắp đặt điện mặt trời",
        "secondary_keywords": ["chống thấm mái", "chống sét", "an toàn điện", "khung giá đỡ"],
        "image_query": "solar panel installation workers roof",
        "image_alt": "Thi công lắp đặt hệ thống điện mặt trời trên mái công trình",
        "hooks": [
            "Thi công lắp đặt điện mặt trời: phần quyết định hệ bền 20 năm hay dột sau một mùa mưa.",
            "Thi công lắp đặt điện mặt trời — những chi tiết không có trên báo giá.",
            "Thi công lắp đặt điện mặt trời: hỏi gì để biết đơn vị làm có kỹ không?",
        ],
        "intros": [
            "Thiết bị tốt nhưng thi công ẩu vẫn cho ra một hệ thống có vấn đề. Với điện "
            "mặt trời, phần lớn sự cố phát sinh sau vài năm đều bắt nguồn từ khâu thi "
            "công lắp đặt điện mặt trời: điểm bắt vít không được xử lý chống thấm, đầu "
            "nối không siết đúng, hoặc hệ tiếp địa làm cho có.",
            "Khác với nhiều hạng mục xây dựng, chất lượng thi công lắp đặt điện mặt trời "
            "không thể hiện ngay lúc nghiệm thu. Hệ vẫn chạy, sản lượng vẫn lên, và vấn "
            "đề chỉ lộ ra sau vài mùa mưa nắng. Đây là lý do nên biết trước những chi "
            "tiết cần kiểm tra.",
        ],
        "sections": [
            ("Chống thấm tại điểm bắt giá đỡ",
             "Mỗi điểm cố định khung giá đỡ vào mái là một điểm có nguy cơ thấm nước. "
             "Với mái tôn, việc chọn đúng loại vít kèm gioăng và xử lý keo chuyên dụng là "
             "bắt buộc. Với mái ngói hoặc mái bê tông, cách xử lý khác nhau và cần đúng "
             "quy trình. Đây là hạng mục hầu như không xuất hiện trong báo giá nhưng lại "
             "là nguyên nhân khiếu nại phổ biến nhất sau khi lắp."),
            ("Khung giá đỡ và tải gió",
             "Khung giá đỡ phải chịu được cả trọng lượng dàn pin lẫn tải gió, vốn có thể "
             "rất lớn ở khu vực trống trải hoặc nhà cao tầng. Vật liệu cần chống ăn mòn "
             "để trụ được ngoài trời hàng chục năm. Khoảng hở giữa tấm pin và mặt mái "
             "cũng cần đủ để thông gió, vì nhiệt độ cao làm giảm hiệu suất phát điện của "
             "tấm pin."),
            ("Đi dây và bảo vệ mạch điện",
             "Dây dẫn phần một chiều phải dùng loại chuyên dụng chịu được tia cực tím và "
             "nhiệt độ ngoài trời, được cố định gọn gàng thay vì thả tự do trên mái. Hệ "
             "thống cần có thiết bị đóng cắt và bảo vệ ở cả phía một chiều lẫn xoay "
             "chiều, đặt ở vị trí thao tác được khi cần cô lập hệ thống để sửa chữa hoặc "
             "xử lý sự cố."),
            ("Tiếp địa và chống sét",
             "Dàn pin đặt ở vị trí cao và trống trải nên hệ tiếp địa cùng thiết bị chống "
             "sét lan truyền là hạng mục bắt buộc, không phải tùy chọn. Đây cũng là chỗ "
             "dễ bị cắt giảm để hạ giá báo giá. Khi so sánh các phương án, nên hỏi rõ "
             "hạng mục này được làm thế nào, vì nó bảo vệ cả hệ thống lẫn thiết bị điện "
             "trong nhà."),
            ("Nghiệm thu và bàn giao hồ sơ",
             "Kết thúc thi công, nên yêu cầu bàn giao hồ sơ gồm sơ đồ đấu nối, danh mục "
             "thiết bị kèm số seri, phiếu bảo hành của từng hạng mục và hướng dẫn vận "
             "hành cơ bản. Bộ hồ sơ này rất cần khi bảo hành hoặc khi cần đơn vị khác "
             "kiểm tra hệ thống về sau. Thiếu nó, việc xử lý sự cố sẽ mất nhiều thời gian "
             "hơn đáng kể."),
        ],
        "closings": [
            "Tóm lại, chất lượng thi công lắp đặt điện mặt trời nằm ở những chi tiết ít "
            "được nhắc: xử lý chống thấm mái tại điểm bắt giá đỡ, khung giá đỡ chịu được "
            "tải gió, hệ chống sét và tiếp địa đầy đủ, cùng an toàn điện ở cả hai phía "
            "một chiều và xoay chiều.",
            "Nói ngắn gọn, khi chọn đơn vị thi công lắp đặt điện mặt trời, hãy hỏi cụ thể "
            "về cách xử lý chống thấm mái, vật liệu khung giá đỡ và phương án chống sét. "
            "Câu trả lời cho ba câu hỏi đó nói lên nhiều điều hơn cả bảng báo giá.",
        ],
        "hashtags": ["#ThiCongSolar", "#LapDatDienMatTroi", "#ChongTham", "#AnToanDien"],
    },
    {
        "id": "bao-tri-van-hanh",
        "focus_keyword": "bảo trì hệ thống điện mặt trời",
        "secondary_keywords": ["vệ sinh tấm pin", "kiểm tra định kỳ", "sản lượng", "inverter"],
        "image_query": "cleaning solar panels maintenance",
        "image_alt": "Vệ sinh và bảo trì định kỳ hệ thống điện mặt trời trên mái",
        "hooks": [
            "Bảo trì hệ thống điện mặt trời: lắp xong không có nghĩa là xong.",
            "Bảo trì hệ thống điện mặt trời — vì sao sản lượng giảm dần mà không ai để ý?",
            "Bảo trì hệ thống điện mặt trời: làm gì và bao lâu một lần?",
        ],
        "intros": [
            "Điện mặt trời thường được giới thiệu là gần như không cần bảo trì. Điều đó "
            "đúng một phần: hệ không có bộ phận chuyển động nên ít hỏng vặt. Nhưng bảo "
            "trì hệ thống điện mặt trời vẫn cần thiết, vì sản lượng có thể giảm dần theo "
            "cách rất khó nhận ra nếu không theo dõi.",
            "Vấn đề lớn nhất của một hệ điện mặt trời không được theo dõi là nó vẫn chạy "
            "khi đã có sự cố. Một chuỗi tấm pin ngừng hoạt động hay tấm pin bám bụi dày "
            "đều không gây ra dấu hiệu gì rõ ràng — chỉ có sản lượng âm thầm giảm. Đây là "
            "lý do bảo trì hệ thống điện mặt trời đáng được lên lịch cụ thể.",
        ],
        "sections": [
            ("Vệ sinh tấm pin",
             "Bụi, lá cây và phân chim bám trên bề mặt làm giảm lượng ánh sáng đến được "
             "tế bào quang điện. Ở khu vực nhiều bụi hoặc gần công trường, mức ảnh hưởng "
             "rõ rệt hơn. Mưa giúp rửa trôi một phần nhưng không thay thế được việc vệ "
             "sinh định kỳ, nhất là với mái có độ dốc thấp nơi nước dễ đọng lại thành vệt "
             "bẩn ở mép dưới tấm pin."),
            ("Theo dõi sản lượng để phát hiện bất thường",
             "Cách hiệu quả nhất để biết hệ có vấn đề là so sánh sản lượng theo thời "
             "gian. Hầu hết inverter hiện nay đều có ứng dụng ghi nhận dữ liệu. Nếu sản "
             "lượng những ngày nắng tốt thấp hơn hẳn so với cùng kỳ trước đó, đó là dấu "
             "hiệu cần kiểm tra. Thói quen xem lại số liệu mỗi tháng giúp phát hiện sự "
             "cố sớm, trước khi thất thoát tích lũy thành con số lớn."),
            ("Kiểm tra đầu nối và dây dẫn",
             "Các mối nối chịu giãn nở nhiệt liên tục ngày qua ngày, lâu dần có thể lỏng "
             "và phát nhiệt tại điểm tiếp xúc. Kiểm tra định kỳ tình trạng đầu nối, vỏ "
             "cách điện của dây dẫn và độ chắc chắn của các điểm cố định là việc nên làm. "
             "Đây là hạng mục liên quan trực tiếp đến an toàn, không chỉ đến sản lượng, "
             "nên cần người có chuyên môn thực hiện."),
            ("Chú ý tới inverter",
             "Inverter là thiết bị điện tử làm việc liên tục nên thường là bộ phận cần "
             "chú ý nhất trong hệ. Nên kiểm tra khu vực lắp đặt có thông thoáng không, "
             "quạt tản nhiệt hoạt động bình thường không, và các cảnh báo lỗi hiển thị "
             "trên thiết bị hoặc ứng dụng. Xử lý sớm cảnh báo thường đơn giản hơn nhiều "
             "so với để đến khi thiết bị ngừng hẳn."),
            ("Kiểm tra phần mái và kết cấu",
             "Ngoài phần điện, nên kiểm tra định kỳ tình trạng mái phía dưới dàn pin: "
             "dấu hiệu thấm dột, tình trạng các điểm bắt giá đỡ và độ chắc của khung. "
             "Phát hiện sớm một điểm thấm nhỏ dễ xử lý hơn nhiều so với khi nước đã ngấm "
             "vào kết cấu. Việc này nên làm trước mùa mưa bão hằng năm."),
        ],
        "closings": [
            "Tóm lại, bảo trì hệ thống điện mặt trời gồm bốn việc chính: vệ sinh tấm pin, "
            "theo dõi sản lượng để phát hiện bất thường, kiểm tra định kỳ đầu nối và kết "
            "cấu, cùng với việc để mắt tới các cảnh báo của inverter.",
            "Nói ngắn gọn, một hệ thống không được theo dõi vẫn chạy nhưng có thể đang "
            "mất sản lượng mỗi ngày. Bảo trì hệ thống điện mặt trời — cụ thể là vệ sinh "
            "tấm pin và kiểm tra định kỳ — chỉ chiếm ít thời gian nhưng giữ cho khoản "
            "đầu tư đạt đúng hiệu quả kỳ vọng.",
        ],
        "hashtags": ["#BaoTriSolar", "#VeSinhTamPin", "#VanHanhHeThong", "#SolarOM"],
    },
    {
        "id": "on-grid-off-grid",
        "focus_keyword": "hệ thống hòa lưới on-grid",
        "secondary_keywords": ["off-grid", "độc lập", "hybrid", "pin lưu trữ"],
        "image_query": "solar power grid connection electricity",
        "image_alt": "So sánh hệ thống điện mặt trời hòa lưới on-grid, độc lập off-grid và hybrid",
        "hooks": [
            "Hệ thống hòa lưới on-grid, off-grid hay hybrid — chọn loại nào?",
            "Hệ thống hòa lưới on-grid: rẻ nhất, nhưng mất điện thì cũng ngừng.",
            "Hệ thống hòa lưới on-grid và hai lựa chọn còn lại: khác nhau ở đâu?",
        ],
        "intros": [
            "Ba khái niệm hệ thống hòa lưới on-grid, hệ độc lập off-grid và hệ hybrid "
            "xuất hiện trong hầu hết tư vấn về điện mặt trời, nhưng không phải ai cũng "
            "được giải thích rõ. Chọn sai loại ngay từ đầu dẫn tới hoặc chi phí thừa, "
            "hoặc hệ thống không đáp ứng đúng nhu cầu. Bài viết này phân biệt ba loại "
            "theo cách dễ hình dung nhất.",
            "Sự khác nhau giữa hệ thống hòa lưới on-grid, hệ độc lập và hệ hybrid nằm ở "
            "chỗ hệ có pin lưu trữ hay không, và có phụ thuộc vào lưới điện hay không. "
            "Hiểu đúng ba loại này giúp anh/chị biết mình thật sự cần gì trước khi nghe "
            "báo giá.",
        ],
        "sections": [
            ("Hệ thống hòa lưới on-grid",
             "Đây là loại phổ biến nhất và có chi phí đầu tư thấp nhất vì không cần pin "
             "lưu trữ. Hệ gồm tấm pin và inverter, điện tạo ra dùng trực tiếp cho tải, "
             "phần dư đưa lên lưới. Hạn chế lớn nhất: khi lưới mất điện, hệ tự động ngừng "
             "hoạt động dù trời đang nắng. Đây là yêu cầu an toàn bắt buộc, nhằm tránh "
             "gây nguy hiểm cho người sửa chữa trên lưới."),
            ("Hệ độc lập off-grid",
             "Hệ off-grid hoạt động hoàn toàn không phụ thuộc lưới điện, nên bắt buộc "
             "phải có pin lưu trữ để cấp điện khi không có nắng. Loại này phù hợp với khu "
             "vực chưa có lưới hoặc rất khó kéo lưới tới. Đổi lại, chi phí cao hơn đáng "
             "kể và cần tính toán dung lượng pin kỹ lưỡng, vì không còn nguồn nào khác "
             "để dự phòng khi pin cạn."),
            ("Hệ hybrid",
             "Hybrid kết hợp ưu điểm của hai loại trên: vẫn đấu nối lưới, đồng thời có "
             "pin lưu trữ. Nhờ đó hệ vừa tận dụng được lưới như nguồn dự phòng, vừa duy "
             "trì điện cho nhóm tải ưu tiên khi lưới mất. Đây là lựa chọn cho khu vực có "
             "lưới nhưng hay mất điện, hoặc gia đình muốn dùng phần điện dư ban ngày vào "
             "buổi tối."),
            ("Chọn theo nhu cầu, không theo giá",
             "Nếu khu vực có lưới ổn định và mục tiêu chính là giảm hóa đơn, hệ hòa lưới "
             "thường là phương án hợp lý nhất về chi phí. Nếu mất điện gây thiệt hại thật "
             "sự — hàng hóa trong kho lạnh, thiết bị không được phép dừng — thì phần đầu "
             "tư thêm cho hybrid là có cơ sở. Off-grid chỉ nên chọn khi thật sự không có "
             "lưới để đấu nối."),
            ("Tính trước khả năng nâng cấp",
             "Nhiều gia đình bắt đầu với hệ hòa lưới rồi vài năm sau muốn bổ sung pin. "
             "Khi đó, inverter ban đầu có hỗ trợ kết nối pin hay không sẽ quyết định chi "
             "phí nâng cấp. Vì vậy ngay cả khi chưa lắp pin ngay, việc trao đổi trước về "
             "khả năng mở rộng ở khâu thiết kế giúp tránh phải thay thiết bị chính về sau."),
        ],
        "closings": [
            "Tóm lại, hệ thống hòa lưới on-grid phù hợp khi lưới ổn định và mục tiêu là "
            "giảm hóa đơn; hệ hybrid dành cho nơi hay mất điện nhờ có pin lưu trữ; còn hệ "
            "độc lập off-grid chỉ nên chọn khi không có lưới để đấu nối.",
            "Nói ngắn gọn, khác biệt giữa hệ thống hòa lưới on-grid, hệ off-grid và hybrid "
            "nằm ở pin lưu trữ và mức độ phụ thuộc lưới. Hãy chọn theo tần suất mất điện "
            "và mức thiệt hại khi mất điện, thay vì chọn theo chênh lệch giá đầu tư.",
        ],
        "hashtags": ["#OnGrid", "#OffGrid", "#Hybrid", "#DienMatTroi"],
    },
    {
        "id": "giam-sat-hieu-suat",
        "focus_keyword": "giám sát hệ thống điện mặt trời",
        "secondary_keywords": ["sản lượng điện", "cảnh báo lỗi", "ứng dụng theo dõi", "hiệu suất"],
        "image_query": "solar monitoring app dashboard energy",
        "image_alt": "Ứng dụng giám sát sản lượng và hiệu suất hệ thống điện mặt trời",
        "hooks": [
            "Giám sát hệ thống điện mặt trời: biết hệ đang chạy tốt hay đang mất tiền mỗi ngày.",
            "Giám sát hệ thống điện mặt trời — đọc số liệu thế nào cho có ích?",
            "Giám sát hệ thống điện mặt trời: tính năng có sẵn mà ít người dùng tới.",
        ],
        "intros": [
            "Hầu hết hệ điện mặt trời hiện nay đều đi kèm khả năng theo dõi qua ứng dụng, "
            "nhưng phần lớn chủ nhà chỉ mở ra vài lần trong tuần đầu rồi thôi. Giám sát "
            "hệ thống điện mặt trời đúng cách là cách rẻ nhất để đảm bảo khoản đầu tư "
            "đang sinh lợi như kỳ vọng.",
            "Một hệ điện mặt trời gặp sự cố hiếm khi ngừng hẳn — thường nó chỉ phát ít đi. "
            "Nếu không có thói quen giám sát hệ thống điện mặt trời, phần sản lượng mất đi "
            "có thể kéo dài nhiều tháng mà không ai nhận ra. Dưới đây là những chỉ số đáng "
            "theo dõi và cách hiểu chúng.",
        ],
        "sections": [
            ("Những chỉ số cơ bản cần nắm",
             "Hai chỉ số quan trọng nhất là sản lượng điện theo ngày và công suất tức "
             "thời. Sản lượng ngày cho biết tổng lượng điện hệ tạo ra, còn công suất tức "
             "thời cho biết hệ đang phát bao nhiêu tại thời điểm xem. Ngoài ra còn có "
             "sản lượng tích lũy theo tháng và năm — con số hữu ích để so sánh giữa các "
             "kỳ và đánh giá xu hướng dài hạn."),
            ("So sánh theo cùng điều kiện thời tiết",
             "Sai lầm thường gặp là so sánh sản lượng giữa hai ngày có thời tiết khác "
             "nhau rồi kết luận hệ có vấn đề. Cách đúng là so sánh những ngày nắng tốt "
             "với nhau, hoặc so tổng sản lượng tháng này với cùng kỳ năm trước. Xu hướng "
             "giảm rõ rệt trong điều kiện tương đương mới là dấu hiệu đáng để kiểm tra "
             "kỹ hơn."),
            ("Dấu hiệu cảnh báo cần lưu ý",
             "Sản lượng giảm đột ngột thường liên quan đến một chuỗi tấm pin ngừng hoạt "
             "động hoặc thiết bị bảo vệ đã ngắt. Sản lượng giảm từ từ theo tháng lại "
             "thường do bụi bẩn tích tụ trên bề mặt tấm pin. Hai kiểu suy giảm này có "
             "nguyên nhân khác nhau nên cách xử lý cũng khác — nhận diện đúng giúp tiết "
             "kiệm thời gian tìm lỗi."),
            ("Thiết lập cảnh báo tự động",
             "Nhiều ứng dụng cho phép bật thông báo khi hệ gặp lỗi hoặc khi sản lượng "
             "xuống dưới ngưỡng đặt trước. Bật sẵn tính năng này hiệu quả hơn nhiều so "
             "với việc phải nhớ mở ứng dụng kiểm tra. Với hệ công suất lớn, nơi mỗi ngày "
             "gián đoạn đều là một khoản thất thoát đáng kể, đây gần như là việc bắt "
             "buộc."),
            ("Lưu số liệu để đối chiếu về sau",
             "Số liệu sản lượng của những tháng đầu, khi hệ còn mới và sạch, là mốc tham "
             "chiếu rất có giá trị. Giữ lại dữ liệu này giúp anh/chị đánh giá được hệ "
             "đang suy giảm ở mức bình thường hay bất thường sau vài năm vận hành, đồng "
             "thời là căn cứ khi cần làm việc với đơn vị bảo hành về cam kết hiệu suất."),
        ],
        "closings": [
            "Tóm lại, giám sát hệ thống điện mặt trời không cần phức tạp: theo dõi sản "
            "lượng điện những ngày nắng tốt, bật cảnh báo lỗi tự động trên ứng dụng theo "
            "dõi, và lưu lại số liệu giai đoạn đầu để đối chiếu hiệu suất về sau.",
            "Nói ngắn gọn, giám sát hệ thống điện mặt trời là việc tốn ít công nhất nhưng "
            "bảo vệ khoản đầu tư hiệu quả nhất. Chỉ cần xem lại sản lượng điện mỗi tháng "
            "và bật cảnh báo lỗi trên ứng dụng theo dõi là đủ để phát hiện sớm hầu hết "
            "vấn đề.",
        ],
        "hashtags": ["#GiamSatSolar", "#SanLuongDien", "#HieuSuat", "#SolarMonitoring"],
    },
]


@dataclass
class SEOPost:
    """Một bài đăng đã sinh, kèm báo cáo SEO."""

    content: str
    topic_id: str
    focus_keyword: str
    hashtags: list[str]
    image_query: str
    image_alt: str
    seo_report: dict = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        return self.seo_report.get("body_word_count", 0)


# --- Tiện ích đo lường SEO --------------------------------------------------
def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    ).lower()


def _tokenize(text: str) -> list[str]:
    """Chuẩn hóa về token không dấu, bỏ mọi ký tự phân cách."""
    return re.findall(r"[a-z0-9]+", _strip_accents(text))


# Số token đệm cho phép chen giữa các từ của cụm từ khóa. Nhờ đó
# "điện mặt trời áp mái" vẫn khớp với "điện mặt trời cho áp mái",
# và "on-grid" khớp với "on grid" — cách các công cụ SEO nhận diện biến thể.
KEYPHRASE_SLACK = 4


def count_words(text: str) -> int:
    """Đếm từ, bỏ qua dòng hashtag."""
    body = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("#")
    )
    return len([w for w in body.split() if any(ch.isalnum() for ch in w)])


def keyword_occurrences(text: str, keyword: str) -> int:
    """Đếm số lần cụm từ khóa xuất hiện, chấp nhận biến thể có từ chen giữa."""
    haystack = _tokenize(text)
    needle = _tokenize(keyword)
    if not needle or len(needle) > len(haystack):
        return 0

    window = len(needle) + KEYPHRASE_SLACK
    count = 0
    i = 0
    while i <= len(haystack) - len(needle):
        if haystack[i] != needle[0]:
            i += 1
            continue
        pos, matched = i + 1, 1
        limit = min(i + window, len(haystack))
        for token in needle[1:]:
            while pos < limit and haystack[pos] != token:
                pos += 1
            if pos >= limit:
                break
            pos += 1
            matched += 1
        if matched == len(needle):
            count += 1
            i = pos  # không cho các lần khớp chồng lấn nhau
        else:
            i += 1
    return count


def build_seo_report(content: str, focus_keyword: str, secondary: list[str],
                     hashtags: list[str], brand: dict) -> dict:
    """Chấm điểm bài đăng theo các tiêu chí SEO cơ bản."""
    words = count_words(content)
    occurrences = keyword_occurrences(content, focus_keyword)
    density = round(occurrences / words * 100, 2) if words else 0.0

    first_chunk = content[:125]
    paragraphs = [p for p in content.split("\n\n") if p.strip()]
    sentences = [s for s in re.split(r"[.!?]\s", content) if s.strip()]
    avg_sentence_len = round(words / len(sentences), 1) if sentences else 0.0
    secondary_hits = [kw for kw in secondary if keyword_occurrences(content, kw)]
    contact = brand.get("hotline") or FIELD_PLACEHOLDERS["hotline"]

    checks = {
        "Độ dài thân bài >= 300 từ": words >= MIN_BODY_WORDS,
        "Từ khóa chính trong 125 ký tự đầu": keyword_occurrences(first_chunk, focus_keyword) > 0,
        "Mật độ từ khóa 0.5–3%": 0.5 <= density <= 3.0,
        "Có >= 2 từ khóa phụ (LSI)": len(secondary_hits) >= 2,
        "Có tiêu đề phụ phân đoạn": content.count("▸") >= 3,
        "Có CTA kèm thông tin liên hệ": contact in content,
        "Số hashtag trong khoảng 5–10": 5 <= len(hashtags) <= 10,
        "Đoạn văn dễ đọc (>= 6 đoạn)": len(paragraphs) >= 6,
        "Câu trung bình <= 35 từ": avg_sentence_len <= 35,
    }

    return {
        "body_word_count": words,
        "focus_keyword": focus_keyword,
        "keyword_occurrences": occurrences,
        "keyword_density_pct": density,
        "secondary_keywords_used": secondary_hits,
        "paragraphs": len(paragraphs),
        "avg_sentence_words": avg_sentence_len,
        "hashtag_count": len(hashtags),
        "checks": checks,
        "passed": all(checks.values()),
        "score": f"{sum(checks.values())}/{len(checks)}",
    }


# --- Bộ sinh nội dung -------------------------------------------------------
class SEOPostGenerator:
    """Sinh bài đăng chuẩn SEO, đảm bảo thân bài vượt ngưỡng từ tối thiểu."""

    def __init__(self, min_words: int = MIN_BODY_WORDS,
                 history_file: Path | None = None,
                 brand: dict | None = None):
        self.min_words = min_words
        self.history_file = history_file if history_file is not None else HISTORY_FILE
        self.brand = load_brand() if brand is None else brand

    # -- lịch sử tránh trùng nội dung --
    def _load_history(self) -> list[str]:
        try:
            return json.loads(self.history_file.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_history(self, history: list[str]) -> None:
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.write_text(
                json.dumps(history[-HISTORY_SIZE:], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass  # Môi trường chỉ đọc (CI) — bỏ qua, không chặn việc đăng bài

    @staticmethod
    def _fingerprint(topic_id: str, section_titles: list[str]) -> str:
        raw = topic_id + "|" + "|".join(sorted(section_titles))
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]

    def _available_proofs(self) -> list[dict]:
        """Chỉ dùng khối uy tín mà cấu hình đã có đủ dữ liệu."""
        return [p for p in PROOF_TEMPLATES if _has(self.brand, *p["requires"])]

    # -- lắp ráp bài đăng --
    def _assemble(self, topic: dict, rng: random.Random) -> tuple[str, list[str], list[str]]:
        hook = rng.choice(topic["hooks"])
        intro = rng.choice(topic["intros"])

        sections = list(topic["sections"])
        rng.shuffle(sections)
        chosen = sections[:3]

        proof = rng.choice(self._available_proofs())
        closing = rng.choice(topic["closings"])
        cta = rng.choice(CTA_TEMPLATES).replace("{contact}", contact_line(self.brand))

        parts = [hook, "", intro]
        for title, body in chosen:
            parts += ["", f"▸ {title}", body]
        parts += ["", f"▸ {proof['title']}", proof["body"]]

        # Phần kết luôn được render nên luôn mang từ khóa chính và các từ khóa
        # phụ, bất kể tổ hợp phần thân nào được chọn ngẫu nhiên ở trên.
        tail = ["", closing, "", cta]

        # Bổ sung thêm phần thân nếu chưa đạt ngưỡng từ tối thiểu
        extra_pool = sections[3:]
        while count_words("\n".join(parts + tail)) < self.min_words and extra_pool:
            title, body = extra_pool.pop(0)
            chosen.append((title, body))
            parts += ["", f"▸ {title}", body]

        parts += tail

        hashtags = topic["hashtags"] + BRAND_HASHTAGS
        content = _fill("\n".join(parts), self.brand) + "\n\n" + " ".join(hashtags)
        return content, hashtags, [t for t, _ in chosen]

    def _build(self, topic: dict, content: str, hashtags: list[str]) -> SEOPost:
        return SEOPost(
            content=content,
            topic_id=topic["id"],
            focus_keyword=topic["focus_keyword"],
            hashtags=hashtags,
            image_query=topic["image_query"],
            image_alt=topic["image_alt"],
            seo_report=build_seo_report(
                content, topic["focus_keyword"],
                topic["secondary_keywords"], hashtags, self.brand,
            ),
        )

    def generate(self, topic_id: str | None = None,
                 seed: int | None = None,
                 rotation_index: int | None = None) -> SEOPost:
        """Sinh một bài đăng. Ưu tiên chủ đề/tổ hợp chưa dùng gần đây.

        `rotation_index` dùng cho môi trường không giữ được file lịch sử giữa
        các lần chạy (ví dụ GitHub Actions): chủ đề được xoay vòng theo chỉ số
        này nên vẫn không lặp lại, kể cả khi lịch sử trống.
        """
        rng = random.Random(seed if seed is not None else rotation_index)
        history = self._load_history()

        if topic_id:
            candidates = [t for t in TOPICS if t["id"] == topic_id]
            if not candidates:
                raise ValueError(f"Không tìm thấy chủ đề: {topic_id}")
        elif rotation_index is not None:
            start = rotation_index % len(TOPICS)
            candidates = TOPICS[start:] + TOPICS[:start]
        else:
            recent_topics = {h.split(":")[0] for h in history[-6:]}
            candidates = [t for t in TOPICS if t["id"] not in recent_topics] or list(TOPICS)
            rng.shuffle(candidates)

        content = hashtags = None
        topic = candidates[0]
        for attempt_topic in candidates:
            for _ in range(6):
                content, hashtags, section_titles = self._assemble(attempt_topic, rng)
                fp = f"{attempt_topic['id']}:{self._fingerprint(attempt_topic['id'], section_titles)}"
                if fp not in history:
                    history.append(fp)
                    self._save_history(history)
                    return self._build(attempt_topic, content, hashtags)
            topic = attempt_topic

        # Mọi tổ hợp đều đã dùng — chấp nhận lặp lại tổ hợp cũ nhất
        return self._build(topic, content, hashtags)


def generate_post(topic_id: str | None = None, seed: int | None = None,
                  rotation_index: int | None = None) -> SEOPost:
    """Hàm tiện ích cho các script đăng bài."""
    return SEOPostGenerator().generate(
        topic_id=topic_id, seed=seed, rotation_index=rotation_index
    )


def daily_rotation_index(now: datetime | None = None) -> int:
    """Chỉ số xoay vòng theo ngày và ca đăng (sáng/tối).

    Hai ca mỗi ngày nên mỗi ngày tăng 2 đơn vị — với 12 chủ đề, một chủ đề chỉ
    quay lại sau 6 ngày ngay cả khi máy chủ không giữ được file lịch sử.
    """
    now = now or datetime.now(timezone.utc)
    return now.toordinal() * 2 + (0 if now.hour < 10 else 1)


# --- CLI: xem thử và kiểm tra chất lượng ------------------------------------
def _print_brand_status() -> int:
    brand = load_brand()
    missing = missing_brand_fields(brand)
    print(f"File cấu hình: {BRAND_CONFIG_FILE}")
    if not BRAND_CONFIG_FILE.exists():
        print("❌ Chưa có file brand_config.json.")
        return 1

    print("\nTrường bắt buộc:")
    for f in REQUIRED_BRAND_FIELDS:
        value = str(brand.get(f, "")).strip()
        print(f"  [{'x' if value else ' '}] {f:<16} {value or '(chưa điền)'}")

    optional = [k for k in brand if k not in REQUIRED_BRAND_FIELDS]
    print("\nTrường tùy chọn (để trống thì phần nội dung tương ứng bị bỏ qua):")
    for f in optional:
        value = brand.get(f)
        shown = ", ".join(value) if isinstance(value, list) else str(value or "")
        print(f"  [{'x' if shown else ' '}] {f:<20} {shown or '(chưa điền)'}")

    usable = [p["title"] for p in PROOF_TEMPLATES if _has(brand, *p["requires"])]
    print(f"\nKhối uy tín dùng được: {len(usable)}/{len(PROOF_TEMPLATES)}")
    for t in usable:
        print(f"  - {t}")

    if missing:
        print(f"\n❌ Còn thiếu trường bắt buộc: {', '.join(missing)}")
        print("   Script đăng bài sẽ từ chối đăng cho tới khi điền đủ.")
        return 1
    print("\n✅ Cấu hình thương hiệu đã đủ để đăng bài.")
    return 0


def _print_post(post: SEOPost) -> None:
    print("=" * 72)
    print(post.content)
    print("=" * 72)
    r = post.seo_report
    print(f"Chủ đề       : {post.topic_id}")
    print(f"Từ khóa chính: {r['focus_keyword']}")
    print(f"Số từ thân bài: {r['body_word_count']}")
    print(f"Mật độ từ khóa: {r['keyword_density_pct']}% ({r['keyword_occurrences']} lần)")
    print(f"Từ khóa phụ  : {', '.join(r['secondary_keywords_used']) or '—'}")
    print(f"Alt text ảnh : {post.image_alt}")
    print(f"Điểm SEO     : {r['score']}")
    for name, ok in r["checks"].items():
        print(f"  [{'x' if ok else ' '}] {name}")

    if missing_brand_fields():
        print("\n⚠️  Bản xem thử đang dùng nhãn «...» vì brand_config.json chưa điền đủ.")


def _audit(runs: int) -> int:
    """Sinh thử nhiều bài, báo cáo bài ngắn nhất và các tiêu chí chưa đạt."""
    import tempfile

    tmp = Path(tempfile.mkdtemp()) / "history.json"
    gen = SEOPostGenerator(history_file=tmp)
    counts, failures = [], []
    for i in range(runs):
        post = gen.generate(seed=i)
        counts.append(post.word_count)
        failed = [k for k, v in post.seo_report["checks"].items() if not v]
        if failed:
            failures.append((post.topic_id, post.word_count, failed))

    print(f"Đã sinh thử {runs} bài trên {len(TOPICS)} chủ đề.")
    print(f"Số từ  — nhỏ nhất: {min(counts)} | trung bình: {sum(counts) // len(counts)} "
          f"| lớn nhất: {max(counts)}")
    print(f"Ngưỡng yêu cầu: >= {MIN_BODY_WORDS} từ "
          f"→ {'ĐẠT' if min(counts) >= MIN_BODY_WORDS else 'CHƯA ĐẠT'}")
    if failures:
        print(f"\n{len(failures)} bài chưa đạt đủ tiêu chí SEO:")
        for topic_id, wc, failed in failures[:10]:
            print(f"  - {topic_id} ({wc} từ): {'; '.join(failed)}")
        return 1
    print("Tất cả bài đều đạt toàn bộ tiêu chí SEO.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Bộ sinh nội dung chuẩn SEO SVPsolar")
    parser.add_argument("--topic", help="ID chủ đề cụ thể (mặc định: tự chọn luân phiên)")
    parser.add_argument("--seed", type=int, help="Seed ngẫu nhiên để tái lập kết quả")
    parser.add_argument("--audit", type=int, metavar="N",
                        help="Sinh thử N bài và kiểm tra toàn bộ tiêu chí SEO")
    parser.add_argument("--list", action="store_true", help="Liệt kê các chủ đề")
    parser.add_argument("--check-brand", action="store_true",
                        help="Kiểm tra brand_config.json đã điền đủ chưa")
    args = parser.parse_args()

    if args.check_brand:
        return _print_brand_status()
    if args.list:
        for t in TOPICS:
            print(f"{t['id']:<32} {t['focus_keyword']}")
        return 0
    if args.audit:
        return _audit(args.audit)

    _print_post(generate_post(topic_id=args.topic, seed=args.seed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
