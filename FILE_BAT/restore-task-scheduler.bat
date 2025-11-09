@echo off
REM ============================================================
REM SCRIPT PHUC HOI TASK SCHEDULER (TINH NANG HEN GIO WINDOWS)
REM Repair/Enable Task Scheduler Service
REM PHAI CHAY VOI QUYEN ADMINISTRATOR!
REM ============================================================

echo ========================================
echo   PHUC HOI TASK SCHEDULER
echo   Restore Task Scheduler Service
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

echo.
echo Dang kiem tra trang thai Task Scheduler...
echo.

REM Kiem tra trang thai hien tai
sc query Schedule >nul 2>&1
if %errorLevel% equ 0 (
    echo [THONG TIN] Task Scheduler service TON TAI trong he thong
    echo.
) else (
    echo [CANH BAO] Task Scheduler service KHONG TON TAI!
    echo            Service co the da bi xoa boi script khac
    echo.
)

REM Hien thi trang thai chi tiet
echo Trang thai hien tai:
echo ========================================
sc query Schedule 2>nul
if %errorLevel% neq 0 (
    echo Service: Schedule
    echo State: NOT FOUND (Da bi xoa)
)
echo ========================================
echo.

echo.
echo Script nay se:
echo - ENABLE Task Scheduler service (neu bi disable)
echo - START Task Scheduler service (neu bi stop)
echo - REPAIR registry keys (neu bi thay doi)
echo - KHONG LAM GI neu Task Scheduler dang hoat dong binh thuong
echo.
choice /c YN /m "Ban co muon tiep tuc? (Y/N)"

if errorlevel 2 goto :cancelled
if errorlevel 1 goto :start

:cancelled
echo.
echo Script da bi huy!
pause
exit /b 0

:start
echo.
echo ========================================
echo   BAT DAU PHUC HOI...
echo ========================================
echo.

echo [1/7] Enable Task Scheduler Service...
echo.

REM Enable Task Scheduler service
sc config Schedule start=auto >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Service startup type - SET TO AUTOMATIC
) else (
    echo [WARNING] Khong the thay doi startup type (co the service khong ton tai)
)
echo.

echo [2/7] Start Task Scheduler Service...
echo.

REM Start Task Scheduler service
sc start Schedule >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Service STARTED successfully
) else (
    REM Kiem tra xem service da chay chua
    sc query Schedule | find "RUNNING" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] Service da chay tu truoc (RUNNING)
    ) else (
        echo [WARNING] Khong the start service (kiem tra Event Viewer de biet ly do)
    )
)
echo.

echo [3/7] Restore Registry Keys for Task Scheduler...
echo.

REM Tao lai registry keys co the da bi xoa hoac thay doi
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Schedule" /v Start /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Schedule" /v Type /t REG_DWORD /d 32 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Schedule" /v ErrorControl /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Schedule" /v ImagePath /t REG_EXPAND_SZ /d "%%SystemRoot%%\system32\svchost.exe -k netsvcs -p" /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Schedule" /v DisplayName /t REG_SZ /d "Task Scheduler" /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Schedule" /v ObjectName /t REG_SZ /d "LocalSystem" /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Schedule" /v Description /t REG_SZ /d "Enables a user to configure and schedule automated tasks on this computer." /f >nul 2>&1

echo [OK] Registry keys - RESTORED
echo.

echo [4/7] Enable Task Scheduler Dependencies...
echo.

REM Enable RPC service (Task Scheduler phu thuoc vao RPC)
sc config RpcSs start=auto >nul 2>&1
sc start RpcSs >nul 2>&1

REM Enable RPC Endpoint Mapper
sc config RpcEptMapper start=auto >nul 2>&1
sc start RpcEptMapper >nul 2>&1

REM Enable DCOM Server Process Launcher
sc config DcomLaunch start=auto >nul 2>&1
sc start DcomLaunch >nul 2>&1

