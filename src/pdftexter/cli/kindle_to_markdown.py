"""
Kindle → Markdown変換の統合ワークフロー

PDF化した時点で完成度を評価し、進むかやり直すかを選択できる
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from pdftexter.cli.pdf_to_text import main as pdf_to_text_main
from pdftexter.kindle.screenshot import KindleScreenshot
from pdftexter.pdf.converter import PDFConverter


def check_pdf_quality(pdf_path: Path) -> bool:
    """
    PDFの品質を簡易チェック（ファイルサイズと存在確認）
    
    Args:
        pdf_path: PDFファイルのパス
        
    Returns:
        品質が良好な場合True
    """
    if not pdf_path.exists():
        return False
    
    # ファイルサイズが0より大きいことを確認
    if pdf_path.stat().st_size == 0:
        print("警告: PDFファイルが空です")
        return False
    
    print(f"PDFファイルサイズ: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
    return True


def interactive_pdf_review(pdf_path: Path) -> bool:
    """
    PDFをレビューして、続行するかやり直すかをユーザーに尋ねる
    
    Args:
        pdf_path: PDFファイルのパス
        
    Returns:
        続行する場合True、やり直す場合False
    """
    print("\n" + "=" * 60)
    print("PDF生成が完了しました")
    print("=" * 60)
    print(f"PDFファイル: {pdf_path}")
    print(f"ファイルサイズ: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
    print("\nPDFファイルを確認してください。")
    print("1. 続行してOCR処理を実行する")
    print("2. やり直す（PDFを再生成する）")
    print("3. 終了する")
    
    while True:
        choice = input("\n選択してください (1/2/3): ").strip()
        if choice == "1":
            return True
        elif choice == "2":
            return False
        elif choice == "3":
            sys.exit(0)
        else:
            print("無効な選択です。1、2、または3を入力してください。")


def kindle_to_markdown_workflow(
    pdf_output_dir: Optional[str] = None,
    pdf_filename: Optional[str] = None,
    text_output: Optional[str] = None,
    ocr_config: Optional[str] = None,
    ocr_prompt: Optional[str] = None,
    ocr_format: str = "markdown",
    skip_review: bool = False,
) -> int:
    """
    Kindle → PDF → Markdown の統合ワークフロー
    
    Args:
        pdf_output_dir: PDF出力ディレクトリ
        pdf_filename: PDFファイル名
        text_output: テキスト出力ファイル
        ocr_config: OCR設定ファイル
        ocr_prompt: OCR用プロンプト
        ocr_format: OCR出力形式
        skip_review: PDFレビューをスキップする
        
    Returns:
        終了コード
    """
    print("=" * 60)
    print("Kindle → PDF → Markdown 変換ワークフロー")
    print("=" * 60)
    
    # ステップ1: Kindleスクリーンショット撮影
    print("\n[ステップ1] Kindleスクリーンショット撮影")
    print("Kindle for PCを準備してください:")
    print("  1. PDF化したい本を開く")
    print("  2. 全画面表示にする")
    print("  3. 見開き表示ではなく、1ページずつの表示に変更")
    print("\n準備ができたら Enter キーを押してください...")
    input()
    
    print("\nGUIを起動します...")
    print("GUIで以下を設定してください:")
    print("  - タイトル（保存フォルダ名）")
    print("  - 保存先フォルダ")
    print("\nスクリーンショット撮影が完了したら、画像フォルダのパスを入力してください。")
    
    # GUIを起動（別プロセスで実行）
    screenshot = KindleScreenshot()
    screenshot.run()
    
    # 画像フォルダのパスを取得
    image_folder = input("\n画像フォルダのパスを入力してください: ").strip()
    image_folder_path = Path(image_folder)
    
    if not image_folder_path.exists():
        print(f"エラー: 画像フォルダが見つかりません: {image_folder}", file=sys.stderr)
        return 1
    
    # ステップ2: 画像 → PDF
    print("\n[ステップ2] 画像 → PDF変換")
    
    if pdf_output_dir is None:
        pdf_output_dir = str(image_folder_path.parent)
    if pdf_filename is None:
        pdf_filename = image_folder_path.name + ".pdf"
    
    converter = PDFConverter()
    success = converter.convert_images_to_pdf(
        folder_path=str(image_folder_path),
        output_folder=pdf_output_dir,
        output_filename=pdf_filename,
        progress_var=None,
        status_var=None,
        root=None,
    )
    
    if not success:
        print("エラー: PDF変換に失敗しました", file=sys.stderr)
        return 1
    
    pdf_path = Path(pdf_output_dir) / pdf_filename
    
    # PDFの品質チェック
    if not check_pdf_quality(pdf_path):
        print("エラー: PDFファイルの品質に問題があります", file=sys.stderr)
        return 1
    
    # PDFレビュー（スキップされていない場合）
    if not skip_review:
        should_continue = interactive_pdf_review(pdf_path)
        if not should_continue:
            print("\nPDFを再生成してください。")
            return 1
    
    # ステップ3: PDF → Text
    print("\n[ステップ3] PDF → Text変換（OCR）")
    
    if text_output is None:
        text_output = str(pdf_path.with_suffix(".md"))
    
    # pdf_to_textの引数を構築
    original_argv = sys.argv
    sys.argv = [
        "pdf-to-text",
        str(pdf_path),
        "-o",
        text_output,
    ]
    
    if ocr_config:
        sys.argv.extend(["-c", ocr_config])
    if ocr_prompt:
        sys.argv.extend(["-p", ocr_prompt])
    if ocr_format:
        sys.argv.extend(["--format", ocr_format])
    
    try:
        result = pdf_to_text_main()
    finally:
        sys.argv = original_argv
    
    if result != 0:
        print("エラー: OCR処理に失敗しました", file=sys.stderr)
        return result
    
    print(f"\n" + "=" * 60)
    print("完了: テキストファイルを作成しました")
    print("=" * 60)
    print(f"PDF: {pdf_path}")
    print(f"Markdown: {text_output}")
    
    return 0


def main() -> int:
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Kindle → PDF → Markdown の統合ワークフロー（PDFレビュー機能付き）"
    )
    parser.add_argument(
        "--pdf-output-dir",
        type=str,
        help="PDF出力ディレクトリ（省略時は画像フォルダの親ディレクトリ）",
    )
    parser.add_argument(
        "--pdf-filename",
        type=str,
        help="PDFファイル名（省略時は画像フォルダ名 + .pdf）",
    )
    parser.add_argument(
        "-o",
        "--text-output",
        type=str,
        help="最終的なテキスト出力ファイルのパス",
    )
    parser.add_argument(
        "--ocr-config",
        type=str,
        help="OCR設定ファイルのパス",
    )
    parser.add_argument(
        "--ocr-prompt",
        type=str,
        help="OCR用カスタムプロンプト",
    )
    parser.add_argument(
        "--ocr-format",
        choices=["markdown", "plain"],
        default="markdown",
        help="OCR出力形式",
    )
    parser.add_argument(
        "--skip-review",
        action="store_true",
        help="PDFレビューをスキップして自動的にOCR処理に進む",
    )
    
    args = parser.parse_args()
    
    return kindle_to_markdown_workflow(
        pdf_output_dir=args.pdf_output_dir,
        pdf_filename=args.pdf_filename,
        text_output=args.text_output,
        ocr_config=args.ocr_config,
        ocr_prompt=args.ocr_prompt,
        ocr_format=args.ocr_format,
        skip_review=args.skip_review,
    )


if __name__ == "__main__":
    sys.exit(main())

