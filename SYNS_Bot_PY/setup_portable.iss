; SYNS Bot System - Inno Setup Script (Portable Python Package)
; Tạo file SETUP.EXE installer chuyên nghiệp cho Windows

#define MyAppName "SYNS Bot System - Portable"
#define MyAppVersion "1.0"
#define MyAppPublisher "SYNS Trading"
#define MyAppURL "http://dungalading.duckdns.org"
#define MyAppExeName "START_0123_BOT.bat"

[Setup]
; Thông tin cơ bản
AppId={{8F3C4D2E-9A1B-4C5D-8E7F-6A5B4C3D2E1F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Đường dẫn cài đặt mặc định
DefaultDirName={autopf}\SYNS_Bot_Portable
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output setup file
OutputDir=..\PACKAGES
OutputBaseFilename=SYNS_Bot_Portable_Setup
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
; Python Embedded
Source: "python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs

; Bot Python files
Source: "sync_http80_sender.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "sync1_sender_optimized.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "sync2_data_receiver.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "sync_server80data.py"; DestDir: "{app}"; Flags: ignoreversion

; Config và launcher
Source: "bot_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "START_0123_BOT.bat"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_PORTABLE_PACKAGE.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
; Start Menu shortcuts
Name: "{group}\SYNS Bot - Start Launcher"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Bot 1 - Sender (VPS)"; Filename: "{app}\python\python.exe"; Parameters: """{app}\sync1_sender_optimized.py"""; WorkingDir: "{app}"; Comment: "Bot 1 - VPS Sender"
Name: "{group}\Bot 2 - Receiver (Local)"; Filename: "{app}\python\python.exe"; Parameters: """{app}\sync2_data_receiver.py"""; WorkingDir: "{app}"; Comment: "Bot 2 - Local Receiver"
Name: "{group}\Bot 3 - Integrated"; Filename: "{app}\python\python.exe"; Parameters: """{app}\sync_server80data.py"""; WorkingDir: "{app}"; Comment: "Bot 3 - 2-in-1"
Name: "{group}\Open Config File"; Filename: "notepad.exe"; Parameters: """{app}\bot_config.json"""; Comment: "Edit bot_config.json"
Name: "{group}\Open Installation Folder"; Filename: "{app}"; Comment: "Mở thư mục cài đặt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop icon
Name: "{autodesktop}\SYNS Bot Launcher"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch icon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\SYNS Bot"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Cài đặt thư viện Python sau khi cài xong
Filename: "{app}\python\python.exe"; Parameters: "-m ensurepip"; StatusMsg: "Installing pip..."; Flags: runhidden
Filename: "{app}\python\python.exe"; Parameters: "-m pip install Flask==3.0.0 flask-cors==4.0.0 requests==2.31.0"; StatusMsg: "Installing Python libraries..."; Flags: runhidden

; Chạy bot sau khi cài xong (tùy chọn)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Xóa các file tạo ra khi chạy
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\python\Lib\site-packages"

[Code]
// Custom code để kiểm tra Python installation
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('SYNS Bot System sẽ được cài đặt.' + #13#10 + #13#10 +
         'Bao gồm:' + #13#10 +
         '- Python 3.10 Embedded' + #13#10 +
         '- 4 Bot files' + #13#10 +
         '- Auto-install Flask, Requests, Flask-CORS' + #13#10 + #13#10 +
         'Cài đặt cần ~200MB dung lượng.', mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  PthFile: String;
  PthContent: TArrayOfString;
  I: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Enable pip by uncommenting "import site" in python310._pth
    PthFile := ExpandConstant('{app}\python\python310._pth');
    if LoadStringsFromFile(PthFile, PthContent) then
    begin
      for I := 0 to GetArrayLength(PthContent) - 1 do
      begin
        if Pos('#import site', PthContent[I]) > 0 then
          PthContent[I] := 'import site';  // Remove #
      end;
      SaveStringsToFile(PthFile, PthContent, False);
    end;

    MsgBox('Cài đặt hoàn tất!' + #13#10 + #13#10 +
           'Để chạy bot:' + #13#10 +
           '1. Mở Config File từ Start Menu' + #13#10 +
           '2. Chỉnh đường dẫn folder cho đúng' + #13#10 +
           '3. Chạy SYNS Bot Launcher', mbInformation, MB_OK);
  end;
end;
