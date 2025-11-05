; SYNS Bot System - Inno Setup Script (EXE Package)
; Tạo file SETUP.EXE installer cho 4 bot .exe files

#define MyAppName "SYNS Bot System - EXE"
#define MyAppVersion "1.0"
#define MyAppPublisher "SYNS Trading"
#define MyAppURL "http://dungalading.duckdns.org"
#define MyAppExeName "START_0123_BOT_EXE.bat"

[Setup]
; Thông tin cơ bản
AppId={{9F4D5E3F-0B2C-5D6E-9F8G-7B6C5D4E3F2G}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Đường dẫn cài đặt mặc định
DefaultDirName={autopf}\SYNS_Bot_EXE
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output setup file
OutputDir=..\PACKAGES
OutputBaseFilename=SYNS_Bot_EXE_Setup
SetupIconFile=compiler:SetupClassicIcon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Quyền admin (cần cho port 80)
PrivilegesRequired=admin

; Hỗ trợ 64-bit
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Tạo shortcut trên Desktop"; GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Tạo Quick Launch icon"; GroupDescription: "Shortcuts:"; Flags: unchecked

[Files]
; NOTE: Installer này giả định bạn đã build 4 .exe files trong dist/ folder
; Chạy build_exe.bat trước khi compile installer này

; 4 Bot EXE files
Source: "..\dist\Bot0_HTTP80_Sender.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\Bot1_Sender_Optimized.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\Bot2_Data_Receiver.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\Bot3_Server_Integrated.exe"; DestDir: "{app}"; Flags: ignoreversion

; Config và launcher
Source: "bot_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "START_0123_BOT_EXE.bat"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README_EXE_PACKAGE.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
; Start Menu shortcuts
Name: "{group}\SYNS Bot - Start Launcher"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Bot 1 - Sender (VPS)"; Filename: "{app}\Bot1_Sender_Optimized.exe"; WorkingDir: "{app}"; Comment: "Bot 1 - VPS Sender"
Name: "{group}\Bot 2 - Receiver (Local)"; Filename: "{app}\Bot2_Data_Receiver.exe"; WorkingDir: "{app}"; Comment: "Bot 2 - Local Receiver"
Name: "{group}\Bot 3 - Integrated"; Filename: "{app}\Bot3_Server_Integrated.exe"; WorkingDir: "{app}"; Comment: "Bot 3 - 2-in-1"
Name: "{group}\Bot 0 - Sender (Variant)"; Filename: "{app}\Bot0_HTTP80_Sender.exe"; WorkingDir: "{app}"; Comment: "Bot 0 - Alternative Sender"
Name: "{group}\Open Config File"; Filename: "notepad.exe"; Parameters: """{app}\bot_config.json"""; Comment: "Edit bot_config.json"
Name: "{group}\Open Installation Folder"; Filename: "{app}"; Comment: "Mở thư mục cài đặt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop icon
Name: "{autodesktop}\SYNS Bot Launcher"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch icon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\SYNS Bot"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Chạy bot sau khi cài xong (tùy chọn)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Xóa các file log/cache tạo ra khi chạy
Type: files; Name: "{app}\*.log"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('SYNS Bot System (EXE Version) sẽ được cài đặt.' + #13#10 + #13#10 +
         'Bao gồm:' + #13#10 +
         '- 4 Bot .exe files (standalone)' + #13#10 +
         '- bot_config.json' + #13#10 +
         '- Launcher scripts' + #13#10 + #13#10 +
         'Không cần Python!' + #13#10 +
         'Cài đặt cần ~60MB dung lượng.', mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Cài đặt hoàn tất!' + #13#10 + #13#10 +
           'LƯU Ý QUAN TRỌNG:' + #13#10 +
           '1. Windows Defender có thể chặn .exe files' + #13#10 +
           '   → Thêm exception nếu cần' + #13#10 +
           '2. Chỉnh bot_config.json trước khi chạy' + #13#10 +
           '   (đường dẫn folder)' + #13#10 +
           '3. Chạy với quyền Administrator' + #13#10 + #13#10 +
           'Để chạy: Start Menu → SYNS Bot Launcher', mbInformation, MB_OK);
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  // Check if .exe files exist in dist/ folder
  if not FileExists(ExpandConstant('{src}\..\dist\Bot1_Sender_Optimized.exe')) then
  begin
    Result := 'ERROR: Bot .exe files not found!' + #13#10 + #13#10 +
              'Bạn phải BUILD .exe files trước!' + #13#10 +
              'Chạy: build_exe.bat' + #13#10 + #13#10 +
              'Sau đó compile lại installer này.';
    exit;
  end;
  Result := '';
end;
