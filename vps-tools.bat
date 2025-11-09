@echo off
REM ============================================================
REM VPS TOOLS - TICH HOP 3 CHUC NANG
REM 1. Quan ly Startup Folder
REM 2. Them App vao Startup
REM 3. Chinh Timezone
REM MENU PHANG - TAT CA OPTIONS TRONG 1 MAN HINH
REM ============================================================

:main_menu
cls
echo ========================================
echo   VPS TOOLS - TICH HOP 3 CHUC NANG
echo ========================================
echo.
echo 1. QUAN LY STARTUP FOLDER
echo   11. Mo User Startup folder
echo   12. Mo System Startup folder
echo   13. Mo ca 2 folders
echo   14. Hien thi danh sach apps trong Startup
echo.
echo 2. THEM APP VAO STARTUP
echo   21. MetaTrader 4 (MT4)
echo   22. MetaTrader 5 (MT5)
echo   23. Python Script (.py)
echo   24. Batch File (.bat)
echo   25. Executable File (.exe) - Tu chon
echo.
echo 3. CHINH TIMEZONE
echo   31. UTC (Mac dinh)
echo   32. London (GMT+0/+1)
echo   33. New York (GMT-5/-4)
echo   34. Vietnam (GMT+7)
echo   35. ICMarket EU (GMT+2/+3)
echo.
echo 0. Thoat
echo.
echo ========================================
set /p CHOICE="Nhap lua chon (11-35 hoac 0): "

REM Startup Folder options
if "%CHOICE%"=="11" goto :func_11
if "%CHOICE%"=="12" goto :func_12
if "%CHOICE%"=="13" goto :func_13
if "%CHOICE%"=="14" goto :func_14

REM Add to Startup options
if "%CHOICE%"=="21" goto :func_21
if "%CHOICE%"=="22" goto :func_22
if "%CHOICE%"=="23" goto :func_23
if "%CHOICE%"=="24" goto :func_24
if "%CHOICE%"=="25" goto :func_25

REM Timezone options
if "%CHOICE%"=="31" goto :func_31
if "%CHOICE%"=="32" goto :func_32
if "%CHOICE%"=="33" goto :func_33
if "%CHOICE%"=="34" goto :func_34
if "%CHOICE%"=="35" goto :func_35

REM Exit
if "%CHOICE%"=="0" goto :exit_program

REM Invalid choice
echo.
echo [LOI] Lua chon khong hop le! Hay nhap so tu 11-35 hoac 0.
echo.
pause
goto :main_menu

REM ============================================================
REM CHUC NANG 1: QUAN LY STARTUP FOLDER
REM ============================================================

:func_11
cls
echo ========================================
echo   [11] MO USER STARTUP FOLDER
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

:func_12
cls
echo ========================================
echo   [12] MO SYSTEM STARTUP FOLDER
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

:func_13
cls
echo ========================================
echo   [13] MO CA 2 STARTUP FOLDERS
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

:func_14
cls
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
goto :main_menu

REM ============================================================
REM CHUC NANG 2: THEM APP VAO STARTUP
REM ============================================================

:func_21
cls
echo ========================================
echo   [21] THEM METATRADER 4 VAO STARTUP
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

:func_22
cls
echo ========================================
echo   [22] THEM METATRADER 5 VAO STARTUP
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
echo   [23] THEM PYTHON SCRIPT VAO STARTUP
echo ========================================
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
    goto :main_menu
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
goto :main_menu

:func_24
cls
echo ========================================
echo   [24] THEM BATCH FILE VAO STARTUP
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

:func_25
cls
echo ========================================
echo   [25] THEM CUSTOM EXE VAO STARTUP
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
REM CHUC NANG 3: CHINH TIMEZONE
REM ============================================================

:func_31
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [31] CHINH GIO MAC DINH - UTC
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

:func_32
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [32] CHINH GIO LONDON
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

:func_33
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [33] CHINH GIO NEW YORK
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

:func_34
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [34] CHINH GIO VIETNAM
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

:func_35
REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 goto :need_admin

cls
echo ========================================
echo   [35] CHINH GIO ICMARKET EU
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
echo 4. Chon lai chuc nang 31-35
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
REM EXIT
REM ============================================================
:exit_program
cls
echo ========================================
echo   CAM ON DA SU DUNG VPS TOOLS!
echo ========================================
echo.
echo Cac chuc nang da su dung:
echo 1. Quan ly Startup Folder (11-14)
echo 2. Them App vao Startup (21-25)
echo 3. Chinh Timezone (31-35)
echo.
echo Cac file goc van con nguyen:
echo - open-startup-folder.bat
echo - add-to-startup.bat
echo - change-timezone.bat
echo.
pause
exit /b 0
