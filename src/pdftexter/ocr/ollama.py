"""
Ollama VLM OCR統合モジュール
"""

import os
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional

import requests

from pdftexter.ocr.config import OCRConfig, load_config
from pdftexter.ocr.ollama_wrapper import OllamaWrapper
from pdftexter.pdf.processor import extract_pdf_pages_as_images, validate_pdf


class OllamaOCR:
    """Ollama VLM OCR統合クラス"""

    def __init__(self, config: Optional[OCRConfig] = None, verify_setup: bool = True) -> None:
        """
        初期化

        Args:
            config: OCR設定オブジェクト（Noneの場合はデフォルト設定を使用）
            verify_setup: セットアップを検証するか（デフォルト: True）

        Raises:
            RuntimeError: セットアップが完了していない場合
        """
        self.config = config or load_config()
        self.wrapper = OllamaWrapper(
            base_url=self.config.ollama_ocr.base_url,
            model_name=self.config.ollama_ocr.model_name,
            timeout=self.config.ollama_ocr.timeout,
            max_retries=self.config.ollama_ocr.max_retries,
            retry_delay=self.config.ollama_ocr.retry_delay,
        )

        if verify_setup:
            self._verify_setup()

    def _verify_setup(self) -> None:
        """Ollamaサーバーとモデルの準備状態を確認する。"""
        tags_url = f"{self.wrapper.base_url}/api/tags"
        try:
            response = requests.get(tags_url, timeout=self.config.ollama_ocr.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError("Ollamaサーバーに接続できません。`ollama serve`が起動しているか確認してください。") from exc

        data = response.json()
        models = data.get("models", [])
        if not self._model_exists(models, self.config.ollama_ocr.model_name):
            raise RuntimeError(
                "指定されたOllamaモデルが見つかりません。"
                f"`ollama pull {self.config.ollama_ocr.model_name}`を実行してください。"
            )

    @staticmethod
    def _model_exists(models: List[dict], model_name: str) -> bool:
        """モデル一覧から指定モデルが存在するか確認する。"""
        if not model_name:
            return False

        normalized_target = model_name.split(":")[0]
        for model in models:
            name = model.get("name", "")
            if name == model_name:
                return True
            if name.split(":")[0] == normalized_target:
                return True
        return False

    def _default_prompt(self) -> str:
        """出力形式に応じた既定プロンプトを生成する。"""
        language = (self.config.ollama_ocr.language or "").strip()
        language_hint = f" The document is mostly {language}." if language else ""

        if self.config.ollama_ocr.output_format == "markdown":
            return (
                "Extract all text from the image. Preserve layout with headings, lists, and tables in Markdown. "
                "Do not summarize or add commentary." + language_hint
            )
        return "Extract all text from the image as plain text." + language_hint

    def process_image(
        self,
        image_path: str,
        prompt: Optional[str] = None,
    ) -> str:
        """
        画像ファイルをOCR処理する

        Args:
            image_path: 画像ファイルのパス
            prompt: プロンプトテキスト（Noneの場合はデフォルト）

        Returns:
            OCR結果のテキスト

        Raises:
            FileNotFoundError: 画像ファイルが見つからない場合
            requests.RequestException: API呼び出しに失敗した場合
        """
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")

        if prompt is None:
            prompt = self._default_prompt()

        return self.wrapper.call_ollama_api(
            image_path=str(image_file),
            prompt=prompt,
            max_tokens=self.config.ollama_ocr.max_tokens,
            temperature=self.config.ollama_ocr.temperature,
        )

    def process_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        prompt: Optional[str] = None,
        progress_callback: Optional[callable] = None,
        keep_temp_images: bool = False,
    ) -> str:
        """
        PDFファイルをOCR処理する

        Args:
            pdf_path: PDFファイルのパス
            output_dir: 中間画像を保存するディレクトリ（Noneの場合は一時ディレクトリ）
            prompt: プロンプトテキスト（Noneの場合はデフォルト）
            progress_callback: 進捗コールバック関数（page, total_pages）を受け取る

        Returns:
            OCR結果のテキスト（全ページ結合）

        Raises:
            FileNotFoundError: PDFファイルが見つからない場合
            ValueError: PDFファイルが無効な場合
        """
        is_valid, error_msg = validate_pdf(pdf_path)
        if not is_valid:
            raise ValueError(error_msg or "PDFファイルが無効です")

        is_temp_dir = False
        if output_dir is None:
            import tempfile

            output_dir = tempfile.mkdtemp(prefix="pdftexter_ocr_")
            is_temp_dir = True
        else:
            os.makedirs(output_dir, exist_ok=True)

        try:
            image_paths = extract_pdf_pages_as_images(pdf_path, output_dir)
            total_pages = len(image_paths)

            results: List[str] = []
            failed_pages: List[int] = []

            for i, image_path in enumerate(image_paths, 1):
                if progress_callback:
                    progress_callback(i, total_pages)

                try:
                    page_result = self.process_image(image_path, prompt)
                    results.append(page_result)
                except Exception as exc:
                    error_msg = f"ページ {i} の処理に失敗しました: {exc}"
                    print(f"警告: {error_msg}", file=sys.stderr)
                    failed_pages.append(i)
                    results.append(f"<!-- {error_msg} -->\n")

            if len(failed_pages) == total_pages:
                raise RuntimeError("すべてのページのOCR処理に失敗しました。")

            if failed_pages:
                print(
                    f"警告: {len(failed_pages)}/{total_pages} ページの処理に失敗しました: {failed_pages}",
                    file=sys.stderr,
                )

            if self.config.ollama_ocr.output_format == "markdown":
                combined = "\n\n---\n\n".join(results)
            else:
                combined = "\n\n".join(results)

            return combined
        finally:
            if is_temp_dir and not keep_temp_images and os.path.exists(output_dir):
                try:
                    shutil.rmtree(output_dir)
                except Exception as exc:
                    print(f"警告: 一時ディレクトリの削除に失敗しました: {exc}", file=sys.stderr)

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
        """
        PDFファイルをOCR処理してファイルに保存する（逐次書き込み方式）

        Args:
            pdf_path: PDFファイルのパス
            output_file: 出力ファイルのパス
            output_dir: 中間画像を保存するディレクトリ（Noneの場合は一時ディレクトリ）
            prompt: プロンプトテキスト（Noneの場合はデフォルト）
            progress_callback: 進捗コールバック関数
            keep_temp_images: 一時画像を保持するか（デフォルト: False）
            resume: 中断した処理を再開するか（デフォルト: False）

        Returns:
            出力ファイルのパス
        """
        from pdftexter.pdf.processor import extract_pdf_pages_as_images, validate_pdf

        is_valid, error_msg = validate_pdf(pdf_path)
        if not is_valid:
            raise ValueError(error_msg or "PDFファイルが無効です")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        progress_file = output_path.with_suffix(output_path.suffix + ".progress")

        is_temp_dir = False
        if output_dir is None:
            import tempfile

            output_dir = tempfile.mkdtemp(prefix="pdftexter_ocr_")
            is_temp_dir = True
        else:
            os.makedirs(output_dir, exist_ok=True)

        start_page = 1
        if resume and progress_file.exists():
            try:
                with open(progress_file, "r", encoding="utf-8") as file:
                    last_line = file.read().strip().split("\n")[-1]
                    if last_line.startswith("page:"):
                        start_page = int(last_line.split(":")[1]) + 1
                        print(f"進捗を再開します: ページ {start_page} から", file=sys.stderr)
            except Exception as exc:
                print(f"警告: 進捗ファイルの読み込みに失敗しました: {exc}", file=sys.stderr)
                start_page = 1

        try:
            image_paths = extract_pdf_pages_as_images(pdf_path, output_dir)
            total_pages = len(image_paths)

            file_mode = "a" if resume and output_path.exists() else "w"
            with open(output_path, file_mode, encoding="utf-8") as file:
                if file_mode == "w":
                    if self.config.ollama_ocr.output_format == "markdown":
                        file.write("# OCR結果\n\n")
                    else:
                        file.write("OCR結果\n\n")

                failed_pages: List[int] = []
                page_separator = (
                    "\n\n---\n\n" if self.config.ollama_ocr.output_format == "markdown" else "\n\n"
                )

                for i, image_path in enumerate(image_paths, start_page - 1):
                    page_num = i + 1

                    if progress_callback:
                        progress_callback(page_num, total_pages)

                    try:
                        page_result = self.process_image(image_path, prompt)

                        if page_num > 1:
                            file.write(page_separator)
                        file.write(page_result)
                        file.flush()

                        with open(progress_file, "w", encoding="utf-8") as pf:
                            pf.write(f"page:{page_num}\n")
                            pf.write(f"total:{total_pages}\n")
                            pf.write(f"timestamp:{time.time()}\n")
                    except Exception as exc:
                        error_msg = f"ページ {page_num} の処理に失敗しました: {exc}"
                        print(f"警告: {error_msg}", file=sys.stderr)
                        failed_pages.append(page_num)

                        if page_num > 1:
                            file.write(page_separator)
                        file.write(f"<!-- {error_msg} -->\n")
                        file.flush()

                if self.config.ollama_ocr.output_format == "markdown":
                    file.write("\n\n---\n\n*OCR処理完了*\n")

            if len(failed_pages) == total_pages:
                raise RuntimeError("すべてのページのOCR処理に失敗しました。")

            if failed_pages:
                print(
                    f"警告: {len(failed_pages)}/{total_pages} ページの処理に失敗しました: {failed_pages}",
                    file=sys.stderr,
                )

            if progress_file.exists():
                try:
                    progress_file.unlink()
                except Exception as exc:
                    print(f"警告: 進捗ファイルの削除に失敗しました: {exc}", file=sys.stderr)

            return str(output_path)
        finally:
            if is_temp_dir and not keep_temp_images and os.path.exists(output_dir):
                try:
                    shutil.rmtree(output_dir)
                except Exception as exc:
                    print(f"警告: 一時ディレクトリの削除に失敗しました: {exc}", file=sys.stderr)
