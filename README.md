# pdftexter

Kindle電子書籍をPDF化し、DeepSeek-OCRを使用してPDFからテキスト（Markdown）に変換する統合ツールです。

## 📋 概要

pdftexterは、Kindle電子書籍をPDF化し、DeepSeek-OCRを使用してPDFからテキスト（Markdown）に変換する統合ツールです。

### 主要機能

1. **Kindle → 画像**: Kindle for PCアプリの画面を自動でキャプチャし、画像ファイルとして保存
   - 自動ページめくり
   - 余白の自動トリミング
   - コンテンツ境界の自動検出

2. **画像 → PDF**: 複数の画像ファイルを1つのPDFファイルに結合
   - 画像の自動ソート
   - 各画像のサイズに合わせたPDFページ生成

3. **PDF → テキスト**: DeepSeek-OCR（HuggingFace Transformers版）を使用してPDFからMarkdown形式のテキストを抽出
   - 長文脈対応の高精度OCR
   - Markdown形式での出力
   - GPU対応（CUDA）で高速処理

### 統合ワークフロー

統合CLIにより、Kindle → PDF → Text の一連の処理を1つのコマンドで実行できます。

### 🎯 特徴

- **自動化**: Kindleページの自動めくりとスクリーンショット撮影
- **高精度OCR**: DeepSeek-OCRによる長文脈対応のOCR処理
- **Markdown出力**: 構造化されたMarkdown形式でのテキスト出力
- **画像抽出**: PDF内の画像も適切に抽出・保存

### 🚨 注意事項

**著作権**には十分にご注意ください。PDF化・OCR化したコンテンツの**個人的な学習・利用の範囲を超えた複製や配布は避けてください**。

## 🏗️ プロジェクト構造

```
pdftexter/
├── src/pdftexter/          # メインモジュール
│   ├── kindle/            # Kindle関連（スクリーンショット）
│   ├── pdf/               # PDF関連（変換・処理）
│   ├── ocr/               # OCR関連（DeepSeek-OCR統合）
│   ├── utils/             # 共通ユーティリティ
│   └── cli/               # CLIインターフェース
├── scripts/               # 実行スクリプト
├── tests/                 # テストコード
├── docs/                  # ドキュメント
│   ├── ARCHITECTURE.md   # アーキテクチャ設計書
│   └── PLAN.md           # 実装プラン
└── config/               # 設定ファイル
```

詳細は [ARCHITECTURE.md](docs/ARCHITECTURE.md) を参照してください。

## 🚀 クイックスタート

### 前提条件

- **Python 3.12+**
- **uv**（依存関係管理、高速インストール） - [インストール](https://docs.astral.sh/uv/getting-started/installation/)
- **Windows環境**（Kindleスクリーンショット機能使用時）
- **CUDA対応GPU**（DeepSeek-OCR使用時、推奨。CPUでも動作可能）
- **poppler-utils**（PDF処理用）
  - Windows: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) をダウンロードして`bin`をPATHに追加

### インストール

#### 方法1: 自動セットアップ（推奨）

**一発でセットアップ完了**：以下のコマンドで、DeepSeek-OCRを含むすべての依存関係を公式推奨環境に合わせてインストールします。

```powershell
# PowerShellで実行
.\scripts\setup_deepseek_ocr.ps1
```

このスクリプトは以下を自動実行します：
1. 仮想環境の作成
2. 基本依存関係のインストール
3. PyTorch 2.6.0 (CUDA 11.8版) のインストール
4. Transformers 4.46.3 のインストール
5. その他の依存関係（einops, addict, easydict）のインストール
6. Flash Attention のインストール試行（オプション）

#### 方法2: 手動インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd pdftexter

# 仮想環境の作成と依存関係インストール
uv venv
uv pip install -e ".[dev]"

# DeepSeek-OCR公式推奨環境に合わせてインストール
uv pip uninstall torch torchvision torchaudio transformers tokenizers
uv pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
uv pip install transformers==4.46.3 tokenizers==0.20.3
uv pip install einops addict easydict

