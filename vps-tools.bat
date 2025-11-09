@echo off
REM ============================================================
REM VPS TOOLS - TICH HOP 3 CHUC NANG STANDALONE
REM 0. Chinh Timezone (0-5)
REM 1. Quan ly Startup Folder (10-13)
REM 2. Them App vao Startup (20, 21, 23, 24)
REM MENU PHANG - TAT CA OPTIONS TRONG 1 MAN HINH
REM ============================================================

:main_menu
cls
echo ========================================
echo   VPS TOOLS - TICH HOP 3 CHUC NANG
echo ========================================
echo.
echo 0. CHINH TIMEZONE
echo   0. UTC (Mac dinh)
echo   1. London (GMT+0/+1)
echo   2. New York (GMT-5/-4)
echo   3. Vietnam (GMT+7)
echo   4. ICMarket EU (GMT+2/+3)
echo   5. Hien thi timezone hien tai
echo.
echo 1. QUAN LY STARTUP FOLDER
echo   10. Mo User Startup folder
echo   11. Mo System Startup folder
echo   12. Mo ca 2 folders
echo   13. Hien thi danh sach apps trong Startup
echo.
echo 2. THEM APP VAO STARTUP
echo   20. MetaTrader 4 (MT4)
echo   21. MetaTrader 5 (MT5)
echo   23. Batch File (.bat)
echo   24. Custom Executable (.exe)
echo.
echo X. Thoat
echo.
echo ========================================
set /p CHOICE="Nhap lua chon: "

REM Timezone options (0-5)
if "%CHOICE%"=="0" goto :func_00
if "%CHOICE%"=="1" goto :func_01
if "%CHOICE%"=="2" goto :func_02
if "%CHOICE%"=="3" goto :func_03
if "%CHOICE%"=="4" goto :func_04
if "%CHOICE%"=="5" goto :func_05

REM Startup Folder options (10-13)
if "%CHOICE%"=="10" goto :func_10
if "%CHOICE%"=="11" goto :func_11
if "%CHOICE%"=="12" goto :func_12
if "%CHOICE%"=="13" goto :func_13

REM Add to Startup options (20, 21, 23, 24)
if "%CHOICE%"=="20" goto :func_20
if "%CHOICE%"=="21" goto :func_21
if "%CHOICE%"=="23" goto :func_23
if "%CHOICE%"=="24" goto :func_24

REM Exit
if /i "%CHOICE%"=="X" goto :exit_program

REM Invalid choice
echo.
echo [LOI] Lua chon khong hop le!
echo.
pause
goto :main_menu

REM ============================================================
REM CHUC NANG 0: CHINH TIMEZONE (0-5)
REM ============================================================

:func_00
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [0] CHINH GIO MAC DINH - UTC
echo ========================================
echo.
tzutil /s "UTC" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang UTC thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :show_timezone_result

:func_01
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [1] CHINH GIO LONDON
echo ========================================
echo.
tzutil /s "GMT Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio London thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :show_timezone_result

:func_02
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [2] CHINH GIO NEW YORK
echo ========================================
echo.
tzutil /s "Eastern Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio New York thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :show_timezone_result

:func_03
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [3] CHINH GIO VIETNAM
echo ========================================
echo.
tzutil /s "SE Asia Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio Vietnam thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :show_timezone_result

:func_04
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [4] CHINH GIO ICMARKET EU
echo ========================================
echo.
tzutil /s "FLE Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio ICMarket EU thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
)
echo.
goto :show_timezone_result

:func_05
cls
echo ========================================
echo   [5] HIEN THI TIMEZONE HIEN TAI
echo ========================================
echo.
echo Timezone hien tai:
for /f "tokens=*" %%i in ('tzutil /g 2^>nul') do set CURRENT_TZ=%%i
echo - %CURRENT_TZ%
echo.
echo Gio he thong: %date% %time%
echo.
echo ========================================
echo.
pause
goto :main_menu

:need_admin
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
echo 4. Chon lai chuc nang 0-4
echo.
pause
goto :main_menu

