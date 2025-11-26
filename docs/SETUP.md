# セットアップガイド

このドキュメントでは、pdftexterのセットアップ手順を詳しく説明します。

## 目次

1. [前提条件](#前提条件)
2. [自動セットアップ（推奨）](#自動セットアップ推奨)
3. [手動セットアップ](#手動セットアップ)
4. [環境テスト](#環境テスト)
5. [トラブルシューティング](#トラブルシューティング)

## 前提条件

- **Python 3.12+**
- **uv**（依存関係管理ツール） - [インストール方法](https://docs.astral.sh/uv/getting-started/installation/)
- **Windows環境**（Kindleスクリーンショット機能使用時）
- **CUDA対応GPU**（DeepSeek-OCR使用時、推奨。CPUでも動作可能）
- **約10GB以上の空き容量**（モデルダウンロード用）

## 自動セットアップ（推奨）

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd pdftexter
```

### 2. DeepSeek-OCR環境のセットアップ

```powershell
# 一発でセットアップ完了
.\scripts\setup_deepseek_ocr.ps1
```

このスクリプトは以下を自動実行します：
- 仮想環境の作成
- 基本依存関係のインストール
- PyTorch 2.6.0 (CUDA 11.8版) のインストール
- Transformers 4.46.3 のインストール
- その他の依存関係（einops, addict, easydict）のインストール
- Flash Attention のインストール試行（オプション）

### 3. Popplerのインストール

```powershell
# Popplerを自動インストール
.\scripts\install_poppler_windows.ps1
```

このスクリプトは以下を自動実行します：
- 最新のpoppler-windowsをダウンロード
- `%LOCALAPPDATA%\poppler` にインストール
- PATH環境変数に追加

**重要**: PowerShellを再起動してPATHを反映させてください。

### 4. DeepSeek-OCRモデルのダウンロード

```bash
# モデルをダウンロード（約6.7GB、時間がかかります）
uv run python scripts/download_deepseek_model.py --model-path ./models/DeepSeek-OCR
```

### 5. 設定ファイルの確認

`config/ocr_config.yaml` を開き、モデルパスを確認：

```yaml
deepseek_ocr:
  model_path: "C:/analysis2/pdftexter/models/DeepSeek-OCR"  # 実際のパスに合わせて修正
  use_huggingface: true  # HuggingFace版を使用（推奨）
```

### 6. 動作確認

```bash
# 環境テストを実行
.\scripts\test_environment.ps1

# PDF変換をテスト
uv run pdftexter pdf-to-text input.pdf -o output.md --skip-verify
```

## 手動セットアップ

自動セットアップが使えない場合や、詳細を理解したい場合は手動セットアップを行ってください。

### 1. 仮想環境の作成

```bash
uv venv
```

### 2. 基本依存関係のインストール

```bash
uv pip install -e ".[dev]"
```

### 3. PyTorchのインストール（CUDA 11.8版）

```bash
# 既存のPyTorchをアンインストール
uv pip uninstall torch torchvision torchaudio

# CUDA 11.8版をインストール（公式推奨）
uv pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
```

### 4. Transformers関連のインストール

```bash
# 既存のバージョンをアンインストール
uv pip uninstall transformers tokenizers

# 公式推奨バージョンをインストール
uv pip install transformers==4.46.3 tokenizers==0.20.3
```

### 5. その他の依存関係のインストール

```bash
uv pip install einops addict easydict
```

### 6. Flash Attentionのインストール（オプション）

```bash
# CUDA環境によっては失敗する可能性があります
uv pip install flash-attn==2.7.3 --no-build-isolation
```

**注意**: Flash Attentionのインストールに失敗しても、基本機能は使用できます。

### 7. Popplerのインストール

詳細は `scripts/install_poppler_windows.md` を参照してください。

## 環境テスト

環境が正しくセットアップされているか確認するには：

```powershell
.\scripts\test_environment.ps1
```

このスクリプトは以下を確認します：
- Popplerのインストール状況
- 必要なパッケージのインストール状況
- GPUの利用可能性

### 個別確認コマンド

```powershell
# Popplerの確認
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
$binDir = "$env:LOCALAPPDATA\poppler\Library\bin"
if (Test-Path $binDir) {
    $env:Path = "$binDir;$env:Path"
    & "$binDir\pdfinfo.exe" -v
}

# パッケージの確認
uv pip list | findstr -i "torch transformers tokenizers einops addict easydict"

# GPUの確認
.\.venv\Scripts\python.exe -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"
```

## トラブルシューティング

詳細は [README.md](../README.md#-トラブルシューティング) のトラブルシューティングセクションを参照してください。

### よくある問題

1. **`pdfinfo` コマンドが見つからない**
   - PopplerがPATHに追加されていない
   - PowerShellを再起動するか、PATHを手動で更新

2. **`LlamaFlashAttention2` のインポートエラー**
   - transformersのバージョンが公式推奨と異なる
   - `.\scripts\setup_deepseek_ocr.ps1` を実行して再インストール

3. **Flash Attentionのインストールに失敗**
   - CUDAバージョンの不一致
   - オプション機能のため、インストールしなくても動作します

4. **GPUが認識されない**
   - CUDAドライバーが正しくインストールされているか確認
   - PyTorchがCUDA対応版でインストールされているか確認

5. **モデルの読み込みに失敗**
   - モデルが正しくダウンロードされているか確認
   - `config/ocr_config.yaml` の `model_path` が正しいか確認

## 次のステップ

セットアップが完了したら、[README.md](../README.md) の「使用方法」セクションを参照して、実際にPDF変換を試してみてください。

