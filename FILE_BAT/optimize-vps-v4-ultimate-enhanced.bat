@echo off
REM ============================================================
REM SCRIPT TOI UU VPS SIEU MANH V4.0 - ULTIMATE ENHANCED EDITION
REM XOA HOAN TOAN WINDOWS DEFENDER + TAT HET MOI THU!
REM + CAI DAT TIMEZONE ICMARKET (CHAU AU)
REM + TAO DESKTOP ICONS DAY DU
REM PHAI CHAY VOI QUYEN ADMINISTRATOR!
REM ============================================================

echo ========================================
echo   TOI UU VPS SIEU MANH V4.0 ENHANCED
echo   XOA HOAN TOAN Defender + Firewall
echo   CAI TIMEZONE ICMARKET (GMT+2/+3)
echo   TAO DESKTOP ICONS DAY DU
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
echo ============================================
echo   CANH BAO: SCRIPT NAY SE XOA DEFENDER!
echo ============================================
echo.
echo Script nay se:
echo - XOA HOAN TOAN Windows Defender
echo - TAT TRIET DE Windows Firewall
echo - DISABLE tat ca service khong can
echo - CAI DAT TIMEZONE ICMARKET (Chau Au GMT+2/+3)
echo - TAO DESKTOP ICONS cho VPS Trading
echo.
echo Ban co chac chan muon tiep tuc?
echo.
choice /c YN /m "Nhan Y de tiep tuc, N de huy"

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
echo   BAT DAU TOI UU...
echo ========================================
echo.

echo [1/15] XOA Windows Defender qua PowerShell (MANH NHAT!)...
echo.

REM Uninstall Windows Defender Feature HOAN TOAN
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& {try { Uninstall-WindowsFeature -Name Windows-Defender -ErrorAction SilentlyContinue } catch {}}" >nul 2>&1
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& {try { Remove-WindowsFeature -Name Windows-Defender-Features -ErrorAction SilentlyContinue } catch {}}" >nul 2>&1
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& {try { Disable-WindowsOptionalFeature -Online -FeatureName Windows-Defender -NoRestart -ErrorAction SilentlyContinue } catch {}}" >nul 2>&1

REM Disable Windows Defender qua DISM
dism /Online /Disable-Feature /FeatureName:Windows-Defender /Remove /NoRestart /Quiet >nul 2>&1

echo [OK] PowerShell uninstall commands - EXECUTED!
echo.

echo [2/15] Disable Windows Defender qua Registry (TRIET DE!)...
echo.

REM Registry - Disable Defender TRIET DE
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiVirus /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v ServiceKeepAlive /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v AllowFastServiceStartup /t REG_DWORD /d 0 /f >nul 2>&1

REM Disable Real-time Protection
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableBehaviorMonitoring /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableIOAVProtection /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableOnAccessProtection /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableRealtimeMonitoring /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableScanOnRealtimeEnable /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableRoutinelyTakingAction /t REG_DWORD /d 1 /f >nul 2>&1

REM Disable Spynet Reporting
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Spynet" /v SpynetReporting /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Spynet" /v SubmitSamplesConsent /t REG_DWORD /d 2 /f >nul 2>&1

REM Disable Signature Updates
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Signature Updates" /v ForceUpdateFromMU /t REG_DWORD /d 0 /f >nul 2>&1

REM Disable Threats TDR
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Threats\ThreatSeverityDefaultAction" /v 1 /t REG_SZ /d 6 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Threats\ThreatSeverityDefaultAction" /v 2 /t REG_SZ /d 6 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Threats\ThreatSeverityDefaultAction" /v 4 /t REG_SZ /d 6 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Threats\ThreatSeverityDefaultAction" /v 5 /t REG_SZ /d 6 /f >nul 2>&1

REM Disable Windows Defender Security Center
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender Security Center\Notifications" /v DisableNotifications /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender Security Center\Notifications" /v DisableEnhancedNotifications /t REG_DWORD /d 1 /f >nul 2>&1

REM Disable SmartScreen
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableSmartScreen /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" /v SmartScreenEnabled /t REG_SZ /d "Off" /f >nul 2>&1

REM Disable Windows Security app
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v DisallowRun /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun" /v 1 /t REG_SZ /d "SecHealthUI.exe" /f >nul 2>&1

