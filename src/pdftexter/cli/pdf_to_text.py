"""
PDF→Text変換CLIモジュール
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from pdftexter.ocr.config import load_config
from pdftexter.ocr.deepseek import DeepSeekOCR


def progress_callback(current: int, total: int) -> None:
    """
    進捗表示コールバック関数

    Args:
        current: 現在のページ番号
        total: 総ページ数
    """
    progress = (current / total) * 100
    print(f"処理中... {current}/{total} ページ ({progress:.1f}%)", end="\r")
    if current == total:
        print()  # 最後に改行


def main() -> int:
    """
    メイン関数
    
    Returns:
        終了コード（0: 成功、1: エラー）
    """
    parser = argparse.ArgumentParser(
        description="PDFファイルをOCR処理してテキスト（Markdown）に変換"
    )
    parser.add_argument(
        "input",
        type=str,
        help="入力PDFファイルのパス",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="出力ファイルのパス（省略時は入力ファイル名に.mdを付加）",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="OCR設定ファイルのパス（省略時はデフォルト設定を使用）",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="カスタムプロンプト（省略時はデフォルトプロンプトを使用）",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "plain"],
        default="markdown",
        help="出力形式（デフォルト: markdown）",
    )
    parser.add_argument(
        "--temp-dir",
        type=str,
        help="中間画像を保存する一時ディレクトリ（省略時は自動生成）",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="進捗表示を無効化",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="OCRセットアップの検証をスキップ",
    )
    parser.add_argument(
        "--keep-temp-images",
        action="store_true",
        help="一時画像を保持する（デバッグ用）",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="中断した処理を再開する（進捗ファイルから続きから開始）",
    )
    
    args = parser.parse_args()
    
    # 入力ファイルの検証
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input}", file=sys.stderr)
        return 1
    
    if not input_path.suffix.lower() == ".pdf":
        print(f"エラー: 入力ファイルがPDF形式ではありません: {args.input}", file=sys.stderr)
        return 1
    
    # 出力ファイルのパスを決定
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".md")
    
    # 設定の読み込み
    try:
        config = load_config(args.config) if args.config else load_config()
        # 出力形式を設定に反映
        config.deepseek_ocr.output_format = args.format
    except Exception as e:
        print(f"エラー: 設定ファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1
    
    # DeepSeek-OCRの初期化（セットアップ検証を実行）
    try:
        ocr = DeepSeekOCR(config, verify_setup=not args.skip_verify)
    except RuntimeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        print("\nヒント: --skip-verify オプションでセットアップ検証をスキップできます", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"エラー: DeepSeek-OCRの初期化に失敗しました: {e}", file=sys.stderr)
        return 1
    
    # OCR処理を実行
    try:
        print(f"PDFファイルを処理中: {input_path}")
        print(f"出力先: {output_path}")
        
        callback = None if args.no_progress else progress_callback
        
        output_file = ocr.process_pdf_to_file(
            pdf_path=str(input_path),
            output_file=str(output_path),
            output_dir=args.temp_dir,
            prompt=args.prompt,
            progress_callback=callback,
            keep_temp_images=args.keep_temp_images,
            resume=args.resume,
        )
        
        print(f"完了: {output_file}")
        return 0
        
    except Exception as e:
        print(f"エラー: OCR処理に失敗しました: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

