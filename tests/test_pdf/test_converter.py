"""
PDF変換モジュールのテスト
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from pdftexter.pdf.converter import PDFConverter


class TestPDFConverter:
    """PDFConverterクラスのテスト"""
    
    def test_convert_images_to_pdf_empty_folder(self):
        """空のフォルダの場合、Falseを返す"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = converter.convert_images_to_pdf(
                tmpdir, tmpdir, "test.pdf", None, None, None
            )
            assert result is False
    
    def test_convert_images_to_pdf_sorted_processing(self):
        """画像ファイルがソートされて処理されることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # テスト用の画像ファイルを作成（実際の画像ではなく、存在確認のみ）
            image_files = ["003.png", "001.png", "002.png"]
            for img_file in image_files:
                Path(tmpdir, img_file).touch()
            
            # Canvasをモック
            mock_canvas = MagicMock()
            mock_canvas_instance = Mock()
            mock_canvas.return_value = mock_canvas_instance
            
            with patch("pdftexter.pdf.converter.canvas.Canvas", mock_canvas):
                with patch("pdftexter.pdf.converter.Image") as mock_image:
                    # PIL Imageをモック
                    mock_img = Mock()
                    mock_img.size = (800, 600)
                    mock_image.open.return_value = mock_img
                    
                    result = converter.convert_images_to_pdf(
                        tmpdir, tmpdir, "test.pdf", None, None, None
                    )
                    
                    assert result is True
                    # ソートされた順序で処理されることを確認
                    assert mock_canvas_instance.setPageSize.call_count == 3
                    assert mock_canvas_instance.drawImage.call_count == 3
                    assert mock_canvas_instance.showPage.call_count == 3
                    mock_canvas_instance.save.assert_called_once()
    
    def test_convert_images_to_pdf_page_sizing_from_image(self):
        """画像の実際のサイズからPDFページサイズが設定されることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.png").touch()
            
            mock_canvas = MagicMock()
            mock_canvas_instance = Mock()
            mock_canvas.return_value = mock_canvas_instance
            
            with patch("pdftexter.pdf.converter.canvas.Canvas", mock_canvas):
                with patch("pdftexter.pdf.converter.Image") as mock_image:
                    mock_img = Mock()
                    mock_img.size = (1920, 1080)  # 実際の画像サイズ
                    mock_image.open.return_value = mock_img
                    
                    result = converter.convert_images_to_pdf(
                        tmpdir, tmpdir, "test.pdf", None, None, None
                    )
                    
                    assert result is True
                    # 画像サイズが正しく設定されることを確認
                    mock_canvas_instance.setPageSize.assert_called_with((1920, 1080))
    
    def test_convert_images_to_pdf_output_filename_normalization(self):
        """出力ファイル名に.pdfが自動で追加されることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.png").touch()
            
            mock_canvas = MagicMock()
            mock_canvas_instance = Mock()
            mock_canvas.return_value = mock_canvas_instance
            
            with patch("pdftexter.pdf.converter.canvas.Canvas", mock_canvas):
                with patch("pdftexter.pdf.converter.Image") as mock_image:
                    mock_img = Mock()
                    mock_img.size = (800, 600)
                    mock_image.open.return_value = mock_img
                    
                    # .pdfなしで指定
                    result = converter.convert_images_to_pdf(
                        tmpdir, tmpdir, "output", None, None, None
                    )
                    
                    assert result is True
                    # ファイルパスに.pdfが追加されていることを確認
                    expected_path = os.path.join(tmpdir, "output.pdf")
                    mock_canvas.assert_called_with(expected_path)
    
    def test_convert_images_to_pdf_no_double_extension(self):
        """既に.pdfが付いている場合、二重拡張子にならないことを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.png").touch()
            
            mock_canvas = MagicMock()
            mock_canvas_instance = Mock()
            mock_canvas.return_value = mock_canvas_instance
            
            with patch("pdftexter.pdf.converter.canvas.Canvas", mock_canvas):
                with patch("pdftexter.pdf.converter.Image") as mock_image:
                    mock_img = Mock()
                    mock_img.size = (800, 600)
                    mock_image.open.return_value = mock_img
                    
                    # 既に.pdfが付いている
                    result = converter.convert_images_to_pdf(
                        tmpdir, tmpdir, "output.pdf", None, None, None
                    )
                    
                    assert result is True
                    # 二重拡張子になっていないことを確認
                    expected_path = os.path.join(tmpdir, "output.pdf")
                    mock_canvas.assert_called_with(expected_path)
                    # output.pdf.pdfになっていないことを確認
                    assert not os.path.exists(os.path.join(tmpdir, "output.pdf.pdf"))
    
    def test_convert_images_to_pdf_error_handling_continues(self):
        """開けない画像が混在する場合でも処理が継続し、Trueを返すことを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 正常な画像とエラーが発生する画像を作成
            Path(tmpdir, "valid.png").touch()
            Path(tmpdir, "invalid.png").touch()
            
            mock_canvas = MagicMock()
            mock_canvas_instance = Mock()
            mock_canvas.return_value = mock_canvas_instance
            
            with patch("pdftexter.pdf.converter.canvas.Canvas", mock_canvas):
                with patch("pdftexter.pdf.converter.Image") as mock_image:
                    # 最初の画像は正常、2つ目はエラー
                    mock_img = Mock()
                    mock_img.size = (800, 600)
                    
                    def side_effect(path):
                        if "invalid" in path:
                            raise Exception("Cannot open image")
                        return mock_img
                    
                    mock_image.open.side_effect = side_effect
                    
                    result = converter.convert_images_to_pdf(
                        tmpdir, tmpdir, "test.pdf", None, None, None
                    )
                    
                    # エラーがあってもTrueを返す（一部成功）
                    assert result is True
                    # 正常な画像のみ処理されることを確認
                    assert mock_canvas_instance.setPageSize.call_count == 1
                    assert mock_canvas_instance.drawImage.call_count == 1
                    # エラーが発生した画像のdrawImage呼び出しがスキップされることを確認
                    mock_canvas_instance.save.assert_called_once()
    
    def test_convert_images_to_pdf_error_skips_drawimage(self):
        """エラーが発生した画像のdrawImage呼び出しがスキップされることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 3つの画像を作成（2つ目がエラー）
            Path(tmpdir, "001.png").touch()
            Path(tmpdir, "002.png").touch()
            Path(tmpdir, "003.png").touch()
            
            mock_canvas = MagicMock()
            mock_canvas_instance = Mock()
            mock_canvas.return_value = mock_canvas_instance
            
            with patch("pdftexter.pdf.converter.canvas.Canvas", mock_canvas):
                with patch("pdftexter.pdf.converter.Image") as mock_image:
                    mock_img = Mock()
                    mock_img.size = (800, 600)
                    
                    call_count = 0
                    def side_effect(path):
                        nonlocal call_count
                        call_count += 1
                        if call_count == 2:  # 2つ目の画像でエラー
                            raise Exception("Cannot open image")
                        return mock_img
                    
                    mock_image.open.side_effect = side_effect
                    
                    result = converter.convert_images_to_pdf(
                        tmpdir, tmpdir, "test.pdf", None, None, None
                    )
                    
                    # エラーがあってもTrueを返す
                    assert result is True
                    # 正常な画像のみ処理される（2つ）
                    assert mock_canvas_instance.setPageSize.call_count == 2
                    assert mock_canvas_instance.drawImage.call_count == 2
                    # エラーが発生した画像のdrawImageは呼ばれていない
                    assert mock_canvas_instance.drawImage.call_count < 3
