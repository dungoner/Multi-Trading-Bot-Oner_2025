@echo off
REM ============================================================
REM VPS TOOLS - TICH HOP 3 CHUC NANG
REM 1. Quan ly Startup Folder
REM 2. Them App vao Startup
REM 3. Chinh Timezone
REM ============================================================

:main_menu
cls
echo ========================================
echo   VPS TOOLS - TICH HOP 3 CHUC NANG
echo ========================================
echo.
echo 1. QUAN LY STARTUP FOLDER
echo    - Mo folder, xem danh sach apps
echo.
echo 2. THEM APP VAO STARTUP
echo    - Tu dong tao shortcut va them vao Startup
echo.
echo 3. CHINH TIMEZONE
echo    - Doi timezone VPS cho trading
echo.
echo 4. Thoat
echo.
echo ========================================
choice /c 1234 /m "Chon chuc nang (1-4)"

if errorlevel 4 goto :exit_program
if errorlevel 3 goto :timezone_menu
if errorlevel 2 goto :add_startup_menu
if errorlevel 1 goto :open_startup_menu

REM ============================================================
REM MENU 1: QUAN LY STARTUP FOLDER
REM ============================================================
:open_startup_menu
cls
echo ========================================
echo   1. QUAN LY STARTUP FOLDER
echo ========================================
echo.
echo 11. Mo User Startup folder
echo 12. Mo System Startup folder
echo 13. Mo ca 2 folders
echo 14. Hien thi danh sach apps trong Startup
echo 15. Quay lai menu chinh
echo.
choice /c 12345 /m "Chon so (11-15)"

if errorlevel 5 goto :main_menu
if errorlevel 4 goto :open_startup_14
if errorlevel 3 goto :open_startup_13
if errorlevel 2 goto :open_startup_12
if errorlevel 1 goto :open_startup_11

:open_startup_11
echo.
echo [11] Mo User Startup folder...
explorer shell:startup
echo.
echo [OK] Da mo User Startup folder!
echo Duong dan: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
echo.
pause
goto :open_startup_menu

:open_startup_12
echo.
echo [12] Mo System Startup folder...
explorer shell:common startup
echo.
echo [OK] Da mo System Startup folder!
echo Duong dan: C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
echo.
pause
goto :open_startup_menu

:open_startup_13
echo.
echo [13] Mo ca 2 Startup folders...
start explorer shell:startup
timeout /t 1 /nobreak >nul
start explorer shell:common startup
echo.
echo [OK] Da mo ca 2 Startup folders!
echo.
pause
goto :open_startup_menu

:open_startup_14
echo.
echo ========================================
echo   [14] DANH SACH APP TRONG STARTUP
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
goto :open_startup_menu

REM ============================================================
REM MENU 2: THEM APP VAO STARTUP
REM ============================================================
:add_startup_menu
cls
echo ========================================
echo   2. THEM APP VAO STARTUP
echo ========================================
echo.
echo 21. MetaTrader 4 (MT4)
echo 22. MetaTrader 5 (MT5)
echo 23. Python Script (.py)
echo 24. Batch File (.bat)
echo 25. Executable File (.exe) - Tu chon
echo 26. Quay lai menu chinh
echo.
choice /c 123456 /m "Chon so (21-26)"

if errorlevel 6 goto :main_menu
if errorlevel 5 goto :add_startup_25
if errorlevel 4 goto :add_startup_24
if errorlevel 3 goto :add_startup_23
if errorlevel 2 goto :add_startup_22
if errorlevel 1 goto :add_startup_21

:add_startup_21
echo.
echo [21] Da chon: MetaTrader 4
echo.
echo Nhap duong dan day du den terminal.exe cua MT4:
echo Vi du: C:\Program Files (x86)\MetaTrader 4\terminal.exe
echo.
set /p MT4_PATH="Duong dan MT4: "

