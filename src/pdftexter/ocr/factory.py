"""
OCRバックエンド生成モジュール
"""

from typing import Optional, Protocol

from pdftexter.ocr.config import OCRConfig
from pdftexter.ocr.deepseek import DeepSeekOCR
from pdftexter.ocr.ollama import OllamaOCR


class OCRRunner(Protocol):
    """OCR実行クラスのプロトコル定義"""

    def process_image(self, image_path: str, prompt: Optional[str] = None) -> str:
        """画像をOCR処理する。"""

    def process_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        prompt: Optional[str] = None,
        progress_callback: Optional[callable] = None,
        keep_temp_images: bool = False,
    ) -> str:
        """PDFをOCR処理する。"""

    def process_pdf_to_file(
        self,
        pdf_path: str,
        output_file: str,
        output_dir: Optional[str] = None,
        prompt: Optional[str] = None,
        progress_callback: Optional[callable] = None,
        keep_temp_images: bool = False,
        resume: bool = False,
    ) -> str:
        """PDFをOCR処理してファイルに書き込む。"""


def create_ocr_engine(config: OCRConfig, verify_setup: bool = True) -> OCRRunner:
    """
    設定に応じたOCRエンジンを生成する

    Args:
        config: OCR設定オブジェクト
        verify_setup: セットアップを検証するか

    Returns:
        OCR実行クラス
    """
    if config.ocr_backend == "ollama":
        return OllamaOCR(config, verify_setup=verify_setup)
    return DeepSeekOCR(config, verify_setup=verify_setup)