# Flash Attention（オプション、CUDA環境によっては失敗する可能性あり）
uv pip install flash-attn==2.7.3 --no-build-isolation
```

### クイックスタート例

```bash
# 1. PDFファイルをテキストに変換
uv run pdftexter pdf-to-text sample.pdf -o output.md

# 2. Kindle → PDF → Markdown（推奨、PDFレビュー機能付き）
uv run pdftexter kindle-to-markdown -o result.md

# 3. 画像フォルダからPDF→Textまで一括処理
uv run pdftexter full ./images -o result.md
```

### DeepSeek-OCR環境のセットアップ

**簡単セットアップ（推奨）**：HuggingFace Transformers版を使用します。vLLMサーバー不要で、GPU/CPUで直接実行できます。

#### ステップ1: Popplerのインストール（PDF処理用）

Windows環境では、PopplerをインストールしてPATHに追加する必要があります。

**自動インストール（推奨）**：
```powershell
.\scripts\install_poppler_windows.ps1
```

このスクリプトは以下を自動実行します：
1. 最新のpoppler-windowsをダウンロード
2. `%LOCALAPPDATA%\poppler` にインストール
3. PATH環境変数に追加

**手動インストール**：
1. [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases/) から最新の `Release-*.zip` をダウンロード
2. 解凍して `C:\poppler` などに配置
3. `Library\bin` フォルダをPATH環境変数に追加
4. PowerShellを再起動

詳細は `scripts/install_poppler_windows.md` を参照してください。

#### ステップ2: DeepSeek-OCRモデルのダウンロード

```bash
# モデルをダウンロード（約6.7GB）
uv run python scripts/download_deepseek_model.py --model-path ./models/DeepSeek-OCR
```

モデルは `./models/DeepSeek-OCR` にダウンロードされます。

#### ステップ3: 設定ファイルの確認

`config/ocr_config.yaml` を開き、以下を確認：

```yaml
deepseek_ocr:
  # モデルのパス（必要に応じて修正）
  model_path: "C:/analysis2/pdftexter/models/DeepSeek-OCR"  # Windowsの場合、絶対パス推奨

  # HuggingFace版を使用（デフォルト）
  use_huggingface: true  # これでvLLMサーバー不要
```

#### ステップ4: 動作確認

```bash
# セットアップ検証付きで実行（推奨）
uv run pdftexter pdf-to-text input.pdf -o output.md

# セットアップ検証をスキップして実行
uv run pdftexter pdf-to-text input.pdf -o output.md --skip-verify
```

**完了！** これでDeepSeek-OCRが使えます。

---

**高度な設定**：vLLM版を使用する場合は、`config/ocr_config.yaml` で `use_huggingface: false` に設定し、vLLMサーバーをセットアップしてください。詳細は [docs/PLAN.md](docs/PLAN.md) を参照。

## 📖 使用方法

### 統合CLI（推奨）

pdftexterは統合CLIを提供しており、Kindle電子書籍をMarkdownテキストに変換できます。

#### 📱 Kindle → Markdown（全自動・推奨）

```bash
# Kindle for PCからMarkdownまで一括変換（PDFレビュー機能付き）
uv run pdftexter kindle-to-markdown -o result.md
```

このコマンドは以下を**すべて自動**で実行します：
1. 📸 Kindleスクリーンショット撮影（GUI）
2. 📄 画像 → PDF変換
3. 👀 **PDFレビュー**（品質確認、続行/やり直し/終了を選択可能）
4. 📝 PDF → Markdown変換（OCR）

#### その他のコマンド

```bash
# ヘルプ表示
uv run pdftexter --help

# PDF → Text変換（既にPDFがある場合）
uv run pdftexter pdf-to-text input.pdf -o output.md

