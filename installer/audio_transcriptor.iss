; Inno Setup script for the Windows installer.
; Build after PyInstaller produced dist\AudioTranscriptor\ (AudioTranscriptorWindows.spec).
; Output: installer\Output\AudioTranscriptorSetup-<version>.exe

#define MyAppName "AudioTranscriptor"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Antonio Aversa"
#define MyAppExeName "AudioTranscriptor.exe"

[Setup]
AppId={{8E1B4C2A-5F3D-4B77-9C1E-6A2D0F9B7E31}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\AudioTranscriptor
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
; Privacy and disclaimer note shown before the license page.
InfoBeforeFile=LEGGIMI.txt
; Per-user install: no administrator rights required.
SetupIconFile=..\assets\AudioTranscriptor.ico
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=AudioTranscriptorSetup-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\AudioTranscriptor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
