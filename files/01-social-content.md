---
name: social-content
description: >
  Viết caption Facebook (100-300 từ) và Instagram (80-150 từ) đúng tone
  brand pin lithium cao cấp. Sau khi viết xong caption, tự động gọi Skill
  "creative-designer" (File 2) để tạo ảnh minh họa tương ứng. Kích hoạt
  khi người dùng nói: "viết caption cho [sản phẩm]", "viết bài Facebook/
  Instagram cho [sản phẩm]", "tạo content mạng xã hội cho [sản phẩm]",
  hoặc bất kỳ yêu cầu nào kết hợp viết caption + sản phẩm pin lithium.
---

# Skill: Social Content (Facebook & Instagram Caption)

## Mục tiêu
Viết caption đăng mạng xã hội cho sản phẩm pin lithium cao cấp, đúng
giọng văn thương hiệu (brand voice), sau đó tự động điều phối sang
Skill 2 để tạo ảnh minh họa đi kèm.

## Input cần có
- `[sản-phẩm]`: tên/mã sản phẩm (bắt buộc)
- `[platform]`: `facebook`, `instagram`, hoặc `both` (mặc định: `both`)
- Ngữ cảnh brand: brand-guideline, customer-persona, product-catalog,
  marketing-channels (đọc trước khi viết nếu có sẵn trong dự án)

Nếu thiếu tên sản phẩm, hỏi lại người dùng trước khi viết. Các thông tin
khác (platform, loại ảnh minh họa) có thể tự suy luận theo mặc định bên
dưới nếu người dùng không nêu rõ.

## Nguyên tắc viết (Brand Voice — Pin lithium cao cấp)
- Giọng văn: chuyên nghiệp, đáng tin cậy, tự tin về công nghệ — không
  cường điệu, không dùng nhiều dấu chấm than hay emoji dày đặc.
- Nhấn mạnh công nghệ cell (LiFePO4/NMC), độ an toàn, tuổi thọ chu kỳ
  sạc/xả, và giá trị vận hành lâu dài, thay vì chỉ hô khẩu hiệu.
- Có thể lồng ghép bối cảnh chính sách (VD: chuyển đổi xe điện, Chỉ thị
  20/CT-TTg) khi phù hợp với chiến dịch, nhưng luôn bám sát thông tin
  thật từ marketing-channels.
- Ưu tiên câu ngắn, rõ ràng, dễ hiểu cho cả khách hàng kỹ thuật lẫn phổ
  thông.
- Call-to-action rõ ràng, hướng hành động (VD: "Liên hệ tư vấn giải
  pháp pin phù hợp", "Xem thông số kỹ thuật chi tiết tại..."), tránh
  thổi phồng công dụng.
- Không bịa thông số kỹ thuật (dung lượng, điện áp, số chu kỳ sạc...)
  hay tính năng không có trong product-catalog.

## Độ dài
| Nền tảng   | Số từ      | Ghi chú |
|------------|------------|---------|
| Facebook   | 100–300 từ | Có thể kể câu chuyện, mô tả ngữ cảnh sử dụng |
| Instagram  | 80–150 từ  | Súc tích, giàu hình ảnh, hashtag cuối bài |

## Quy trình
1. Đọc ngữ cảnh brand-guideline / customer-persona / product-catalog /
   marketing-channels nếu có trong dự án để bám đúng tone và thông số
   kỹ thuật sản phẩm pin.
2. Viết caption cho từng nền tảng được yêu cầu (đúng khung số từ ở trên).
3. Xác định loại ảnh minh họa phù hợp với nội dung caption, chọn 1 trong
   4 loại của Skill 2: `lifestyle`, `product-hero`, `detail-shot`,
   `human-touch`. Suy ra prompt mô tả ảnh bằng tiếng Anh từ nội dung
   caption.
4. Gọi Skill 2 (`02-creative-designer.md` → `creative-api.py`) với
   `[product]`, `[platform]` (fb/ig), và `[prompt]` tương ứng để tạo ảnh
   cho từng nền tảng đã viết caption.
5. Lưu kết quả (caption + đường dẫn ảnh) vào:
   `output/content/[YYYY-MM-DD]-[sản-phẩm].md`

## Định dạng file output
```markdown
# [Tên sản phẩm] — Content [YYYY-MM-DD]

## Facebook
[caption facebook]

Ảnh: output/images/[product]-fb-[YYYY-MM-DD]-01.png

## Instagram
[caption instagram]

Ảnh: output/images/[product]-ig-[YYYY-MM-DD]-01.png
```

## Không tự động thực hiện
- Không tự đăng bài lên Facebook/Instagram — skill này chỉ viết caption
  và tạo ảnh, việc đăng bài (nếu cần) thuộc skill riêng
  (`buffer-facebook-post` / `post-to-facebook`).
