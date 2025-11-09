@echo off
REM ============================================================
REM SCRIPT MO STARTUP FOLDER NHANH
REM Quick Open Startup Folder
REM KHONG DAU TIENG VIET DE TRANH LOI ENCODING!
REM ============================================================

echo ========================================
echo   MO STARTUP FOLDER
echo   Open Startup Folder
echo ========================================
echo.

echo Chon Startup folder ban muon mo:
echo.
echo 1. User Startup (chi cho user hien tai)
echo 2. System Startup (cho tat ca users - can Admin)
echo 3. Mo ca 2
echo 4. Hien thi danh sach app trong Startup
echo 5. Thoat
echo.
choice /c 12345 /m "Chon so (1-5)"

if errorlevel 5 goto :end
if errorlevel 4 goto :list_apps
if errorlevel 3 goto :open_both
if errorlevel 2 goto :open_system
if errorlevel 1 goto :open_user

:open_user
echo.
echo Mo User Startup folder...
explorer shell:startup
echo.
echo [OK] Da mo User Startup folder!
echo Duong dan: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
echo.
pause
exit /b 0

:open_system
echo.
echo Mo System Startup folder...
explorer shell:common startup
echo.
echo [OK] Da mo System Startup folder!
echo Duong dan: C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
echo.
pause
exit /b 0

:open_both
echo.
echo Mo ca 2 Startup folders...
start explorer shell:startup
timeout /t 1 /nobreak >nul
start explorer shell:common startup
echo.
echo [OK] Da mo ca 2 Startup folders!
echo.
pause
exit /b 0

:list_apps
echo.
echo ========================================
echo   DANH SACH APP TRONG STARTUP
echo ========================================
echo.

echo [USER STARTUP]:
echo Duong dan: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
echo.
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\*.*" (
    dir /b "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
) else (
    echo (Trong - No apps)
)
echo.

echo [SYSTEM STARTUP]:
echo Duong dan: C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
echo.
if exist "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\*.*" (
    dir /b "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
) else (
    echo (Trong - No apps)
)
echo.

echo ========================================
echo.
pause
exit /b 0

:end
exit /b 0
