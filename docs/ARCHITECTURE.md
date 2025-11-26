# pdftexter アーキテクチャ設計書

## 📋 概要

pdftexterは、Kindle電子書籍をPDF化し、さらにPDFからテキスト（Markdown）に変換するためのPythonプロジェクトです。DeepSeek-OCRモデルを活用して、長文脈に対応した高精度なOCR処理を実現します。

## 🏗️ プロジェクト構造

```
pdftexter/
├── src/
│   └── pdftexter/
│       ├── __init__.py
│       ├── kindle/              # Kindle関連モジュール
│       │   ├── __init__.py
│       │   ├── screenshot.py    # スクリーンショット撮影機能
│       │   └── window.py        # ウィンドウ操作ユーティリティ
│       ├── pdf/                 # PDF関連モジュール
│       │   ├── __init__.py
│       │   ├── converter.py    # 画像→PDF変換機能
│       │   └── processor.py    # PDF処理ユーティリティ
│       ├── ocr/                 # OCR関連モジュール
│       │   ├── __init__.py
│       │   ├── deepseek.py     # DeepSeek-OCR統合
│       │   ├── vllm_wrapper.py # vLLM版ラッパー
│       │   └── config.py       # OCR設定管理
│       ├── utils/               # 共通ユーティリティ
│       │   ├── __init__.py
│       │   ├── image.py        # 画像処理ユーティリティ
│       │   ├── file.py         # ファイル操作ユーティリティ
│       │   └── gui.py          # GUI共通コンポーネント
│       └── cli/                 # CLIインターフェース
│           ├── __init__.py
│           ├── kindle_to_pdf.py # Kindle→PDF CLI
│           └── pdf_to_text.py  # PDF→Text CLI
├── tests/                       # テストコード
│   ├── __init__.py
│   ├── test_kindle/
│   ├── test_pdf/
│   └── test_ocr/
├── scripts/                     # 実行スクリプト
│   ├── kindle_screenshot.py    # 既存スクリプト（互換性維持）
│   ├── kindle_pdf_convert.py   # 既存スクリプト（互換性維持）
│   └── pdf_to_text.py          # PDF→Text実行スクリプト
├── docs/                        # ドキュメント
│   ├── ARCHITECTURE.md         # 本ファイル
│   └── PLAN.md                 # 実装プラン
├── config/                      # 設定ファイル
│   └── ocr_config.yaml         # OCR設定
├── output/                      # 出力ディレクトリ（.gitignore）
│   ├── images/                 # スクリーンショット画像
│   ├── pdfs/                   # 生成されたPDF
│   └── texts/                  # OCR結果（Markdown）
├── pyproject.toml              # プロジェクト設定
├── README.md                   # プロジェクト説明
└── LICENSE                     # ライセンス
```

## 🔧 モジュール設計

### 1. kindle モジュール

Kindle for PCアプリケーションとの連携を担当します。

#### `screenshot.py`
- **責務**: Kindleウィンドウの自動操作とスクリーンショット撮影
- **主要機能**:
  - ウィンドウ検出とフォーカス設定
  - 全画面表示への切り替え
  - ページ自動めくり
  - スクリーンショット撮影と保存
  - コンテンツ境界検出（余白削除）

#### `window.py`
- **責務**: Windows APIを使用したウィンドウ操作
- **主要機能**:
  - ウィンドウ検索（EnumWindows）
  - ウィンドウフォーカス設定
  - ウィンドウサイズ・位置取得

### 2. pdf モジュール

PDFファイルの生成と処理を担当します。

#### `converter.py`
- **責務**: 画像ファイル群をPDFに変換
- **主要機能**:
  - 画像ファイルの読み込みとソート
  - PDFページ生成（reportlab使用）
  - 進捗管理とGUI連携

#### `processor.py`
- **責務**: PDFファイルの前処理・後処理
- **主要機能**:
  - PDFメタデータ取得
  - PDFページ分割（必要に応じて）
  - PDF検証

### 3. ocr モジュール

DeepSeek-OCRモデルとの統合を担当します。

