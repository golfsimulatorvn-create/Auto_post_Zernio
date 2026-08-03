@echo off
REM ============================================
REM SVPsolar Auto Poster - Service Manager
REM Quản lý dịch vụ Windows
REM ============================================

setlocal enabledelayedexpansion
color 0A

:menu
cls
echo.
echo ============================================
echo 🌞 SVPsolar Auto Poster - Service Manager
echo ============================================
echo.
echo Chọn thao tác:
echo   1. Xem trạng thái dịch vụ
echo   2. Khởi động dịch vụ
echo   3. Dừng dịch vụ
echo   4. Khởi động lại dịch vụ
echo   5. Xem logs
echo   6. Xóa dịch vụ
echo   0. Thoát
echo.
set /p choice="Nhập lựa chọn (0-6): "

if "%choice%"=="1" goto status
if "%choice%"=="2" goto start_service
if "%choice%"=="3" goto stop_service
if "%choice%"=="4" goto restart_service
if "%choice%"=="5" goto view_logs
if "%choice%"=="6" goto remove_service
if "%choice%"=="0" goto exit_script
goto menu

:status
cls
echo.
echo ============================================
echo 📋 Trạng thái dịch vụ
echo ============================================
echo.
sc query SVPsolarAutoPost
echo.
pause
goto menu

:start_service
cls
echo.
echo ============================================
echo ▶️  Khởi động dịch vụ
echo ============================================
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Lỗi: Cần chạy dưới quyền Administrator
    echo Vui lòng nhấp chuột phải vào script và chọn "Run as administrator"
    pause
    goto menu
)

sc query SVPsolarAutoPost >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dịch vụ không tồn tại
    echo Vui lòng chạy install_windows_service.bat trước
    pause
    goto menu
)

net start SVPsolarAutoPost
if %errorlevel% equ 0 (
    echo ✅ Dịch vụ đã khởi động thành công
) else (
    echo ❌ Lỗi khi khởi động dịch vụ
)
echo.
pause
goto menu

:stop_service
cls
echo.
echo ============================================
echo ⏹️  Dừng dịch vụ
echo ============================================
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Lỗi: Cần chạy dưới quyền Administrator
    pause
    goto menu
)

sc query SVPsolarAutoPost >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dịch vụ không tồn tại
    pause
    goto menu
)

net stop SVPsolarAutoPost
if %errorlevel% equ 0 (
    echo ✅ Dịch vụ đã dừng thành công
) else (
    echo ❌ Lỗi khi dừng dịch vụ
)
echo.
pause
goto menu

:restart_service
cls
echo.
echo ============================================
echo 🔄 Khởi động lại dịch vụ
echo ============================================
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Lỗi: Cần chạy dưới quyền Administrator
    pause
    goto menu
)

sc query SVPsolarAutoPost >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dịch vụ không tồn tại
    pause
    goto menu
)

echo ⏹️  Đang dừng dịch vụ...
net stop SVPsolarAutoPost
timeout /t 2 /nobreak

echo ▶️  Đang khởi động dịch vụ...
net start SVPsolarAutoPost

if %errorlevel% equ 0 (
    echo ✅ Dịch vụ đã khởi động lại thành công
) else (
    echo ❌ Lỗi khi khởi động lại dịch vụ
)
echo.
pause
goto menu

:view_logs
cls
echo.
echo ============================================
echo 📝 Logs (50 dòng cuối cùng)
echo ============================================
echo.

cd /d "%~dp0"

if exist "auto_post.log" (
    echo --- auto_post.log ---
    powershell -Command "Get-Content 'auto_post.log' -Tail 50"
    echo.
) else (
    echo ⚠️  Chưa có file auto_post.log
    echo.
)

pause
goto menu

:remove_service
cls
echo.
echo ============================================
echo 🗑️  Xóa dịch vụ
echo ============================================
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Lỗi: Cần chạy dưới quyền Administrator
    pause
    goto menu
)

set /p confirm="⚠️  Bạn chắc chắn muốn xóa dịch vụ SVPsolarAutoPost? (Y/N): "
if /i "%confirm%"=="Y" (
    echo ⏹️  Đang dừng dịch vụ...
    net stop SVPsolarAutoPost >nul 2>&1
    timeout /t 2 /nobreak

    REM Find NSSM
    for /r "nssm" %%F in (nssm.exe) do (
        set "NSSM_PATH=%%F"
        goto found_nssm_remove
    )

    :found_nssm_remove
    if defined NSSM_PATH (
        "!NSSM_PATH!" remove SVPsolarAutoPost confirm
    ) else (
        sc delete SVPsolarAutoPost
    )

    if %errorlevel% equ 0 (
        echo ✅ Dịch vụ đã xóa thành công
    ) else (
        echo ❌ Lỗi khi xóa dịch vụ
    )
) else (
    echo ⏸️  Hủy xóa dịch vụ
)
echo.
pause
goto menu

:exit_script
exit /b 0