# 画像フォルダ → PDF → Text の一括処理（既に画像がある場合）
uv run pdftexter full image_folder -o output.md
```

---

### 詳細な手順（個別実行）

個別にステップを実行したい場合は、以下の手順を参照してください。

### 1. Kindle → 画像（スクリーンショット撮影）

#### ステップ1: Kindleスクリーンショット撮影

1. **Kindle for PCの準備**
   - PDF化したい本を開く
   - **全画面表示**にする
   - **見開き表示ではなく、1ページずつの表示**に変更

2. **スクリプトの実行**
   ```bash
   uv run kindle-screenshot
   # または
   uv run python scripts/kindle_screenshot.py
   ```

3. **GUI設定**
   - タイトルを入力（保存フォルダ名）
   - 保存先フォルダを選択

4. **自動撮影**
   - 設定後、自動でページめくりとスクリーンショット撮影が開始
   - **この間はマウスやキーボードに触れないでください**
   - ページは自動的にめくられ、余白は自動トリミングされます

#### ステップ2: 画像 → PDF変換

```bash
uv run kindle-pdf-convert
# または
uv run python scripts/kindle_pdf_convert.py
```

- 画像フォルダを選択
- 出力先フォルダとファイル名を指定
- 「変換」ボタンをクリック

### 2. PDF → テキスト（Markdown）

#### 事前準備：DeepSeek-OCRのセットアップ

**重要**: OCR処理を実行する前に、DeepSeek-OCRモデルのダウンロードが必要です。

詳細は上記「**DeepSeek-OCR環境のセットアップ**」セクションを参照してください。

**クイックチェック**：
```bash
# OCRセットアップが完了しているか自動検証されます
uv run pdftexter pdf-to-text input.pdf -o output.md
```

セットアップが完了していない場合、エラーメッセージが表示されます。

#### DeepSeek-OCRを使用した変換

```bash
# 統合CLI経由（推奨、セットアップ検証付き）
uv run pdftexter pdf-to-text input.pdf -o output.md

# セットアップ検証をスキップする場合
uv run pdftexter pdf-to-text input.pdf -o output.md --skip-verify

# 個別コマンド経由
uv run pdf-to-text input.pdf -o output.md

# スクリプト経由
uv run python scripts/pdf_to_text.py input.pdf -o output.md
```

**注意**: 
- OCR処理は**一枚ずつ画像を順次処理**します。PDFの各ページが画像に変換され、それぞれがOCR処理されます。
- GPUが利用可能な場合は自動的にGPUを使用します（CPUでも動作可能ですが、処理が遅くなります）。
- Flash Attentionがインストールされていない場合でも動作しますが、パフォーマンスが低下する可能性があります。

#### オプション

```bash
# 設定ファイルを指定
uv run pdftexter pdf-to-text input.pdf -c config/ocr_config.yaml

# カスタムプロンプトを指定
uv run pdftexter pdf-to-text input.pdf -p "カスタムプロンプト"

# 出力形式を指定（markdown or plain）
uv run pdftexter pdf-to-text input.pdf --format plain

# 進捗表示を無効化
uv run pdftexter pdf-to-text input.pdf --no-progress
```

#### 設定ファイル

`config/ocr_config.yaml` でOCR設定をカスタマイズできます：

```yaml
deepseek_ocr:
  model_path: "/path/to/deepseek-ocr"
  vllm_server_url: "http://localhost:8000"  # オプション
  max_tokens: 4096
  temperature: 0.1
  output_format: "markdown"  # "markdown" or "plain"
  timeout: 300
  max_retries: 3
  retry_delay: 5

output:
  base_dir: "./output"
  images_dir: "./output/images"
  pdfs_dir: "./output/pdfs"
  texts_dir: "./output/texts"
