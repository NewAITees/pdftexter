"""
pdftexter統合CLI

Kindle → PDF → Text の一連のワークフローを統合したCLIインターフェース
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from pdftexter.cli.pdf_to_text import main as pdf_to_text_main
from pdftexter.kindle.screenshot import KindleScreenshot
from pdftexter.pdf.converter import PDFConverter


def kindle_to_pdf_cli(args: argparse.Namespace) -> int:
    """
    Kindle → PDF変換のCLI処理
    
    Args:
        args: コマンドライン引数
        
    Returns:
        終了コード
    """
    # 現在はGUIを使用しているため、CLI版は未実装
    print("Kindle → PDF変換は現在GUI版のみ対応しています。")
    print("以下のコマンドでGUIを起動してください:")
    print("  poetry run python scripts/kindle_screenshot.py")
    print("  poetry run python scripts/kindle_pdf_convert.py")
    return 0


def pdf_to_text_cli(args: argparse.Namespace) -> int:
    """
    PDF → Text変換のCLI処理
    
    Args:
        args: コマンドライン引数
        
    Returns:
        終了コード
    """
    # pdf_to_textモジュールのmain関数を呼び出し
    # 引数を再構築
    sys.argv = ["pdf-to-text", args.input] + (
        ["-o", args.output] if args.output else []
    ) + (
        ["-c", args.config] if args.config else []
    ) + (
        ["-p", args.prompt] if args.prompt else []
    ) + (
        ["--format", args.format] if args.format else []
    ) + (
        ["--temp-dir", args.temp_dir] if args.temp_dir else []
    ) + (
        ["--no-progress"] if args.no_progress else []
    )
    
    return pdf_to_text_main()


def full_workflow_cli(args: argparse.Namespace) -> int:
    """
    Kindle → PDF → Text の一括処理
    
    Args:
        args: コマンドライン引数
        
    Returns:
        終了コード
    """
    print("Kindle → PDF → Text の一括処理")
    print("=" * 50)
    
    # ステップ1: Kindle → 画像（現在はGUIのみ）
    print("\n[ステップ1] Kindleスクリーンショット撮影")
    print("注意: このステップは現在GUI版のみ対応しています。")
    print("以下のコマンドでGUIを起動してください:")
    print("  poetry run python scripts/kindle_screenshot.py")
    
    # ユーザーに画像フォルダの入力を求める
    image_folder = args.image_folder
    if not image_folder:
        image_folder = input("\n画像フォルダのパスを入力してください: ").strip()
    
    if not Path(image_folder).exists():
        print(f"エラー: 画像フォルダが見つかりません: {image_folder}", file=sys.stderr)
        return 1
    
    # ステップ2: 画像 → PDF
    print("\n[ステップ2] 画像 → PDF変換")
    pdf_output_dir = args.pdf_output_dir or Path(image_folder).parent
    pdf_filename = args.pdf_filename or Path(image_folder).name + ".pdf"
    
    converter = PDFConverter()
    success = converter.convert_images_to_pdf(
        folder_path=image_folder,
        output_folder=str(pdf_output_dir),
        output_filename=pdf_filename,
        progress_var=None,
        status_var=None,
        root=None,
    )
    
    if not success:
        print("エラー: PDF変換に失敗しました", file=sys.stderr)
        return 1
    
    pdf_path = Path(pdf_output_dir) / pdf_filename
    print(f"PDFファイルを作成しました: {pdf_path}")
    
    # ステップ3: PDF → Text
    print("\n[ステップ3] PDF → Text変換（OCR）")
    
    # pdf_to_textの引数を構築
    text_output = args.text_output or pdf_path.with_suffix(".md")
    
    # 一時的にsys.argvを設定
    original_argv = sys.argv
    sys.argv = [
        "pdf-to-text",
        str(pdf_path),
        "-o",
        str(text_output),
    ]
    
    if args.ocr_config:
        sys.argv.extend(["-c", args.ocr_config])
    if args.ocr_prompt:
        sys.argv.extend(["-p", args.ocr_prompt])
    if args.ocr_format:
        sys.argv.extend(["--format", args.ocr_format])
    
    try:
        result = pdf_to_text_main()
    finally:
        sys.argv = original_argv
    
    if result != 0:
        print("エラー: OCR処理に失敗しました", file=sys.stderr)
        return result
    
    print(f"\n完了: テキストファイルを作成しました: {text_output}")
    return 0


def main() -> int:
    """
    メイン関数
    
    Returns:
        終了コード
    """
    parser = argparse.ArgumentParser(
        description="pdftexter: Kindle電子書籍をPDF化し、OCRでテキストに変換する統合ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # PDF → Text変換のみ
  pdftexter pdf-to-text input.pdf -o output.md
  
  # Kindle → PDF → Markdown（PDFレビュー機能付き）
  pdftexter kindle-to-markdown -o output.md
  
  # Kindle → PDF → Text の一括処理（画像フォルダから開始）
  pdftexter full input_folder -o output.md
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="サブコマンド")
    
    # kindle-to-pdf サブコマンド
    kindle_parser = subparsers.add_parser(
        "kindle-to-pdf",
        help="Kindle → PDF変換（現在はGUI版のみ）",
    )
    kindle_parser.set_defaults(func=kindle_to_pdf_cli)
    
    # pdf-to-text サブコマンド
    pdf_text_parser = subparsers.add_parser(
        "pdf-to-text",
        help="PDF → Text変換（OCR）",
    )
    pdf_text_parser.add_argument("input", type=str, help="入力PDFファイルのパス")
    pdf_text_parser.add_argument(
        "-o", "--output", type=str, help="出力ファイルのパス"
    )
    pdf_text_parser.add_argument(
        "-c", "--config", type=str, help="OCR設定ファイルのパス"
    )
    pdf_text_parser.add_argument(
        "-p", "--prompt", type=str, help="カスタムプロンプト"
    )
    pdf_text_parser.add_argument(
        "--format",
        choices=["markdown", "plain"],
        default="markdown",
        help="出力形式",
    )
    pdf_text_parser.add_argument(
        "--temp-dir", type=str, help="中間画像を保存する一時ディレクトリ"
    )
    pdf_text_parser.add_argument(
        "--no-progress", action="store_true", help="進捗表示を無効化"
    )
    pdf_text_parser.set_defaults(func=pdf_to_text_cli)
    
    # kindle-to-markdown サブコマンド（PDFレビュー機能付き）
    kindle_md_parser = subparsers.add_parser(
        "kindle-to-markdown",
        help="Kindle → PDF → Markdown 変換（PDFレビュー機能付き）",
    )
    kindle_md_parser.add_argument(
        "--pdf-output-dir",
        type=str,
        help="PDF出力ディレクトリ",
    )
    kindle_md_parser.add_argument(
        "--pdf-filename",
        type=str,
        help="PDFファイル名",
    )
    kindle_md_parser.add_argument(
        "-o",
        "--text-output",
        type=str,
        help="最終的なテキスト出力ファイルのパス",
    )
    kindle_md_parser.add_argument(
        "--ocr-config",
        type=str,
        help="OCR設定ファイルのパス",
    )
    kindle_md_parser.add_argument(
        "--ocr-prompt",
        type=str,
        help="OCR用カスタムプロンプト",
    )
    kindle_md_parser.add_argument(
        "--ocr-format",
        choices=["markdown", "plain"],
        default="markdown",
        help="OCR出力形式",
    )
    kindle_md_parser.add_argument(
        "--skip-review",
        action="store_true",
        help="PDFレビューをスキップ",
    )
    def kindle_to_markdown_wrapper(args: argparse.Namespace) -> int:
        """kindle-to-markdownコマンドのラッパー"""
        from pdftexter.cli.kindle_to_markdown import kindle_to_markdown_workflow
        return kindle_to_markdown_workflow(
            pdf_output_dir=args.pdf_output_dir,
            pdf_filename=args.pdf_filename,
            text_output=args.text_output,
            ocr_config=args.ocr_config,
            ocr_prompt=args.ocr_prompt,
            ocr_format=args.ocr_format,
            skip_review=args.skip_review,
        )
    
    kindle_md_parser.set_defaults(func=kindle_to_markdown_wrapper)
    
    # full サブコマンド（一括処理）
    full_parser = subparsers.add_parser(
        "full",
        help="Kindle → PDF → Text の一括処理（画像フォルダから開始）",
    )
    full_parser.add_argument(
        "image_folder",
        type=str,
        nargs="?",
        help="Kindleスクリーンショット画像のフォルダパス",
    )
    full_parser.add_argument(
        "-o",
        "--text-output",
        type=str,
        help="最終的なテキスト出力ファイルのパス",
    )
    full_parser.add_argument(
        "--pdf-output-dir",
        type=str,
        help="PDF出力ディレクトリ（省略時は画像フォルダの親ディレクトリ）",
    )
    full_parser.add_argument(
        "--pdf-filename",
        type=str,
        help="PDFファイル名（省略時は画像フォルダ名 + .pdf）",
    )
    full_parser.add_argument(
        "--ocr-config",
        type=str,
        help="OCR設定ファイルのパス",
    )
    full_parser.add_argument(
        "--ocr-prompt",
        type=str,
        help="OCR用カスタムプロンプト",
    )
    full_parser.add_argument(
        "--ocr-format",
        choices=["markdown", "plain"],
        default="markdown",
        help="OCR出力形式",
    )
    full_parser.set_defaults(func=full_workflow_cli)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

