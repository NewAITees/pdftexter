"""
DeepSeek-OCR統合モジュールのテスト
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from pdftexter.ocr.config import DeepSeekOCRConfig, OCRConfig, OutputConfig
from pdftexter.ocr.deepseek import DeepSeekOCR


class TestDeepSeekOCR:
    """DeepSeekOCRクラスのテスト"""
    
    def test_process_pdf_all_pages_fail_raises_error(self):
        """全ページのOCR処理が失敗した場合、例外が発生することを確認"""
        # 設定を作成
        config = OCRConfig(
            deepseek_ocr=DeepSeekOCRConfig(
                model_path="/test/path",
                model_name="test-model",
                vllm_server_url="http://localhost:8000",
            ),
            output=OutputConfig(),
        )
        
        ocr = DeepSeekOCR(config, verify_setup=False)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # テスト用PDFを作成（実際には画像に変換される）
            pdf_path = Path(tmpdir, "test.pdf")
            pdf_path.touch()
            
            # extract_pdf_pages_as_imagesをモック（2ページ分の画像を返す）
            with patch("pdftexter.ocr.deepseek.extract_pdf_pages_as_images") as mock_extract:
                with patch("pdftexter.ocr.deepseek.validate_pdf") as mock_validate:
                    mock_validate.return_value = (True, None)
                    mock_extract.return_value = [
                        str(Path(tmpdir, "page_0001.png")),
                        str(Path(tmpdir, "page_0002.png")),
                    ]
                    
                    # process_imageをモック（常にエラーを発生）
                    with patch.object(ocr, "process_image") as mock_process:
                        mock_process.side_effect = Exception("OCR failed")
                        
                        # 全ページが失敗した場合、例外が発生することを確認
                        with pytest.raises(RuntimeError, match="すべてのページのOCR処理に失敗しました"):
                            ocr.process_pdf(str(pdf_path), output_dir=tmpdir)
    
    def test_process_pdf_some_pages_fail_continues(self):
        """一部のページが失敗した場合、処理が継続されることを確認"""
        config = OCRConfig(
            deepseek_ocr=DeepSeekOCRConfig(
                model_path="/test/path",
                model_name="test-model",
                vllm_server_url="http://localhost:8000",
            ),
            output=OutputConfig(),
        )
        
        ocr = DeepSeekOCR(config, verify_setup=False)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir, "test.pdf")
            pdf_path.touch()
            
            with patch("pdftexter.ocr.deepseek.extract_pdf_pages_as_images") as mock_extract:
                with patch("pdftexter.ocr.deepseek.validate_pdf") as mock_validate:
                    mock_validate.return_value = (True, None)
                    mock_extract.return_value = [
                        str(Path(tmpdir, "page_0001.png")),
                        str(Path(tmpdir, "page_0002.png")),
                    ]
                    
                    with patch.object(ocr, "process_image") as mock_process:
                        # 1ページ目は成功、2ページ目は失敗
                        mock_process.side_effect = ["Page 1 result", Exception("OCR failed")]
                        
                        # 処理が継続されることを確認
                        result = ocr.process_pdf(str(pdf_path), output_dir=tmpdir)
                        
                        # 結果が返される（警告付きで継続）
                        assert result is not None
                        assert "Page 1 result" in result
    
    def test_process_pdf_cleans_up_temp_directory(self):
        """一時ディレクトリがクリーンアップされることを確認"""
        config = OCRConfig(
            deepseek_ocr=DeepSeekOCRConfig(
                model_path="/test/path",
                model_name="test-model",
                vllm_server_url="http://localhost:8000",
            ),
            output=OutputConfig(),
        )
        
        ocr = DeepSeekOCR(config, verify_setup=False)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir, "test.pdf")
            pdf_path.touch()
            
            temp_dirs = []
            
            def mock_extract(pdf, out_dir):
                temp_dirs.append(out_dir)
                return [str(Path(out_dir, "page_0001.png"))]
            
            with patch("pdftexter.ocr.deepseek.extract_pdf_pages_as_images", side_effect=mock_extract):
                with patch("pdftexter.ocr.deepseek.validate_pdf", return_value=(True, None)):
                    with patch.object(ocr, "process_image", return_value="Result"):
                        # output_dir=Noneで実行（一時ディレクトリが作成される）
                        result = ocr.process_pdf(str(pdf_path), output_dir=None)
                        
                        # 結果が返される
                        assert result is not None
                        
                        # 一時ディレクトリが削除されていることを確認
                        if temp_dirs:
                            temp_dir = temp_dirs[0]
                            assert not os.path.exists(temp_dir), "一時ディレクトリが削除されていません"
    
    def test_process_pdf_preserves_user_specified_directory(self):
        """ユーザー指定のディレクトリは削除されないことを確認"""
        config = OCRConfig(
            deepseek_ocr=DeepSeekOCRConfig(
                model_path="/test/path",
                model_name="test-model",
                vllm_server_url="http://localhost:8000",
            ),
            output=OutputConfig(),
        )
        
        ocr = DeepSeekOCR(config, verify_setup=False)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir, "test.pdf")
            pdf_path.touch()
            user_output_dir = Path(tmpdir, "user_output")
            user_output_dir.mkdir()
            
            with patch("pdftexter.ocr.deepseek.extract_pdf_pages_as_images") as mock_extract:
                with patch("pdftexter.ocr.deepseek.validate_pdf", return_value=(True, None)):
                    mock_extract.return_value = [str(user_output_dir / "page_0001.png")]
                    
                    with patch.object(ocr, "process_image", return_value="Result"):
                        result = ocr.process_pdf(str(pdf_path), output_dir=str(user_output_dir))
                        
                        # 結果が返される
                        assert result is not None
                        
                        # ユーザー指定のディレクトリは残っている
                        assert user_output_dir.exists(), "ユーザー指定のディレクトリが削除されています"

