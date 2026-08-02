# Hướng dẫn hệ thống nội dung chuẩn SEO

Tài liệu này mô tả `content_generator.py` — bộ sinh nội dung dùng chung cho tất
cả script đăng bài trong repo.

## Vấn đề trước đây

Nội dung cũ được ghép từ template ngắn:

```
💡 Kiến thức về {topic}:
{detail}          ← 2-3 câu
{hashtags}        ← 5 hashtag lấy ngẫu nhiên
```

Kết quả: **~56 từ/bài**, và có một số vấn đề khác:

| Vấn đề | Chi tiết |
|---|---|
| Quá ngắn | 56 từ, không đủ để xếp hạng hay giữ chân người đọc |
| Không có cấu trúc SEO | Không có từ khóa chính, không tiêu đề phụ, không CTA |
| Sai định vị thương hiệu | Chủ đề xoay quanh tấm pin mặt trời/inverter, trong khi Hoa Huy sản xuất **pin lithium LiFePO4** cho EV và ESS |
| Thông số bịa | "PERC hiệu suất 22%", "giảm 70-80% chi phí điện" — không có trong `product-catalog.md` |
| Sai tone | Emoji dày đặc, trái với `brand-guideline.md` |
| Dễ trùng lặp | 10 chủ đề chọn ngẫu nhiên, không có cơ chế chống lặp |
| Trùng code | Khối nội dung bị copy-paste ở 3 script |

## Cách hoạt động

Mỗi bài được lắp ráp từ các khối:

```
Hook (chứa từ khóa chính trong ~125 ký tự đầu)
Mở bài
▸ Phần thân 1   ┐
▸ Phần thân 2   ├─ chọn ngẫu nhiên 3 trong 5 phần của chủ đề
▸ Phần thân 3   ┘
▸ Khối E-E-A-T  ── nhà máy / chứng nhận / kiểm soát chất lượng
Phần kết        ── luôn xuất hiện, mang từ khóa chính + từ khóa phụ
CTA + liên hệ
Hashtag
```

Kết quả thực tế: **498–596 từ/bài**, tất cả đạt 9/9 tiêu chí SEO.

Phần kết luôn được render, nên dù tổ hợp phần thân nào được chọn thì từ khóa
chính và các từ khóa phụ (LSI) vẫn luôn có mặt.

## 9 tiêu chí SEO được kiểm tra tự động

1. Độ dài thân bài >= 300 từ (không tính hashtag)
2. Từ khóa chính trong 125 ký tự đầu
3. Mật độ từ khóa 0.5–3%
4. Có >= 2 từ khóa phụ (LSI)
5. Có tiêu đề phụ phân đoạn
6. Có CTA kèm thông tin liên hệ
7. Số hashtag trong khoảng 5–10
8. Đoạn văn dễ đọc (>= 6 đoạn)
9. Câu trung bình <= 35 từ

Việc nhận diện từ khóa dùng so khớp theo token, bỏ dấu và bỏ ký tự phân cách,
cho phép có từ chen giữa. Nhờ vậy "pin lithium xe máy điện" vẫn khớp với
"pin lithium cho xe máy điện", và "OEM/ODM" khớp với "OEM ODM" — giống cách các
công cụ SEO nhận diện biến thể cụm từ.

## 12 chủ đề

Tất cả bám đúng sản phẩm thật của Hoa Huy:

| ID chủ đề | Từ khóa chính |
|---|---|
| `pin-xe-may-dien` | pin lithium xe máy điện |
| `ess-ho-gia-dinh` | hệ thống lưu trữ năng lượng ESS |
| `lifepo4-vs-chi-axit` | pin LiFePO4 |
| `pin-xe-golf` | pin xe golf lithium |
| `pin-xe-nang-agv` | pin xe nâng lithium |
| `oem-odm-pin-lithium` | gia công pin lithium OEM ODM |
| `an-toan-pin-lithium` | an toàn pin lithium |
| `sac-du-phong-tram-sac` | sạc dự phòng LiFePO4 |
| `battery-swapping` | trạm đổi pin xe điện |
| `chuyen-doi-xe-dien-doanh-nghiep` | chuyển đổi sang xe điện |
| `bms-quan-ly-pin` | hệ thống quản lý pin BMS |
| `ess-cong-nghiep` | lưu trữ năng lượng công nghiệp |

## Chống trùng nội dung

Hai lớp bảo vệ:

- **Có lịch sử** (chạy trên máy/server giữ được file): `output/post_history.json`
  lưu 40 tổ hợp gần nhất, tránh lặp cả chủ đề lẫn tổ hợp phần thân.
- **Không có lịch sử** (GitHub Actions dùng runner mới mỗi lần chạy):
  `daily_rotation_index()` xoay chủ đề theo ngày và ca đăng. Với 12 chủ đề và 2
  ca/ngày, một chủ đề chỉ quay lại sau 6 ngày, và khi quay lại thì tổ hợp phần
  thân cũng khác.

## Lệnh sử dụng

```bash
# Xem thử một bài + báo cáo SEO
python content_generator.py

# Xem thử một chủ đề cụ thể (tái lập được nhờ seed)
python content_generator.py --topic pin-xe-golf --seed 7

# Liệt kê toàn bộ chủ đề
python content_generator.py --list

# Kiểm tra chất lượng: sinh thử 100 bài, kiểm tra đủ 9 tiêu chí
python content_generator.py --audit 100
```

`--audit` trả về exit code 1 nếu có bài không đạt, nên có thể đưa vào CI.

## Nguyên tắc khi thêm chủ đề mới

1. **Chỉ dùng số liệu đã công bố** trong `product-catalog.md`. Các trường ghi
   "chưa công bố" (số chu kỳ sạc, giá, kích thước của phần lớn dòng sản phẩm)
   thì không được suy diễn hay bịa ra.
2. **Bám tone** trong `brand-guideline.md`: kỹ thuật, đáng tin cậy, hạn chế
   emoji, không dùng tính từ sáo rỗng.
3. Mỗi chủ đề cần **tối thiểu 5 phần thân** để tổ hợp đủ đa dạng.
4. **Phần kết bắt buộc chứa từ khóa chính và >= 2 từ khóa phụ**, vì đây là khối
   luôn được render.
5. Chạy `--audit` sau khi thêm để xác nhận không phá vỡ tiêu chí nào.

## Điểm còn tồn đọng

- **Ảnh minh họa**: Unsplash chỉ trả ảnh stock chung chung, không phải sản phẩm
  Hoa Huy. Ảnh thật trong `Products/` là lựa chọn tốt hơn cho uy tín thương hiệu.
- **Alt text ảnh**: mỗi chủ đề đã có sẵn `image_alt` chuẩn SEO, hiện được ghi
  vào file lưu trong `output/content/` và log. Chưa gửi kèm lên Zernio vì chưa
  xác nhận được tên trường trong API của Zernio — cần đối chiếu tài liệu Zernio
  trước khi thêm vào payload để tránh làm hỏng luồng đăng bài đang chạy.