```

設定ファイルのサンプルは `config/ocr_config.yaml.example` を参照してください。

### 3. 一括処理

#### 3.1 Kindle → PDF → Markdown（PDFレビュー機能付き、推奨）

PDF生成後に品質を確認してからOCR処理に進むことができます：

```bash
uv run pdftexter kindle-to-markdown -o output.md
```

このコマンドは以下を実行します：
1. Kindleスクリーンショット撮影（GUI）
2. 画像 → PDF変換
3. **PDFレビュー**（品質確認、続行/やり直し/終了を選択可能）
4. PDF → Markdown変換（OCR）

オプション：
```bash
# PDFレビューをスキップ
uv run pdftexter kindle-to-markdown -o output.md --skip-review

# PDF出力先を指定
uv run pdftexter kindle-to-markdown --pdf-output-dir ./pdfs --pdf-filename book.pdf

# OCR設定を指定
uv run pdftexter kindle-to-markdown --ocr-config config/ocr_config.yaml
```

#### 3.2 画像フォルダから一括処理

画像フォルダから最終的なMarkdownファイルまで一括で処理します：

```bash
uv run pdftexter full image_folder -o output.md
```

このコマンドは以下を自動実行します：
1. 画像フォルダからPDFを生成
2. 生成したPDFをOCR処理してMarkdownに変換

**注意**: このコマンドにはPDFレビュー機能はありません。PDFレビューが必要な場合は `kindle-to-markdown` コマンドを使用してください。

オプション：
```bash
# PDF出力先を指定
uv run pdftexter full image_folder --pdf-output-dir ./pdfs --pdf-filename book.pdf

# OCR設定を指定
uv run pdftexter full image_folder --ocr-config config/ocr_config.yaml

# OCR出力形式を指定
uv run pdftexter full image_folder --ocr-format plain
```

## 🛠️ 開発

### プロジェクト構造の詳細

- **アーキテクチャ設計**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **実装プラン**: [docs/PLAN.md](docs/PLAN.md)

### 開発環境のセットアップ

```bash
# 開発依存関係のインストール
uv pip install -e ".[dev]" --with dev

# 型チェック
uv run mypy src/

# テスト実行
uv run pytest

# コードフォーマット
uv run black src/
uv run isort src/
```

### コード品質

- **型ヒント**: すべての関数に型ヒントを付与
- **Docstring**: JSDocスタイルのドキュメント文字列
- **テスト**: pytestを使用したユニットテスト・統合テスト
- **静的解析**: mypy, vulture, pydanticを使用

### コマンド一覧

```bash
# 統合CLI
uv run pdftexter --help                          # ヘルプ表示
uv run pdftexter pdf-to-text --help              # PDF→Text変換のヘルプ
uv run pdftexter kindle-to-markdown --help       # Kindle→Markdown変換のヘルプ
uv run pdftexter full --help                     # 一括処理のヘルプ

