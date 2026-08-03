@echo off
REM ============================================
REM SVPsolar Auto Poster - Windows Service Setup
REM Cài đặt dịch vụ Windows chạy 24/7
REM ============================================

setlocal enabledelayedexpansion
cd /d "%~dp0"
color 0A

echo.
echo ============================================
echo 🌞 SVPsolar
echo    Windows Service Installer
echo ============================================
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Lỗi: Chương trình cần chạy dưới quyền Administrator
    echo.
    echo Vui lòng:
    echo 1. Nhấp chuột phải vào file này
    echo 2. Chọn "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ✅ Chương trình chạy dưới quyền Administrator
echo.

REM Check if NSSM is installed
where nssm >nul 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Đang tải NSSM (Non-Sucking Service Manager)...
    echo.

    if not exist "nssm" mkdir nssm

    REM Download NSSM
    cd nssm
    powershell -Command "(New-Object System.Net.ServicePointManager).SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://nssm.cc/ci/nssm-2.24-101-g897c7f7.zip' -OutFile 'nssm.zip'"

    if %errorlevel% neq 0 (
        echo ❌ Lỗi khi tải NSSM
        echo.
        echo Cách khác:
        echo 1. Tải NSSM từ https://nssm.cc/download
        echo 2. Giải nén vào thư mục này
        echo 3. Chạy lại script này
        echo.
        pause
        exit /b 1
    )

    echo ✅ Giải nén NSSM...
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.'"

    cd ..
)

REM Find NSSM executable
for /r "nssm" %%F in (nssm.exe) do (
    set "NSSM_PATH=%%F"
    goto found_nssm
)

:found_nssm
if not defined NSSM_PATH (
    echo ❌ Không tìm thấy NSSM executable
    pause
    exit /b 1
)

echo ✅ NSSM được tìm thấy: !NSSM_PATH!
echo.

REM Get Python path
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i

echo ✅ Python được tìm thấy: !PYTHON_PATH!
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%facebook_auto_post_advanced.py

echo 📝 Cấu hình dịch vụ:
echo    - Tên dịch vụ: SVPsolarAutoPost
echo    - Python: !PYTHON_PATH!
echo    - Script: !SCRIPT_PATH!
echo    - Thư mục: %SCRIPT_DIR%
echo.

REM Check if service already exists
echo ⏳ Kiểm tra dịch vụ hiện có...
sc query SVPsolarAutoPost >nul 2>&1
if %errorlevel% equ 0 (
    echo ⏳ Dịch vụ SVPsolarAutoPost đã tồn tại, đang xóa...
    net stop SVPsolarAutoPost >nul 2>&1
    "!NSSM_PATH!" remove SVPsolarAutoPost confirm
    timeout /t 2 /nobreak
)

echo ✅ Tạo dịch vụ Windows mới...
"!NSSM_PATH!" install SVPsolarAutoPost "!PYTHON_PATH!" "!SCRIPT_PATH!"

if %errorlevel% neq 0 (
    echo ❌ Lỗi khi tạo dịch vụ
    pause
    exit /b 1
)

echo ✅ Dịch vụ được tạo thành công
echo.

REM Set service properties
echo ⏳ Cấu hình dịch vụ...
"!NSSM_PATH!" set SVPsolarAutoPost AppDirectory "%SCRIPT_DIR%"
"!NSSM_PATH!" set SVPsolarAutoPost AppStdout "%SCRIPT_DIR%auto_post_stdout.log"
"!NSSM_PATH!" set SVPsolarAutoPost AppStderr "%SCRIPT_DIR%auto_post_stderr.log"
"!NSSM_PATH!" set SVPsolarAutoPost AppRotateFiles 1
"!NSSM_PATH!" set SVPsolarAutoPost AppRotateOnline 1
"!NSSM_PATH!" set SVPsolarAutoPost AppRotateSeconds 86400

echo ✅ Cấu hình hoàn tất
echo.

REM Start service
echo ⏳ Khởi động dịch vụ...
net start SVPsolarAutoPost

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo ✅ Cài đặt thành công!
    echo ============================================
    echo.
    echo 📋 Thông tin dịch vụ:
    echo    - Tên: SVPsolarAutoPost
    echo    - Trạng thái: Running
    echo    - Khởi động tự động: Có
    echo.
    echo 📁 Logs:
    echo    - Stdout: auto_post_stdout.log
    echo    - Stderr: auto_post_stderr.log
    echo    - App: auto_post.log
    echo.
    echo 🔧 Lệnh quản lý:
    echo    - Xem trạng thái: sc query SVPsolarAutoPost
    echo    - Dừng: net stop SVPsolarAutoPost
    echo    - Khởi động: net start SVPsolarAutoPost
    echo    - Xóa: "!NSSM_PATH!" remove SVPsolarAutoPost confirm
    echo.
    echo ✅ Dịch vụ sẽ chạy 24/7 trên background
    echo    Để xem logs, mở auto_post.log
    echo.
) else (
    echo.
    echo ❌ Lỗi khi khởi động dịch vụ
    echo Kiểm tra lại cấu hình trong file .env
    echo.
)

pause
