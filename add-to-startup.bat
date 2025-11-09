@echo off
REM ============================================================
REM SCRIPT THEM SHORTCUT VAO STARTUP FOLDER
REM Add Application to Windows Startup (Auto-run on Login)
REM KHONG CAN QUYEN ADMINISTRATOR!
REM ============================================================

echo ========================================
echo   THEM APP VAO STARTUP FOLDER
echo   Add Application to Auto-Start
echo ========================================
echo.

REM Lay duong dan Startup folder cua user hien tai
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo Startup folder hien tai:
echo %STARTUP_FOLDER%
echo.

echo Script nay giup ban them shortcut vao Startup folder.
echo App se TU DONG CHAY khi ban login vao Windows.
echo.
echo Vi du pho bien cho VPS Trading:
echo - MetaTrader 4 (terminal.exe)
echo - MetaTrader 5 (terminal64.exe)
echo - Python trading bot (.py hoac .bat)
echo - TradeLocker bot
echo.

REM Hoi user muon them app nao
echo.
echo ==================================================
echo   CHON APP BAN MUON THEM VAO STARTUP
echo ==================================================
echo.
echo 1. MetaTrader 4 (MT4)
echo 2. MetaTrader 5 (MT5)
echo 3. Python Script (.py)
echo 4. Batch File (.bat)
echo 5. Executable File (.exe) - Tu chon
echo 6. Thoat
echo.
choice /c 123456 /m "Chon so (1-6)"

if errorlevel 6 goto :end
if errorlevel 5 goto :custom_exe
if errorlevel 4 goto :batch_file
if errorlevel 3 goto :python_script
if errorlevel 2 goto :mt5
if errorlevel 1 goto :mt4

:mt4
echo.
echo Da chon: MetaTrader 4
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
    exit /b 1
)

set APP_NAME=MetaTrader 4
set APP_PATH=%MT4_PATH%
goto :create_shortcut

:mt5
echo.
echo Da chon: MetaTrader 5
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
    exit /b 1
)

set APP_NAME=MetaTrader 5
set APP_PATH=%MT5_PATH%
goto :create_shortcut

:python_script
echo.
echo Da chon: Python Script
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
    exit /b 1
)

REM Tao file .bat trung gian de chay Python script
set BAT_WRAPPER=%STARTUP_FOLDER%\run_python_bot.bat
echo @echo off > "%BAT_WRAPPER%"
echo cd /d "%~dp0" >> "%BAT_WRAPPER%"
echo python "%PY_PATH%" >> "%BAT_WRAPPER%"

echo.
echo [OK] Da tao file wrapper: %BAT_WRAPPER%
echo Python script se tu dong chay khi login!
echo.
pause
exit /b 0

:batch_file
echo.
echo Da chon: Batch File
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
    exit /b 1
)

REM Copy truc tiep file .bat vao Startup folder
copy "%BAT_PATH%" "%STARTUP_FOLDER%\" >nul 2>&1

echo.
echo [OK] Da copy file vao Startup folder!
echo File .bat se tu dong chay khi login!
echo.
pause
exit /b 0

:custom_exe
echo.
echo Da chon: Custom Executable
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
    exit /b 1
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

REM Tao file VBScript de tao shortcut
set VBS_FILE=%TEMP%\CreateStartupShortcut.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_FILE%"
echo sLinkFile = "%STARTUP_FOLDER%\%APP_NAME%.lnk" >> "%VBS_FILE%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_FILE%"
echo oLink.TargetPath = "%APP_PATH%" >> "%VBS_FILE%"
echo oLink.WorkingDirectory = "%~dp0" >> "%VBS_FILE%"
echo oLink.Description = "%APP_NAME% - Auto-start on login" >> "%VBS_FILE%"
echo oLink.Save >> "%VBS_FILE%"

REM Chay VBScript
cscript //nologo "%VBS_FILE%" >nul 2>&1

REM Cleanup
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

REM Hoi co muon mo Startup folder khong
choice /c YN /m "Ban co muon mo Startup folder de kiem tra? (Y/N)"

if errorlevel 2 goto :end
if errorlevel 1 goto :open_folder

:open_folder
explorer "%STARTUP_FOLDER%"
goto :end

:end
echo.
echo ========================================
echo   HOAN TAT!
echo ========================================
echo.
echo CACH MO STARTUP FOLDER:
echo - Nhan Windows+R
echo - Gõ: shell:startup
echo - Enter
echo.
echo CACH XOA APP KHOI STARTUP:
echo - Mo Startup folder
echo - Xoa shortcut tuong ung
echo.
pause
exit /b 0
