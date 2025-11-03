@echo off
chcp 65001 >nul
cls

echo ============================================================
echo      SYNC SERVER - CHON BOT DE CHAY
echo ============================================================
echo.
echo  [1] Bot 1 - SENDER (Backup)
echo      File: sync_http80_sender.py
echo.
echo  [2] Bot 2 - RECEIVER (Backup)
echo      File: sync2_data_receiver.py
echo.
echo  [3] Bot 3 - INTEGRATED (2-in-1) - KHUYEN NGHI
echo      File: sync_server80data.py
echo      - Mode 0: SENDER (Bot 1)
echo      - Mode 1: RECEIVER (Bot 2)
echo      - Chon mode trong bot_config.json
echo.
echo ============================================================
echo  NEU KHONG CHON GI TRONG 60S - TU DONG CHAY BOT 3
echo ============================================================
echo.

choice /C 123 /T 60 /D 3 /M "Nhap lua chon (1/2/3)"

if errorlevel 3 goto BOT3
if errorlevel 2 goto BOT2
if errorlevel 1 goto BOT1

:BOT1
cls
echo ============================================================
echo  DANG CHAY BOT 1 - SENDER (Backup)
echo ============================================================
echo.
cd /d "%~dp0"
python\python.exe sync_http80_sender.py
pause
exit

:BOT2
cls
echo ============================================================
echo  DANG CHAY BOT 2 - RECEIVER (Backup)
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
echo.
echo  Kiem tra file bot_config.json:
echo  - "mode": 0 -^> SENDER (Bot 1)
echo  - "mode": 1 -^> RECEIVER (Bot 2)
echo.
cd /d "%~dp0"
python\python.exe sync_server80data.py
pause
exit
