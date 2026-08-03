# Hướng dẫn hệ thống nội dung chuẩn SEO — SVPsolar

Tài liệu này mô tả `content_generator.py` — bộ sinh nội dung dùng chung cho tất
cả script đăng bài trong repo. Nội dung hướng về lĩnh vực **điện mặt trời**.

## Bước 1 (bắt buộc): điền `brand_config.json`

Script đăng bài sẽ **từ chối chạy** cho tới khi ba trường bắt buộc được điền:

| Trường | Bắt buộc | Dùng ở đâu |
|---|---|---|
| `company_name` | ✅ | Tên công ty trong khối uy tín và CTA |
| `website` | ✅ | Dòng liên hệ cuối bài |
| `hotline` | ✅ | Dòng liên hệ cuối bài |
| `sales_contact`, `email`, `address` | | Bổ sung vào dòng liên hệ |
| `service_area` | | Mở khóa khối "Phạm vi thi công và hỗ trợ tại chỗ" |
| `years_experience` + `projects_completed` | | Mở khóa khối "Kinh nghiệm triển khai thực tế" |
| `warranty_years` | | Mở khóa khối "Bảo hành và đồng hành sau nghiệm thu" |
| `certifications` | | Mở khóa khối "Thiết bị và tiêu chuẩn áp dụng" |
| `partner_brands` | | Mở khóa khối "Thiết bị từ các hãng có bảo hành chính hãng" |

Trường tùy chọn để trống thì khối nội dung tương ứng **bị bỏ qua**, không có giá
trị mặc định tự chế. Đây là chủ ý: thà bài ngắn hơn một đoạn còn hơn đăng thông
tin không đúng sự thật.

Kiểm tra sau khi điền:

```bash
python content_generator.py --check-brand
```

## Nguyên tắc không bịa số liệu

Đây là ràng buộc thiết kế quan trọng nhất của hệ thống:

- **Phần thân bài không chứa bất kỳ khẳng định riêng nào về công ty.** Toàn bộ
  là kiến thức kỹ thuật điện mặt trời mang tính phổ quát (inverter làm gì, bóng
  che ảnh hưởng ra sao, hai loại bảo hành tấm pin khác nhau thế nào...).
- **Mọi thông tin thương hiệu chỉ đến từ `brand_config.json`** — không hard-code
  ở bất kỳ đâu trong code.
- **Không có con số tiết kiệm, hoàn vốn hay sản lượng cụ thể.** Những con số này
  phụ thuộc bức xạ khu vực, hướng mái và mức tiêu thụ, nên nội dung luôn dẫn về
  "cần khảo sát thực tế" thay vì đưa ra một tỷ lệ chung.

Ràng buộc thứ ba là để tránh lặp lại lỗi của phiên bản nội dung cũ, vốn khẳng
định "giảm 70-80% chi phí điện" và "PERC hiệu suất 22%" mà không có căn cứ.

## Cách hoạt động

Mỗi bài được lắp ráp từ các khối:

```
Hook (chứa từ khóa chính trong ~125 ký tự đầu)
Mở bài
▸ Phần thân 1   ┐
▸ Phần thân 2   ├─ chọn ngẫu nhiên 3 trong 5 phần của chủ đề
▸ Phần thân 3   ┘
▸ Khối uy tín   ── chọn trong số khối mà brand_config đã đủ dữ liệu
Phần kết        ── luôn xuất hiện, mang từ khóa chính + từ khóa phụ
CTA + liên hệ   ── dựng từ brand_config
Hashtag
```

Kết quả thực tế: **474–579 từ/bài**, tất cả đạt 9/9 tiêu chí SEO.

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
cho phép có từ chen giữa. Nhờ vậy "điện mặt trời áp mái" vẫn khớp với "điện mặt
trời cho áp mái", và "on-grid" khớp với "on grid" — giống cách các công cụ SEO
nhận diện biến thể cụm từ.

## 12 chủ đề