# 個別コマンド
uv run kindle-screenshot                         # Kindleスクリーンショット（GUI）
uv run kindle-pdf-convert                        # 画像→PDF変換（GUI）
uv run pdf-to-text input.pdf -o output.md        # PDF→Text変換（CLI）
```

### OCR処理の仕組み

#### 処理フロー

1. **PDF → 画像変換**: PDFの各ページを画像に変換（pdf2image使用）
2. **一枚ずつOCR処理**: 各画像をDeepSeek-OCRモデルで順次処理（GPU/CPU）
3. **結果の結合**: 各ページのOCR結果を結合してMarkdown形式で出力

**推奨**: GPUを使用すると高速に処理できます（RTX 4090で実測）。

#### モデルダウンロード

DeepSeek-OCRモデルは手動でダウンロードが必要です：

```bash
# モデルをダウンロード（約6.7GB）
uv run python scripts/download_deepseek_model.py --model-path ./models/DeepSeek-OCR
```

詳細は「DeepSeek-OCR環境のセットアップ」セクションを参照してください。

## 📚 ドキュメント

- [SETUP.md](docs/SETUP.md) - 詳細なセットアップガイド
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - アーキテクチャ設計書
- [PLAN.md](docs/PLAN.md) - 実装プランとロードマップ

## 🔧 技術スタック

### コアライブラリ
- Python 3.12+
- uv（依存関係管理、高速インストール）

### Kindle関連
- pyautogui（自動操作）
- Pillow（画像処理）
- opencv-python（画像処理・境界検出）
- ctypes（Windows API呼び出し）

### PDF関連
- reportlab（PDF生成）
- Pillow（画像読み込み）

### OCR関連
- transformers（HuggingFace、モデル実行）
- torch（深層学習フレームワーク、CUDA対応）
- DeepSeek-OCR（OCRモデル）
- pdf2image（PDF画像変換）

### 開発・品質管理
- mypy（静的型チェック）
- vulture（未使用コード検出）
- pydantic（データ検証）
- pytest（テストフレームワーク）

## 🗺️ ロードマップ

現在の実装状況と今後の予定については [PLAN.md](docs/PLAN.md) を参照してください。

### 実装済み
- ✅ プロジェクト構造の設計
- ✅ アーキテクチャドキュメント
- ✅ 実装プラン

### 実装中
- ⏳ ディレクトリ構造の作成
- ⏳ DeepSeek-OCR統合
- ⏳ CLIインターフェース

### 予定
- 📋 既存コードのリファクタリング
- 📋 テストの実装
- 📋 ドキュメント整備

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します。詳細は [CONTRIBUTING.md](CONTRIBUTING.md)（作成予定）を参照してください。

## 📄 ライセンス

このプロジェクトのライセンスについては [LICENSE](LICENSE) を参照してください。

## 🙏 謝辞

- [DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR) - 高精度OCRモデル
- [vLLM](https://github.com/vllm-project/vllm) - 高速推論エンジン

---

## 📝 既存の詳細ドキュメント

以下のセクションには、既存の実装詳細が記載されています。

-----

## 📚 Kindle電子書籍をPDF化するPythonドキュメント（既存）

このドキュメントでは、Kindle for PCで閲覧できる電子書籍を、タブレット等での利用に適したPDFファイルに変換する手順とPythonコードを解説します。

### 🛠️ 全体の処理フロー

KindleのPDF化は、以下の3つの主要なステップに分かれます。

1.  **スクリーンショット撮影:** Kindle PCアプリの画面を自動でキャプチャし、画像ファイルとして保存する。
2.  **余白の削除・トリミング:** 撮影した画像から不要な余白を削除し、コンテンツ部分のみを切り出す。（*本ドキュメントではこのコードは省略し、ステップ1のコードに簡易的な境界検出機能を含めています*）
3.  **PDF変換:** 整えた複数の画像ファイルを、1つのPDFに変換して結合する。

-----

## 1\. 🖼️ ステップ1：スクリーンショット撮影と保存

Kindle PCアプリを自動操作し、全画面表示のページを連続でキャプチャして画像ファイルとして保存します。

### 💻 必要なライブラリのインストール

以下のライブラリを事前にインストールしてください。

```bash
pip install pyautogui Pillow opencv-python
```

### 🐍 Pythonコード全文 (kindle\_screenshot.py)

このコードは、Kindleウィンドウを検出し、全画面表示にしてからページを自動でめくりながらスクリーンショットを撮影します。

```python
# 必要なライブラリのインポート
import pyautogui as pag
import os, os.path as osp
import datetime, time
from PIL import ImageGrab
from tkinter import messagebox, simpledialog, filedialog
import cv2
import numpy as np
from ctypes import *
from ctypes.wintypes import *

# グローバル変数の設定
kindle_window_title = 'Kindle for PC'  # Kindle for PCのウィンドウタイトル
page_change_key = 'right'      # 次のページへ移動するキー
kindle_fullscreen_wait = 5     # フルスクリーン後の待機時間(秒)
l_margin = 1                   # 左側マージン（境界検出用）
r_margin = 1                   # 右側マージン（境界検出用）
waitsec = 0.15                 # キー押下後の待機時間(秒)

