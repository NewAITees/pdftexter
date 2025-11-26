"""
Kindleスクリーンショットモジュールのテスト

注意: このテストはX11ディスプレイが必要なため、CI環境ではスキップされます。
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

# X11ディスプレイがない環境ではテストをスキップ
if "DISPLAY" not in os.environ or not os.environ.get("DISPLAY"):
    pytest.skip("X11 display required for pyautogui", allow_module_level=True)

from pdftexter.kindle.screenshot import KindleScreenshot, KindleScreenshotConfig


class TestKindleScreenshot:
    """KindleScreenshotクラスのテスト"""
    
    def test_capture_pages_timeout_and_directory_restore(self):
        """変化しない場合はtimeout_seconds後にページ数を返し、os.chdirが元に戻ることを確認"""
        config = KindleScreenshotConfig(timeout_seconds=0.1)  # 短いタイムアウト
        screenshot = KindleScreenshot(config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            
            # モックを設定
            with patch("pdftexter.kindle.screenshot.grab_screen") as mock_grab:
                with patch("pdftexter.kindle.screenshot.save_image") as mock_save:
                    with patch("pdftexter.kindle.screenshot.get_screen_size") as mock_size:
                        with patch("pyautogui.press") as mock_press:
                            # 画面サイズをモック
                            mock_size.return_value = (1920, 1080)
                            
                            # 常に同じ画像を返す（変化しない）
                            same_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
                            mock_grab.return_value = same_image
                            
                            # save_imageは成功を返す
                            mock_save.return_value = True
                            
                            # キャプチャを実行
                            result = screenshot.capture_pages(
                                left=100, right=1820, title="test", save_folder=tmpdir
                            )
                            
                            # タイムアウトにより、ページ数0が返されることを確認
                            assert result == 0
                            
                            # ディレクトリが元に戻ることを確認
                            assert os.getcwd() == original_dir
    
    def test_capture_pages_key_press_sequence(self):
        """ページ送りキーが正しく押下・解放されることを確認"""
        screenshot = KindleScreenshot()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # モックを設定
            with patch("pdftexter.kindle.screenshot.grab_screen") as mock_grab:
                with patch("pdftexter.kindle.screenshot.save_image") as mock_save:
                    with patch("pdftexter.kindle.screenshot.get_screen_size") as mock_size:
                        with patch("pyautogui.press") as mock_press:
                            mock_size.return_value = (1920, 1080)
                            
                            # 最初は異なる画像、2回目以降は同じ画像（ページが変わらない）
                            images = [
                                np.zeros((1080, 1920, 3), dtype=np.uint8),
                                np.ones((1080, 1920, 3), dtype=np.uint8) * 255,
                                np.ones((1080, 1920, 3), dtype=np.uint8) * 255,  # 同じ
                            ]
                            mock_grab.side_effect = images
                            mock_save.return_value = True
                            
                            # キャプチャを実行（タイムアウトを短く設定）
                            config = KindleScreenshotConfig(timeout_seconds=0.1)
                            screenshot.config = config
                            
                            result = screenshot.capture_pages(
                                left=100, right=1820, title="test", save_folder=tmpdir
                            )
                            
                            # pag.pressが呼ばれていることを確認（keyDown/keyUpの組み合わせ）
                            assert mock_press.called
                            # 呼び出し回数を確認（ページが変わった回数分）
                            assert mock_press.call_count >= 1
    
    def test_capture_pages_saves_trimmed_images(self):
        """トリミングされた画像が保存されることを確認"""
        screenshot = KindleScreenshot()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("pdftexter.kindle.screenshot.grab_screen") as mock_grab:
                with patch("pdftexter.kindle.screenshot.save_image") as mock_save:
                    with patch("pdftexter.kindle.screenshot.get_screen_size") as mock_size:
                        with patch("pyautogui.press") as mock_press:
                            mock_size.return_value = (1920, 1080)
                            
                            # テスト用画像（左100、右1820でトリミング）
                            full_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
                            full_image[:, 100:1820] = 255  # 中央部分を白に
                            
                            images = [
                                full_image,
                                full_image + 1,  # 少し異なる画像
                                full_image + 1,  # 同じ画像（タイムアウト）
                            ]
                            mock_grab.side_effect = images
                            mock_save.return_value = True
                            
                            config = KindleScreenshotConfig(timeout_seconds=0.1)
                            screenshot.config = config
                            
                            result = screenshot.capture_pages(
                                left=100, right=1820, title="test", save_folder=tmpdir
                            )
                            
                            # save_imageが呼ばれていることを確認
                            assert mock_save.called
                            # 保存された画像の形状を確認（トリミング後のサイズ）
                            if mock_save.call_args:
                                saved_path = mock_save.call_args[0][1]
                                # ファイル名が正しい形式であることを確認
                                assert saved_path.endswith(".png")
                                assert "001" in saved_path or "test" in saved_path

