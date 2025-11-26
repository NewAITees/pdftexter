"""
画像処理ユーティリティのエッジケーステスト
"""

import numpy as np
import pytest

from pdftexter.utils.image import find_content_boundaries


class TestImageEdgeCases:
    """画像処理のエッジケーステスト"""
    
    def test_find_content_boundaries_small_image_raises_error(self):
        """高さが不足している画像の場合、例外が発生することを確認"""
        # 高さ20px未満の画像
        small_img = np.ones((15, 200, 3), dtype=np.uint8) * 255
        
        # 例外が発生することを確認
        with pytest.raises(ValueError, match="画像の高さが不足しています"):
            find_content_boundaries(small_img)
    
    def test_find_content_boundaries_minimum_height(self):
        """最小高さ（21px）の画像が処理できることを確認"""
        # 最小高さの画像
        min_height_img = np.ones((21, 200, 3), dtype=np.uint8) * 255
        
        # 例外が発生しないことを確認
        left, right = find_content_boundaries(min_height_img)
        assert left is not None
        assert right is not None
    
    def test_find_content_boundaries_very_wide_image(self):
        """非常に幅の広い画像が処理できることを確認"""
        wide_img = np.ones((100, 5000, 3), dtype=np.uint8) * 255
        
        left, right = find_content_boundaries(wide_img)
        assert left is not None
        assert right is not None
        assert left < right