def find_kindle_window():
    """Kindleウィンドウを検索してハンドルを返す関数"""
    EnumWindows = windll.user32.EnumWindows
    GetWindowText = windll.user32.GetWindowTextW
    GetWindowTextLength = windll.user32.GetWindowTextLengthW
    WNDENUMPROC = WINFUNCTYPE(c_bool, POINTER(c_int), POINTER(c_int))
    ghwnd = None
    def EnumWindowsProc(hwnd, lParam):
        """ウィンドウ列挙のためのコールバック関数"""
        nonlocal ghwnd
        length = GetWindowTextLength(hwnd)
        buff = create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        if kindle_window_title in buff.value:
            ghwnd = hwnd
            return False
        return True
    EnumWindows(WNDENUMPROC(EnumWindowsProc), 0)
    return ghwnd

def setup_kindle_window(hwnd):
    """Kindleウィンドウを前面に表示しフォーカスを設定"""
    SetForegroundWindow = windll.user32.SetForegroundWindow
    GetWindowRect = windll.user32.GetWindowRect
    SetForegroundWindow(hwnd)
    rect = RECT()
    GetWindowRect(hwnd, pointer(rect))
    # クリックしてフォーカスを設定
    pag.moveTo(rect.left+60, rect.top + 10)
    pag.click()
    time.sleep(1)

def get_screen_size():
    """画面サイズを取得"""
    return pag.size()

def get_title():
    """保存用のタイトルを取得"""
    default_title = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    tt = simpledialog.askstring('タイトルを入力','タイトルを入力して下さい(空白の場合現在の時刻)')
    return tt if tt != '' else default_title

def get_save_folder():
    """保存先フォルダを選択"""
    return filedialog.askdirectory(title='保存するフォルダを選択してください')

def find_content_boundaries(img):
    """
    画像内のコンテンツ境界を検出（簡易的な方法）
    Args:
        img: 画像データ（NumPy配列）
    Returns:
        lft: 左端の位置, rht: 右端の位置
    """
    def cmps(img, rng):
        """ピクセルの色を比較して境界を検出"""
        # Kindleの余白とコンテンツの色の境界を検出（実装依存）
        for i in rng:
            # ページ上の特定のピクセル（例：20行目）で、左上のピクセルと異なる色を探す
            if np.all(img[20][i] != img[19][0]):
                return i
    lft = cmps(img, range(l_margin, img.shape[1]-r_margin))
    rht = cmps(img, reversed(range(l_margin, img.shape[1]-r_margin)))
    return lft, rht

def capture_and_save_pages(lft, rht, title):
    """ページをキャプチャして保存"""
    sc_h, _ = get_screen_size()
    # ページめくりを検知するための比較用画像
    old = np.zeros((sc_h, rht-lft, 3), np.uint8)
    page = 1
    
    # 保存先フォルダの設定
    global base_save_folder
    cd = os.getcwd()
    save_path = osp.join(base_save_folder, title)
    os.makedirs(save_path, exist_ok=True)
    os.chdir(save_path)
    
    while True:
        filename = f"{page:03d}.png"
        start = time.perf_counter()
        while True:
            time.sleep(waitsec)
            s = ImageGrab.grab()
            s = np.array(s)
            ss = cv2.cvtColor(s, cv2.COLOR_RGB2BGR)
            # コンテンツ境界に基づいてトリミング
            ss = ss[:, lft: rht]
            
            # ページめくりが完了したか確認
            if not np.array_equal(old, ss):
                break
            
            # タイムアウト処理（最終ページなどで変化がなかった場合）
            if time.perf_counter() - start > 5.0:
                os.chdir(cd)
                return page - 1 # 最後に成功したページ数を返す

        # 画像保存と次ページへ
        cv2.imwrite(filename, ss)
        old = ss
        print(f'Page: {page}, {ss.shape}, {time.perf_counter() - start:.2f} sec')
        page += 1
        pag.keyDown(page_change_key)

