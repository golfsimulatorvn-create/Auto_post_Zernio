# 🚀 GitHub Actions - Quick Start (5 Phút)

Cách cài đặt GitHub Actions để chạy Auto Poster tự động.

---

## 1️⃣ Đẩy Code lên GitHub

```bash
git init
git remote add origin https://github.com/your-username/hoa-huy-auto-poster.git
git branch -M main
git add .
git commit -m "Initial commit: SVPsolar Auto Poster"
git push -u origin main
```

---

## 2️⃣ Thêm Secrets (3 bước)

### Bước A: Vào Settings
- GitHub → Repository → **Settings**

### Bước B: Vào Secrets
- Left sidebar → **Secrets and variables** → **Actions**

### Bước C: Thêm 3 Secrets

**Secret 1: ZERNIO_API_KEY**
```
Name: ZERNIO_API_KEY
Secret: sk_live_your_key_here
```

**Secret 2: FACEBOOK_ACCOUNT_ID**
```
Name: FACEBOOK_ACCOUNT_ID
Secret: 123456789
```

**Secret 3: UNSPLASH_ACCESS_KEY** (optional)
```
Name: UNSPLASH_ACCESS_KEY
Secret: your_unsplash_key_here
```

---

## 3️⃣ Test (1 phút)

1. **Repository → Actions tab**
2. **Chọn:** "🌞 SVPsolar Auto Facebook Poster"
3. **Nhấp:** "Run workflow" → "Run workflow"
4. **Chờ:** 2-3 phút để chạy xong

✅ **Done!** Nếu không có lỗi đỏ, workflow hoạt động!

---

## 4️⃣ Hoàn Thành ✨

GitHub sẽ **tự động chạy** vào:
- **7 AM UTC+7** (7:00 sáng Việt Nam)
- **8 PM UTC+7** (8:00 tối Việt Nam)

---

## 📝 Lấy API Keys

### Zernio API Key
1. https://zernio.com/dashboard
2. **Settings** → **API Keys**
3. Sao chép key

### Facebook Account ID
1. Zernio Dashboard
2. **Connected Accounts**
3. Sao chép Account ID

### Unsplash Key (Optional)
1. https://unsplash.com/developers
2. Tạo app
3. Sao chép Access Key

---

## ❓ FAQ

**Q: Có chạy được nếu tôi không online?**
A: ✅ Có, chạy 24/7 trên GitHub servers

**Q: Có mất tiền không?**
A: ✅ Không, miễn phí 2,000 phút/tháng

**Q: Mất bao lâu để chạy?**
A: ~1-2 phút mỗi lần

**Q: Muốn xem logs?**
A: Actions → Chọn Run → Xem chi tiết

---

## 🔐 An Toàn?

✅ API keys được mã hóa  
✅ Không hiển thị trong logs  
✅ Thêm `.gitignore` để không commit

---

## 🎉 Xong!

Workflow sẽ chạy tự động theo lịch.

Kiểm tra **Actions tab** để xem logs mỗi lần chạy.

**Happy Automating! 🚀**

---

Xem `GITHUB_ACTIONS_SETUP.md` để có hướng dẫn chi tiết hơn.
