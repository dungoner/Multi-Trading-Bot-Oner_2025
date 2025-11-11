@echo off
REM ============================================================================
REM SYNS Bot System - One-Click Build Script
REM ============================================================================
REM This script builds all 4 bots into standalone .exe files
REM Requirements: Python 3.x + pip install -r requirements.txt
REM ============================================================================

echo.
echo ============================================================================
echo   SYNS BOT SYSTEM - ONE-CLICK BUILD
echo ============================================================================
echo.
echo This script will build all 4 bots into standalone .exe files.
echo Each .exe file can run on any Windows computer without Python installed.
echo.
echo Requirements:
echo   - Python 3.7+ installed
echo   - PyInstaller installed (pip install -r requirements.txt)
echo.
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] PyInstaller not found!
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo [INFO] All dependencies OK!
echo.

REM Clean previous builds
echo [STEP 0/4] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build_temp rmdir /s /q build_temp
echo [OK] Previous builds cleaned
echo.

REM Build Bot 0
echo [STEP 1/4] Building Bot 0 (SENDER Full Features)...
pyinstaller --clean --noconfirm build_bot0.spec
if %errorlevel% neq 0 (
    echo [ERROR] Bot 0 build failed!
    pause
    exit /b 1
)
echo [OK] Bot 0 built successfully
echo.

REM Build Bot 1
echo [STEP 2/4] Building Bot 1 (SENDER Optimized)...
pyinstaller --clean --noconfirm build_bot1.spec
if %errorlevel% neq 0 (
    echo [ERROR] Bot 1 build failed!
    pause
    exit /b 1
)
echo [OK] Bot 1 built successfully
echo.

REM Build Bot 2
echo [STEP 3/4] Building Bot 2 (RECEIVER)...
pyinstaller --clean --noconfirm build_bot2.spec
if %errorlevel% neq 0 (
    echo [ERROR] Bot 2 build failed!
    pause
    exit /b 1
)
echo [OK] Bot 2 built successfully
echo.

REM Build Bot 3
echo [STEP 4/4] Building Bot 3 (All-in-One)...
pyinstaller --clean --noconfirm build_bot3.spec
if %errorlevel% neq 0 (
    echo [ERROR] Bot 3 build failed!
    pause
    exit /b 1
)
echo [OK] Bot 3 built successfully
echo.

REM Copy bot_config.json to dist folder
echo [FINAL] Copying bot_config.json to dist folder...
copy ..\SYNS_Bot_PY\bot_config.json dist\bot_config.json >nul
echo [OK] Config file copied
echo.

echo ============================================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ============================================================================
echo.
echo Output folder: %cd%\dist\
echo.
echo Built executables:
echo   - SYNS_Bot0_Sender_Full.exe      (Bot 0 - Full Features)
echo   - SYNS_Bot1_Sender_Optimized.exe (Bot 1 - Optimized)
echo   - SYNS_Bot2_Receiver.exe         (Bot 2 - Receiver)
echo   - SYNS_Bot3_All_In_One.exe       (Bot 3 - All-in-One)
echo   - bot_config.json                (Config file)
echo.
echo You can now copy the entire dist\ folder to any Windows computer.
echo No Python installation required!
echo.
echo ============================================================================
pause
