"""
画像処理ユーティリティのテスト
"""

import numpy as np
import pytest

from pdftexter.utils.image import find_content_boundaries, images_equal, trim_image


class TestFindContentBoundaries:
    """find_content_boundaries関数のテスト"""

    def test_find_content_boundaries_detects_left_and_right(self):
        """余白とコンテンツ色が異なる場合に左右位置が期待通りになることを確認"""
        # テスト用画像を作成: 左側に余白（白）、中央にコンテンツ（黒）、右側に余白（白）
        img = np.ones((100, 200, 3), dtype=np.uint8) * 255  # 白い背景

        # コンテンツ領域を黒で塗りつぶす（x=50からx=150まで）
        img[:, 50:150] = [0, 0, 0]  # 黒（全行に渡って）

        # 境界を検出
        left, right = find_content_boundaries(img, left_margin=1, right_margin=1)

        # 左端は50付近、右端は150付近になることを確認
        assert 45 <= left <= 55, f"Left boundary should be around 50, got {left}"
        assert 145 <= right <= 155, f"Right boundary should be around 150, got {right}"

    def test_find_content_boundaries_default_values(self):
        """境界が見つからない場合、デフォルト値が返されることを確認"""
        # 全て同じ色の画像（境界がない）
        img = np.ones((100, 200, 3), dtype=np.uint8) * 255

        left, right = find_content_boundaries(img, left_margin=5, right_margin=10)

        # デフォルト値が返される
        assert left == 5
        assert right == 200 - 10  # img.shape[1] - right_margin

    def test_find_content_boundaries_gray_margins(self):
        """グレー余白が正しくトリミングされることを確認"""
        # グレー(128)の余白、白(255)のコンテンツ
        img = np.ones((100, 300, 3), dtype=np.uint8) * 128  # グレー背景
        img[:, 50:250] = 255  # 中央に白いコンテンツ

        left, right = find_content_boundaries(img)

        assert 45 <= left <= 55, f"Left boundary should be around 50, got {left}"
        assert 245 <= right <= 255, f"Right boundary should be around 250, got {right}"

    def test_find_content_boundaries_dark_margins(self):
        """暗い余白でも正しくトリミングされることを確認"""
        # 黒(50)の余白、白(255)のコンテンツ
        img = np.ones((100, 300, 3), dtype=np.uint8) * 50
        img[:, 60:240] = 255

        left, right = find_content_boundaries(img)

        assert 55 <= left <= 65, f"Left boundary should be around 60, got {left}"
        assert 235 <= right <= 245, f"Right boundary should be around 240, got {right}"

    def test_find_content_boundaries_invalid_margins(self):
        """無効なマージン指定で例外になることを確認"""
        img = np.ones((100, 50, 3), dtype=np.uint8) * 255

        with pytest.raises(ValueError):
            find_content_boundaries(img, left_margin=30, right_margin=30)

        with pytest.raises(ValueError):
            find_content_boundaries(img, left_margin=-1, right_margin=1)


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
