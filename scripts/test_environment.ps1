# 環境テストスクリプト

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "環境テスト" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# PATHを更新
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
$binDir = "$env:LOCALAPPDATA\poppler\Library\bin"
if (Test-Path $binDir) {
    $env:Path = "$binDir;$env:Path"
}

# 1. Popplerの確認
Write-Host "1. Popplerの確認..." -ForegroundColor Yellow
try {
    $pdfinfoPath = Join-Path $binDir "pdfinfo.exe"
    if (Test-Path $pdfinfoPath) {
        $version = & $pdfinfoPath -v 2>&1
        Write-Host "   ✓ Poppler: $($version[0])" -ForegroundColor Green
    } else {
        Write-Host "   ✗ pdfinfo.exe が見つかりません" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Popplerの確認に失敗: $_" -ForegroundColor Red
}

Write-Host ""

# 2. パッケージの確認
Write-Host "2. インストール済みパッケージの確認..." -ForegroundColor Yellow
$packages = @("torch", "transformers", "tokenizers", "einops", "addict", "easydict")
foreach ($pkg in $packages) {
    $result = uv pip list 2>&1 | Select-String -Pattern "^$pkg\s+" | ForEach-Object { $_.Line }
    if ($result) {
        Write-Host "   ✓ $result" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $pkg が見つかりません" -ForegroundColor Red
    }
}

Write-Host ""

# 3. GPUの確認
Write-Host "3. GPUの確認..." -ForegroundColor Yellow
$pythonPath = ".\.venv\Scripts\python.exe"
if (Test-Path $pythonPath) {
    $gpuCheck = @"
import torch
cuda_available = torch.cuda.is_available()
cuda_version = torch.version.cuda if cuda_available else 'N/A'
print(f'CUDA available: {cuda_available}')
print(f'CUDA version: {cuda_version}')
if cuda_available:
    print(f'GPU device: {torch.cuda.get_device_name(0)}')
"@
    $gpuCheck | & $pythonPath
} else {
    Write-Host "   ✗ Pythonが見つかりません" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "テスト完了" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

