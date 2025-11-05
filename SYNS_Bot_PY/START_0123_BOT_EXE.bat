@echo off
chcp 65001 >nul
cls

echo ============================================================
echo      SYNC SERVER - CHON BOT DE CHAY (4 OPTIONS) - EXE VERSION
echo ============================================================
echo.
echo  [0] Bot 0 - SENDER (Variant)
echo      File: Bot0_HTTP80_Sender.exe
echo      Port 80 + 9070
echo.
echo  [1] Bot 1 - SENDER (Optimized) - KHUYEN NGHI
echo      File: Bot1_Sender_Optimized.exe
echo      Port 80 + 9070
echo.
echo  [2] Bot 2 - RECEIVER
echo      File: Bot2_Data_Receiver.exe
echo      Port 9070
echo      Pull from: dungalading.duckdns.org:80
echo.
echo  [3] Bot 3 - INTEGRATED (2-in-1)
echo      File: Bot3_Server_Integrated.exe
echo      - Mode 0: SENDER (Bot 1)
echo      - Mode 1: RECEIVER (Bot 2)
echo      - Chon mode trong bot_config.json
echo.
echo ============================================================
echo  NEU KHONG CHON GI TRONG 60S - TU DONG CHAY BOT 1
echo ============================================================
echo.

choice /C 0123 /T 60 /D 1 /M "Nhap lua chon (0/1/2/3)"

if errorlevel 4 goto BOT3
if errorlevel 3 goto BOT2
if errorlevel 2 goto BOT1
if errorlevel 1 goto BOT0

:BOT0
cls
echo ============================================================
echo  DANG CHAY BOT 0 - SENDER (Variant)
echo ============================================================
echo  File: Bot0_HTTP80_Sender.exe
echo  Port: 80 (API) + 9070 (Dashboard)
echo ============================================================
echo.
cd /d "%~dp0"
start "" "%~dp0Bot0_HTTP80_Sender.exe"
echo Bot 0 started in background window.
echo Close this window or press any key to exit launcher.
pause
exit

:BOT1
cls
echo ============================================================
echo  DANG CHAY BOT 1 - SENDER (Optimized)
echo ============================================================
echo  File: Bot1_Sender_Optimized.exe
echo  Port: 80 (API) + 9070 (Dashboard)
echo  Domain: dungalading.duckdns.org
echo ============================================================
echo.
cd /d "%~dp0"
start "" "%~dp0Bot1_Sender_Optimized.exe"
echo Bot 1 started in background window.
echo Close this window or press any key to exit launcher.
pause
exit

:BOT2
cls
echo ============================================================
echo  DANG CHAY BOT 2 - RECEIVER
echo ============================================================
echo  File: Bot2_Data_Receiver.exe
echo  Port: 9070 (Dashboard only)
echo  Pull from: http://dungalading.duckdns.org:80
echo ============================================================
echo.
cd /d "%~dp0"
start "" "%~dp0Bot2_Data_Receiver.exe"
echo Bot 2 started in background window.
echo Close this window or press any key to exit launcher.
pause
exit

:BOT3
cls
echo ============================================================
echo  DANG CHAY BOT 3 - INTEGRATED (2-in-1)
echo ============================================================
echo  File: Bot3_Server_Integrated.exe
echo.
echo  Kiem tra file bot_config.json:
echo  - "mode": 0 -^> SENDER (Bot 1)
echo  - "mode": 1 -^> RECEIVER (Bot 2)
echo ============================================================
echo.
cd /d "%~dp0"
start "" "%~dp0Bot3_Server_Integrated.exe"
echo Bot 3 started in background window.
echo Close this window or press any key to exit launcher.
pause
exit
