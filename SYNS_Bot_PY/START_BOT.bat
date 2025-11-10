@echo off
chcp 65001 >nul
cls

echo ============================================================
echo      SYNC SERVER - CHON BOT DE CHAY (4 OPTIONS)
echo ============================================================
echo.
echo  [0] Bot 0 - SENDER (Variant)
echo      File: sync0_http80_sender.py
echo      Port 80 + 9070
echo.
echo  [1] Bot 1 - SENDER (Optimized) - KHUYEN NGHI
echo      File: sync1_sender_optimized.py
echo      Port 80 + 9070
echo.
echo  [2] Bot 2 - RECEIVER
echo      File: sync2_data_receiver.py
echo      Port 9070
echo      Pull from: dungalading.duckdns.org:80
echo.
echo  [3] Bot 3 - INTEGRATED (2-in-1)
echo      File: sync3_server80data.py
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
echo  File: sync0_http80_sender.py
echo  Port: 80 (API) + 9070 (Dashboard)
echo ============================================================
echo.
cd /d "%~dp0"
python\python.exe sync0_http80_sender.py
pause
exit

:BOT1
cls
echo ============================================================
echo  DANG CHAY BOT 1 - SENDER (Optimized)
echo ============================================================
echo  File: sync1_sender_optimized.py
echo  Port: 80 (API) + 9070 (Dashboard)
echo  Domain: dungalading.duckdns.org
echo ============================================================
echo.
cd /d "%~dp0"
python\python.exe sync1_sender_optimized.py
pause
exit

:BOT2
cls
echo ============================================================
echo  DANG CHAY BOT 2 - RECEIVER
echo ============================================================
echo  File: sync2_data_receiver.py
echo  Port: 9070 (Dashboard only)
echo  Pull from: http://dungalading.duckdns.org:80
echo ============================================================
echo.
cd /d "%~dp0"
python\python.exe sync2_data_receiver.py
pause
exit

:BOT3
cls
echo ============================================================
echo  DANG CHAY BOT 3 - INTEGRATED (2-in-1)
echo ============================================================
echo  File: sync3_server80data.py
echo.
echo  Kiem tra file bot_config.json:
echo  - "mode": 0 -^> SENDER (Bot 1)
echo  - "mode": 1 -^> RECEIVER (Bot 2)
echo ============================================================
echo.
cd /d "%~dp0"
python\python.exe sync3_server80data.py
pause
exit