| ID chủ đề | Từ khóa chính |
|---|---|
| `dien-mat-troi-ap-mai` | điện mặt trời áp mái |
| `dien-mat-troi-doanh-nghiep` | điện mặt trời cho doanh nghiệp |
| `he-thong-hybrid` | hệ thống điện mặt trời hybrid |
| `chon-tam-pin` | tấm pin năng lượng mặt trời |
| `chon-inverter` | inverter điện mặt trời |
| `pin-luu-tru-solar` | pin lưu trữ điện mặt trời |
| `bai-toan-hoan-von` | chi phí lắp điện mặt trời |
| `khao-sat-thiet-ke` | khảo sát thiết kế hệ thống điện mặt trời |
| `thi-cong-an-toan` | thi công lắp đặt điện mặt trời |
| `bao-tri-van-hanh` | bảo trì hệ thống điện mặt trời |
| `on-grid-off-grid` | hệ thống hòa lưới on-grid |
| `giam-sat-hieu-suat` | giám sát hệ thống điện mặt trời |

## Chống trùng nội dung

Hai lớp bảo vệ:

- **Có lịch sử** (chạy trên máy/server giữ được file): `output/post_history.json`
  lưu 40 tổ hợp gần nhất, tránh lặp cả chủ đề lẫn tổ hợp phần thân.
- **Không có lịch sử** (GitHub Actions dùng runner mới mỗi lần chạy):
  `daily_rotation_index()` xoay chủ đề theo ngày và ca đăng. Với 12 chủ đề và 2
  ca/ngày, một chủ đề chỉ quay lại sau 6 ngày, và khi quay lại thì tổ hợp phần
  thân cũng khác.

## Ảnh minh họa và alt text

Ảnh lấy từ Unsplash theo từ khóa riêng của từng chủ đề (`image_query`), nên bài
về inverter sẽ lấy ảnh inverter chứ không phải ảnh tấm pin chung chung.

Mỗi chủ đề có sẵn `image_alt` chuẩn SEO, được gửi kèm lên Zernio qua trường
`mediaItems[].altText`. Do tài liệu Zernio không truy cập được để xác nhận
trường này có được chấp nhận khi tạo bài hay không, script gửi kèm `altText`
trước; nếu API trả về 400 hoặc 422, nó tự gửi lại không kèm alt text thay vì bỏ
luôn bài. Log sẽ ghi rõ trường hợp nào đã xảy ra.

## Lệnh sử dụng

```bash
# Kiểm tra cấu hình thương hiệu
python content_generator.py --check-brand

# Xem thử một bài + báo cáo SEO
python content_generator.py

# Xem thử một chủ đề cụ thể (tái lập được nhờ seed)
python content_generator.py --topic chon-inverter --seed 7

# Liệt kê toàn bộ chủ đề
python content_generator.py --list

# Kiểm tra chất lượng: sinh thử 100 bài, kiểm tra đủ 9 tiêu chí
python content_generator.py --audit 100
```

`--audit` trả về exit code 1 nếu có bài không đạt, nên có thể đưa vào CI.

## Nguyên tắc khi thêm chủ đề mới

1. **Phần thân phải trung tính về thương hiệu** — chỉ kiến thức kỹ thuật phổ
   quát. Mọi khẳng định về công ty phải đi qua `brand_config.json`.
2. **Không đưa số liệu tiết kiệm/hoàn vốn/sản lượng cụ thể.**
3. Mỗi chủ đề cần **tối thiểu 5 phần thân** để tổ hợp đủ đa dạng.
4. **Phần kết bắt buộc chứa từ khóa chính và >= 2 từ khóa phụ**, vì đây là khối
   luôn được render. Hook và mở bài cũng nên chứa từ khóa chính — với cụm từ
   khóa dài (5-6 từ), cần đủ 3 lần xuất hiện mới đạt ngưỡng mật độ 0.5%.
5. Chạy `--audit` sau khi thêm để xác nhận không phá vỡ tiêu chí nào.