#### `deepseek.py`
- **責務**: DeepSeek-OCRの統合インターフェース
- **主要機能**:
  - vLLM版DeepSeek-OCRの呼び出し
  - PDF/画像ファイルのOCR処理
  - Markdown形式での出力
  - エラーハンドリング

#### `vllm_wrapper.py`
- **責務**: vLLM版DeepSeek-OCRのラッパー実装
- **主要機能**:
  - vLLMサーバーとの通信
  - リクエスト/レスポンス処理
  - バッチ処理対応
  - タイムアウト・リトライ処理

#### `config.py`
- **責務**: OCR設定の管理
- **主要機能**:
  - 設定ファイル（YAML）の読み込み
  - デフォルト設定の提供
  - 設定の検証

### 4. utils モジュール

共通ユーティリティ関数を提供します。

#### `image.py`
- 画像処理ユーティリティ（OpenCV, PIL）
- 境界検出アルゴリズム
- 画像形式変換

#### `file.py`
- ファイル操作ユーティリティ
- パス操作
- ディレクトリ作成・管理

#### `gui.py`
- GUI共通コンポーネント（tkinter）
- 進捗バー表示
- ファイル選択ダイアログ

### 5. cli モジュール

コマンドラインインターフェースを提供します。

#### `kindle_to_pdf.py`
- Kindle→PDF変換のCLI実装
- 引数解析（argparse）
- エラーハンドリング

#### `pdf_to_text.py`
- PDF→Text変換のCLI実装
- DeepSeek-OCR呼び出し
- 出力形式選択（Markdown/Plain Text）

## 🔄 データフロー

### フロー1: Kindle → PDF

```
Kindle for PC
    ↓
[window.py] ウィンドウ検出・フォーカス
    ↓
[screenshot.py] スクリーンショット撮影
    ↓
[image.py] 境界検出・トリミング
    ↓
[converter.py] PDF生成
    ↓
PDFファイル
```

### フロー2: PDF → Text (Markdown)

```
PDFファイル
    ↓
[processor.py] PDF検証・前処理
    ↓
[deepseek.py] DeepSeek-OCR呼び出し
    ↓
[vllm_wrapper.py] vLLMサーバー通信
    ↓
DeepSeek-OCR Model
    ↓
Markdown形式テキスト
    ↓
[file.py] ファイル保存
```

## 🛠️ 技術スタック

### コアライブラリ
- **Python 3.12+**: メイン言語
- **Poetry**: 依存関係管理
- **pyenv**: Pythonバージョン管理

### Kindle関連
- **pyautogui**: 自動操作
- **Pillow (PIL)**: 画像処理
- **opencv-python**: 画像処理・境界検出
- **ctypes**: Windows API呼び出し

### PDF関連
- **reportlab**: PDF生成
- **Pillow**: 画像読み込み

### OCR関連
- **vLLM**: 推論エンジン
- **torch**: 深層学習フレームワーク
- **DeepSeek-OCR**: OCRモデル

### 開発・品質管理
- **mypy**: 静的型チェック
- **vulture**: 未使用コード検出
- **pydantic**: データ検証
- **pytest**: テストフレームワーク

## 📦 依存関係管理

### Poetry設定
- `pyproject.toml`で依存関係を管理
- 開発依存関係と本番依存関係を分離
- バージョン固定による再現性確保

### 環境変数
- `DEEPSEEK_OCR_MODEL_PATH`: モデルパス
- `VLLM_SERVER_URL`: vLLMサーバーURL（オプション）
- `OUTPUT_BASE_DIR`: デフォルト出力ディレクトリ

## 🔒 セキュリティ・注意事項

1. **著作権**: PDF化・OCR化したコンテンツの著作権に注意
2. **個人利用**: 個人的な学習・利用の範囲を超えた複製・配布は禁止
3. **データ保護**: 処理したデータの適切な管理

## 🚀 拡張性

### 将来の拡張候補
- 他のOCRエンジン対応（Tesseract, EasyOCR等）
- バッチ処理機能の強化
- Web UIの提供（Flask/FastAPI）
- クラウドOCRサービスの統合
- 多言語対応の強化
