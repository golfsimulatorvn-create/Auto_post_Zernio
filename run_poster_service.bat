@echo off
REM ============================================
REM Hoa Huy Green Energy - Auto Poster Service
REM Chạy Facebook Auto Poster 24/7
REM ============================================

setlocal enabledelayedexpansion

REM Get script directory
cd /d "%~dp0"

REM Colors and formatting
color 0A

echo.
echo ============================================
echo 🌞 Hoa Huy Green Energy
echo    Auto Facebook Poster Service
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Lỗi: Python chưa được cài đặt hoặc không được thêm vào PATH
    echo.
    echo Vui lòng:
    echo 1. Cài đặt Python từ https://www.python.org
    echo 2. Đảm bảo chọn "Add Python to PATH" khi cài đặt
    echo.
    pause
    exit /b 1
)

echo ✅ Python được tìm thấy
python --version
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ❌ Lỗi: File .env không tồn tại
    echo.
    echo Vui lòng:
    echo 1. Sao chép .env.example thành .env
    echo 2. Điền Zernio API Key và Facebook Account ID vào .env
    echo.
    pause
    exit /b 1
)

echo ✅ File .env được tìm thấy
echo.

REM Check if requirements are installed
echo 📦 Kiểm tra các thư viện cần thiết...
pip show schedule >nul 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Cài đặt các thư viện cần thiết...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Lỗi khi cài đặt thư viện
        pause
        exit /b 1
    )
    echo ✅ Cài đặt thư viện thành công
) else (
    echo ✅ Các thư viện đã được cài đặt
)

echo.
echo ============================================
echo 🚀 Bắt đầu chạy Auto Poster Service
echo ============================================
echo.
echo ⏰ Thời gian lên lịch:
echo    - 7:00 AM: Đăng bài với hình ảnh
echo    - 8:00 PM: Đăng bài mà không hình ảnh
echo.
echo 📝 Logs sẽ được lưu vào: auto_post.log
echo.
echo ⚠️  Nhấn Ctrl+C để dừng chương trình
echo.

REM Run the advanced poster
python facebook_auto_post_advanced.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Lỗi khi chạy chương trình
    echo Kiểm tra file auto_post.log để xem chi tiết
    pause
    exit /b 1
)

pause
