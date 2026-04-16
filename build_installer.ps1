Write-Host "Iniciando compilação de Produção do C.R.D.F Premium..." -ForegroundColor Cyan

Write-Host "`n[1/4] Instalando Base C++ Backend (PyInstaller)..." -ForegroundColor Yellow
pip install pyinstaller Pillow customtkinter matplotlib pyserial

Write-Host "`n[2/4] Garantindo que o motor base extraiu o crdf_icon.ico nativo..." -ForegroundColor Yellow
python -c "from PIL import Image; import os; Image.open('assets/crdf_icon.png').save('assets/crdf_icon.ico', format='ICO', sizes=[(32, 32), (64, 64)]) if os.path.exists('assets/crdf_icon.png') else None"

Write-Host "`n[3/4] Empacotando projeto Fonte com PyInstaller..." -ForegroundColor Yellow
pyinstaller --clean build.spec

Write-Host "`n[4/4] Verificando compilador do Windows (Inno Setup)..." -ForegroundColor Yellow
$isccPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-Not (Test-Path $isccPath)) {
    Write-Host "Inno Setup não encontrado. Acionando Winget Windows Package Manager para instalar localmente..." -ForegroundColor Magenta
    winget install -e --id JRSoftware.InnoSetup --accept-source-agreements --accept-package-agreements --silent
    Start-Sleep -Seconds 8
}

if (Test-Path $isccPath) {
    Write-Host "`n>> Construindo Setup_CRDF_V1.0.exe [Aguarde alguns segundos]..." -ForegroundColor Green
    & $isccPath "setup.iss"
    Write-Host "`n`n>>> INSTALADOR GERADO COM SUCESSO! Verifique a pasta 'Instalador Final' <<<" -ForegroundColor Green
} else {
    Write-Host "Inno Setup não pôde ser instalado automaticamente devido a politicas corporativas de seu Windows." -ForegroundColor Red
    Write-Host "Baixe instalar: https://jrsoftware.org/download.php/is.exe"
    Write-Host "Após instalar na sua máquina, clique com botão direito no 'setup.iss' -> Compile."
}
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
