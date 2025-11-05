@echo off
REM ============================================================================
REM SYNS Bot System - Build ALL SETUP.EXE Files
REM ============================================================================
REM
REM Tạo tất cả installer files:
REM 1. Build 4 .exe với PyInstaller
REM 2. Compile Portable Setup.exe
REM 3. Compile EXE Setup.exe
REM
REM YÊU CẦU:
REM - Python + PyInstaller
REM - Inno Setup 6 (tải từ https://jrsoftware.org/isdl.php)
REM
REM ============================================================================

echo ============================================================================
echo SYNS Bot System - Building ALL SETUP.EXE Files
echo ============================================================================
echo.

REM Check if Inno Setup installed
set INNO_COMPILER="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_COMPILER% (
    echo [ERROR] Inno Setup not found!
    echo.
    echo Please install Inno Setup 6 from:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo Default location: C:\Program Files ^(x86^)\Inno Setup 6\
    echo.
    pause
    exit /b 1
)

REM Step 1: Build 4 .exe files
echo.
echo ============================================================================
echo [STEP 1/3] Building 4 Bot .exe files with PyInstaller...
echo ============================================================================
echo.

call build_exe.bat
if errorlevel 1 (
    echo [ERROR] Failed to build .exe files!
    pause
    exit /b 1
)

REM Step 2: Compile Portable Setup
echo.
echo ============================================================================
echo [STEP 2/3] Compiling Portable Setup Installer...
echo ============================================================================
echo.

%INNO_COMPILER% setup_portable.iss
if errorlevel 1 (
    echo [ERROR] Failed to compile Portable Setup!
    pause
    exit /b 1
)

REM Step 3: Compile EXE Setup
echo.
echo ============================================================================
echo [STEP 3/3] Compiling EXE Setup Installer...
echo ============================================================================
echo.

%INNO_COMPILER% setup_exe.iss
if errorlevel 1 (
    echo [ERROR] Failed to compile EXE Setup!
    pause
    exit /b 1
)

REM Success!
echo.
echo ============================================================================
echo SUCCESS! ALL SETUP FILES CREATED!
echo ============================================================================
echo.
echo Output files in PACKAGES\ folder:
echo.
echo   [1] SYNS_Bot_Portable_Setup.exe     (~7.5 MB)
echo       - Python Embedded + Code
echo       - Auto-install libraries
echo       - Recommended for beginners
echo.
echo   [2] SYNS_Bot_EXE_Setup.exe          (~15-20 MB)
echo       - 4 standalone .exe files
echo       - No Python needed
echo       - For experienced users
echo.
echo ============================================================================
echo DISTRIBUTION READY!
echo ============================================================================
echo.
echo You can now distribute these SETUP.EXE files to users.
echo They just need to:
echo   1. Download SETUP.exe
echo   2. Double-click to install
echo   3. Follow the wizard
echo   4. Run from Start Menu
echo.
pause
