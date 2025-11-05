@echo off
REM ============================================================================
REM SYNS Bot System - Build 4 EXE Files with PyInstaller
REM ============================================================================
REM
REM USAGE:
REM 1. Install PyInstaller: pip install pyinstaller
REM 2. Run this script: build_exe.bat
REM 3. Find EXE files in: dist/ folder
REM
REM ============================================================================

echo ============================================================================
echo SYNS Bot System - Building 4 EXE Files
echo ============================================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller not installed!
    echo.
    echo Installing PyInstaller...
    pip install pyinstaller
    echo.
)

echo [1/4] Building Bot 0 - sync_http80_sender.exe...
pyinstaller --onefile --noconsole ^
    --name "Bot0_HTTP80_Sender" ^
    --icon NONE ^
    --add-data "bot_config.json;." ^
    sync_http80_sender.py

echo.
echo [2/4] Building Bot 1 - sync1_sender_optimized.exe...
pyinstaller --onefile --noconsole ^
    --name "Bot1_Sender_Optimized" ^
    --icon NONE ^
    --add-data "bot_config.json;." ^
    sync1_sender_optimized.py

echo.
echo [3/4] Building Bot 2 - sync2_data_receiver.exe...
pyinstaller --onefile --noconsole ^
    --name "Bot2_Data_Receiver" ^
    --icon NONE ^
    --add-data "bot_config.json;." ^
    sync2_data_receiver.py

echo.
echo [4/4] Building Bot 3 - sync_server80data.exe...
pyinstaller --onefile --noconsole ^
    --name "Bot3_Server_Integrated" ^
    --icon NONE ^
    --add-data "bot_config.json;." ^
    sync_server80data.py

echo.
echo ============================================================================
echo BUILD COMPLETE!
echo ============================================================================
echo.
echo EXE files location: dist\
echo.
echo Files created:
echo   - Bot0_HTTP80_Sender.exe
echo   - Bot1_Sender_Optimized.exe
echo   - Bot2_Data_Receiver.exe
echo   - Bot3_Server_Integrated.exe
echo.
echo NEXT STEPS:
echo 1. Copy all .exe files from dist\ folder
echo 2. Copy bot_config.json to same folder as .exe files
echo 3. Copy START_0123_BOT.bat (will be updated to run .exe)
echo.
pause
