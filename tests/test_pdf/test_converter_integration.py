"""
PDF変換の統合テスト（実際の処理を検証）
"""

import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from pdftexter.pdf.converter import PDFConverter


class TestPDFConverterIntegration:
    """PDFConverterの統合テスト（実際の画像とPDF生成を検証）"""
    
    def test_convert_real_images_to_pdf(self):
        """実際の画像ファイルからPDFを生成し、正しく作成されることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 実際の画像ファイルを作成
            image_dir = Path(tmpdir, "images")
            image_dir.mkdir()
            output_dir = Path(tmpdir, "output")
            output_dir.mkdir()
            
            # テスト用の画像を3枚作成
            for i in range(1, 4):
                img = Image.new('RGB', (800, 600), color=(i * 50, i * 50, i * 50))
                img_path = image_dir / f"{i:03d}.png"
                img.save(img_path)
            
            # PDF変換を実行
            result = converter.convert_images_to_pdf(
                str(image_dir),
                str(output_dir),
                "test_output",
                None, None, None
            )
            
            # 変換が成功したことを確認
            assert result is True
            
            # PDFファイルが実際に生成されていることを確認
            pdf_path = output_dir / "test_output.pdf"
            assert pdf_path.exists(), "PDFファイルが生成されていません"
            
            # PDFファイルのサイズが0より大きいことを確認
            assert pdf_path.stat().st_size > 0, "PDFファイルが空です"
    
    def test_convert_images_sorted_order(self):
        """画像がソートされた順序でPDFに変換されることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            image_dir = Path(tmpdir, "images")
            image_dir.mkdir()
            output_dir = Path(tmpdir, "output")
            output_dir.mkdir()
            
            # 順序を意図的にバラバラにして画像を作成
            order = [3, 1, 2]
            for i in order:
                img = Image.new('RGB', (400, 300), color=(i * 80, 0, 0))
                img_path = image_dir / f"{i:03d}.png"
                img.save(img_path)
            
            # PDF変換を実行
            result = converter.convert_images_to_pdf(
                str(image_dir),
                str(output_dir),
                "sorted_test",
                None, None, None
            )
            
            assert result is True
            
            # PDFが生成されていることを確認
            pdf_path = output_dir / "sorted_test.pdf"
            assert pdf_path.exists()
    
    def test_convert_different_image_sizes(self):
        """異なるサイズの画像が正しく処理されることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            image_dir = Path(tmpdir, "images")
            image_dir.mkdir()
            output_dir = Path(tmpdir, "output")
            output_dir.mkdir()
            
            # 異なるサイズの画像を作成
            sizes = [(800, 600), (1920, 1080), (400, 300)]
            for i, size in enumerate(sizes, 1):
                img = Image.new('RGB', size, color=(100, 100, 100))
                img_path = image_dir / f"{i:03d}.png"
                img.save(img_path)
            
            # PDF変換を実行
            result = converter.convert_images_to_pdf(
                str(image_dir),
                str(output_dir),
                "different_sizes",
                None, None, None
            )
            
            assert result is True
            
            pdf_path = output_dir / "different_sizes.pdf"
            assert pdf_path.exists()
            assert pdf_path.stat().st_size > 0
    
    def test_convert_jpg_images(self):
        """JPG形式の画像も正しく処理されることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            image_dir = Path(tmpdir, "images")
            image_dir.mkdir()
            output_dir = Path(tmpdir, "output")
            output_dir.mkdir()
            
            # JPG画像を作成
            img = Image.new('RGB', (800, 600), color=(255, 0, 0))
            img_path = image_dir / "test.jpg"
            img.save(img_path, "JPEG")
            
            # PDF変換を実行
            result = converter.convert_images_to_pdf(
                str(image_dir),
                str(output_dir),
                "jpg_test",
                None, None, None
            )
            
            assert result is True
            
            pdf_path = output_dir / "jpg_test.pdf"
            assert pdf_path.exists()
    
    def test_output_filename_without_extension(self):
        """拡張子なしのファイル名に.pdfが追加されることを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            image_dir = Path(tmpdir, "images")
            image_dir.mkdir()
            output_dir = Path(tmpdir, "output")
            output_dir.mkdir()
            
            # 画像を作成
            img = Image.new('RGB', (800, 600), color=(0, 255, 0))
            img_path = image_dir / "001.png"
            img.save(img_path)
            
            # 拡張子なしで指定
            result = converter.convert_images_to_pdf(
                str(image_dir),
                str(output_dir),
                "no_extension",
                None, None, None
            )
            
            assert result is True
            
            # .pdfが追加されていることを確認
            pdf_path = output_dir / "no_extension.pdf"
            assert pdf_path.exists()
            # 拡張子なしのファイルは存在しないことを確認
            assert not (output_dir / "no_extension").exists()
    
    def test_output_filename_with_extension(self):
        """既に.pdfが付いている場合、二重拡張子にならないことを確認"""
        converter = PDFConverter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            image_dir = Path(tmpdir, "images")
            image_dir.mkdir()
            output_dir = Path(tmpdir, "output")
            output_dir.mkdir()
            
            # 画像を作成
            img = Image.new('RGB', (800, 600), color=(0, 0, 255))
            img_path = image_dir / "001.png"
            img.save(img_path)
            
            # 既に.pdfが付いている
            result = converter.convert_images_to_pdf(
                str(image_dir),
                str(output_dir),
                "with_extension.pdf",
                None, None, None
            )
            
            assert result is True
            
            # 正しいファイル名で生成されていることを確認
            pdf_path = output_dir / "with_extension.pdf"
            assert pdf_path.exists()
            # 二重拡張子になっていないことを確認
            assert not (output_dir / "with_extension.pdf.pdf").exists()

