@echo off
REM ============================================================
REM SCRIPT CHINH TIMEZONE CHO VPS TRADING
REM Change VPS Timezone for Trading (London/NY/Vietnam/ICMarket)
REM PHAI CHAY VOI QUYEN ADMINISTRATOR!
REM ============================================================

echo ========================================
echo   CHINH TIMEZONE CHO VPS TRADING
echo   Change VPS Timezone
echo ========================================
echo.

REM Kiem tra quyen Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [LOI] Phai chay voi quyen Administrator!
    echo Right-click file nay va chon "Run as administrator"
    pause
    exit /b 1
)

:menu
cls
echo ========================================
echo   CHINH TIMEZONE CHO VPS TRADING
echo ========================================
echo.

REM Hien thi timezone hien tai
echo Timezone hien tai:
for /f "tokens=*" %%i in ('tzutil /g 2^>nul') do set CURRENT_TZ=%%i
echo - %CURRENT_TZ%
echo.

REM Hien thi gio hien tai
echo Gio he thong hien tai:
echo - %date% %time%
echo.

echo ========================================
echo   CHON TIMEZONE
echo ========================================
echo.
echo 1. Chinh gio MAC DINH cua he thong VPS (UTC)
echo 2. Chinh sang gio LONDON (GMT+0/+1)
echo 3. Chinh sang gio NEW YORK (GMT-5/-4)
echo 4. Chinh sang gio VIETNAM (GMT+7)
echo 5. Chinh sang gio EU cua ICMARKET (GMT+2/+3)
echo 6. Thoat
echo.
choice /c 123456 /m "Chon so (1-6)"

if errorlevel 6 goto :end
if errorlevel 5 goto :icmarket
if errorlevel 4 goto :vietnam
if errorlevel 3 goto :newyork
if errorlevel 2 goto :london
if errorlevel 1 goto :default_utc

:default_utc
echo.
echo ========================================
echo   CHINH GIO MAC DINH - UTC
echo ========================================
echo.
echo Timezone: UTC (Coordinated Universal Time)
echo GMT Offset: GMT+0 (khong thay doi theo mua)
echo Phu hop: VPS chuan, server backend
echo.

REM Set timezone to UTC
tzutil /s "UTC" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang UTC thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
    echo Hay thu chay lai voi quyen Administrator.
)
echo.
goto :show_result

:london
echo.
echo ========================================
echo   CHINH GIO LONDON
echo ========================================
echo.
echo Timezone: GMT Standard Time
echo GMT Offset: GMT+0 (mua dong), GMT+1 (mua he - BST)
echo Phu hop: Forex London session, UK brokers
echo.

REM Set timezone to London
tzutil /s "GMT Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio London thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
    echo Hay thu chay lai voi quyen Administrator.
)
echo.
goto :show_result

:newyork
echo.
echo ========================================
echo   CHINH GIO NEW YORK
echo ========================================
echo.
echo Timezone: Eastern Standard Time
echo GMT Offset: GMT-5 (mua dong - EST), GMT-4 (mua he - EDT)
echo Phu hop: Forex NY session, US brokers
echo.

REM Set timezone to New York
tzutil /s "Eastern Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio New York thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
    echo Hay thu chay lai voi quyen Administrator.
)
echo.
goto :show_result

:vietnam
echo.
echo ========================================
echo   CHINH GIO VIETNAM
echo ========================================
echo.
echo Timezone: SE Asia Standard Time
echo GMT Offset: GMT+7 (khong thay doi theo mua)
echo Phu hop: Trader Vietnam, local time
echo.

REM Set timezone to Vietnam
tzutil /s "SE Asia Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio Vietnam thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
    echo Hay thu chay lai voi quyen Administrator.
)
echo.
goto :show_result

:icmarket
echo.
echo ========================================
echo   CHINH GIO ICMARKET EU
echo ========================================
echo.
echo Timezone: FLE Standard Time (Cyprus/Greece)
echo GMT Offset: GMT+2 (mua dong - EET), GMT+3 (mua he - EEST)
echo Phu hop: ICMarket server time, EU brokers
echo.

REM Set timezone to ICMarket EU (Cyprus)
tzutil /s "FLE Standard Time" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Da chuyen sang gio ICMarket EU thanh cong!
) else (
    echo [LOI] Khong the chuyen timezone!
    echo Hay thu chay lai voi quyen Administrator.
)
echo.
goto :show_result

:show_result
echo ========================================
echo   KET QUA
echo ========================================
echo.

REM Hien thi timezone moi
echo Timezone moi:
for /f "tokens=*" %%i in ('tzutil /g 2^>nul') do set NEW_TZ=%%i
echo - %NEW_TZ%
echo.

REM Hien thi gio moi
echo Gio he thong moi:
echo - %date% %time%
echo.

echo ========================================
echo.
echo LUU Y:
echo - Timezone da duoc thay doi!
echo - Ung dung dang chay co the can RESTART de ap dung gio moi
echo - MT4/MT5: Dong va mo lai terminal
echo - Python bots: Restart scripts
echo.

REM Hoi co muon quay lai menu khong
choice /c YN /m "Ban co muon thay doi timezone khac? (Y=Quay lai menu, N=Thoat)"

if errorlevel 2 goto :end
if errorlevel 1 goto :menu

:end
echo.
echo ========================================
echo   HOAN TAT!
echo ========================================
echo.
echo Timezone hien tai: %NEW_TZ%
echo.
echo CACH KIEM TRA TIMEZONE:
echo - Lenh: tzutil /g
echo - Windows Settings: Time ^& Language ^> Date ^& time
echo.
echo CACH DOI TIMEZONE BANG TAY:
echo - Settings ^> Time ^& Language ^> Date ^& time
echo - Chon "Time zone" ^> Chon timezone mong muon
echo.
pause
exit /b 0