if not exist "%MT4_PATH%" (
    echo.
    echo [LOI] File khong ton tai: %MT4_PATH%
    echo.
    pause
    goto :add_startup_menu
)

set APP_NAME=MetaTrader 4
set APP_PATH=%MT4_PATH%
goto :add_startup_create_shortcut

:add_startup_22
echo.
echo [22] Da chon: MetaTrader 5
echo.
echo Nhap duong dan day du den terminal64.exe cua MT5:
echo Vi du: C:\Program Files\MetaTrader 5\terminal64.exe
echo.
set /p MT5_PATH="Duong dan MT5: "

if not exist "%MT5_PATH%" (
    echo.
    echo [LOI] File khong ton tai: %MT5_PATH%
    echo.
    pause
    goto :add_startup_menu
)

set APP_NAME=MetaTrader 5
set APP_PATH=%MT5_PATH%
goto :add_startup_create_shortcut

:add_startup_23
echo.
echo [23] Da chon: Python Script
echo.
echo Nhap duong dan day du den file .py:
echo Vi du: C:\Trading\bot.py
echo.
set /p PY_PATH="Duong dan .py: "

if not exist "%PY_PATH%" (
    echo.
    echo [LOI] File khong ton tai: %PY_PATH%
    echo.
    pause
    goto :add_startup_menu
)

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set BAT_WRAPPER=%STARTUP_FOLDER%\run_python_bot.bat
echo @echo off > "%BAT_WRAPPER%"
echo cd /d "%%~dp0" >> "%BAT_WRAPPER%"
echo python "%PY_PATH%" >> "%BAT_WRAPPER%"

echo.
echo [OK] Da tao file wrapper: %BAT_WRAPPER%
echo Python script se tu dong chay khi login!
echo.
pause
goto :add_startup_menu

:add_startup_24
echo.
echo [24] Da chon: Batch File
echo.
echo Nhap duong dan day du den file .bat:
echo Vi du: C:\Trading\start_bot.bat
echo.
set /p BAT_PATH="Duong dan .bat: "

if not exist "%BAT_PATH%" (
    echo.
    echo [LOI] File khong ton tai: %BAT_PATH%
    echo.
    pause
    goto :add_startup_menu
)

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy "%BAT_PATH%" "%STARTUP_FOLDER%\" >nul 2>&1

echo.
echo [OK] Da copy file vao Startup folder!
echo File .bat se tu dong chay khi login!
echo.
pause
goto :add_startup_menu

:add_startup_25
echo.
echo [25] Da chon: Custom Executable
echo.
echo Nhap duong dan day du den file .exe:
echo Vi du: C:\Program Files\MyApp\app.exe
echo.
set /p EXE_PATH="Duong dan .exe: "

if not exist "%EXE_PATH%" (
    echo.
    echo [LOI] File khong ton tai: %EXE_PATH%
    echo.
    pause
    goto :add_startup_menu
)

echo.
echo Nhap ten shortcut (khong can .lnk):
echo Vi du: MyTradingApp
echo.
set /p APP_NAME="Ten shortcut: "

set APP_PATH=%EXE_PATH%
goto :add_startup_create_shortcut

:add_startup_create_shortcut
echo.
echo ========================================
echo   TAO SHORTCUT
echo ========================================
echo.

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set VBS_FILE=%TEMP%\CreateStartupShortcut.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_FILE%"
echo sLinkFile = "%STARTUP_FOLDER%\%APP_NAME%.lnk" >> "%VBS_FILE%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_FILE%"
echo oLink.TargetPath = "%APP_PATH%" >> "%VBS_FILE%"
echo oLink.WorkingDirectory = "%%~dp0" >> "%VBS_FILE%"
echo oLink.Description = "%APP_NAME% - Auto-start on login" >> "%VBS_FILE%"
echo oLink.Save >> "%VBS_FILE%"

cscript //nologo "%VBS_FILE%" >nul 2>&1
del /f /q "%VBS_FILE%" >nul 2>&1

