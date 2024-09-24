#include <idp.iss>

#define SWATPlusVersion "3.0"
#define SWATPlusPatchVersion "8"
#define SWATPlusToolsPatchVersion "8"
#define QSWATPlusVersion "3.0"
#define QSWATPlusPatchVersion "0"
#define ToolboxVersion "2.0"
#define ToolboxPatchVersion "7"
#define ModelVersion "61.0.1"
#define SWATURL "https://swat.tamu.edu/"

[Setup]
AppId={{31E602D4-5220-421E-BE21-8F0A111FC4AD}
AppName=SWAT+ Tools
AppVersion={#SWATPlusVersion}.{#SWATPlusToolsPatchVersion}
DefaultDirName=C:\SWAT\SWATPlus
PrivilegesRequired=lowest
SetupIconFile=build\icons\256x256.ico
DisableProgramGroupPage=yes
AppPublisher=Texas A&M AgriLife Research
AppPublisherURL={#SWATURL}
AppSupportURL={#SWATURL}
AppUpdatesURL={#SWATURL}
OutputBaseFilename=swatplus-windows-installer-{#SWATPlusVersion}.{#SWATPlusToolsPatchVersion}
OutputDir=output
ArchitecturesInstallIn64BitMode=x64
LicenseFile=..\license.txt
EnableDirDoesntExistWarning=True
DirExistsWarning=no
DisableDirPage=no

[Files]
Source: "data\downloads\QSWATPlusinstall{#QSWATPlusVersion}.{#QSWATPlusPatchVersion}.exe"; DestDir: "{tmp}"; Components: qswat; 
Source: "dist\swatplus-editor-{#SWATPlusVersion}.{#SWATPlusPatchVersion}-win32-x64.exe"; DestDir: "{tmp}"; Components: editor; 
Source: "data\downloads\SWATPlusToolbox-v{#ToolboxVersion}.{#ToolboxPatchVersion}.exe"; DestDir: "{tmp}"; Components: toolbox;  
Source: "{tmp}\swatplus_soils.zip"; DestDir: "{tmp}"; Flags: external; ExternalSize: 44190170; Components: soils
Source: "{tmp}\swatplus_wgn.zip"; DestDir: "{tmp}"; Flags: external; ExternalSize: 188325993; Components: wgn

[Dirs]
Name: "{app}\Databases"

[Components]
Name: "qswat"; Description: "QSWAT+ QGIS interface {#QSWATPlusVersion}.{#QSWATPlusPatchVersion}"; Types: typical full custom
Name: "qswat\swatGraph"; Description: "SWATGraph tool.  Not needed if you have QSWAT."; Types: typical full custom
Name: "qswat\manual"; Description: "QSWAT+ user manual"; Types: typical full custom
Name: "editor"; Description: "SWAT+ Editor {#SWATPlusVersion}.{#SWATPlusPatchVersion} (includes model rev. {#ModelVersion})"; Types: typical full custom
Name: "toolbox"; Description: "SWAT+ Toolbox {#ToolboxVersion}.{#ToolboxPatchVersion}"; Types: typical full custom
Name: "wgn"; Description: "Global weather generator data for SWAT+ (download)"; Types: full
Name: "soils"; Description: "US SSURGO/STATSGO soil data for SWAT+ (download)"; Types: full

[Types]
Name: "typical"; Description: "Typical installation"
Name: "full"; Description: "Full installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Files]
Source: "data\downloads\SWATPlus\*"; DestDir: "{app}"; Excludes: "\Tools\SWATGraph, \Documents"; Components: qswat; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "data\downloads\SWATPlus\Tools\SWATGraph\runSWATGraph.bat"; DestDir: "{app}\Tools\SWATGraph"; Components: qswat\swatGraph; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "data\downloads\SWATPlus\Documents\QSWATPlus Manual_v{#QSWATPlusVersion}.pdf"; DestDir: "{app}\Documents"; Components: qswat\manual;  Flags: ignoreversion recursesubdirs createallsubdirs

[Run]
Filename: "{tmp}\QSWATPlusinstall{#QSWATPlusVersion}.{#QSWATPlusPatchVersion}.exe"; WorkingDir: "{tmp}"; Flags: skipifdoesntexist skipifsilent
Filename: "{tmp}\swatplus-editor-{#SWATPlusVersion}.{#SWATPlusPatchVersion}-win32-x64.exe"; Parameters: "/D=""{app}\SWATPlusEditor"""; WorkingDir: "{tmp}"; Flags: skipifdoesntexist skipifsilent
Filename: "{tmp}\SWATPlusToolbox-v{#ToolboxVersion}.{#ToolboxPatchVersion}.exe"; WorkingDir: "{tmp}"; Flags: skipifdoesntexist skipifsilent shellexec
Filename: "{tmp}\QSWATPlusinstall{#QSWATPlusVersion}.{#QSWATPlusPatchVersion}.exe"; Parameters: "/VERYSILENT /CURRENTUSER"; WorkingDir: "{tmp}"; Flags: skipifdoesntexist skipifnotsilent
Filename: "{tmp}\swatplus-editor-{#SWATPlusVersion}.{#SWATPlusPatchVersion}-win32-x64.exe"; Parameters: "/S /D=""{app}\SWATPlusEditor"""; WorkingDir: "{tmp}"; Flags: skipifdoesntexist skipifnotsilent
Filename: "{tmp}\SWATPlusToolbox-v{#ToolboxVersion}.{#ToolboxPatchVersion}.exe"; Parameters: "/VERYSILENT /CURRENTUSER"; WorkingDir: "{tmp}"; Flags: skipifdoesntexist skipifnotsilent shellexec

[Messages]
SelectDirBrowseLabel=If you select a different location from the default, you will need to set this location in the QSWAT+ Parameters form the first time you run QSWAT+.
ConfirmUninstall=Are you sure you want to remove %1? SWAT+ Editor, tools, and documents will be removed. The QSWAT+ plugin and SWAT+ Toolbox will need to be uninstalled separately.

[UninstallRun]
Filename: "{app}\SWATPlusEditor\Uninstall SWATPlusEditor.exe"; WorkingDir: "{app}\SWATPlusEditor"; Flags: skipifdoesntexist

[Code]
procedure InitializeWizard;
begin
    idpAddFileComp('https://plus.swat.tamu.edu/downloads/swatplus_soils.zip', ExpandConstant('{tmp}\swatplus_soils.zip'), 'soils');
    idpAddFileComp('https://plus.swat.tamu.edu/downloads/swatplus_wgn.zip', ExpandConstant('{tmp}\swatplus_wgn.zip'), 'wgn');
    idpDownloadAfter(wpReady);
end;


const
  SHCONTCH_NOPROGRESSBOX = 4;
  SHCONTCH_RESPONDYESTOALL = 16;

procedure UnZip(ZipFile, TargetFldr: PAnsiChar);
var
  shellobj: variant;
  ZipFileV, TargetFldrV: variant;
  SrcFldr, DestFldr: variant;
  shellfldritems: variant;
begin
  if FileExists(ZipFile) then begin
    ForceDirectories(TargetFldr);
    shellobj := CreateOleObject('Shell.Application');
    ZipFileV := string(ZipFile);
    TargetFldrV := string(TargetFldr);
    SrcFldr := shellobj.NameSpace(ZipFileV);
    DestFldr := shellobj.NameSpace(TargetFldrV);
    shellfldritems := SrcFldr.Items;
    DestFldr.CopyHere(shellfldritems, SHCONTCH_NOPROGRESSBOX or SHCONTCH_RESPONDYESTOALL);  
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
    if CurStep = ssPostInstall then 
    begin
        UnZip(ExpandConstant('{tmp}\swatplus_soils.zip'), ExpandConstant('{app}\Databases'))
        UnZip(ExpandConstant('{tmp}\swatplus_wgn.zip'), ExpandConstant('{app}\Databases'))
    end;
end;