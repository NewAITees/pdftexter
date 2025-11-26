"""
画像処理ユーティリティのテスト
"""

import numpy as np
import pytest

from pdftexter.utils.image import (
    find_content_boundaries,
    images_equal,
    trim_image,
)


class TestFindContentBoundaries:
    """find_content_boundaries関数のテスト"""
    
    def test_find_content_boundaries_detects_left_and_right(self):
        """余白とコンテンツ色が異なる場合に左右位置が期待通りになることを確認"""
        # テスト用画像を作成: 左側に余白（白）、中央にコンテンツ（黒）、右側に余白（白）
        img = np.ones((100, 200, 3), dtype=np.uint8) * 255  # 白い背景
        
        # コンテンツ領域を黒で塗りつぶす（x=50からx=150まで）
        img[20:80, 50:150] = [0, 0, 0]  # 黒
        
        # 境界を検出
        left, right = find_content_boundaries(img, left_margin=1, right_margin=1)
        
        # 左端は50付近、右端は150付近になることを確認
        # 実際の検出は20行目で行われるため、若干の誤差は許容
        assert 40 <= left <= 60, f"Left boundary should be around 50, got {left}"
        assert 140 <= right <= 160, f"Right boundary should be around 150, got {right}"
    
    def test_find_content_boundaries_default_values(self):
        """境界が見つからない場合、デフォルト値が返されることを確認"""
        # 全て同じ色の画像（境界がない）
        img = np.ones((100, 200, 3), dtype=np.uint8) * 255
        
        left, right = find_content_boundaries(img, left_margin=5, right_margin=10)
        
        # デフォルト値が返される
        assert left == 5
        assert right == 200 - 10  # img.shape[1] - right_margin


class TestTrimImage:
    """trim_image関数のテスト"""
    
    def test_trim_image_correct_slicing(self):
        """画像が正しくトリミングされることを確認"""
        # テスト用画像を作成
        img = np.zeros((100, 200, 3), dtype=np.uint8)
        img[:, 50:150] = 255  # 中央部分を白に
        
        # 左50、右150でトリミング
        trimmed = trim_image(img, 50, 150)
        
        # 形状が正しいことを確認
        assert trimmed.shape == (100, 100, 3)
        # トリミング後の画像は全て白であることを確認
        assert np.all(trimmed == 255)
    
    def test_trim_image_preserves_height(self):
        """トリミング後も高さが保持されることを確認"""
        img = np.zeros((300, 500, 3), dtype=np.uint8)
        
        trimmed = trim_image(img, 100, 400)
        
        assert trimmed.shape[0] == 300  # 高さは変わらない
        assert trimmed.shape[1] == 300  # 幅は100から400まで = 300


class TestImagesEqual:
    """images_equal関数のテスト"""
    
    def test_images_equal_same_images(self):
        """同じ画像の場合、Trueを返すことを確認"""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        
        assert images_equal(img1, img2) is True
    
    def test_images_equal_different_images(self):
        """異なる画像の場合、Falseを返すことを確認"""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        assert images_equal(img1, img2) is False
    
    def test_images_equal_different_shapes(self):
        """形状が異なる場合、Falseを返すことを確認"""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 200, 3), dtype=np.uint8)
        
        assert images_equal(img1, img2) is False

