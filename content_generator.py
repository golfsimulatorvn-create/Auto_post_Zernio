"""
Bộ sinh nội dung chuẩn SEO cho Hoa Huy Green Energy.

Mục tiêu:
- Mỗi bài đăng có phần thân >= 300 từ (không tính hashtag).
- Cấu trúc chuẩn SEO: hook chứa từ khóa chính trong ~125 ký tự đầu, mở bài,
  3 phần thân có tiêu đề phụ, khối E-E-A-T (nhà máy + chứng nhận), CTA, hashtag.
- Chỉ dùng số liệu đã công bố trong product-catalog.md / brand-guideline.md.
  Không bịa thông số (số chu kỳ sạc, giá, kích thước chưa công bố).
- Tone theo brand-guideline: kỹ thuật, đáng tin cậy, hạn chế emoji.
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

HISTORY_FILE = Path(__file__).parent / "output" / "post_history.json"
HISTORY_SIZE = 40

BRAND_HASHTAGS = ["#HoaHuyGreenEnergy", "#PinLithium", "#LiFePO4"]

CONTACT_LINE = "Mr. Hiếu — 0904.789.969 | hoahuy.com"


# --- Khối E-E-A-T dùng chung: năng lực nhà máy, chứng nhận, con người -------
PROOF_BLOCKS = [
    (
        "Năng lực sản xuất trong nước",
        "Toàn bộ sản phẩm được lắp ráp tại nhà máy Hoa Huy Green Energy — Lô CN03, "
        "KCN Thái Hà, xã Bắc Lý, tỉnh Ninh Bình. Nhà máy có hơn 200 nhân sự, trong đó "
        "100% kỹ thuật viên được đào tạo về an toàn hóa chất, an toàn điện và vận hành "
        "pin lithium. Sản xuất trong nước đồng nghĩa với thời gian giao hàng ngắn hơn "
        "hàng nhập khẩu, và quan trọng hơn với khách hàng B2B là khả năng bảo hành, "
        "thay thế và hỗ trợ kỹ thuật tại chỗ khi có sự cố.",
    ),
    (
        "Chứng nhận quốc tế đầy đủ",
        "Sản phẩm Hoa Huy đáp ứng bộ tiêu chuẩn UL1642, UL1973, IEC62619, IEC62133 và "
        "UN38.3, cùng hệ thống quản lý chất lượng ISO 9001:2015 và quản lý môi trường "
        "ISO 14001:2015. Đây chính là bộ hồ sơ thường được yêu cầu khi tham gia đấu "
        "thầu, ký hợp đồng xuất khẩu hoặc vận chuyển pin lithium bằng đường hàng không "
        "và đường biển. Với chủ đầu tư, chứng nhận là cách kiểm chứng chất lượng khách "
        "quan thay vì chỉ tin vào lời giới thiệu của nhà cung cấp.",
    ),
    (
        "Kiểm soát chất lượng đa công đoạn",
        "Quy trình sản xuất áp dụng dây chuyền hàn laser công suất cao và kiểm soát "
        "chất lượng qua nhiều công đoạn trước khi xuất xưởng, theo hệ thống ISO "
        "9001:2015 mà nhà máy đang vận hành. Cell được phân loại trước khi lắp ráp để "
        "các cell trong cùng một khối pin có thông số đồng đều — yếu tố ảnh hưởng trực "
        "tiếp đến tuổi thọ thực tế của cả bộ pin, bởi một khối pin thường xuống cấp "
        "theo cell yếu nhất trong đó.",
    ),
    (
        "Đồng hành kỹ thuật, không chỉ bán hàng",
        "Ngoài sản phẩm tiêu chuẩn, Hoa Huy cung cấp dịch vụ OEM/ODM, thiết kế kiến "
        "trúc pin và BMS theo yêu cầu, hiệu chuẩn và kiểm tra chất lượng pin, cho thuê "
        "pin lưu trữ công nghiệp và giải pháp hoán đổi pin (battery swapping). Đội kỹ "
        "thuật tham gia từ khâu khảo sát nhu cầu vận hành thực tế, nên cấu hình đề "
        "xuất bám sát bài toán của khách hàng thay vì chỉ chọn một mã sản phẩm có sẵn "
        "trong danh mục.",
    ),
]

CTA_BLOCKS = [
    "Anh/chị đang cần tư vấn cấu hình phù hợp với nhu cầu vận hành thực tế? Liên hệ "
    f"phòng kinh doanh Hoa Huy Green Energy: {CONTACT_LINE}. Đội kỹ thuật sẽ trao đổi "
    "về dải điện áp, dung lượng và điều kiện lắp đặt trước khi đề xuất phương án.",
    "Cần báo giá hoặc hồ sơ kỹ thuật đầy đủ cho dự án của mình? Liên hệ Hoa Huy Green "
    f"Energy: {CONTACT_LINE}. Chúng tôi hỗ trợ cả phương án mẫu thử (pilot) trước khi "
    "khách hàng quyết định đặt số lượng lớn.",
    "Anh/chị muốn so sánh trực tiếp với giải pháp đang dùng? Gửi thông số hệ thống "
    f"hiện tại cho đội kỹ thuật Hoa Huy Green Energy: {CONTACT_LINE} để nhận phân tích "
    "cụ thể theo điều kiện vận hành của mình.",
]


# --- Dữ liệu chủ đề ---------------------------------------------------------
# Mỗi chủ đề: từ khóa chính, từ khóa phụ (LSI), hook, mở bài, >=4 phần thân,
# hashtag riêng và mô tả ảnh (alt text phục vụ SEO ảnh).
TOPICS: list[dict] = [
    {
        "id": "pin-xe-may-dien",
        "focus_keyword": "pin lithium xe máy điện",
        "secondary_keywords": [
            "cell LiFePO4",
            "đội xe máy điện",
            "tuổi thọ pin",
            "dải điện áp",
        ],
        "closings": [
            "Tóm lại, chọn pin lithium xe máy điện là bài toán cân giữa chi phí đầu tư "
            "ban đầu, tuổi thọ pin và độ an toàn của cell LiFePO4 — nên bắt đầu từ điều "
            "kiện vận hành thật của đội xe máy điện thay vì chỉ so sánh giá niêm yết.",
            "Nói ngắn gọn, một bộ pin lithium xe máy điện tốt được đánh giá qua tuổi thọ "
            "pin sau hàng nghìn chu kỳ, chất lượng cell LiFePO4 và mức độ khớp với dải "
            "điện áp của xe — ba yếu tố quyết định chi phí thật của cả đội xe máy điện.",
        ],
        "image_query": "electric motorbike battery",
        "image_alt": "Pin lithium xe máy điện LiFePO4 Hoa Huy Green Energy sản xuất tại Ninh Bình",
        "hooks": [
            "Pin lithium xe máy điện: chọn đúng ngay từ đầu để không phải thay sớm.",
            "Pin lithium xe máy điện LiFePO4 — vì sao đang thay thế dần ắc quy chì?",
            "Đánh giá pin lithium xe máy điện: nhìn vào đâu ngoài con số Ah?",
        ],
        "intros": [
            "Khi chọn pin lithium xe máy điện, phần lớn người dùng chỉ nhìn vào dung "
            "lượng Ah và quãng đường đi được sau mỗi lần sạc. Nhưng với chủ đội xe hay "
            "đại lý, con số quyết định lại là độ ổn định sau hàng nghìn chu kỳ sạc/xả "
            "và mức độ an toàn nhiệt khi vận hành liên tục. Dưới đây là những yếu tố kỹ "
            "thuật nên cân nhắc trước khi xuống tiền cho cả một đội xe.",
            "Thị trường pin lithium xe máy điện hiện có rất nhiều mức giá, và chênh "
            "lệch giữa các lựa chọn thường nằm ở những thứ không nhìn thấy được từ bên "
            "ngoài: loại cell, chất lượng mối hàn, thiết kế BMS và quy trình kiểm soát "
            "chất lượng. Bài viết này phân tích các tiêu chí kỹ thuật giúp anh/chị so "
            "sánh giữa các nhà cung cấp một cách có cơ sở.",
        ],
        "sections": [
            (
                "Cell LiFePO4 — nền tảng của độ an toàn",
                "Điểm khác biệt lớn nhất của pin lithium xe máy điện Hoa Huy nằm ở hóa "
                "học cell: LiFePO4 (lithium sắt phốt phát). So với các dòng lithium phổ "
                "thông khác, LiFePO4 được đánh giá cao về độ ổn định nhiệt và độ bền chu "
                "kỳ — hai yếu tố quyết định trực tiếp đến rủi ro cháy nổ và tuổi thọ "
                "thực tế. Với xe máy điện hoạt động ngoài trời, chịu nắng nóng và rung "
                "xóc liên tục, đặc tính an toàn nhiệt của cell không phải là chi tiết "
                "kỹ thuật phụ mà là điều kiện bắt buộc.",
            ),
            (
                "Thông số thực tế của dòng pin xe máy điện Hoa Huy",
                "Mã HHXM6025A2 là bộ ắc quy LiFePO4 60V/25Ah, năng lượng 1.500Wh, cấp "
                "bảo vệ IP65 chống bụi và nước, khối lượng 13,5kg, kích thước 263 x 170 "
                "x 165mm — phù hợp các dòng xe máy điện tầm trung. Mã HHXM7230B ở phân "
                "khúc cao hơn với 72V/30Ah. Ngoài ra Hoa Huy còn có dải 48V (25–40Ah) "
                "cho phân khúc phổ thông, dải 60V (25–50Ah), dải 72V (25–100Ah) và các "
                "dòng 76V, 96V cho nhu cầu tầm hoạt động mở rộng.",
            ),
            (
                "Bài toán chi phí vận hành cho đội xe",
                "Với một đội xe vài chục đến vài trăm chiếc, chi phí thực sự không nằm ở "
                "giá mua ban đầu mà ở tổng chi phí sở hữu: số lần phải thay pin trong "
                "vòng đời xe, thời gian xe nằm chờ sửa và rủi ro dừng vận hành đột "
                "xuất. Một bộ pin rẻ hơn nhưng phải thay sớm hơn, kèm theo những ngày xe "
                "không chạy được, thường đắt hơn đáng kể khi tính trên toàn đội xe và "
                "cả chu kỳ khai thác.",
            ),
            (
                "Tương thích và lắp đặt",
                "Trước khi chọn pin lithium xe máy điện, cần xác định đúng ba thông số: "
                "dải điện áp danh định của xe, không gian khoang chứa pin và kiểu đầu "
                "nối. Sai lệch điện áp có thể khiến bộ điều khiển không nhận pin hoặc "
                "hoạt động sai thông số thiết kế. Đội kỹ thuật Hoa Huy hỗ trợ đối chiếu "
                "thông số xe hiện có trước khi đề xuất mã pin, đặc biệt với các trường "
                "hợp thay thế pin cho đội xe đã vận hành nhiều năm.",
            ),
            (
                "Bảo hành và hỗ trợ sau bán hàng",
                "Với khách hàng B2B, tốc độ phản hồi khi có sự cố kỹ thuật quan trọng "
                "không kém chất lượng sản phẩm. Vì pin được sản xuất ngay trong nước, "
                "quy trình kiểm tra, bảo hành và thay thế không phải chờ chu kỳ nhập "
                "khẩu như hàng ngoại nhập. Đây là khác biệt rõ rệt khi một sự cố nhỏ có "
                "thể khiến nhiều xe trong đội phải dừng hoạt động cùng lúc.",
            ),
        ],
        "hashtags": ["#PinXeMayDien", "#XeMayDien", "#PinXeDien", "#NangLuongXanh"],
    },
    {
        "id": "ess-ho-gia-dinh",
        "focus_keyword": "hệ thống lưu trữ năng lượng ESS",
        "secondary_keywords": [
            "pin lưu trữ LiFePO4",
            "điện mặt trời áp mái",
            "dung lượng kWh",
            "kiểu dáng lắp đặt",
        ],
        "closings": [
            "Nói ngắn gọn, một hệ thống lưu trữ năng lượng ESS phù hợp là hệ được chọn "
            "theo mức tiêu thụ thật và điều kiện lắp đặt thật — từ dung lượng kWh, kiểu "
            "dáng lắp đặt cho đến khả năng ghép với hệ điện mặt trời áp mái sẵn có. Pin "
            "lưu trữ LiFePO4 của Hoa Huy có đủ ba kiểu dáng để bám theo mặt bằng thực tế.",
            "Tóm lại, đầu tư hệ thống lưu trữ năng lượng ESS nên bắt đầu từ hóa đơn điện "
            "và công suất điện mặt trời áp mái đang có, rồi mới chốt dung lượng kWh và "
            "kiểu dáng lắp đặt. Pin lưu trữ LiFePO4 cho phép mở rộng dần thay vì phải "
            "tính đúng ngay từ lần đầu.",
        ],
        "image_query": "home battery energy storage system",
        "image_alt": "Hệ thống lưu trữ năng lượng ESS LiFePO4 Hoa Huy cho hộ gia đình dùng điện mặt trời",
        "hooks": [
            "Hệ thống lưu trữ năng lượng ESS: giải bài toán điện mặt trời chỉ phát ban ngày.",
            "Hệ thống lưu trữ năng lượng ESS cho hộ gia đình — cần bao nhiêu kWh là đủ?",
            "Lắp điện mặt trời rồi, có nên đầu tư thêm hệ thống lưu trữ năng lượng ESS?",
        ],
        "intros": [
            "Điện mặt trời áp mái chỉ phát điện vào ban ngày, trong khi phần lớn hộ gia "
            "đình lại tiêu thụ nhiều nhất vào buổi tối. Hệ thống lưu trữ năng lượng ESS "
            "sinh ra để lấp đúng khoảng trống đó: tích điện dư ban ngày và trả lại vào "
            "giờ cao điểm hoặc khi mất điện. Câu hỏi thực tế không phải có nên lắp hay "
            "không, mà là chọn dung lượng và kiểu dáng nào cho phù hợp.",
            "Với khu vực giá điện cao hoặc mất điện thường xuyên, hệ thống lưu trữ năng "
            "lượng ESS đang trở thành phần bổ sung tự nhiên cho hệ điện mặt trời áp "
            "mái. Tuy nhiên, chọn sai dung lượng hoặc sai kiểu lắp đặt sẽ khiến khoản "
            "đầu tư không phát huy hết giá trị. Dưới đây là cách tiếp cận theo nhu cầu "
            "tiêu thụ thực tế thay vì chọn theo cảm tính.",
        ],
        "sections": [
            (
                "Chọn dung lượng theo mức tiêu thụ thực tế",
                "Nguyên tắc là bắt đầu từ lượng điện cần dùng trong khoảng thời gian "
                "muốn chủ động, chứ không phải từ dung lượng lớn nhất có thể mua. Dòng "
                "ESS của Hoa Huy dùng cell LiFePO4 ở điện áp chuẩn 51.2V, với các mức "
                "phổ biến: HHEA51280V01 (280Ah, 14,34 kWh) và HHEA51314V01 (314Ah, "
                "16,08 kWh). Việc quy đổi từ hóa đơn điện hàng tháng sang nhu cầu lưu "
                "trữ nên có kỹ thuật viên hỗ trợ, vì còn phụ thuộc vào công suất dàn "
                "pin mặt trời đang có.",
            ),
            (
                "Ba kiểu dáng cho ba điều kiện lắp đặt",
                "Hoa Huy cung cấp ba kiểu dáng ESS để phù hợp với mặt bằng thực tế. Bản "
                "All-In-One tích hợp sẵn các thành phần, giúp rút ngắn thời gian và chi "
                "phí nhân công lắp đặt. Bản Stand dạng tủ đứng phù hợp phòng kỹ thuật "
                "hoặc khu vực có sẵn không gian sàn. Bản Wall-Mount treo tường tiết "
                "kiệm diện tích cho nhà ở đô thị. Cả ba đều có ở hai mức 280Ah và "
                "314Ah, tương ứng khoảng 14,3 kWh và 16 kWh.",
            ),
            (
                "Khả năng mở rộng cho nhà xưởng và công nghiệp",
                "Với nhà xưởng hoặc cơ sở có nhu cầu lớn hơn, dòng Stacked ESS dạng "
                "module xếp chồng cho phép tăng dung lượng theo từng giai đoạn thay vì "
                "đầu tư toàn bộ ngay từ đầu. Series HHD6 có các phiên bản 5,2 / 10,4 / "
                "15,6 / 20,9 / 26,1 kWh; series HHEC dành cho quy mô công nghiệp với "
                "16 / 32 / 48,2 / 64,3 / 80,4 kWh. Cách tiếp cận module hóa giúp chi "
                "phí đầu tư đi theo tốc độ tăng trưởng của tải tiêu thụ.",
            ),
            (
                "An toàn khi lắp đặt trong nhà",
                "Lo ngại phổ biến nhất khi đặt pin lưu trữ trong khu vực sinh hoạt là "
                "an toàn cháy nổ và tản nhiệt. Đây là lý do toàn bộ dòng ESS của Hoa Huy "
                "dùng cell LiFePO4 — hóa học pin có độ ổn định nhiệt cao hơn so với "
                "nhiều dòng lithium phổ thông khác. Bên cạnh đó, hệ thống quản lý pin "
                "BMS giám sát điện áp, dòng và nhiệt độ để ngắt bảo vệ khi vượt ngưỡng "
                "an toàn trong quá trình sạc và xả.",
            ),
            (
                "Tương thích với hệ inverter sẵn có",
                "Một rủi ro thường gặp là mua pin lưu trữ về mới phát hiện không tương "
                "thích với inverter đang dùng. Trước khi chốt phương án, cần đối chiếu "
                "dải điện áp, giao thức truyền thông giữa BMS và inverter, cùng công "
                "suất sạc/xả tối đa mà hệ thống hiện tại cho phép. Đội kỹ thuật Hoa Huy "
                "hỗ trợ khâu đối chiếu này với các nhà tích hợp EPC ngay từ giai đoạn "
                "thiết kế hệ thống.",
            ),
        ],
        "hashtags": ["#ESS", "#LuuTruNangLuong", "#DienMatTroi", "#PinLuuTru"],
    },
    {
        "id": "lifepo4-vs-chi-axit",
        "focus_keyword": "pin LiFePO4",
        "secondary_keywords": [
            "ắc quy chì axit",
            "tuổi thọ chu kỳ",
            "tổng chi phí sở hữu",
            "độ sâu xả",
        ],
        "closings": [
            "Kết luận: so sánh pin LiFePO4 với ắc quy chì-axit nên đặt trên tổng chi phí "
            "sở hữu — gồm tuổi thọ chu kỳ, độ sâu xả khai thác được thực tế và chi phí "
            "bảo trì lặp lại — thay vì chỉ nhìn vào giá mua ban đầu.",
            "Tóm lại, khác biệt giữa pin LiFePO4 và ắc quy chì-axit nằm ở tuổi thọ chu "
            "kỳ, độ sâu xả cho phép và khối lượng công việc bảo trì. Đưa đủ ba yếu tố này "
            "vào bảng tính tổng chi phí sở hữu thì kết quả thường khác hẳn cảm nhận ban đầu.",
        ],
        "image_query": "lithium battery cells industrial",
        "image_alt": "So sánh pin LiFePO4 Hoa Huy với ắc quy chì-axit truyền thống",
        "hooks": [
            "Pin LiFePO4 hay ắc quy chì-axit: so sánh trên tổng chi phí, không chỉ giá mua.",
            "Pin LiFePO4 đắt hơn ắc quy chì — nhưng đắt hơn thật không?",
            "Pin LiFePO4 khác ắc quy chì-axit ở đâu, ngoài trọng lượng?",
        ],
        "intros": [
            "Khi so sánh pin LiFePO4 với ắc quy chì-axit, phép so sánh chỉ dựa trên giá "
            "mua ban đầu gần như luôn dẫn đến kết luận sai. Hai công nghệ khác nhau về "
            "tuổi thọ chu kỳ, độ sâu xả cho phép, hiệu suất nạp/xả và cả chi phí bảo "
            "trì. Bài viết này phân tích các yếu tố cần đưa vào bảng tính trước khi "
            "quyết định cho một dự án hay một đội xe.",
            "Nhiều doanh nghiệp vẫn đang dùng ắc quy chì-axit vì quen thuộc và giá mua "
            "thấp. Nhưng khi tính đủ chi phí trong toàn bộ vòng đời khai thác, pin "
            "LiFePO4 thường cho kết quả khác với cảm nhận ban đầu. Dưới đây là những "
            "khác biệt kỹ thuật có ảnh hưởng trực tiếp đến chi phí vận hành.",
        ],
        "sections": [
            (
                "Tuổi thọ chu kỳ và tần suất thay thế",
                "Khác biệt căn bản nằm ở số chu kỳ sạc/xả mà mỗi công nghệ chịu được "
                "trước khi dung lượng suy giảm đáng kể. Pin LiFePO4 có độ bền chu kỳ cao "
                "hơn rõ rệt so với ắc quy chì-axit, đồng nghĩa số lần phải thay thế "
                "trong cùng một khoảng thời gian khai thác ít hơn. Với thiết bị vận hành "
                "hàng ngày như xe nâng, xe golf hay hệ lưu trữ, mỗi lần thay pin đều kéo "
                "theo chi phí vật tư, nhân công và thời gian dừng máy.",
            ),
            (
                "Độ sâu xả và dung lượng dùng được thực tế",
                "Một điểm dễ bị bỏ qua: dung lượng ghi trên nhãn không phải dung lượng "
                "sử dụng được. Ắc quy chì-axit thường được khuyến cáo không xả quá sâu "
                "để tránh giảm tuổi thọ nhanh, nghĩa là một phần dung lượng danh nghĩa "
                "gần như không dùng tới. Pin LiFePO4 cho phép khai thác phần lớn dung "
                "lượng danh định mà vẫn giữ được độ bền, nên dung lượng thực dùng trên "
                "mỗi đồng đầu tư cao hơn đáng kể so với con số trên nhãn.",
            ),
            (
                "Trọng lượng, thể tích và điều kiện lắp đặt",
                "Với cùng một mức năng lượng, pin LiFePO4 gọn và nhẹ hơn ắc quy chì-axit. "
                "Trên xe điện, chênh lệch trọng lượng ảnh hưởng trực tiếp đến quãng "
                "đường và khả năng tải. Trong phòng kỹ thuật, thể tích nhỏ hơn giúp bố "
                "trí dễ hơn và giảm yêu cầu gia cố sàn. Bộ pin HHXM6025A2 60V/25Ah của "
                "Hoa Huy có năng lượng 1.500Wh với khối lượng 13,5kg và kích thước 263 x "
                "170 x 165mm — mức gọn nhẹ khó đạt được với công nghệ chì-axit.",
            ),
            (
                "Bảo trì và chi phí ẩn",
                "Ắc quy chì-axit thường đòi hỏi quy trình bảo dưỡng định kỳ và điều kiện "
                "thông gió riêng, kéo theo chi phí nhân công lặp lại mà ít được tính vào "
                "bảng so sánh ban đầu. Pin LiFePO4 tích hợp hệ thống quản lý pin BMS "
                "giám sát tự động các thông số vận hành, giúp giảm khối lượng công việc "
                "bảo trì thủ công và hạn chế rủi ro do thao tác sai của người vận hành.",
            ),
            (
                "Khi nào thì nên chuyển đổi?",
                "Thời điểm hợp lý nhất để chuyển sang pin LiFePO4 thường là khi lô ắc "
                "quy hiện tại sắp đến hạn thay thế — lúc đó chi phí chuyển đổi được so "
                "sánh trực tiếp với chi phí mua lô ắc quy mới, thay vì bị coi là khoản "
                "đầu tư phát sinh. Hoa Huy hỗ trợ phương án mẫu thử trên một phần đội xe "
                "hoặc một nhánh hệ thống, để khách hàng có số liệu vận hành thực tế "
                "trước khi chuyển đổi toàn bộ.",
            ),
        ],
        "hashtags": ["#LiFePO4", "#AcQuyChi", "#TietKiemChiPhi", "#CongNghePin"],
    },
    {
        "id": "pin-xe-golf",
        "focus_keyword": "pin xe golf lithium",
        "secondary_keywords": [
            "cell LiFePO4",
            "sân golf",
            "dung lượng pin",
            "dải điện áp",
        ],
        "closings": [
            "Tóm lại, chọn pin xe golf lithium nên đi từ số vòng khai thác mỗi ngày và "
            "địa hình sân golf, rồi mới chốt dải điện áp và dung lượng pin. Cell LiFePO4 "
            "giúp xe giữ điện áp ổn định suốt ca thay vì yếu dần về cuối ngày.",
            "Nói ngắn gọn, hiệu quả của pin xe golf lithium được đo bằng số xe sẵn sàng "
            "phục vụ mỗi ngày. Chọn đúng dải điện áp và dung lượng pin theo đặc thù sân "
            "golf, cộng với độ ổn định của cell LiFePO4, là cách rút ngắn thời gian xe "
            "nằm chờ sạc.",
        ],
        "image_query": "golf cart battery",
        "image_alt": "Pin xe golf lithium LiFePO4 Hoa Huy dải 48V đến 96V",
        "hooks": [
            "Pin xe golf lithium: giảm thời gian sạc, tăng số vòng khai thác mỗi ngày.",
            "Pin xe golf lithium LiFePO4 — chọn dung lượng theo địa hình sân.",
            "Nâng cấp pin xe golf lithium: bài toán của đơn vị vận hành sân.",
        ],
        "intros": [
            "Với đơn vị vận hành sân golf, mỗi chiếc xe nằm chờ sạc là một lượt khách "
            "không phục vụ được. Đó là lý do pin xe golf lithium đang thay thế dần ắc "
            "quy truyền thống: thời gian sạc ngắn hơn, dung lượng khai thác được nhiều "
            "hơn và ít yêu cầu bảo dưỡng thủ công hơn. Vấn đề còn lại là chọn đúng cấu "
            "hình điện áp và dung lượng cho đặc thù từng sân.",
            "Không phải sân golf nào cũng cần cùng một cấu hình pin. Địa hình đồi dốc, "
            "số vòng khai thác mỗi ngày và loại xe đang sử dụng đều ảnh hưởng đến lựa "
            "chọn pin xe golf lithium phù hợp. Dưới đây là cách khoanh vùng cấu hình "
            "trước khi yêu cầu báo giá.",
        ],
        "sections": [
            (
                "Dải sản phẩm theo điện áp và dung lượng",
                "Hoa Huy cung cấp pin xe golf LiFePO4 trải trên nhiều dải điện áp. Ở mức "
                "48V có G48100 (100Ah, 4,8 kWh), G48280 (280Ah, 13,4 kWh) và G48314 "
                "(314Ah, 15,1 kWh). Mức 60V có G60100 (6,0 kWh), G60280 (16,8 kWh), "
                "G60314 (18,8 kWh). Mức 72V có G72100 (7,2 kWh), G72280 (20,2 kWh), "
                "G72314 (22,6 kWh). Ngoài ra còn có mã 76280 (76V, 20,2 kWh) và dải 96V "
                "với G96280 (26,9 kWh), G96314 (30,1 kWh) cho nhu cầu công suất cao.",
            ),
            (
                "Chọn dung lượng theo số vòng khai thác",
                "Cách chọn thực tế nhất là đi từ số vòng sân mỗi xe phải chạy trong một "
                "ngày cao điểm, cộng thêm biên dự phòng cho địa hình dốc và điều hòa "
                "trên xe nếu có. Chọn dư quá nhiều làm tăng chi phí đầu tư và trọng "
                "lượng xe không cần thiết; chọn thiếu khiến xe phải sạc giữa ca, đúng "
                "vào lúc nhu cầu phục vụ cao nhất. Đây là bài toán nên tính trên dữ liệu "
                "vận hành thật của sân.",
            ),
            (
                "Giảm thời gian dừng xe trong ngày",
                "Ưu điểm lớn nhất của pin lithium trong môi trường sân golf là khả năng "
                "rút ngắn thời gian xe không sẵn sàng phục vụ. Ít phải bảo dưỡng thủ "
                "công hơn, không cần quy trình châm nước định kỳ như ắc quy chì-axit, và "
                "điện áp giữ ổn định hơn trong suốt quá trình xả — xe không bị yếu dần "
                "về cuối ca, điều mà khách chơi golf cảm nhận được rất rõ.",
            ),
            (
                "Vận hành ngoài trời và điều kiện thời tiết",
                "Xe golf hoạt động gần như hoàn toàn ngoài trời, chịu nắng nóng, độ ẩm "
                "cao và rung xóc trên địa hình không bằng phẳng. Cell LiFePO4 được đánh "
                "giá cao về độ ổn định nhiệt, phù hợp với điều kiện khí hậu Việt Nam. "
                "Kết cấu khối pin và hệ thống BMS đóng vai trò bảo vệ khi nhiệt độ hoặc "
                "dòng vượt ngưỡng thiết kế trong quá trình vận hành liên tục.",
            ),
            (
                "Chuyển đổi cả đội xe theo giai đoạn",
                "Không nhất thiết phải thay pin toàn bộ đội xe cùng lúc. Phương án phổ "
                "biến là chuyển đổi theo lô, bắt đầu từ nhóm xe có tần suất khai thác "
                "cao nhất, vừa phân bổ được chi phí đầu tư vừa thu được số liệu vận hành "
                "thực tế trước khi mở rộng. Hoa Huy hỗ trợ cả phương án mẫu thử cho "
                "khách hàng cần đánh giá trước khi đặt số lượng lớn.",
            ),
        ],
        "hashtags": ["#PinXeGolf", "#XeGolf", "#SanGolf", "#PinLithium48V"],
    },
    {
        "id": "pin-xe-nang-agv",
        "focus_keyword": "pin xe nâng lithium",
        "secondary_keywords": [
            "xe AGV",
            "cell LiFePO4",
            "thời gian dừng máy",
            "sạc tranh thủ",
        ],
        "closings": [
            "Tóm lại, giá trị lớn nhất của pin xe nâng lithium không nằm ở thông số trên "
            "nhãn mà ở thời gian dừng máy giảm được: sạc tranh thủ giữa ca, bỏ được khu "
            "vực sạc riêng, và độ an toàn của cell LiFePO4 trong nhà xưởng. Với xe AGV "
            "chạy theo lịch tự động, tính liên tục này còn quan trọng hơn nữa.",
            "Nói ngắn gọn, bài toán pin xe nâng lithium là bài toán thời gian dừng máy. "
            "Khả năng sạc tranh thủ trong giờ nghỉ, độ ổn định nhiệt của cell LiFePO4 và "
            "thiết kế riêng cho từng dòng xe nâng hay xe AGV là ba yếu tố quyết định "
            "hiệu quả thực tế.",
        ],
        "image_query": "forklift warehouse industrial",
        "image_alt": "Pin xe nâng và xe AGV lithium LiFePO4 Hoa Huy cho nhà máy công nghiệp",
        "hooks": [
            "Pin xe nâng lithium: bỏ phòng sạc riêng, bỏ luôn quy trình thay ắc quy giữa ca.",
            "Pin xe nâng lithium cho nhà máy chạy nhiều ca — tính lại bài toán downtime.",
            "Pin xe nâng lithium và xe AGV: khi thời gian sạc là chi phí sản xuất.",
        ],
        "intros": [
            "Trong nhà máy chạy nhiều ca, mỗi giờ xe nâng nằm chờ sạc là một giờ gián "
            "đoạn của cả dây chuyền phía sau. Pin xe nâng lithium thay đổi cách tổ chức "
            "vận hành: có thể sạc tranh thủ trong các khoảng nghỉ ngắn thay vì phải "
            "tháo lắp ắc quy giữa ca. Với đơn vị vận hành xe AGV, tính liên tục còn "
            "quan trọng hơn nữa vì thiết bị chạy theo lịch trình tự động.",
            "Xe nâng và xe AGV là những thiết bị mà thời gian dừng gây thiệt hại lan "
            "sang toàn bộ chuỗi vận hành phía sau. Khi đánh giá pin xe nâng lithium, "
            "câu hỏi không chỉ là pin chạy được bao lâu, mà là cách nó tác động đến "
            "cách tổ chức ca kíp và mặt bằng nhà xưởng.",
        ],
        "sections": [
            (
                "Sạc tranh thủ thay vì thay ắc quy giữa ca",
                "Mô hình vận hành truyền thống với ắc quy chì-axit thường phải bố trí "
                "khu vực sạc riêng, ắc quy dự phòng và quy trình tháo lắp giữa ca — kéo "
                "theo nhân công, thiết bị nâng hạ và diện tích nhà xưởng. Pin lithium "
                "cho phép tổ chức lại theo hướng sạc tranh thủ trong các khoảng nghỉ "
                "ngắn của ca làm việc, giúp giảm đáng kể thời gian thiết bị không sẵn "
                "sàng và đơn giản hóa quy trình cho tổ vận hành.",
            ),
            (
                "Giải phóng diện tích và giảm yêu cầu hạ tầng",
                "Bỏ được khu vực sạc chuyên dụng đồng nghĩa với việc thu hồi một phần "
                "diện tích nhà xưởng cho hoạt động sản xuất. Bên cạnh đó, pin lithium "
                "không đòi hỏi quy trình bảo dưỡng định kỳ nặng nề như ắc quy chì-axit, "
                "giúp giảm khối lượng công việc lặp lại của bộ phận bảo trì và hạn chế "
                "rủi ro phát sinh từ thao tác thủ công.",
            ),
            (
                "Thiết kế theo yêu cầu cho thiết bị chuyên dụng",
                "Xe nâng và xe AGV thường có yêu cầu riêng về kích thước khoang pin, vị "
                "trí đầu nối và giao thức truyền thông với bộ điều khiển. Đây là lý do "
                "nhóm sản phẩm này thường được triển khai theo hướng OEM/ODM: Hoa Huy "
                "tham gia từ khâu thiết kế kiến trúc pin và BMS để bộ pin khớp với "
                "thiết bị thực tế, thay vì buộc khách hàng chọn trong danh mục có sẵn.",
            ),
            (
                "An toàn trong môi trường nhà xưởng",
                "Trong không gian kín có nhiều người và vật tư, rủi ro cháy nổ từ pin "
                "ảnh hưởng trực tiếp đến an toàn lao động và uy tín doanh nghiệp. Cell "
                "LiFePO4 được lựa chọn cho nhóm sản phẩm công nghiệp chính vì độ ổn "
                "định nhiệt cao. Hệ thống BMS giám sát liên tục điện áp, dòng và nhiệt "
                "độ, ngắt bảo vệ khi vượt ngưỡng — lớp bảo vệ cần thiết với thiết bị vận "
                "hành cường độ cao suốt ngày.",
            ),
            (
                "Phương án thuê thay vì mua",
                "Với doanh nghiệp muốn kiểm soát dòng tiền hoặc chưa muốn ghi nhận một "
                "khoản đầu tư lớn ngay, Hoa Huy có dịch vụ cho thuê pin lưu trữ công "
                "nghiệp và giải pháp hoán đổi pin (battery swapping). Đây là hướng tiếp "
                "cận phù hợp khi nhu cầu còn biến động theo mùa vụ hoặc khi doanh nghiệp "
                "muốn đánh giá hiệu quả thực tế trước khi đầu tư dài hạn.",
            ),
        ],
        "hashtags": ["#PinXeNang", "#XeAGV", "#Logistics", "#NhaMayThongMinh"],
    },
    {
        "id": "oem-odm-pin-lithium",
        "focus_keyword": "gia công pin lithium OEM ODM",
        "secondary_keywords": [
            "thiết kế BMS",
            "nhà máy pin lithium",
            "chứng nhận UN38.3",
            "sản xuất theo yêu cầu",
        ],
        "closings": [
            "Tóm lại, chọn đối tác gia công pin lithium OEM/ODM nên dựa trên ba thứ kiểm "
            "chứng được: năng lực nhà máy pin lithium thực tế, bộ chứng nhận UN38.3 cùng "
            "các tiêu chuẩn quốc tế, và khả năng thiết kế BMS cho sản xuất theo yêu cầu.",
            "Nói ngắn gọn, một đối tác gia công pin lithium OEM/ODM đáng tin là bên cho "
            "phép kiểm chứng nhà máy pin lithium tận nơi, có sẵn chứng nhận UN38.3 cho "
            "xuất khẩu, và đủ năng lực thiết kế BMS để sản xuất theo yêu cầu riêng của "
            "từng thiết bị.",
        ],
        "image_query": "battery factory production line",
        "image_alt": "Dây chuyền gia công pin lithium OEM ODM tại nhà máy Hoa Huy Ninh Bình",
        "hooks": [
            "Gia công pin lithium OEM/ODM: chọn nhà máy theo năng lực thật, không theo brochure.",
            "Gia công pin lithium OEM/ODM tại Việt Nam — cần kiểm tra những gì trước khi ký?",
            "Gia công pin lithium OEM/ODM: từ bản vẽ BMS đến lô sản xuất hàng loạt.",
        ],
        "intros": [
            "Với doanh nghiệp sản xuất thiết bị điện hoặc thương hiệu muốn gắn logo "
            "riêng lên sản phẩm pin, việc chọn đối tác gia công pin lithium OEM/ODM là "
            "quyết định dài hạn. Yếu tố quyết định không nằm ở lời giới thiệu mà ở năng "
            "lực nhà máy thực tế: dây chuyền, chứng nhận, quy mô nhân sự và khả năng "
            "giữ chất lượng ổn định giữa các lô sản xuất.",
            "Tìm được nhà máy vừa đạt chuẩn quốc tế vừa đủ linh hoạt để tùy biến theo "
            "yêu cầu riêng là bài toán khó với nhiều doanh nghiệp. Bài viết này liệt kê "
            "những gì nên kiểm tra khi đánh giá một đối tác gia công pin lithium "
            "OEM/ODM, dựa trên các tiêu chí mà khách hàng công nghiệp thường đưa vào "
            "hồ sơ thẩm định nhà cung cấp.",
        ],
        "sections": [
            (
                "Tùy biến từ kiến trúc pin đến BMS",
                "Gia công OEM/ODM đúng nghĩa không dừng ở việc dán nhãn lên sản phẩm có "
                "sẵn. Hoa Huy nhận thiết kế kiến trúc pin và hệ thống quản lý pin BMS "
                "theo yêu cầu — bao gồm hình dạng khối pin, dung lượng, dải điện áp và "
                "các thông số bảo vệ phù hợp với thiết bị đích. Cách làm này quan trọng "
                "với những sản phẩm có ràng buộc riêng về không gian lắp đặt hoặc giao "
                "thức truyền thông với bộ điều khiển.",
            ),
            (
                "Hồ sơ chứng nhận sẵn sàng cho xuất khẩu",
                "Với đối tác có kế hoạch xuất khẩu, bộ chứng nhận của nhà máy quyết định "
                "sản phẩm có ra được thị trường mục tiêu hay không. Hoa Huy đáp ứng "
                "UL1642, UL1973, IEC62619, IEC62133, UN38.3 cùng ISO 9001:2015 và ISO "
                "14001:2015. Riêng UN38.3 là điều kiện bắt buộc cho vận chuyển pin "
                "lithium bằng đường hàng không và đường biển — thiếu chứng nhận này, lô "
                "hàng không thể lên tàu hay lên máy bay.",
            ),
            (
                "Tính nhất quán giữa các lô sản xuất",
                "Rủi ro lớn nhất khi gia công số lượng lớn là chất lượng dao động giữa "
                "các lô. Nhà máy Hoa Huy áp dụng dây chuyền hàn laser công suất cao và "
                "quy trình phân loại cell trước khi lắp ráp, để các cell trong cùng khối "
                "pin có thông số đồng đều. Kết hợp với hệ thống quản lý chất lượng ISO "
                "9001:2015, đây là cơ sở để giữ ổn định thông số đầu ra qua nhiều đợt "
                "sản xuất khác nhau.",
            ),
            (
                "Năng lực nhà máy có thể kiểm chứng",
                "Nhà máy đặt tại Lô CN03, KCN Thái Hà, xã Bắc Lý, tỉnh Ninh Bình với hơn "
                "200 nhân sự, trong đó 100% kỹ thuật viên được đào tạo về an toàn hóa "
                "chất, an toàn điện và vận hành pin lithium. Đối tác OEM/ODM có thể sắp "
                "xếp tham quan nhà máy và làm việc trực tiếp với đội kỹ thuật — cách "
                "kiểm chứng năng lực đáng tin cậy hơn nhiều so với tài liệu giới thiệu.",
            ),
            (
                "Dịch vụ hiệu chuẩn và kiểm tra chất lượng",
                "Ngoài gia công, Hoa Huy cung cấp dịch vụ hiệu chuẩn và kiểm tra chất "
                "lượng pin. Với doanh nghiệp cần đánh giá độc lập hiệu năng của lô pin "
                "trước khi đưa vào sản phẩm cuối, đây là bước kiểm soát giúp phát hiện "
                "sai lệch sớm, thay vì để lỗi đi tới tay người dùng cuối và phát sinh "
                "chi phí bảo hành lớn hơn nhiều lần.",
            ),
        ],
        "hashtags": ["#OEM", "#ODM", "#SanXuatPin", "#MadeInVietnam"],
    },
    {
        "id": "an-toan-pin-lithium",
        "focus_keyword": "an toàn pin lithium",
        "secondary_keywords": [
            "cell LiFePO4",
            "hệ thống BMS",
            "chứng nhận UL",
            "quá nhiệt",
        ],
        "closings": [
            "Tóm lại, an toàn pin lithium là kết quả của ba lớp cộng lại: hóa học cell "
            "LiFePO4, chất lượng chế tạo, và hệ thống BMS ngắt bảo vệ khi quá nhiệt hay "
            "quá dòng — cùng bộ chứng nhận UL, IEC làm cơ sở kiểm chứng khách quan.",
            "Nói ngắn gọn, an toàn pin lithium hoàn toàn có thể kiểm soát được: chọn cell "
            "LiFePO4 ổn định nhiệt, yêu cầu chứng nhận UL và IEC cho đúng dòng sản phẩm "
            "mình mua, và đảm bảo hệ thống BMS đủ năng lực ngắt bảo vệ khi quá nhiệt.",
        ],
        "image_query": "battery safety testing laboratory",
        "image_alt": "Kiểm tra an toàn pin lithium LiFePO4 theo tiêu chuẩn UL và IEC tại Hoa Huy",
        "hooks": [
            "An toàn pin lithium: rủi ro đến từ đâu và kiểm soát bằng cách nào?",
            "An toàn pin lithium không phải chuyện may rủi — đó là chuyện tiêu chuẩn.",
            "An toàn pin lithium cho đội xe điện: ba lớp bảo vệ cần có.",
        ],
        "intros": [
            "An toàn pin lithium là mối quan tâm hàng đầu của mọi doanh nghiệp vận hành "
            "đội xe điện hay hệ lưu trữ, bởi một sự cố không chỉ gây thiệt hại tài sản "
            "mà còn ảnh hưởng trực tiếp đến an toàn lao động và uy tín thương hiệu. Tin "
            "tốt là phần lớn rủi ro có thể kiểm soát được nếu hiểu đúng nguồn gốc và "
            "chọn đúng loại sản phẩm ngay từ đầu.",
            "Những thông tin về sự cố pin xe điện khiến nhiều doanh nghiệp e ngại khi "
            "chuyển đổi. Tuy nhiên, an toàn pin lithium phụ thuộc rất lớn vào hóa học "
            "cell, chất lượng chế tạo và hệ thống bảo vệ đi kèm — những yếu tố hoàn "
            "toàn có thể kiểm chứng qua chứng nhận và hồ sơ kỹ thuật trước khi mua.",
        ],
        "sections": [
            (
                "Lớp thứ nhất: hóa học cell",
                "Không phải pin lithium nào cũng giống nhau. LiFePO4 (lithium sắt phốt "
                "phát) được đánh giá cao về độ ổn định nhiệt so với nhiều dòng lithium "
                "phổ thông khác — đây là lý do toàn bộ sản phẩm Hoa Huy đều dùng cell "
                "LiFePO4, từ pin xe máy điện, xe golf, xe nâng cho đến hệ lưu trữ ESS. "
                "Chọn đúng hóa học cell là lớp bảo vệ đầu tiên và cũng là lớp khó thay "
                "đổi nhất sau khi sản phẩm đã hoàn thiện.",
            ),
            (
                "Lớp thứ hai: chất lượng chế tạo",
                "Phần lớn sự cố pin không đến từ bản thân cell mà từ mối hàn kém, cell "
                "không đồng đều hoặc kết cấu khối pin không chịu được rung xóc. Nhà máy "
                "Hoa Huy dùng dây chuyền hàn laser công suất cao và phân loại cell trước "
                "khi lắp ráp, để các cell trong cùng khối pin có thông số tương đồng. "
                "Cell lệch thông số sẽ chịu tải không đều khi sạc và xả, dẫn đến suy "
                "giảm nhanh và phát nhiệt cục bộ.",
            ),
            (
                "Lớp thứ ba: hệ thống quản lý pin BMS",
                "BMS là bộ não giám sát toàn bộ khối pin trong suốt quá trình vận hành. "
                "Nó theo dõi điện áp từng nhánh cell, dòng sạc/xả và nhiệt độ, ngắt bảo "
                "vệ khi thông số vượt ngưỡng an toàn. Với các dự án OEM/ODM, Hoa Huy "
                "tham gia thiết kế BMS theo đặc thù thiết bị, vì ngưỡng bảo vệ phù hợp "
                "cho xe máy điện chạy đường phố khác với xe nâng vận hành liên tục trong "
                "nhà xưởng.",
            ),
            (
                "Chứng nhận — cách kiểm chứng khách quan",
                "Bộ chứng nhận UL1642, UL1973, IEC62619, IEC62133 và UN38.3 là kết quả "
                "của các bài thử nghiệm độc lập về an toàn pin lithium. Với chủ đầu tư "
                "hoặc bên mua, đây là cách xác minh chất lượng khách quan thay vì chỉ "
                "dựa vào cam kết của nhà cung cấp. Khi thẩm định nhà cung cấp, nên yêu "
                "cầu bản chứng nhận cụ thể cho dòng sản phẩm mình mua, không chỉ chứng "
                "nhận chung của doanh nghiệp.",
            ),
            (
                "Vận hành đúng cách kéo dài tuổi thọ",
                "Ngay cả với pin đạt chuẩn, cách sử dụng vẫn ảnh hưởng lớn đến độ bền và "
                "an toàn. Nên dùng bộ sạc đúng thông số do nhà sản xuất chỉ định, tránh "
                "để pin phơi nắng gắt kéo dài, và kiểm tra định kỳ tình trạng đầu nối, "
                "dây dẫn. Với đội xe nhiều đầu phương tiện, việc đào tạo người vận hành "
                "về quy trình sạc chuẩn thường mang lại hiệu quả cao hơn nhiều so với "
                "chi phí bỏ ra.",
            ),
        ],
        "hashtags": ["#AnToanPin", "#BMS", "#TieuChuanUL", "#PinAnToan"],
    },
    {
        "id": "sac-du-phong-tram-sac",
        "focus_keyword": "sạc dự phòng LiFePO4",
        "secondary_keywords": [
            "trạm sạc dự phòng",
            "cell LiFePO4",
            "dung lượng mAh",
            "chứng nhận UN38.3",
        ],
        "closings": [
            "Tóm lại, với sạc dự phòng LiFePO4 và trạm sạc dự phòng, điều đáng hỏi trước "
            "tiên là loại cell LiFePO4 bên trong chứ không phải con số dung lượng mAh in "
            "trên vỏ hộp — cùng với chứng nhận UN38.3 nếu sản phẩm cần vận chuyển quốc tế.",
            "Nói ngắn gọn, chọn sạc dự phòng LiFePO4 hay trạm sạc dự phòng nên bắt đầu từ "
            "hóa học cell LiFePO4 và nhu cầu sử dụng thật, rồi mới đến dung lượng mAh. "
            "Chứng nhận UN38.3 là điều kiện bắt buộc nếu hàng đi đường hàng không.",
        ],
        "image_query": "portable power station outdoor",
        "image_alt": "Sạc dự phòng và trạm sạc LiFePO4 Hoa Huy cho nhu cầu di động",
        "hooks": [
            "Sạc dự phòng LiFePO4: an toàn hơn cho thiết bị mang theo người mỗi ngày.",
            "Sạc dự phòng LiFePO4 và trạm sạc di động — chọn theo nhu cầu thực tế.",
            "Sạc dự phòng LiFePO4: vì sao hóa học cell lại quan trọng với thiết bị cầm tay?",
        ],
        "intros": [
            "Sạc dự phòng là thiết bị được mang theo người, để trong túi xách, trong "
            "cabin xe hoặc trên bàn làm việc suốt ngày. Chính vì luôn ở gần người dùng, "
            "yếu tố an toàn của sạc dự phòng LiFePO4 đáng được cân nhắc kỹ hơn nhiều so "
            "với một thiết bị đặt cố định. Hóa học cell là điểm khác biệt căn bản mà "
            "thông số dung lượng trên vỏ hộp không nói ra.",
            "Giữa hàng loạt sản phẩm sạc dự phòng trên thị trường, tiêu chí phân biệt rõ "
            "nhất không phải con số mAh mà là loại cell bên trong. Sạc dự phòng LiFePO4 "
            "hướng đến nhóm người dùng và doanh nghiệp coi trọng độ an toàn và độ bền "
            "hơn là mức giá thấp nhất có thể.",
        ],
        "sections": [
            (
                "Dải dung lượng cho từng nhu cầu",
                "Hoa Huy có sạc dự phòng LiFePO4 ở các mức 5.000, 10.000, 15.000, 20.000 "
                "và 30.000 mAh. Mức 10.000 mAh phù hợp nhu cầu hàng ngày với đặc điểm "
                "điện áp phẳng và độ an toàn cao. Mức 15.000 mAh cân bằng giữa dung "
                "lượng và độ gọn. Các mức 20.000 và 30.000 mAh hướng đến người dùng di "
                "chuyển nhiều, cần sạc nhiều thiết bị hoặc làm việc dài ngày ngoài văn "
                "phòng.",
            ),
            (
                "Trạm sạc cho công việc hiện trường",
                "Với đội kỹ thuật làm việc ngoài hiện trường hoặc nhu cầu dã ngoại, dòng "
                "trạm sạc dự phòng LiFePO4 có hai mức: 286Wh cho nhu cầu nhỏ gọn và "
                "768Wh cho các buổi làm việc dài hơn. Khác với sạc dự phòng cầm tay, "
                "trạm sạc hướng tới việc cấp nguồn cho nhiều thiết bị cùng lúc trong "
                "điều kiện không có nguồn điện lưới sẵn có.",
            ),
            (
                "Vì sao chọn LiFePO4 cho thiết bị cầm tay",
                "Với sản phẩm thường xuyên tiếp xúc gần người dùng, độ ổn định nhiệt của "
                "cell là ưu tiên hàng đầu. LiFePO4 được đánh giá cao ở đặc tính này so "
                "với nhiều dòng lithium phổ thông khác, đồng thời cho điện áp ổn định "
                "hơn trong quá trình xả — thiết bị được cấp nguồn đều thay vì yếu dần về "
                "cuối. Đây là lý do Hoa Huy chọn LiFePO4 cho toàn bộ dòng thiết bị di "
                "động của mình.",
            ),
            (
                "Hướng OEM cho doanh nghiệp",
                "Nhóm sản phẩm thiết bị di động đặc biệt phù hợp với các thương hiệu "
                "muốn phát triển dòng sạc dự phòng riêng hoặc doanh nghiệp cần quà tặng "
                "đối tác có gắn nhận diện. Hoa Huy nhận gia công OEM/ODM cho nhóm này, "
                "từ dung lượng, kiểu dáng đến nhận diện thương hiệu in trên sản phẩm, "
                "trên nền tảng cùng bộ tiêu chuẩn chất lượng áp dụng cho các dòng pin "
                "công nghiệp.",
            ),
            (
                "Lưu ý khi vận chuyển và bảo quản",
                "Pin lithium thuộc nhóm hàng có quy định riêng khi vận chuyển bằng đường "
                "hàng không và đường biển, với UN38.3 là chứng nhận bắt buộc. Sản phẩm "
                "Hoa Huy đáp ứng tiêu chuẩn này, thuận lợi cho doanh nghiệp có nhu cầu "
                "xuất khẩu hoặc phân phối quốc tế. Về bảo quản, nên để nơi khô ráo, "
                "tránh nhiệt độ cao kéo dài và không lưu kho ở trạng thái cạn kiệt hoàn "
                "toàn trong thời gian dài.",
            ),
        ],
        "hashtags": ["#SacDuPhong", "#TramSac", "#ThietBiDiDong", "#PinAnToan"],
    },
    {
        "id": "battery-swapping",
        "focus_keyword": "trạm đổi pin xe điện",
        "secondary_keywords": [
            "hoán đổi pin",
            "cho thuê pin",
            "đội xe điện",
            "thời gian sạc",
        ],
        "closings": [
            "Tóm lại, mô hình trạm đổi pin xe điện phù hợp nhất với đội xe điện khai thác "
            "cường độ cao, nơi thời gian sạc ăn trực tiếp vào doanh thu. Kết hợp với dịch "
            "vụ cho thuê pin và hoán đổi pin, doanh nghiệp giảm được cả vốn đầu tư ban "
            "đầu lẫn thời gian phương tiện nằm chờ.",
            "Nói ngắn gọn, trạm đổi pin xe điện đưa thời gian sạc ra khỏi giờ khai thác "
            "của đội xe điện. Với doanh nghiệp còn cân nhắc vốn, dịch vụ cho thuê pin và "
            "hoán đổi pin cho phép thử mô hình ở quy mô nhỏ trước khi mở rộng.",
        ],
        "image_query": "battery swapping station electric vehicle",
        "image_alt": "Giải pháp trạm đổi pin xe điện và cho thuê pin lưu trữ của Hoa Huy Green Energy",
        "hooks": [
            "Trạm đổi pin xe điện: bỏ hẳn thời gian chờ sạc ra khỏi bài toán vận hành.",
            "Trạm đổi pin xe điện và cho thuê pin — hai cách giảm vốn đầu tư ban đầu.",
            "Trạm đổi pin xe điện: mô hình phù hợp với đội xe nào?",
        ],
        "intros": [
            "Với đội xe giao hàng hoặc xe dịch vụ chạy liên tục, thời gian sạc là thời "
            "gian không tạo ra doanh thu. Mô hình trạm đổi pin xe điện giải quyết đúng "
            "điểm nghẽn đó: thay vì chờ sạc đầy, phương tiện đổi lấy một khối pin đã sạc "
            "sẵn và tiếp tục hành trình. Cách tiếp cận này thay đổi cả cấu trúc chi phí "
            "lẫn cách tổ chức vận hành.",
            "Không phải doanh nghiệp nào cũng muốn bỏ vốn mua toàn bộ pin cho đội xe "
            "ngay từ đầu, nhất là khi nhu cầu còn biến động. Mô hình trạm đổi pin xe "
            "điện và dịch vụ cho thuê pin cho phép chuyển một khoản đầu tư tài sản thành "
            "chi phí vận hành theo kỳ, dễ kiểm soát dòng tiền hơn.",
        ],
        "sections": [
            (
                "Đổi pin thay vì chờ sạc",
                "Điểm mấu chốt của mô hình là tách thời gian sạc ra khỏi thời gian khai "
                "thác phương tiện. Khối pin cạn được thu về trạm để sạc theo lịch, trong "
                "khi xe nhận khối pin đã đầy và tiếp tục vận hành ngay. Với đội xe giao "
                "hàng chạy nhiều ca hoặc phương tiện dịch vụ có khung giờ cao điểm rõ "
                "rệt, phần thời gian tiết kiệm được cộng dồn trên toàn đội là con số "
                "đáng kể.",
            ),
            (
                "Chuyển đầu tư tài sản thành chi phí vận hành",
                "Pin thường chiếm tỷ trọng lớn trong giá trị một chiếc xe điện. Dịch vụ "
                "cho thuê pin lưu trữ công nghiệp và giải pháp hoán đổi pin của Hoa Huy "
                "cho phép doanh nghiệp giảm vốn đầu tư ban đầu, chuyển sang chi phí theo "
                "kỳ. Với đơn vị đang trong giai đoạn mở rộng hoặc thử nghiệm chuyển đổi "
                "sang xe điện, đây là cách giảm rủi ro tài chính khi quy mô đội xe chưa "
                "ổn định.",
            ),
            (
                "Quản lý vòng đời pin tập trung",
                "Khi pin được quản lý tập trung tại trạm, quy trình sạc diễn ra trong "
                "điều kiện kiểm soát được thay vì phụ thuộc vào thói quen của từng người "
                "vận hành. Điều này giúp giảm các sai sót phổ biến như dùng sai bộ sạc "
                "hoặc để pin ở trạng thái cạn kiệt kéo dài — những yếu tố ảnh hưởng trực "
                "tiếp đến tuổi thọ thực tế của khối pin.",
            ),
            (
                "Yêu cầu về tính đồng nhất của khối pin",
                "Mô hình đổi pin chỉ vận hành trơn tru khi các khối pin trong hệ thống "
                "đồng nhất về thông số, đầu nối và giao thức BMS. Đây là lý do năng lực "
                "OEM/ODM và tính nhất quán giữa các lô sản xuất trở nên quan trọng — nhà "
                "máy Hoa Huy áp dụng phân loại cell trước lắp ráp và hệ thống ISO "
                "9001:2015 để giữ ổn định thông số đầu ra qua nhiều đợt sản xuất.",
            ),
            (
                "Bắt đầu từ quy mô nhỏ",
                "Với doanh nghiệp muốn thử mô hình trước khi cam kết dài hạn, phương án "
                "hợp lý là triển khai trên một nhánh tuyến hoặc một nhóm xe có tần suất "
                "khai thác cao nhất. Số liệu vận hành thu được từ giai đoạn này là cơ sở "
                "để tính toán quy mô trạm và số lượng pin luân chuyển cần thiết khi mở "
                "rộng ra toàn đội.",
            ),
        ],
        "hashtags": ["#BatterySwapping", "#DoiPin", "#XeDien", "#ChoThuePin"],
    },
    {
        "id": "chuyen-doi-xe-dien-doanh-nghiep",
        "focus_keyword": "chuyển đổi sang xe điện",
        "secondary_keywords": [
            "đội xe điện",
            "tổng chi phí sở hữu",
            "hạ tầng sạc",
            "hoán đổi pin",
        ],
        "closings": [
            "Tóm lại, chuyển đổi sang xe điện nên triển khai theo giai đoạn: chọn nhóm "
            "phương tiện phù hợp trước, tính đủ tổng chi phí sở hữu, chuẩn bị hạ tầng "
            "sạc, rồi cân nhắc hoán đổi pin cho nhóm đội xe điện chạy cường độ cao.",
            "Nói ngắn gọn, chuyển đổi sang xe điện là bài toán lộ trình chứ không phải "
            "một lần mua sắm. Tổng chi phí sở hữu, hạ tầng sạc và phương án hoán đổi pin "
            "cần được tính cùng nhau ngay từ giai đoạn thí điểm trên một phần đội xe điện.",
        ],
        "image_query": "electric vehicle fleet delivery",
        "image_alt": "Giải pháp pin lithium Hoa Huy cho doanh nghiệp chuyển đổi sang đội xe điện",
        "hooks": [
            "Chuyển đổi sang xe điện: lộ trình cho doanh nghiệp vận tải bắt đầu từ đâu?",
            "Chuyển đổi sang xe điện — chi phí pin chiếm bao nhiêu trong bài toán tổng?",
            "Chuyển đổi sang xe điện theo giai đoạn: cách giảm rủi ro cho đội xe.",
        ],
        "intros": [
            "Xu hướng chuyển đổi sang xe điện đang tăng tốc ở các đô thị lớn, kéo theo "
            "nhu cầu thực tế của doanh nghiệp vận tải và dịch vụ: chuyển đổi thế nào để "
            "không gián đoạn hoạt động và không dồn quá nhiều vốn vào một thời điểm. "
            "Pin thường là hạng mục chiếm tỷ trọng lớn nhất, nên cũng là nơi quyết định "
            "phần lớn hiệu quả của cả lộ trình.",
            "Chuyển đổi sang xe điện không phải là một quyết định mua sắm đơn lẻ mà là "
            "một lộ trình nhiều giai đoạn, chạm đến hạ tầng sạc, quy trình vận hành và "
            "cả cách tổ chức nhân sự. Bài viết này phác thảo cách tiếp cận theo giai "
            "đoạn để doanh nghiệp kiểm soát được chi phí và rủi ro.",
        ],
        "sections": [
            (
                "Bắt đầu từ nhóm phương tiện phù hợp nhất",
                "Không nên chuyển đổi toàn bộ đội xe cùng lúc. Cách làm ít rủi ro hơn là "
                "chọn nhóm phương tiện có lộ trình ổn định, quãng đường hàng ngày dự "
                "đoán được và có thể quay về điểm tập kết để sạc. Nhóm này cho số liệu "
                "vận hành thực tế về mức tiêu thụ, thời gian sạc và chi phí, làm cơ sở "
                "để tính toán cho các giai đoạn mở rộng tiếp theo.",
            ),
            (
                "Tính đúng chi phí vòng đời, không chỉ giá mua",
                "So sánh xe điện với xe xăng chỉ dựa trên giá mua ban đầu sẽ bỏ sót phần "
                "lớn bức tranh. Cần tính cả chi phí năng lượng trên mỗi kilômét, chi phí "
                "bảo dưỡng định kỳ, tuổi thọ pin và chi phí thay thế. Với pin LiFePO4 có "
                "độ bền chu kỳ cao, số lần thay thế trong vòng đời khai thác ít hơn, "
                "kéo theo cả chi phí vật tư lẫn thời gian xe dừng hoạt động giảm theo.",
            ),
            (
                "Chọn cấu hình pin theo đặc thù tuyến",
                "Cấu hình pin nên đi từ nhu cầu vận hành thật: quãng đường mỗi ca, địa "
                "hình, tải trọng và số giờ khai thác liên tục. Hoa Huy có dải sản phẩm "
                "trải từ 48V (25–40Ah) cho phân khúc phổ thông, 60V (25–50Ah), 72V "
                "(25–100Ah) đến các dòng 76V và 96V cho nhu cầu tầm hoạt động mở rộng. "
                "Chọn dư gây lãng phí vốn và tăng trọng lượng; chọn thiếu buộc xe phải "
                "sạc giữa ca.",
            ),
            (
                "Hạ tầng sạc và tổ chức ca kíp",
                "Chuyển đổi phương tiện luôn đi kèm với thay đổi cách tổ chức vận hành. "
                "Cần xác định sớm vị trí sạc, công suất nguồn tại điểm tập kết và lịch "
                "sạc phù hợp với ca làm việc. Với đội xe chạy cường độ cao, mô hình hoán "
                "đổi pin (battery swapping) là phương án đáng cân nhắc để loại bỏ thời "
                "gian chờ sạc khỏi giờ khai thác.",
            ),
            (
                "Phương án tài chính linh hoạt",
                "Với doanh nghiệp muốn hạn chế vốn đầu tư ban đầu, dịch vụ cho thuê pin "
                "lưu trữ công nghiệp và giải pháp hoán đổi pin của Hoa Huy cho phép "
                "chuyển một phần chi phí tài sản sang chi phí vận hành theo kỳ. Cách này "
                "phù hợp trong giai đoạn thử nghiệm, khi quy mô đội xe và nhu cầu thực "
                "tế còn đang được điều chỉnh.",
            ),
        ],
        "hashtags": ["#XeDien", "#DoiXeDien", "#VanTaiXanh", "#ChuyenDoiXanh"],
    },
    {
        "id": "bms-quan-ly-pin",
        "focus_keyword": "hệ thống quản lý pin BMS",
        "secondary_keywords": [
            "cân bằng cell",
            "bảo vệ quá dòng",
            "tuổi thọ pin",
            "thiết kế BMS",
        ],
        "closings": [
            "Tóm lại, hệ thống quản lý pin BMS quyết định phần lớn tuổi thọ pin mà người "
            "dùng cảm nhận được: từ cân bằng cell, bảo vệ quá dòng và quá nhiệt, cho đến "
            "việc thiết kế BMS bám đúng đặc thù của từng ứng dụng.",
            "Nói ngắn gọn, khi thẩm định nhà cung cấp, nên hỏi về hệ thống quản lý pin "
            "BMS chứ không dừng ở điện áp và dung lượng: cơ chế cân bằng cell, ngưỡng bảo "
            "vệ quá dòng và năng lực thiết kế BMS riêng là những thứ quyết định tuổi thọ "
            "pin về sau.",
        ],
        "image_query": "battery management system circuit board",
        "image_alt": "Hệ thống quản lý pin BMS trong khối pin LiFePO4 Hoa Huy Green Energy",
        "hooks": [
            "Hệ thống quản lý pin BMS: thành phần quyết định tuổi thọ mà ít ai hỏi tới.",
            "Hệ thống quản lý pin BMS làm gì bên trong khối pin lithium?",
            "Hệ thống quản lý pin BMS — vì sao hai bộ pin cùng thông số lại bền khác nhau?",
        ],
        "intros": [
            "Hai bộ pin có cùng điện áp và dung lượng danh định vẫn có thể cho tuổi thọ "
            "khác nhau đáng kể sau vài năm khai thác. Khác biệt thường nằm ở hệ thống "
            "quản lý pin BMS — thành phần ít được nhắc tới trong bảng thông số nhưng "
            "quyết định phần lớn độ bền và độ an toàn thực tế của khối pin.",
            "Khi so sánh báo giá giữa các nhà cung cấp pin lithium, phần chênh lệch khó "
            "giải thích nhất thường nằm ở chất lượng hệ thống quản lý pin BMS. Hiểu BMS "
            "làm gì sẽ giúp anh/chị đặt đúng câu hỏi khi thẩm định nhà cung cấp, thay vì "
            "chỉ so sánh trên hai con số điện áp và dung lượng.",
        ],
        "sections": [
            (
                "Giám sát và bảo vệ theo thời gian thực",
                "Chức năng cơ bản nhất của BMS là theo dõi liên tục điện áp từng nhánh "
                "cell, dòng sạc/xả và nhiệt độ khối pin. Khi bất kỳ thông số nào vượt "
                "ngưỡng an toàn — quá áp, quá dòng, quá nhiệt hoặc xả quá sâu — BMS ngắt "
                "mạch bảo vệ trước khi hư hỏng lan rộng. Đây là lớp bảo vệ chủ động, "
                "hoạt động độc lập với thao tác của người vận hành.",
            ),
            (
                "Cân bằng cell và tuổi thọ thực tế",
                "Một khối pin gồm nhiều cell mắc nối tiếp, và theo thời gian các cell "
                "không suy giảm hoàn toàn đồng đều. Nếu không có cơ chế cân bằng, cell "
                "yếu nhất sẽ giới hạn dung lượng dùng được của cả khối và ngày càng "
                "xuống cấp nhanh hơn. BMS thực hiện cân bằng để giữ các cell trong dải "
                "hoạt động tương đồng — đây chính là lý do chất lượng BMS ảnh hưởng trực "
                "tiếp đến tuổi thọ mà người dùng cảm nhận được.",
            ),
            (
                "Đồng đều cell ngay từ khâu lắp ráp",
                "BMS làm việc hiệu quả hơn nhiều khi các cell đầu vào đã tương đồng. Nhà "
                "máy Hoa Huy áp dụng quy trình phân loại cell trước khi lắp ráp, để các "
                "cell trong cùng một khối pin có thông số gần nhau. Kết hợp với dây "
                "chuyền hàn laser công suất cao đảm bảo chất lượng mối nối, đây là nền "
                "tảng vật lý mà không thuật toán BMS nào bù đắp được nếu bị bỏ qua.",
            ),
            (
                "Thiết kế BMS theo đặc thù ứng dụng",
                "Ngưỡng bảo vệ phù hợp cho xe máy điện chạy đường phố khác với xe nâng "
                "vận hành liên tục trong nhà xưởng, và khác tiếp với hệ lưu trữ ESS sạc "
                "xả theo chu kỳ ngày. Hoa Huy cung cấp dịch vụ thiết kế BMS và kiến trúc "
                "pin LiFePO4 theo yêu cầu, để thông số bảo vệ bám sát điều kiện vận hành "
                "thật thay vì dùng chung một cấu hình mặc định cho mọi ứng dụng.",
            ),
            (
                "Truyền thông với thiết bị và inverter",
                "Với hệ lưu trữ ESS, BMS cần trao đổi dữ liệu với inverter để phối hợp "
                "quá trình sạc và xả. Với xe điện, BMS làm việc với bộ điều khiển của "
                "phương tiện. Đây là điểm cần đối chiếu sớm khi tích hợp vào hệ thống có "
                "sẵn — sai giao thức truyền thông có thể khiến thiết bị không nhận pin "
                "dù thông số điện áp hoàn toàn phù hợp.",
            ),
        ],
        "hashtags": ["#BMS", "#QuanLyPin", "#CongNghePin", "#KyThuatPin"],
    },
    {
        "id": "ess-cong-nghiep",
        "federated": True,
        "focus_keyword": "lưu trữ năng lượng công nghiệp",
        "secondary_keywords": [
            "Stacked ESS",
            "giờ cao điểm",
            "cell LiFePO4",
            "cho thuê pin",
        ],
        "closings": [
            "Tóm lại, hệ thống lưu trữ năng lượng công nghiệp mang lại giá trị kép: dịch "
            "tải khỏi giờ cao điểm để giảm chi phí điện, và giữ nguồn cho phụ tải quan "
            "trọng. Dòng Stacked ESS dùng cell LiFePO4 cho phép mở rộng theo module, và "
            "có thể triển khai qua hình thức cho thuê pin nếu doanh nghiệp muốn hạn chế "
            "vốn đầu tư.",
            "Nói ngắn gọn, đầu tư lưu trữ năng lượng công nghiệp nên bắt đầu từ biểu đồ "
            "phụ tải và mức chênh giá giờ cao điểm của chính nhà máy. Dòng Stacked ESS "
            "với cell LiFePO4 cho phép mở rộng dần, còn dịch vụ cho thuê pin là lựa chọn "
            "khi chưa muốn ghi nhận đầu tư tài sản lớn.",
        ],
        "image_query": "industrial energy storage container",
        "image_alt": "Hệ thống lưu trữ năng lượng công nghiệp Stacked ESS Hoa Huy cho nhà máy",
        "hooks": [
            "Lưu trữ năng lượng công nghiệp: cắt đỉnh tải và giữ sản xuất không gián đoạn.",
            "Lưu trữ năng lượng công nghiệp cho nhà xưởng — đầu tư theo module, không dồn một lần.",
            "Lưu trữ năng lượng công nghiệp: bài toán của nhà máy có giá điện giờ cao điểm.",
        ],
        "intros": [
            "Với nhà máy và xưởng sản xuất, điện không chỉ là chi phí mà còn là điều "
            "kiện để dây chuyền vận hành liên tục. Hệ thống lưu trữ năng lượng công "
            "nghiệp phục vụ hai mục tiêu song song: giảm chi phí điện bằng cách dịch tải "
            "khỏi giờ cao điểm, và giữ nguồn cho các phụ tải quan trọng khi lưới gặp sự "
            "cố.",
            "Đầu tư hệ thống lưu trữ năng lượng công nghiệp thường bị coi là khoản chi "
            "lớn khó quyết. Nhưng với kiến trúc module hóa, doanh nghiệp có thể bắt đầu "
            "ở quy mô vừa đủ và mở rộng dần theo tốc độ tăng trưởng của tải tiêu thụ — "
            "cách tiếp cận giúp dòng tiền và nhu cầu thực tế đi cùng nhịp với nhau.",
        ],
        "sections": [
            (
                "Kiến trúc module hóa, mở rộng theo giai đoạn",
                "Dòng Stacked ESS của Hoa Huy được thiết kế dạng module xếp chồng. Series "
                "HHD6 có các phiên bản 5,2 / 10,4 / 15,6 / 20,9 / 26,1 kWh, phù hợp "
                "xưởng nhỏ và cơ sở kinh doanh. Series HHEC dành cho quy mô công nghiệp "
                "với 16 / 32 / 48,2 / 64,3 / 80,4 kWh. Doanh nghiệp có thể khởi đầu ở "
                "mức phù hợp hiện tại rồi bổ sung module khi tải tăng, thay vì đầu tư "
                "toàn bộ công suất ngay từ đầu.",
            ),
            (
                "Dịch tải khỏi giờ cao điểm",
                "Với cơ sở áp dụng biểu giá điện theo khung giờ, chênh lệch giữa giờ cao "
                "điểm và giờ thấp điểm tạo ra dư địa tiết kiệm rõ rệt. Hệ lưu trữ tích "
                "điện vào khung giờ giá thấp hoặc từ nguồn điện mặt trời áp mái, rồi "
                "cấp lại cho phụ tải trong khung giờ giá cao. Hiệu quả cụ thể phụ thuộc "
                "vào biểu đồ phụ tải và biểu giá đang áp dụng, nên cần khảo sát số liệu "
                "thực tế trước khi tính toán.",
            ),
            (
                "Giữ nguồn cho phụ tải quan trọng",
                "Ngoài bài toán chi phí, giá trị lớn của ESS công nghiệp nằm ở khả năng "
                "duy trì nguồn cho các phụ tải không được phép mất điện: hệ thống điều "
                "khiển, kho lạnh, thiết bị đo lường hay hạ tầng viễn thông. Với nhiều "
                "dây chuyền, một lần mất điện đột ngột không chỉ dừng sản xuất mà còn "
                "gây hỏng mẻ nguyên liệu đang xử lý, thiệt hại vượt xa phần điện năng "
                "bị gián đoạn.",
            ),
            (
                "An toàn và độ bền cho vận hành liên tục",
                "Toàn bộ dòng ESS của Hoa Huy dùng cell LiFePO4 ở điện áp chuẩn 51.2V — "
                "hóa học pin được đánh giá cao về độ ổn định nhiệt, phù hợp với hệ thống "
                "sạc/xả theo chu kỳ ngày trong thời gian dài. Hệ thống BMS giám sát điện "
                "áp, dòng và nhiệt độ, ngắt bảo vệ khi vượt ngưỡng — yếu tố quan trọng "
                "khi thiết bị đặt trong khu vực sản xuất có người làm việc.",
            ),
            (
                "Thuê thay vì mua",
                "Với doanh nghiệp chưa muốn ghi nhận một khoản đầu tư tài sản lớn, Hoa "
                "Huy có dịch vụ cho thuê pin lưu trữ công nghiệp. Phương án này phù hợp "
                "khi nhu cầu còn biến động theo mùa vụ, hoặc khi doanh nghiệp muốn đánh "
                "giá hiệu quả thực tế trên số liệu vận hành của chính mình trước khi "
                "quyết định đầu tư dài hạn.",
            ),
        ],
        "hashtags": ["#ESSCongNghiep", "#StackedESS", "#NhaMay", "#TietKiemDien"],
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
# "pin lithium xe máy điện" vẫn khớp với "pin lithium cho xe máy điện",
# và "OEM/ODM" khớp với "OEM ODM" — cách các công cụ SEO nhận diện biến thể cụm từ.
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
        # Khớp lần lượt các token còn lại trong phạm vi cửa sổ cho phép
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
                     hashtags: list[str]) -> dict:
    """Chấm điểm bài đăng theo các tiêu chí SEO cơ bản."""
    words = count_words(content)
    occurrences = keyword_occurrences(content, focus_keyword)
    density = round(occurrences / words * 100, 2) if words else 0.0

    first_chunk = content[:125]
    paragraphs = [p for p in content.split("\n\n") if p.strip()]
    sentences = [s for s in re.split(r"[.!?]\s", content) if s.strip()]
    avg_sentence_len = round(words / len(sentences), 1) if sentences else 0.0
    secondary_hits = [kw for kw in secondary if keyword_occurrences(content, kw)]

    checks = {
        "Độ dài thân bài >= 300 từ": words >= MIN_BODY_WORDS,
        "Từ khóa chính trong 125 ký tự đầu": keyword_occurrences(first_chunk, focus_keyword) > 0,
        "Mật độ từ khóa 0.5–3%": 0.5 <= density <= 3.0,
        "Có >= 2 từ khóa phụ (LSI)": len(secondary_hits) >= 2,
        "Có tiêu đề phụ phân đoạn": content.count("▸") >= 3,
        "Có CTA kèm thông tin liên hệ": "0904.789.969" in content,
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
                 history_file: Path | None = None):
        self.min_words = min_words
        self.history_file = history_file if history_file is not None else HISTORY_FILE

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

    # -- lắp ráp bài đăng --
    def _assemble(self, topic: dict, rng: random.Random) -> tuple[str, list[str], list[str]]:
        hook = rng.choice(topic["hooks"])
        intro = rng.choice(topic["intros"])

        sections = list(topic["sections"])
        rng.shuffle(sections)
        chosen = sections[:3]

        proof_title, proof_body = rng.choice(PROOF_BLOCKS)
        closing = rng.choice(topic["closings"])
        cta = rng.choice(CTA_BLOCKS)

        parts = [hook, "", intro]
        for title, body in chosen:
            parts += ["", f"▸ {title}", body]
        parts += ["", f"▸ {proof_title}", proof_body]

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
        content = "\n".join(parts) + "\n\n" + " ".join(hashtags)
        return content, hashtags, [t for t, _ in chosen]

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

        content = hashtags = section_titles = None
        topic = candidates[0]
        for attempt_topic in candidates:
            for _ in range(6):
                content, hashtags, section_titles = self._assemble(attempt_topic, rng)
                fp = f"{attempt_topic['id']}:{self._fingerprint(attempt_topic['id'], section_titles)}"
                if fp not in history:
                    topic = attempt_topic
                    history.append(fp)
                    self._save_history(history)
                    report = build_seo_report(
                        content, topic["focus_keyword"],
                        topic["secondary_keywords"], hashtags,
                    )
                    return SEOPost(
                        content=content,
                        topic_id=topic["id"],
                        focus_keyword=topic["focus_keyword"],
                        hashtags=hashtags,
                        image_query=topic["image_query"],
                        image_alt=topic["image_alt"],
                        seo_report=report,
                    )

        # Mọi tổ hợp đều đã dùng — chấp nhận lặp lại tổ hợp cũ nhất
        report = build_seo_report(
            content, topic["focus_keyword"], topic["secondary_keywords"], hashtags
        )
        return SEOPost(
            content=content,
            topic_id=topic["id"],
            focus_keyword=topic["focus_keyword"],
            hashtags=hashtags,
            image_query=topic["image_query"],
            image_alt=topic["image_alt"],
            seo_report=report,
        )


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
    day_number = now.toordinal()
    slot = 0 if now.hour < 10 else 1
    return day_number * 2 + slot


# --- CLI: xem thử và kiểm tra chất lượng ------------------------------------
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
    print(f"Điểm SEO     : {r['score']}")
    for name, ok in r["checks"].items():
        print(f"  [{'x' if ok else ' '}] {name}")


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
    parser = argparse.ArgumentParser(description="Bộ sinh nội dung chuẩn SEO Hoa Huy")
    parser.add_argument("--topic", help="ID chủ đề cụ thể (mặc định: tự chọn luân phiên)")
    parser.add_argument("--seed", type=int, help="Seed ngẫu nhiên để tái lập kết quả")
    parser.add_argument("--audit", type=int, metavar="N",
                        help="Sinh thử N bài và kiểm tra toàn bộ tiêu chí SEO")
    parser.add_argument("--list", action="store_true", help="Liệt kê các chủ đề")
    args = parser.parse_args()

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