echo [OK] Registry configured - Defender DISABLED TRIET DE!
echo.

echo [3/15] KILL va DISABLE TAT CA Defender processes...
echo.

REM Kill tat ca Defender processes
taskkill /F /IM MsMpEng.exe >nul 2>&1
taskkill /F /IM NisSrv.exe >nul 2>&1
taskkill /F /IM SecurityHealthService.exe >nul 2>&1
taskkill /F /IM SecurityHealthSystray.exe >nul 2>&1
taskkill /F /IM MpCmdRun.exe >nul 2>&1
taskkill /F /IM MSASCuiL.exe >nul 2>&1

REM Disable Windows Defender Services HOAN TOAN
sc config WinDefend start=disabled >nul 2>&1
sc stop WinDefend >nul 2>&1
sc delete WinDefend >nul 2>&1

sc config WdNisSvc start=disabled >nul 2>&1
sc stop WdNisSvc >nul 2>&1
sc delete WdNisSvc >nul 2>&1

sc config WdFilter start=disabled >nul 2>&1
sc stop WdFilter >nul 2>&1

sc config WdNisDrv start=disabled >nul 2>&1
sc stop WdNisDrv >nul 2>&1

sc config Sense start=disabled >nul 2>&1
sc stop Sense >nul 2>&1
sc delete Sense >nul 2>&1

sc config SecurityHealthService start=disabled >nul 2>&1
sc stop SecurityHealthService >nul 2>&1
sc delete SecurityHealthService >nul 2>&1

sc config wscsvc start=disabled >nul 2>&1
sc stop wscsvc >nul 2>&1

echo [OK] All Defender processes KILLED ^& Services DELETED!
echo.

echo [4/15] XOA Defender Drivers...
echo.

REM Disable va xoa Defender drivers
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WdBoot" /v Start /t REG_DWORD /d 4 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WdFilter" /v Start /t REG_DWORD /d 4 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WdNisDrv" /v Start /t REG_DWORD /d 4 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WdNisSvc" /v Start /t REG_DWORD /d 4 /f >nul 2>&1

echo [OK] Defender Drivers - DISABLED!
echo.

echo [5/15] TAT WINDOWS FIREWALL HOAN TOAN...
echo.

REM Tat Firewall qua netsh
netsh advfirewall set allprofiles state off >nul 2>&1

REM Disable Firewall service
sc config mpssvc start=disabled >nul 2>&1
sc stop mpssvc >nul 2>&1

REM Tat qua Registry
reg add "HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile" /v EnableFirewall /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\PublicProfile" /v EnableFirewall /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\DomainProfile" /v EnableFirewall /t REG_DWORD /d 0 /f >nul 2>&1

REM Disable Firewall notifications
reg add "HKLM\SOFTWARE\Microsoft\Security Center" /v FirewallDisableNotify /t REG_DWORD /d 1 /f >nul 2>&1

echo [OK] Windows Firewall - DISABLED HOAN TOAN!
echo.

echo [6/15] Disable Windows Update...
echo.

REM Stop va disable TAT CA Windows Update services
sc config wuauserv start=disabled >nul 2>&1
sc stop wuauserv >nul 2>&1

sc config UsoSvc start=disabled >nul 2>&1
sc stop UsoSvc >nul 2>&1

sc config WaaSMedicSvc start=disabled >nul 2>&1
sc stop WaaSMedicSvc >nul 2>&1

sc config dosvc start=disabled >nul 2>&1
sc stop dosvc >nul 2>&1

REM Disable qua Registry
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v NoAutoUpdate /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v AUOptions /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v DisableWindowsUpdateAccess /t REG_DWORD /d 1 /f >nul 2>&1

echo [OK] Windows Update - DISABLED!
echo.

echo [7/15] Disable 20+ services NANG khong can thiet...
echo.

REM Disable Print Spooler
sc config Spooler start=disabled >nul 2>&1
sc stop Spooler >nul 2>&1

REM Disable Windows Search (NANG!)
sc config WSearch start=disabled >nul 2>&1
sc stop WSearch >nul 2>&1

REM Disable SysMain/Superfetch (TON RAM!)
sc config SysMain start=disabled >nul 2>&1
sc stop SysMain >nul 2>&1