:show_timezone_result
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
goto :main_menu

REM ============================================================
REM CHUC NANG 1: QUAN LY STARTUP FOLDER (10-13)
REM ============================================================

:func_10
cls
echo ========================================
echo   [10] MO USER STARTUP FOLDER
echo ========================================
echo.
echo Mo User Startup folder...
explorer shell:startup
echo.
echo [OK] Da mo User Startup folder!
echo Duong dan: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
echo.
pause
goto :main_menu

:func_11
cls
echo ========================================
echo   [11] MO SYSTEM STARTUP FOLDER
echo ========================================
echo.
echo Mo System Startup folder...
explorer shell:common startup
echo.
echo [OK] Da mo System Startup folder!
echo Duong dan: C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
echo.
pause
goto :main_menu

:func_12
cls
echo ========================================
echo   [12] MO CA 2 STARTUP FOLDERS
echo ========================================
echo.
echo Mo ca 2 Startup folders...
start explorer shell:startup
timeout /t 1 /nobreak >nul
start explorer shell:common startup
echo.
echo [OK] Da mo ca 2 Startup folders!
echo.
pause
goto :main_menu

:func_13
cls
echo ========================================
echo   [13] DANH SACH APP TRONG STARTUP
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
goto :main_menu

REM ============================================================
REM CHUC NANG 2: THEM APP VAO STARTUP (20-24)
REM ============================================================

:func_20
cls
echo ========================================
echo   [20] THEM METATRADER 4 VAO STARTUP
echo ========================================
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
    goto :main_menu
)

set APP_NAME=MetaTrader 4
set APP_PATH=%MT4_PATH%
goto :create_shortcut

:func_21
cls
echo ========================================
echo   [21] THEM METATRADER 5 VAO STARTUP
echo ========================================
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
    goto :main_menu
)

set APP_NAME=MetaTrader 5
set APP_PATH=%MT5_PATH%
goto :create_shortcut

:func_23
cls
echo ========================================
echo   [23] THEM BATCH FILE VAO STARTUP
echo ========================================
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
    goto :main_menu
)

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy "%BAT_PATH%" "%STARTUP_FOLDER%\" >nul 2>&1

echo.
echo [OK] Da copy file vao Startup folder!
echo File .bat se tu dong chay khi login!
echo.
pause
goto :main_menu

:func_24
cls
echo ========================================
echo   [24] THEM CUSTOM EXE VAO STARTUP
echo ========================================
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
    goto :main_menu
)

echo.
echo Nhap ten shortcut (khong can .lnk):
echo Vi du: MyTradingApp
echo.
set /p APP_NAME="Ten shortcut: "

set APP_PATH=%EXE_PATH%
goto :create_shortcut

:create_shortcut
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
goto :main_menu

REM ============================================================
REM EXIT
REM ============================================================
:exit_program
cls
echo ========================================
echo   CAM ON DA SU DUNG VPS TOOLS!
echo ========================================
echo.
echo CONG CU TICH HOP 3 CHUC NANG:
echo.
echo 0. CHINH TIMEZONE (0-5)
echo   - UTC, London, New York, Vietnam, ICMarket EU
echo   - Tu dong ap dung DST (Daylight Saving Time)
echo.
echo 1. QUAN LY STARTUP FOLDER (10-13)
echo   - Mo User/System Startup folders
echo   - Xem danh sach apps tu dong chay
echo.
echo 2. THEM APP VAO STARTUP (20, 21, 23, 24)
echo   - MetaTrader 4/5
echo   - Batch files, Custom executables
echo   - Tu dong tao shortcuts
echo.
echo ========================================
echo.
echo CACH MO STARTUP FOLDER:
echo - Nhan Windows+R
echo - Go: shell:startup
echo - Enter
echo.
echo CACH XOA APP KHOI STARTUP:
echo - Mo Startup folder
echo - Xoa shortcut tuong ung
echo.
echo ========================================
echo.
pause
exit /b 0
