# DeepSeek-OCR セットアップスクリプト
# 公式推奨環境に合わせて依存関係をインストールします

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DeepSeek-OCR セットアップスクリプト" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# プロジェクトディレクトリに移動
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
Set-Location $projectDir

Write-Host "プロジェクトディレクトリ: $projectDir" -ForegroundColor Green
Write-Host ""

# 1. 仮想環境の確認・作成
Write-Host "1. 仮想環境の確認..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    Write-Host "   仮想環境を作成中..." -ForegroundColor Yellow
    uv venv
    Write-Host "   ✓ 仮想環境を作成しました" -ForegroundColor Green
} else {
    Write-Host "   ✓ 仮想環境は既に存在します" -ForegroundColor Green
}

Write-Host ""

# 2. 基本依存関係のインストール
Write-Host "2. 基本依存関係のインストール..." -ForegroundColor Yellow
uv pip install -e ".[dev]"
Write-Host "   ✓ 基本依存関係をインストールしました" -ForegroundColor Green

Write-Host ""

# 3. PyTorch (CUDA 11.8版) のインストール
Write-Host "3. PyTorch (CUDA 11.8版) のインストール..." -ForegroundColor Yellow
Write-Host "   公式推奨: torch==2.6.0, torchvision==0.21.0" -ForegroundColor White
uv pip uninstall torch torchvision torchaudio -y 2>$null
uv pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
Write-Host "   ✓ PyTorchをインストールしました" -ForegroundColor Green

Write-Host ""

# 4. Transformers関連のインストール
Write-Host "4. Transformers関連のインストール..." -ForegroundColor Yellow
Write-Host "   公式推奨: transformers==4.46.3, tokenizers==0.20.3" -ForegroundColor White
uv pip uninstall transformers tokenizers -y 2>$null
uv pip install transformers==4.46.3 tokenizers==0.20.3
Write-Host "   ✓ Transformersをインストールしました" -ForegroundColor Green

Write-Host ""

# 5. その他の依存関係のインストール
Write-Host "5. その他の依存関係のインストール..." -ForegroundColor Yellow
uv pip install einops addict easydict
Write-Host "   ✓ 依存関係をインストールしました" -ForegroundColor Green

Write-Host ""

# 6. Flash Attention のインストール試行（オプション）
Write-Host "6. Flash Attention のインストール試行（オプション）..." -ForegroundColor Yellow
Write-Host "   注意: CUDAバージョンの不一致で失敗する可能性があります" -ForegroundColor White
try {
    uv pip install flash-attn==2.7.3 --no-build-isolation 2>&1 | Out-Null
    Write-Host "   ✓ Flash Attentionをインストールしました" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Flash Attentionのインストールに失敗しました（オプション機能のため問題ありません）" -ForegroundColor Yellow
    Write-Host "      CUDA 11.8環境で再試行するか、このまま続行できます" -ForegroundColor White
}

Write-Host ""

# 7. インストール確認
Write-Host "7. インストール確認..." -ForegroundColor Yellow
$packages = @("torch", "transformers", "tokenizers", "einops", "addict", "easydict")
$allInstalled = $true
foreach ($pkg in $packages) {
    $result = uv pip list 2>&1 | Select-String -Pattern "^$pkg\s+"
    if ($result) {
        Write-Host "   ✓ $result" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $pkg が見つかりません" -ForegroundColor Red
        $allInstalled = $false
    }
}

Write-Host ""

# 8. GPU確認
Write-Host "8. GPU確認..." -ForegroundColor Yellow
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
Write-Host "セットアップ完了" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Yellow
Write-Host "1. DeepSeek-OCRモデルをダウンロード（未ダウンロードの場合）:" -ForegroundColor White
Write-Host "   uv run python scripts/download_deepseek_model.py --model-path ./models/DeepSeek-OCR" -ForegroundColor Gray
Write-Host ""
Write-Host "2. PDF変換をテスト:" -ForegroundColor White
Write-Host "   uv run pdftexter pdf-to-text input.pdf -o output.md --skip-verify" -ForegroundColor Gray
Write-Host ""