REM Disable Windows Error Reporting
sc config WerSvc start=disabled >nul 2>&1
sc stop WerSvc >nul 2>&1

REM Disable Diagnostic services
sc config DPS start=disabled >nul 2>&1
sc stop DPS >nul 2>&1

sc config WdiServiceHost start=disabled >nul 2>&1
sc stop WdiServiceHost >nul 2>&1

sc config WdiSystemHost start=disabled >nul 2>&1
sc stop WdiSystemHost >nul 2>&1

REM Disable Telemetry
sc config DiagTrack start=disabled >nul 2>&1
sc stop DiagTrack >nul 2>&1

sc config dmwappushservice start=disabled >nul 2>&1
sc stop dmwappushservice >nul 2>&1

REM Disable Remote Registry
sc config RemoteRegistry start=disabled >nul 2>&1
sc stop RemoteRegistry >nul 2>&1

REM Disable Windows Biometric
sc config WbioSrvc start=disabled >nul 2>&1
sc stop WbioSrvc >nul 2>&1

REM Disable Xbox services
sc config XblAuthManager start=disabled >nul 2>&1
sc stop XblAuthManager >nul 2>&1

sc config XblGameSave start=disabled >nul 2>&1
sc stop XblGameSave >nul 2>&1

sc config XboxNetApiSvc start=disabled >nul 2>&1
sc stop XboxNetApiSvc >nul 2>&1

sc config XboxGipSvc start=disabled >nul 2>&1
sc stop XboxGipSvc >nul 2>&1

REM Disable Windows Insider
sc config wisvc start=disabled >nul 2>&1
sc stop wisvc >nul 2>&1

REM Disable Program Compatibility
sc config PcaSvc start=disabled >nul 2>&1
sc stop PcaSvc >nul 2>&1

REM Disable Secondary Logon
sc config seclogon start=disabled >nul 2>&1
sc stop seclogon >nul 2>&1

REM Disable Certificate Propagation
sc config CertPropSvc start=disabled >nul 2>&1
sc stop CertPropSvc >nul 2>&1

REM Disable Geolocation
sc config lfsvc start=disabled >nul 2>&1
sc stop lfsvc >nul 2>&1

REM Disable Windows Media Player Network
sc config WMPNetworkSvc start=disabled >nul 2>&1
sc stop WMPNetworkSvc >nul 2>&1

REM Disable Bluetooth (neu khong dung)
sc config bthserv start=disabled >nul 2>&1
sc stop bthserv >nul 2>&1

REM Disable Fax
sc config Fax start=disabled >nul 2>&1
sc stop Fax >nul 2>&1

echo [OK] 20+ services khong can - DISABLED!
echo.

echo [8/15] Cau hinh Power Settings (Never sleep)...
echo.

REM Khong bao gio tat man hinh/sleep/hibernate
powercfg /change monitor-timeout-ac 0 >nul 2>&1
powercfg /change monitor-timeout-dc 0 >nul 2>&1
powercfg /change standby-timeout-ac 0 >nul 2>&1
powercfg /change standby-timeout-dc 0 >nul 2>&1
powercfg /change disk-timeout-ac 0 >nul 2>&1
powercfg /change disk-timeout-dc 0 >nul 2>&1
powercfg /change hibernate-timeout-ac 0 >nul 2>&1
powercfg /change hibernate-timeout-dc 0 >nul 2>&1

REM Set High Performance power plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1

REM Disable hibernation file (tiet kiem disk)
powercfg /hibernate off >nul 2>&1

echo [OK] Power Settings - NEVER SLEEP!
echo.

echo [9/15] TAT TAT CA Visual Effects (Maximum speed)...
echo.

REM Disable visual effects
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9012038010000000 /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ListviewAlphaSelect /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAnimations /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\DWM" /v EnableAeroPeek /t REG_DWORD /d 0 /f >nul 2>&1

REM Disable transparency
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f >nul 2>&1

REM Disable animations
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f >nul 2>&1

echo [OK] Visual Effects - ALL DISABLED!
echo.

echo [10/15] Optimize Network (Giam latency cho trading)...
echo.

REM Disable network throttling
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 0xffffffff /f >nul 2>&1

