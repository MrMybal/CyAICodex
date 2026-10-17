#define AppVersion "0.6.3"
[Setup]
AppId={{89159947-E319-4B18-9A29-F4016E32BF26}
AppName=CyAICodex
AppVersion={#AppVersion}
AppPublisher=Cyberalien
AppPublisherURL=https://github.com/MrMybal/CyAICodex
DefaultDirName={localappdata}\Programs\CyAICodex
DefaultGroupName=CyAICodex
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=CyAICodex-Setup-{#AppVersion}
SetupIconFile=..\methodes\web\logo-cy-book-transparent.ico
UninstallDisplayIcon={app}\CyAICodex.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
DisableProgramGroupPage=yes
DisableDirPage=auto
UsePreviousTasks=yes
LanguageDetectionMethod=none

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[CustomMessages]
french.DesktopShortcut=Créer un raccourci sur le bureau
english.DesktopShortcut=Create a desktop shortcut
french.Startup=Démarrer CyAICodex avec Windows
english.Startup=Start CyAICodex with Windows
french.StopFailed=CyAICodex ne peut pas être arrêté. Quittez-le depuis la zone de notification et réessayez.
english.StopFailed=CyAICodex could not be stopped. Quit it from the notification area and retry.
french.DataFailed=La bibliothèque n’a pas pu être préparée. Vos données d’origine sont conservées. Consultez le journal ou relancez sans migration.
english.DataFailed=The library could not be prepared. Your original data is preserved. Check the log or retry without migration.

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; Flags: unchecked
Name: "startup"; Description: "{cm:Startup}"

[Files]
Source: "..\dist\CyAICodex\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "installed.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Readme-v0.6.3.txt"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: PrepareData

[Icons]
Name: "{autoprograms}\CyAICodex"; Filename: "{app}\CyAICodex.exe"
Name: "{autodesktop}\CyAICodex"; Filename: "{app}\CyAICodex.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Methode"; ValueData: """{app}\CyAICodex.exe"" --no-open"; Tasks: startup; Flags: uninsdeletevalue

[Run]
Filename: "{app}\CyAICodex.exe"; Description: "CyAICodex"; Flags: nowait postinstall skipifsilent; Check: DataReady
Filename: "{app}\CyAICodex.exe"; Parameters: "--no-open"; Flags: nowait runhidden; Check: SilentStart

[Code]
var
  InstallMutex: THandle;
  Prepared: Boolean;

function CreateMutex(lpMutexAttributes: Integer; bInitialOwner: Boolean; lpName: String): THandle;
  external 'CreateMutexW@kernel32.dll stdcall';
function CloseHandle(hObject: THandle): Boolean;
  external 'CloseHandle@kernel32.dll stdcall';

function DataReady: Boolean;
begin
  Result := Prepared;
end;

function SilentStart: Boolean;
begin
  Result := Prepared and WizardSilent and (ExpandConstant('{param:NOLAUNCH|0}') <> '1');
end;

procedure Unlock;
begin
  if InstallMutex <> 0 then begin
    CloseHandle(InstallMutex);
    InstallMutex := 0;
  end;
end;

procedure InitializeWizard;
var Tasks: String;
begin
  { Reflect a startup preference changed in the app since the previous install. }
  if RegKeyExists(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{89159947-E319-4B18-9A29-F4016E32BF26}_is1') then begin
    Tasks := '';
    if WizardIsTaskSelected('desktopicon') then Tasks := 'desktopicon';
    if RegValueExists(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', 'Methode') then
      Tasks := Tasks + ',startup';
    WizardSelectTasks(Tasks);
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var Code: Integer;
begin
  Result := '';
  if InstallMutex = 0 then InstallMutex := CreateMutex(0, False, 'Local\CyAICodex-Install');
  if FileExists(ExpandConstant('{app}\CyAICodex.exe')) then begin
    if not Exec(ExpandConstant('{app}\CyAICodex.exe'), '--stop', '', SW_HIDE, ewWaitUntilTerminated, Code) then
      Result := CustomMessage('StopFailed')
    else if Code <> 0 then Result := CustomMessage('StopFailed');
    Sleep(1000);
  end;
end;

procedure PrepareData;
var Code: Integer; Args, Legacy: String;
begin
    Args := '--finish-install';
    if WizardIsTaskSelected('startup') then Args := Args + ' --startup enabled'
    else Args := Args + ' --startup disabled';
    Legacy := ExpandConstant('{param:LEGACYDATA|}');
    if Legacy <> '' then Args := Args + ' --legacy-data ' + AddQuotes(Legacy);
    Prepared := Exec(ExpandConstant('{app}\CyAICodex.exe'), Args, '', SW_HIDE, ewWaitUntilTerminated, Code);
    Prepared := Prepared and (Code = 0);
    if not Prepared then SuppressibleMsgBox(CustomMessage('DataFailed'), mbError, MB_OK, IDOK);
    Unlock;
end;

function GetCustomSetupExitCode: Integer;
begin
  if Prepared then Result := 0 else Result := 1;
end;

procedure DeinitializeSetup;
begin
  Unlock;
end;

function InitializeUninstall: Boolean;
var Code: Integer;
begin
  InstallMutex := CreateMutex(0, False, 'Local\CyAICodex-Install');
  Result := Exec(ExpandConstant('{app}\CyAICodex.exe'), '--stop', '', SW_HIDE, ewWaitUntilTerminated, Code);
  Result := Result and (Code = 0);
  if not Result then Unlock;
  Sleep(1000);
end;

procedure DeinitializeUninstall;
begin
  Unlock;
end;
