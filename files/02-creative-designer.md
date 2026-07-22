---
name: creative-designer
description: >
  Tạo ảnh sản phẩm pin lithium cao cấp bằng Gemini API — model
  `gemini-3.1-flash-image` (Nano Banana 2). Hỗ trợ 4 loại ảnh: Lifestyle,
  Product Hero, Detail Shot, Human Touch. Chạy qua skills/creative-api.py.
  Có thể gọi độc lập ("tạo ảnh sản phẩm cho [product]", "làm ảnh
  lifestyle cho [product]") hoặc được Skill 1 (social-content) gọi tự
  động sau khi viết caption.
---

# Skill: Creative Designer (Gemini Image Generation)

## Mục tiêu
Sinh ảnh sản phẩm chất lượng cao từ ảnh gốc sản phẩm (pin lithium/
LiFePO4, xe điện, thiết bị lưu trữ năng lượng...), dùng Gemini API
(model `gemini-3.1-flash-image`, tên thân quen "Nano Banana"), phục vụ
nội dung Facebook/Instagram.

## 4 loại ảnh hỗ trợ

| Loại | Mô tả | Khi dùng |
|------|-------|----------|
| `lifestyle` | Sản phẩm đặt trong bối cảnh sử dụng thực tế (xe điện đang sạc, hệ thống lưu trữ năng lượng mặt trời tại nhà/xưởng...) | Bài đăng kể câu chuyện ứng dụng thực tế |
| `product-hero` | Ảnh pin/sản phẩm làm chủ thể chính, nền sạch, ánh sáng studio, làm nổi bật thiết kế và logo | Giới thiệu sản phẩm mới, ảnh đại diện bài viết |
| `detail-shot` | Cận cảnh cell pin, mạch BMS, cổng kết nối, tem thông số kỹ thuật | Nhấn mạnh chất lượng, độ an toàn, công nghệ chế tạo |
| `human-touch` | Có người tương tác với sản phẩm (kỹ thuật viên lắp đặt, khách hàng sử dụng xe điện...) | Truyền tải độ tin cậy và trải nghiệm sử dụng thực tế |

## Input cần có
- `[product]`: tên/mã sản phẩm — dùng để tìm ảnh gốc trong thư mục
  `Products/[product]/` (VD: `Products/HHXM6025A2/`)
- `[platform]`: `fb` hoặc `ig` (ảnh hưởng khung hình/tỉ lệ mô tả trong
  prompt)
- `[prompt]`: mô tả tiếng Anh cho ảnh cần tạo, nên nêu rõ loại ảnh
  (lifestyle/product-hero/detail-shot/human-touch) và bối cảnh mong muốn
- `[filename]` (tùy chọn): tên file ảnh cụ thể trong thư mục
  `Products/[product]/` — dùng khi thư mục có nhiều ảnh và cần chỉ rõ
  ảnh nào, hoặc khi phát hiện ảnh không khớp mã sản phẩm (xem lưu ý bên
  dưới)

Nếu không có sẵn prompt, xây dựng prompt theo mẫu:
```
"[loại ảnh] photo of [product], [bối cảnh/ánh sáng mong muốn],
premium lithium battery, clean tech aesthetic, photorealistic, 4k"
```

## Quy trình
1. Kiểm tra thư mục `Products/[product]/` tồn tại và có ít nhất 1 ảnh
   hợp lệ (`.jpg`/`.jpeg`/`.png`, loại trừ file có chữ "Drawing" — bản vẽ
   kỹ thuật — và file video). Nếu không có, báo lỗi và dừng lại — không
   tự bịa ảnh gốc.
2. Nếu thư mục có nhiều ảnh, mặc định dùng ảnh đầu tiên theo thứ tự tên
   file — **nhưng phải đọc thử (Read tool) ít nhất 1 ảnh để xác nhận tem
   thông số trên ảnh đúng là mã sản phẩm `[product]` đang cần**, vì thực
   tế đã từng có ảnh của SKU khác bị để nhầm thư mục. Nếu ảnh mặc định
   không khớp, chọn ảnh khác bằng cách truyền `[filename]` cụ thể.
3. Gọi `skills/creative-api.py` với 3-4 tham số:
   ```bash
   python3 skills/creative-api.py "[product]" "[platform]" "[prompt]" ["[filename]"]
   ```
4. Script tự động:
   - Đọc ảnh gốc trong `Products/[product]/`, mã hóa base64 (không cần
     upload lên dịch vụ trung gian — Gemini nhận ảnh input trực tiếp).
   - Gọi Gemini API (`gemini-3.1-flash-image`) qua endpoint
     `POST https://generativelanguage.googleapis.com/v1beta/interactions`
     để sinh ảnh mới từ ảnh gốc + prompt.
   - Tải ảnh kết quả (base64 trong response) về
     `output/images/[product]-[fb|ig]-[YYYY-MM-DD]-01.png`.
5. Trả lại đường dẫn ảnh đã tạo cho Skill 1 (nếu được gọi từ Skill 1) để
   chèn vào file content markdown.

## Yêu cầu môi trường
- File `.env` ở thư mục gốc dự án chứa:
  ```
  GEMINI_API_KEY=...
  ```
  (Lấy API key tại Google AI Studio — https://aistudio.google.com/apikey)
- Ảnh gốc sản phẩm đặt sẵn tại `Products/[product]/` (có thể chứa nhiều
  file — ảnh chụp thật, bản vẽ kỹ thuật, video — script tự lọc bản vẽ/
  video, chỉ lấy ảnh chụp thật).

## Gọi độc lập
Có thể gọi thẳng skill này mà không qua Skill 1, ví dụ: "làm ảnh
detail-shot cho pin LiFePO4 100Ah" → xác định `product=pin-lifepo4-100ah`,
`platform` mặc định `fb` nếu không nêu rõ, tự soạn prompt theo mẫu ở
trên rồi chạy `creative-api.py`.