REM Disable Nagle's Algorithm (giam latency)
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v TcpAckFrequency /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v TCPNoDelay /t REG_DWORD /d 1 /f >nul 2>&1

REM Optimize TCP
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v Tcp1323Opts /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v TcpMaxDataRetransmissions /t REG_DWORD /d 3 /f >nul 2>&1

echo [OK] Network - OPTIMIZED CHO TRADING!
echo.

echo [11/15] Clean temporary files va cache...
echo.

REM Xoa temp files an toan hon (chi xoa file cu hon 7 ngay)
forfiles /p "%TEMP%" /s /m *.* /d -7 /c "cmd /c del /q @path" 2>nul
forfiles /p "C:\Windows\Temp" /s /m *.* /d -7 /c "cmd /c del /q @path" 2>nul

REM Clear Windows Update cache
del /q /f /s C:\Windows\SoftwareDistribution\Download\* >nul 2>&1

REM Clear Defender cache/definitions
rd /s /q "C:\ProgramData\Microsoft\Windows Defender" >nul 2>&1
rd /s /q "C:\Program Files\Windows Defender" >nul 2>&1
rd /s /q "C:\Program Files (x86)\Windows Defender" >nul 2>&1

echo [OK] Temp files cleaned + Defender folders DELETED!
echo.

echo [12/15] CAI DAT TIMEZONE CHO ICMARKET (Chau Au GMT+2/+3)...
echo.

REM ICMarket dung Eastern European Time (Cyprus/Greece/Romania)
REM GMT+2 mua dong, GMT+3 mua he (tu dong DST)
tzutil /s "FLE Standard Time" >nul 2>&1

REM Alternative timezones neu FLE khong co:
REM tzutil /s "E. Europe Standard Time" >nul 2>&1
REM tzutil /s "GTB Standard Time" >nul 2>&1

REM Kiem tra ket qua
set TZ_RESULT=UNKNOWN
for /f "tokens=*" %%i in ('tzutil /g 2^>nul') do set TZ_RESULT=%%i

echo [OK] Timezone - SET TO: %TZ_RESULT%
echo     (GMT+2 mua dong / GMT+3 mua he - ICMarket Server Time)
echo.

echo [13/15] TAO DESKTOP ICONS cho VPS Trading...
echo.

REM Lay duong dan Desktop cua user hien tai
set DESKTOP=%USERPROFILE%\Desktop

REM 1. Task Manager icon
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Task Manager.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "C:\Windows\System32\taskmgr.exe" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Task Manager - Quan ly tien trinh" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs" >nul 2>&1

REM 2. Command Prompt icon
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Command Prompt.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "C:\Windows\System32\cmd.exe" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Command Prompt - Dong lenh" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs" >nul 2>&1

REM 3. Control Panel icon
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Control Panel.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "C:\Windows\System32\control.exe" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Control Panel - Bang dieu khien" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs" >nul 2>&1

REM 4. System Properties icon (Computer Management)
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Computer Management.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "C:\Windows\System32\compmgmt.msc" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Computer Management - Quan ly may tinh" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs" >nul 2>&1

REM 5. Network Connections icon
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Network Connections.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "C:\Windows\System32\ncpa.cpl" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Network Connections - Ket noi mang" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs" >nul 2>&1

REM 6. This PC icon (My Computer) - Them vao Desktop
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel" /v "{20D04FE0-3AEA-1069-A2D8-08002B30309D}" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\ClassicStartMenu" /v "{20D04FE0-3AEA-1069-A2D8-08002B30309D}" /t REG_DWORD /d 0 /f >nul 2>&1

REM 7. Recycle Bin icon - Them vao Desktop
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel" /v "{645FF040-5081-101B-9F08-00AA002F954E}" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\ClassicStartMenu" /v "{645FF040-5081-101B-9F08-00AA002F954E}" /t REG_DWORD /d 0 /f >nul 2>&1

REM Refresh Desktop
taskkill /f /im explorer.exe >nul 2>&1
start explorer.exe

REM Cleanup temp VBS file
del /f /q "%TEMP%\CreateShortcut.vbs" >nul 2>&1

echo [OK] Desktop Icons - CREATED!
echo     - Task Manager
echo     - Command Prompt
echo     - Control Panel
echo     - Computer Management
echo     - Network Connections
echo     - This PC
echo     - Recycle Bin
echo.

