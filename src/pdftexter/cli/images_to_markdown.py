"""
画像フォルダ → Markdown変換CLIモジュール
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from pdftexter.ocr.config import OCRConfig, load_config
from pdftexter.ocr.factory import create_ocr_engine

DEFAULT_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff")
DEFAULT_DEEPSEEK_PROMPT = "<image>\nFree OCR."
DEFAULT_OLLAMA_PROMPT = (
    "Extract all text from the image. Preserve layout with headings, lists, and tables in Markdown. "
    "The document is mostly Japanese. Do not summarize or add commentary."
)


def natural_sort_key(path: Path) -> List[object]:
    """パス名を数値込みで自然順ソートするキーを生成する。"""
    parts = re.split(r"(\d+)", path.name)
    key: List[object] = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key


def collect_images(folder: Path, extensions: Sequence[str]) -> List[Path]:
    """フォルダ内の画像を拡張子で収集する。"""
    images = [
        path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in extensions
    ]
    images.sort(key=natural_sort_key)
    return images


def is_page_number(line: str) -> bool:
    """ページ番号らしい行を判定する。"""
    stripped = line.strip()
    if not stripped:
        return False
    return re.match(r"^[-–—]?\s*\d+\s*[-–—]?$", stripped) is not None


def normalize_lines(text: str) -> List[str]:
    """OCRテキストを行単位に正規化する。"""
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def strip_edge_noise(lines: List[str]) -> List[str]:
    """ページ番号などの端ノイズを削除する。"""
    trimmed = list(lines)
    for _ in range(2):
        if trimmed and is_page_number(trimmed[0]):
            trimmed.pop(0)
        if trimmed and is_page_number(trimmed[-1]):
            trimmed.pop()
    return trimmed


def find_repeated_edges(
    pages: List[List[str]],
    edge_lines: int = 2,
) -> tuple[set[str], set[str]]:
    """複数ページで繰り返されるヘッダー/フッター候補を抽出する。"""
    header_counter: Counter[str] = Counter()
    footer_counter: Counter[str] = Counter()

    for lines in pages:
        for line in lines[:edge_lines]:
            cleaned = line.strip()
            if cleaned:
                header_counter[cleaned] += 1
        for line in lines[-edge_lines:]:
            cleaned = line.strip()
            if cleaned:
                footer_counter[cleaned] += 1

    threshold = max(2, len(pages) // 3)
    headers = {line for line, count in header_counter.items() if count >= threshold}
    footers = {line for line, count in footer_counter.items() if count >= threshold}
    return headers, footers


def remove_repeated_edges(
    lines: List[str],
    headers: set[str],
    footers: set[str],
) -> List[str]:
    """ヘッダー/フッターとして繰り返される行を除去する。"""
    trimmed = list(lines)
    while trimmed and trimmed[0].strip() in headers:
        trimmed.pop(0)
    while trimmed and trimmed[-1].strip() in footers:
        trimmed.pop()
    return trimmed


def needs_join(prev_text: str, next_text: str) -> bool:
    """ページまたぎで行継ぎ足しが必要か判定する。"""
    prev_text = prev_text.rstrip()
    next_text = next_text.lstrip()
    if not prev_text or not next_text:
        return False
    if not prev_text.endswith("-"):
        return False
    if len(prev_text) < 2 or not prev_text[-2].isalpha():
        return False
    return re.match(r"^[a-z]", next_text) is not None


def merge_pages(pages: List[str]) -> str:
    """ページテキストを連結して1つのドキュメントにする。"""
    combined_parts: List[str] = []
    prev_text: Optional[str] = None
    for page_text in pages:
        if prev_text is None:
            prev_text = page_text
            continue

        if needs_join(prev_text, page_text):
            prev_text = prev_text.rstrip()[:-1]
            separator = ""
        else:
            separator = "\n\n"

        combined_parts.append(prev_text + separator)
        prev_text = page_text

    if prev_text is not None:
        combined_parts.append(prev_text)

    return "".join(combined_parts).strip() + "\n"


def default_prompt_for_backend(config: OCRConfig) -> str:
    """OCRバックエンドに応じた既定プロンプトを返す。"""
    if config.ocr_backend == "ollama":
        return DEFAULT_OLLAMA_PROMPT
    return DEFAULT_DEEPSEEK_PROMPT


def ocr_images_to_markdown(
    folder: Path,
    output_path: Path,
    config_path: Optional[str],
    prompt: Optional[str],
    output_format: str,
    skip_verify: bool,
    no_progress: bool,
    apply_cleanup: bool,
) -> int:
    """画像フォルダをOCR処理してMarkdownに保存する。"""
    images = collect_images(folder, DEFAULT_EXTENSIONS)
    if not images:
        print(f"エラー: 画像ファイルが見つかりません: {folder}", file=sys.stderr)
        return 1

    try:
        config = load_config(config_path) if config_path else load_config()
        if config.ocr_backend == "ollama":
            config.ollama_ocr.output_format = output_format
        else:
            config.deepseek_ocr.output_format = output_format
    except Exception as exc:
        print(f"エラー: 設定ファイルの読み込みに失敗しました: {exc}", file=sys.stderr)
        return 1

    try:
        ocr = create_ocr_engine(config, verify_setup=not skip_verify)
    except Exception as exc:
        print(f"エラー: OCRエンジンの初期化に失敗しました: {exc}", file=sys.stderr)
        return 1

    ocr_prompt = prompt or default_prompt_for_backend(config)
    total = len(images)
    results: List[str] = []

    for idx, image_path in enumerate(images, 1):
        if not no_progress:
            print(f"処理中... {idx}/{total} {image_path.name}", end="\r")
        try:
            page_text = ocr.process_image(str(image_path), prompt=ocr_prompt).strip()
        except Exception as exc:
            page_text = f"<!-- ページ {idx} の処理に失敗しました: {exc} -->"
        results.append(page_text)

    if not no_progress:
        print()

    if apply_cleanup:
        normalized_pages = [strip_edge_noise(normalize_lines(text)) for text in results]
        headers, footers = find_repeated_edges(normalized_pages)
        cleaned_pages = [
            "\n".join(remove_repeated_edges(page_lines, headers, footers)).strip()
            for page_lines in normalized_pages
        ]
    else:
        cleaned_pages = [text.strip() for text in results]

    combined = merge_pages(cleaned_pages)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(combined, encoding="utf-8")

    print(f"完了: {output_path}")
    return 0


def main() -> int:
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="画像フォルダをOCR処理してMarkdownにまとめる",
    )
    parser.add_argument("input", type=str, help="入力画像フォルダのパス")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="出力ファイルのパス（省略時はフォルダ名.md）",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="バッチ時の出力先ディレクトリ（省略時は入力フォルダ配下）",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="入力フォルダ直下の各サブフォルダを順次処理する",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="OCR設定ファイルのパス",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="OCR用カスタムプロンプト",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "plain"],
        default="markdown",
        help="出力形式（デフォルト: markdown）",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="OCRセットアップの検証をスキップ",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="進捗表示を無効化",
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="ヘッダー/フッター除去などの後処理を無効化",
    )

    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"エラー: 入力フォルダが見つかりません: {args.input}", file=sys.stderr)
        return 1

    target_folders: Iterable[Path]
    if args.batch:
        target_folders = [path for path in input_path.iterdir() if path.is_dir()]
    else:
        target_folders = [input_path]

    output_dir = Path(args.output_dir) if args.output_dir else None
    status = 0
    for folder in target_folders:
        if not folder.exists():
            print(f"警告: フォルダが見つかりません: {folder}", file=sys.stderr)
            status = 1
            continue

        if args.output and not args.batch:
            output_path = Path(args.output)
        else:
            base_dir = output_dir if output_dir else folder
            output_path = base_dir / f"{folder.name}.md"

        result = ocr_images_to_markdown(
            folder=folder,
            output_path=output_path,
            config_path=args.config,
            prompt=args.prompt,
            output_format=args.format,
            skip_verify=args.skip_verify,
            no_progress=args.no_progress,
            apply_cleanup=not args.no_cleanup,
        )
        status = max(status, result)

    return status


if __name__ == "__main__":
    sys.exit(main())
