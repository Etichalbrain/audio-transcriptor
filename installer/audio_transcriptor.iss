; Inno Setup script for the Windows installer.
; Build after PyInstaller produced dist\AudioTranscriptor\ (AudioTranscriptorWindows.spec).
; Output: installer\Output\AudioTranscriptorSetup-<version>.exe

#define MyAppName "AudioTranscriptor"
#define MyAppVersion "1.0.2"
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

; English comes first so it is the fallback. With ShowLanguageDialog at its
; default (yes) Inno Setup preselects the language of the Windows UI and only
; asks when that language is not available. Each language shows its own
; privacy and disclaimer note (InfoBeforeFile) before the license page.
; The .txt notices carry a UTF-8 BOM, which Inno Setup needs to read accents.
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"; InfoBeforeFile: "README-INSTALL-en.txt"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"; InfoBeforeFile: "LEGGIMI.txt"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"; InfoBeforeFile: "README-INSTALL-de.txt"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"; InfoBeforeFile: "README-INSTALL-fr.txt"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\AudioTranscriptor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