echo [OK] Dependencies - ENABLED
echo.

echo [5/7] Repair Task Scheduler Permissions...
echo.

REM Tao lai thu muc Task Scheduler neu khong ton tai
if not exist "C:\Windows\System32\Tasks" (
    mkdir "C:\Windows\System32\Tasks" >nul 2>&1
    echo [OK] Created Tasks folder
) else (
    echo [OK] Tasks folder already exists
)

REM Set permissions cho thu muc Tasks
icacls "C:\Windows\System32\Tasks" /grant "SYSTEM:(OI)(CI)F" /T >nul 2>&1
icacls "C:\Windows\System32\Tasks" /grant "Administrators:(OI)(CI)F" /T >nul 2>&1

echo [OK] Permissions - SET
echo.

echo [6/7] Remove potential blocking registry keys...
echo.

REM Xoa cac registry keys co the chan Task Scheduler
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\Task Scheduler" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Configuration\DisableScheduledTasks" /f >nul 2>&1

echo [OK] Blocking keys - REMOVED (neu co)
echo.

echo [7/7] Verify Task Scheduler Status...
echo.

REM Restart service de ap dung thay doi
sc stop Schedule >nul 2>&1
timeout /t 2 /nobreak >nul
sc start Schedule >nul 2>&1
timeout /t 2 /nobreak >nul

REM Kiem tra trang thai cuoi cung
sc query Schedule | find "RUNNING" >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Task Scheduler - RUNNING
    set SERVICE_STATUS=RUNNING
) else (
    echo [WARNING] Task Scheduler - NOT RUNNING (kiem tra Event Viewer)
    set SERVICE_STATUS=NOT_RUNNING
)
echo.

echo ========================================
echo   KET QUA PHUC HOI
echo ========================================
echo.

REM Hien thi trang thai chi tiet
sc query Schedule 2>nul
echo.

echo ========================================
echo   TONG KET
echo ========================================
echo.
echo [OK] Service Startup Type - AUTOMATIC
echo [OK] Registry Keys - RESTORED
echo [OK] Dependencies - ENABLED
echo [OK] Permissions - SET
echo [OK] Blocking Keys - REMOVED

if "%SERVICE_STATUS%"=="RUNNING" (
    echo [OK] Task Scheduler - RUNNING SUCCESSFULLY
    echo.
    echo THANH CONG! Task Scheduler da duoc phuc hoi!
    echo.
    echo Ban co the su dung:
    echo - Control Panel ^> Administrative Tools ^> Task Scheduler
    echo - Lenh: taskschd.msc
    echo - Lenh: schtasks /query
) else (
    echo [WARNING] Task Scheduler - CHUA CHAY
    echo.
    echo THONG BAO:
    echo - Service da duoc enable nhung chua start thanh cong
    echo - Co the can restart VPS de ap dung hoan toan
    echo - Hoac kiem tra Event Viewer (eventvwr.msc) de xem loi
    echo.
    choice /c YN /m "Ban co muon RESTART VPS de ap dung hoan toan? (Y/N)"

    if errorlevel 2 goto :end
    if errorlevel 1 goto :restart
)

goto :end

:restart
echo.
echo ==========================================
echo   RESTART VPS TRONG 60 GIAY...
echo ==========================================
echo.
shutdown /r /t 60 /c "VPS restart - PHUC HOI TASK SCHEDULER"
echo VPS se restart sau 60 giay.
echo Ket noi lai sau 2-3 phut va kiem tra Task Scheduler.
echo.
goto :end

:end
echo.
echo ========================================
echo   SCRIPT HOAN TAT!
echo ========================================
echo.
echo CACH KIEM TRA TASK SCHEDULER:
echo.
echo 1. Mo Run (Windows+R)
echo 2. Nhap: taskschd.msc
echo 3. Enter
echo.
echo Hoac su dung lenh:
echo    schtasks /query
echo    sc query Schedule
echo.
pause
exit /b 0