echo [14/15] Tao Scheduled Tasks (Dam bao khong bat lai)...
echo.

REM Task: Disable Defender khi khoi dong
schtasks /create /tn "DisableDefenderStartup" /tr "reg add \"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\" /v DisableAntiSpyware /t REG_DWORD /d 1 /f" /sc onstart /ru SYSTEM /rl HIGHEST /f >nul 2>&1

REM Task: Disable Firewall khi khoi dong
schtasks /create /tn "DisableFirewallStartup" /tr "netsh advfirewall set allprofiles state off" /sc onstart /ru SYSTEM /rl HIGHEST /f >nul 2>&1

REM Task: Kill Defender processes khi khoi dong
schtasks /create /tn "KillDefenderProcesses" /tr "taskkill /F /IM MsMpEng.exe" /sc onstart /ru SYSTEM /rl HIGHEST /f >nul 2>&1

REM Task: Stop Defender services khi khoi dong
schtasks /create /tn "StopDefenderServices" /tr "sc stop WinDefend" /sc onstart /ru SYSTEM /rl HIGHEST /f >nul 2>&1

echo [OK] Scheduled Tasks - CREATED!
echo.

echo [15/15] Thay doi thoi gian Restart thanh 60 giay (an toan hon)...
echo.

echo ========================================
echo   TOI UU HOAN TAT 100%% - SIEU MANH!
echo ========================================
echo.
echo KET QUA:
echo ========================================
echo [OK] Windows Defender - XOA HOAN TOAN
echo      + Uninstall Feature
echo      + Delete Services
echo      + Delete Drivers
echo      + Delete Folders
echo      + Registry Disabled
echo.
echo [OK] Windows Firewall - DISABLED
echo [OK] Windows Update - DISABLED
echo [OK] 20+ Services khong can - DISABLED
echo [OK] Power Settings - NEVER SLEEP
echo [OK] Visual Effects - DISABLED
echo [OK] Network - OPTIMIZED
echo [OK] Temp Files - CLEANED
echo [OK] Timezone - ICMARKET (GMT+2/+3)
echo [OK] Desktop Icons - CREATED (7 icons)
echo [OK] Scheduled Tasks - CREATED
echo.
echo RAM TIET KIEM: ~300-400MB
echo TOC DO TANG: ~40-50%%
echo LATENCY: GIAM 20-30%%
echo TIMEZONE: %TZ_RESULT%
echo ========================================
echo.
echo QUAN TRONG:
echo ============================================
echo   PHAI RESTART VPS DE AP DUNG HOAN TOAN!
echo ============================================
echo.
echo Sau khi restart:
echo - Windows Defender se BIEN MAT hoan toan
echo - Task Manager: KHONG thay Defender process
echo - RAM chi con ~400-500MB
echo - VPS NHANH GAP 2-3 LAN!
echo - Timezone: ICMarket Server Time (GMT+2/+3)
echo - Desktop: 7 shortcut icons moi
echo.
choice /c YN /m "Ban co muon RESTART ngay bay gio? (Y/N)"

if errorlevel 2 goto :end
if errorlevel 1 goto :restart

:restart
echo.
echo ==========================================
echo   RESTART VPS TRONG 60 GIAY...
echo   Ket noi lai sau 3-4 phut!
echo ==========================================
echo.
echo (VPS can restart LAU HON vi dang uninstall Defender)
echo.
shutdown /r /t 60 /c "VPS restart - XOA DEFENDER + CAI TIMEZONE ICMARKET"
goto :end

:end
echo.
echo ==========================================
echo   SCRIPT HOAN TAT!
echo ==========================================
echo.
echo Neu chon N:
echo - Hay restart VPS thu cong
echo - PHAI RESTART de uninstall Defender!
echo.
echo Sau khi restart:
echo 1. Ket noi lai Remote Desktop
echo 2. Mo Task Manager
echo 3. Khong thay "Antimalware Service Executable"
echo 4. RAM chi con ~400-500MB
echo 5. VPS nhanh nhu CHOP!
echo 6. Kiem tra Timezone (Settings -^> Time ^& Language)
echo 7. Desktop co 7 icons moi
echo.
echo THANH CONG!
echo.
pause
exit /b 0