def main():
    """メイン処理"""
    global base_save_folder
    
    hwnd = find_kindle_window()
    if hwnd is None:
        messagebox.showerror("エラー", "Kindleが見つかりません")
        return
    
    setup_kindle_window(hwnd)
    
    # 画面サイズを取得してマウスを画面外に移動（フルスクリーン表示の邪魔にならないように）
    sc_w, sc_h = get_screen_size()
    pag.moveTo(sc_w - 200, sc_h - 1)
    time.sleep(kindle_fullscreen_wait)
    
    # タイトルと保存先の取得
    title = get_title()
    base_save_folder = get_save_folder()
    if not base_save_folder:
        messagebox.showerror("エラー", "保存先フォルダが選択されていません")
        return
    
    # 初期画像を取得して境界を検出
    img = ImageGrab.grab()
    img = np.array(img)
    imp = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    lft, rht = find_content_boundaries(imp)
    
    # キャプチャを実行
    total_pages = capture_and_save_pages(lft, rht, title)
    
    # 完了メッセージを表示
    messagebox.showinfo("完了", 
                       f"スクリーンショットの撮影が終了しました。\n"
                       f"合計 {total_pages} ページを保存しました。")

if __name__ == "__main__":
    main()
```

### 実行手順

1.  **Kindle for PCの準備:** PDF化したい本を開き、**全画面表示**にします。
2.  **表示設定の確認:** **見開き表示ではなく、1ページずつの表示**に変更します。
3.  **コードの実行:** 上記の`kindle_screenshot.py`を実行します。
4.  **GUI設定:**
      * **タイトルを入力:** 保存するフォルダの名前を入力します（空白の場合は現在時刻が使用されます）。
      * **保存先フォルダを選択:** 画像ファイルを保存する親フォルダを選択します。
5.  **自動撮影開始:** 設定後、自動でページめくりとスクリーンショット撮影が開始されます。**この間はマウスやキーボードに触れないでください。**
6.  **完了:** 最終ページに到達すると、プログラムが自動で終了し、保存したページ数が表示されます。

-----

## 2\. 📄 ステップ3：PDF変換編

ステップ1で保存した画像ファイル群を、1つのPDFファイルにまとめます。

### 💻 必要なライブラリのインストール

以下のライブラリを事前にインストールしてください。

```bash
pip install Pillow reportlab
```

### 🐍 Pythonコード全文 (kindle\_pdf\_convert.py)

このコードは、GUIを提供し、指定フォルダ内の連番画像を順番にPDFに結合します。

```python
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from reportlab.pdfgen import canvas
import threading

def select_folder():
    """フォルダ選択ダイアログを表示する関数"""
    return filedialog.askdirectory()

