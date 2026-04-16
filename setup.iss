[Setup]
AppName=CRDF Premium
AppVersion=1.0
AppPublisher=SENAI
DefaultDirName={autopf}\CRDF Inteligente
DefaultGroupName=CRDF Inteligente
OutputDir=Instalador Final
OutputBaseFilename=Setup_CRDF_V1.0
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=assets\crdf_icon.ico
UninstallDisplayIcon={app}\Carrinho_CRDF.exe

[Files]
Source: "dist\Carrinho_CRDF\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CRDF Inteligente"; Filename: "{app}\Carrinho_CRDF.exe"; IconFilename: "{app}\assets\crdf_icon.ico"
Name: "{autodesktop}\CRDF Inteligente"; Filename: "{app}\Carrinho_CRDF.exe"; IconFilename: "{app}\assets\crdf_icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Atalhos Adicionais:"

[Run]
Filename: "{app}\Carrinho_CRDF.exe"; Description: "Executar CRDF Premium"; Flags: nowait postinstall skipifsilent
