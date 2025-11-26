"""
PDF処理ユーティリティモジュール
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image


def extract_pdf_pages_as_images(
    pdf_path: str,
    output_dir: str,
    dpi: int = 200,
) -> List[str]:
    """
    PDFファイルを画像に変換して各ページを保存する
    
    Args:
        pdf_path: PDFファイルのパス
        output_dir: 画像を保存するディレクトリ
        dpi: 画像の解像度（デフォルト: 200）
        
    Returns:
        生成された画像ファイルのパスのリスト
        
    Raises:
        ImportError: pdf2imageがインストールされていない場合
        FileNotFoundError: PDFファイルが見つからない場合
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError(
            "pdf2image is required for PDF processing. "
            "Install it with: pip install pdf2image"
        )
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
    
    # 出力ディレクトリを作成
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # PDFを画像に変換
    images = convert_from_path(pdf_path, dpi=dpi)
    
    # 各ページを画像として保存
    image_paths = []
    for i, image in enumerate(images, 1):
        image_filename = f"page_{i:04d}.png"
        image_path = output_path / image_filename
        image.save(image_path, "PNG")
        image_paths.append(str(image_path))
    
    return image_paths


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    PDFファイルのメタデータを取得する
    
    Args:
        pdf_path: PDFファイルのパス
        
    Returns:
        メタデータの辞書（ページ数、ファイルサイズなど）
        
    Raises:
        FileNotFoundError: PDFファイルが見つからない場合
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError(
            "pdf2image is required for PDF processing. "
            "Install it with: pip install pdf2image"
        )
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
    
    # ページ数を取得（全ページを読み込む）
    all_images = convert_from_path(pdf_path)
    total_pages = len(all_images)
    
    metadata = {
        "file_path": str(pdf_path),
        "file_size": pdf_file.stat().st_size,
        "total_pages": total_pages,
    }
    
    return metadata


def validate_pdf(pdf_path: str) -> Tuple[bool, Optional[str]]:
    """
    PDFファイルの妥当性を検証する
    
    Args:
        pdf_path: PDFファイルのパス
        
    Returns:
        (有効かどうか, エラーメッセージ)のタプル
    """
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        return False, f"PDFファイルが見つかりません: {pdf_path}"
    
    if not pdf_file.is_file():
        return False, f"パスがファイルではありません: {pdf_path}"
    
    if pdf_file.suffix.lower() != ".pdf":
        return False, f"ファイルがPDF形式ではありません: {pdf_path}"
    
    if pdf_file.stat().st_size == 0:
        return False, f"PDFファイルが空です: {pdf_path}"
    
    # PDFの内容を検証（pdf2imageで読み込めるか確認）
    try:
        from pdf2image import convert_from_path
        # 最初のページのみ読み込んで検証
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if len(images) == 0:
            return False, "PDFファイルにページが含まれていません"
    except Exception as e:
        return False, f"PDFファイルの読み込みに失敗しました: {e}"
    
    return True, None