echo [OK] Shortcut da duoc tao!
echo.
echo CHI TIET:
echo ========================================
echo Ten: %APP_NAME%
echo Duong dan: %APP_PATH%
echo Shortcut: %STARTUP_FOLDER%\%APP_NAME%.lnk
echo ========================================
echo.
echo App se TU DONG CHAY khi ban login vao Windows!
echo.
pause
goto :add_startup_menu

REM ============================================================
REM MENU 3: CHINH TIMEZONE
REM ============================================================
:timezone_menu
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    cls
    echo ========================================
    echo   CHINH TIMEZONE - CAN ADMIN
    echo ========================================
    echo.
    echo [LOI] Chuc nang nay can quyen Administrator!
    echo.
    echo Cach chay voi Admin:
    echo 1. Dong file nay
    echo 2. Right-click vps-tools.bat
    echo 3. Chon "Run as administrator"
    echo 4. Chon lai chuc nang 3
    echo.
    pause
    goto :main_menu
)

cls
echo ========================================
echo   3. CHINH TIMEZONE
echo ========================================
echo.

REM Hien thi timezone hien tai
echo Timezone hien tai:
for /f "tokens=*" %%i in ('tzutil /g 2^>nul') do set CURRENT_TZ=%%i
echo - %CURRENT_TZ%
echo.

echo ========================================
echo.
echo 31. Chinh gio MAC DINH (UTC)
echo 32. Chinh sang gio LONDON (GMT+0/+1)
echo 33. Chinh sang gio NEW YORK (GMT-5/-4)
echo 34. Chinh sang gio VIETNAM (GMT+7)
echo 35. Chinh sang gio ICMARKET EU (GMT+2/+3)
echo 36. Quay lai menu chinh
echo.
choice /c 123456 /m "Chon so (31-36)"

if errorlevel 6 goto :main_menu
if errorlevel 5 goto :timezone_35
if errorlevel 4 goto :timezone_34
if errorlevel 3 goto :timezone_33
if errorlevel 2 goto :timezone_32
if errorlevel 1 goto :timezone_31

:timezone_31
echo.
echo [31] Chinh gio MAC DINH - UTC
echo.
tzutil /s "UTC" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang UTC thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :timezone_show_result

:timezone_32
echo.
echo [32] Chinh gio LONDON
echo.
tzutil /s "GMT Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio London thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :timezone_show_result

:timezone_33
echo.
echo [33] Chinh gio NEW YORK
echo.
tzutil /s "Eastern Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio New York thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :timezone_show_result

:timezone_34
echo.
echo [34] Chinh gio VIETNAM
echo.
tzutil /s "SE Asia Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio Vietnam thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :timezone_show_result

:timezone_35
echo.
echo [35] Chinh gio ICMARKET EU
echo.
tzutil /s "FLE Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio ICMarket EU thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :timezone_show_result

:timezone_show_result
echo ========================================
echo   KET QUA
echo ========================================
echo.
echo Timezone moi:
for /f "tokens=*" %%i in ('tzutil /g 2^>nul') do set NEW_TZ=%%i
echo - %NEW_TZ%
echo.
echo Gio he thong: %date% %time%
echo.
echo LUU Y: MT4/MT5 can dong va mo lai de ap dung gio moi!
echo.
pause
goto :timezone_menu

REM ============================================================
REM EXIT
REM ============================================================
:exit_program
cls
echo ========================================
echo   CAM ON DA SU DUNG VPS TOOLS!
echo ========================================
echo.
echo Cac chuc nang da su dung:
echo 1. Quan ly Startup Folder
echo 2. Them App vao Startup
echo 3. Chinh Timezone
echo.
echo Cac file goc van con nguyen:
echo - open-startup-folder.bat
echo - add-to-startup.bat
echo - change-timezone.bat
echo.
pause
exit /b 0