def image_to_pdf(folder_path, output_folder, output_filename, progress_var, status_var, root):
    """
    指定フォルダ内の画像をPDFに変換する関数
    """
    # 画像ファイルの取得とソート
    image_files = [f for f in os.listdir(folder_path) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort()

    if not image_files:
        messagebox.showerror("エラー", "指定されたフォルダに画像ファイルが見つかりません。")
        return False

    # PDFの作成
    output_pdf = os.path.join(output_folder, output_filename)
    try:
        c = canvas.Canvas(output_pdf)
    except Exception as e:
        messagebox.showerror("エラー", f"PDFファイルの初期化に失敗しました: {e}")
        return False
        
    total_files = len(image_files)

    for i, image_file in enumerate(image_files, 1):
        # 画像の読み込みとPDFページの作成
        full_path = os.path.join(folder_path, image_file)
        try:
            img = Image.open(full_path)
            width, height = img.size
            c.setPageSize((width, height))
            c.drawImage(full_path, 0, 0, width, height)
            c.showPage()
        except Exception as e:
            messagebox.showerror("エラー", f"画像ファイル '{image_file}' の処理に失敗しました: {e}")
            continue

        # 進捗状況の更新
        progress = (i / total_files) * 100
        progress_var.set(progress)
        status_var.set(f"処理中... {i}/{total_files} ファイル")
        root.update_idletasks()

    c.save()
    progress_var.set(100)
    status_var.set("完了")
    return True

def run_conversion(root, folder_var, output_folder_var, output_filename_var, progress_var, status_var, convert_button):
    """変換処理を実行する関数"""
    # 入力値の取得と検証
    folder_path = folder_var.get()
    output_folder = output_folder_var.get()
    output_filename = output_filename_var.get()

    if not folder_path or not output_folder or not output_filename:
        messagebox.showerror("エラー", 
                           "入力フォルダ、出力フォルダ、ファイル名をすべて指定してください。")
        return

    # 拡張子の確認と追加
    if not output_filename.lower().endswith('.pdf'):
        output_filename += '.pdf'

    # UI状態の初期化
    progress_var.set(0)
    status_var.set("開始中...")
    convert_button.config(state=tk.DISABLED)

    def conversion_thread():
        """変換処理を実行するスレッド"""
        success = image_to_pdf(folder_path, output_folder, output_filename, 
                             progress_var, status_var, root)
        
        # 変換完了後のUI操作はメインスレッドで実行
        root.after(0, lambda: post_conversion(success, output_folder, output_filename, convert_button, root))

    def post_conversion(success, output_folder, output_filename, convert_button, root):
        if success:
            messagebox.showinfo("完了", 
                              f"PDFファイルが作成されました: {os.path.join(output_folder, output_filename)}")
            convert_button.config(text="終了", command=root.quit)
        convert_button.config(state=tk.NORMAL)

    # 別スレッドで変換処理を実行
    thread = threading.Thread(target=conversion_thread)
    thread.start()

# GUIの設定
def setup_gui():
    global root
    root = tk.Tk()
    root.title("Image to PDF Converter")

    # 変数の初期化
    folder_var = tk.StringVar()
    output_folder_var = tk.StringVar()
    output_filename_var = tk.StringVar()
    progress_var = tk.DoubleVar()
    status_var = tk.StringVar()

    # フォルダ選択部分のUI
    tk.Label(root, text="画像があるフォルダを選択:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="参照", 
             command=lambda: folder_var.set(select_folder())).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(root, text="PDFファイルの出力先フォルダを選択:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
    tk.Button(root, text="参照", 
             command=lambda: output_folder_var.set(select_folder())).grid(row=1, column=2, padx=5, pady=5)

    # ファイル名入力部分のUI
    tk.Label(root, text="出力ファイル名:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=output_filename_var, width=50).grid(row=2, column=1, padx=5, pady=5)

    # 変換ボタン
    convert_button = tk.Button(root, text="変換", command=lambda: run_conversion(
        root, folder_var, output_folder_var, output_filename_var, progress_var, status_var, convert_button
    ))
    convert_button.grid(row=3, column=0, columnspan=3, pady=10)

    # プログレスバーとステータス表示
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
    status_label = tk.Label(root, textvariable=status_var)
    status_label.grid(row=5, column=0, columnspan=3, pady=5)

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
```

### 実行手順

1.  **コードの実行:** 上記の`kindle_pdf_convert.py`を実行すると、GUIウィンドウが表示されます。
2.  **入力設定:**
      * **画像があるフォルダを選択:** ステップ1で作成した画像ファイル群が保存されているフォルダを選択します。
      * **PDFファイルの出力先フォルダを選択:** 生成するPDFファイルの保存先フォルダを選択します。
      * **出力ファイル名:** 作成したいPDFファイル名を入力します（例：`my_kindle_book`）。拡張子`.pdf`は自動で追加されます。
3.  **変換実行:** 「**変換**」ボタンをクリックします。
4.  **完了:** 処理が完了すると、完了メッセージが表示され、指定したフォルダにPDFファイルが作成されます。
