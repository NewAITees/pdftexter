"""
画像処理ユーティリティの統合テスト（実際の画像処理を検証）
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from pdftexter.utils.image import (
    convert_rgb_to_bgr,
    find_content_boundaries,
    save_image,
    trim_image,
)


class TestImageUtilsIntegration:
    """画像処理ユーティリティの統合テスト"""
    
    def test_find_content_boundaries_with_real_image(self):
        """実際の画像で境界検出が動作することを確認"""
        # 実際の画像を作成（左に余白、中央にコンテンツ、右に余白）
        img_array = np.ones((100, 200, 3), dtype=np.uint8) * 255  # 白背景
        
        # コンテンツ領域（x=50からx=150まで）を黒で塗りつぶす
        img_array[20:80, 50:150] = [0, 0, 0]
        
        # 境界を検出
        left, right = find_content_boundaries(img_array, left_margin=1, right_margin=1)
        
        # 境界が検出されることを確認
        assert left is not None
        assert right is not None
        assert left < right
        # 左端は50付近、右端は150付近になることを確認
        assert 40 <= left <= 60
        assert 140 <= right <= 160
    
    def test_trim_image_creates_correct_size(self):
        """トリミングが正しいサイズの画像を生成することを確認"""
        # テスト用画像を作成
        img_array = np.zeros((300, 500, 3), dtype=np.uint8)
        img_array[:, 100:400] = 255  # 中央部分を白に
        
        # トリミング
        trimmed = trim_image(img_array, 100, 400)
        
        # 形状が正しいことを確認
        assert trimmed.shape == (300, 300, 3)
        # トリミング後の画像が全て白であることを確認
        assert np.all(trimmed == 255)
    
    def test_save_image_creates_file(self):
        """画像が実際にファイルに保存されることを確認"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # テスト用画像を作成
            img_array = np.zeros((100, 100, 3), dtype=np.uint8)
            img_array[:50, :50] = 255  # 左上を白に
            
            # 画像を保存
            save_path = Path(tmpdir) / "test_image.png"
            result = save_image(img_array, str(save_path))
            
            # 保存が成功したことを確認
            assert result is True
            assert save_path.exists()
            assert save_path.stat().st_size > 0
            
            # 保存された画像を読み込んで検証
            loaded_img = Image.open(save_path)
            assert loaded_img.size == (100, 100)
    
    def test_convert_rgb_to_bgr_preserves_data(self):
        """RGBからBGRへの変換がデータを保持することを確認"""
        # RGB画像を作成
        rgb_img = np.zeros((100, 100, 3), dtype=np.uint8)
        rgb_img[:, :, 0] = 255  # 赤チャンネル
        
        # BGRに変換
        bgr_img = convert_rgb_to_bgr(rgb_img)
        
        # 形状が保持されることを確認
        assert bgr_img.shape == rgb_img.shape
        # データが変換されることを確認（RGBのRがBGRのBになる）
        assert np.all(bgr_img[:, :, 2] == 255)  # BGRのBチャンネル

