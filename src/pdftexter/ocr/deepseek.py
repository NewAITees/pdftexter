"""
DeepSeek-OCR統合モジュール
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from pdftexter.ocr.config import OCRConfig, load_config
from pdftexter.ocr.vllm_wrapper import VLLMWrapper
from pdftexter.pdf.processor import extract_pdf_pages_as_images, validate_pdf


class DeepSeekOCR:
    """DeepSeek-OCR統合クラス"""
    
    def __init__(self, config: Optional[OCRConfig] = None, verify_setup: bool = True):
        """
        初期化
        
        Args:
            config: OCR設定オブジェクト（Noneの場合はデフォルト設定を使用）
            verify_setup: セットアップを検証するか（デフォルト: True）
            
        Raises:
            RuntimeError: セットアップが完了していない場合
        """
        self.config = config or load_config()
        
        # セットアップの検証
        if verify_setup:
            from pdftexter.ocr.model_checker import verify_ocr_setup
            is_ready, message = verify_ocr_setup()
            if not is_ready:
                raise RuntimeError(f"OCRセットアップが完了していません: {message}")
        
        # モデル名を設定から取得
        model_name = self.config.deepseek_ocr.model_name
        
        self.vllm_wrapper = VLLMWrapper(
            server_url=self.config.deepseek_ocr.vllm_server_url,
            model_name=model_name,
            timeout=self.config.deepseek_ocr.timeout,
            max_retries=self.config.deepseek_ocr.max_retries,
            retry_delay=self.config.deepseek_ocr.retry_delay,
        )
    
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
            OCR結果のテキスト（Markdown形式）
            
        Raises:
            FileNotFoundError: 画像ファイルが見つからない場合
            requests.RequestException: API呼び出しに失敗した場合
        """
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
        
        # デフォルトプロンプト
        if prompt is None:
            if self.config.deepseek_ocr.output_format == "markdown":
                prompt = "<image>\n<|grounding|>Convert the document to markdown."
            else:
                prompt = "<image>\nFree OCR."
        
        # vLLM APIを呼び出し
        result = self.vllm_wrapper.call_vllm_api(
            image_path=str(image_file),
            prompt=prompt,
            max_tokens=self.config.deepseek_ocr.max_tokens,
            temperature=self.config.deepseek_ocr.temperature,
        )
        
        return result
    
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
            OCR結果のテキスト（全ページ結合、Markdown形式）
            
        Raises:
            FileNotFoundError: PDFファイルが見つからない場合
            ValueError: PDFファイルが無効な場合
        """
        # PDFの検証
        is_valid, error_msg = validate_pdf(pdf_path)
        if not is_valid:
            raise ValueError(error_msg or "PDFファイルが無効です")
        
        # 出力ディレクトリの設定
        is_temp_dir = False
        if output_dir is None:
            import tempfile
            output_dir = tempfile.mkdtemp(prefix="pdftexter_ocr_")
            is_temp_dir = True
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # PDFを画像に変換
            image_paths = extract_pdf_pages_as_images(pdf_path, output_dir)
            total_pages = len(image_paths)
            
            # 各ページをOCR処理（一枚ずつ順次処理）
            # 注意: 現在の実装では、vLLM APIに一枚ずつ画像を送信します
            # バッチ処理が必要な場合は、vLLM APIの仕様に応じて実装を変更してください
            results: List[str] = []
            failed_pages: List[int] = []
            
            for i, image_path in enumerate(image_paths, 1):
                if progress_callback:
                    progress_callback(i, total_pages)
                
                try:
                    # 一枚ずつ画像をOCR処理
                    page_result = self.process_image(image_path, prompt)
                    results.append(page_result)
                except Exception as e:
                    # エラーが発生したページを記録
                    error_msg = f"ページ {i} の処理に失敗しました: {e}"
                    print(f"警告: {error_msg}", file=sys.stderr)
                    failed_pages.append(i)
                    results.append(f"<!-- {error_msg} -->\n")
            
            # 全ページが失敗した場合は例外を発生
            if len(failed_pages) == total_pages:
                raise RuntimeError(
                    f"すべてのページのOCR処理に失敗しました。"
                    f"vLLMサーバーが起動しているか、設定が正しいか確認してください。"
                )
            
            # 一部のページが失敗した場合は警告を表示
            if failed_pages:
                print(
                    f"警告: {len(failed_pages)}/{total_pages} ページの処理に失敗しました: {failed_pages}",
                    file=sys.stderr
                )
            
            # 結果を結合
            if self.config.deepseek_ocr.output_format == "markdown":
                # Markdown形式で結合（ページ区切りを追加）
                combined = "\n\n---\n\n".join(results)
            else:
                # プレーンテキスト形式で結合
                combined = "\n\n".join(results)
            
            return combined
        finally:
            # 一時ディレクトリのクリーンアップ（keep_temp_imagesがFalseの場合のみ）
            if is_temp_dir and not keep_temp_images and os.path.exists(output_dir):
                try:
                    shutil.rmtree(output_dir)
                except Exception as e:
                    print(f"警告: 一時ディレクトリの削除に失敗しました: {e}", file=sys.stderr)
    
    def process_pdf_to_file(
        self,
        pdf_path: str,
        output_file: str,
        output_dir: Optional[str] = None,
        prompt: Optional[str] = None,
        progress_callback: Optional[callable] = None,
    ) -> str:
        """
        PDFファイルをOCR処理してファイルに保存する
        
        Args:
            pdf_path: PDFファイルのパス
            output_file: 出力ファイルのパス
            output_dir: 中間画像を保存するディレクトリ（Noneの場合は一時ディレクトリ）
            prompt: プロンプトテキスト（Noneの場合はデフォルト）
            progress_callback: 進捗コールバック関数
            
        Returns:
            出力ファイルのパス
        """
        # OCR処理を実行
        result_text = self.process_pdf(pdf_path, output_dir, prompt, progress_callback)
        
        # ファイルに保存
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result_text)
        
        return str(output_path)

