"""
Kindleスクリーンショットモジュールのユニットテスト

注意: このテストはWindows環境での実行を想定しています。
WSL環境ではスキップされます。
"""

import os

# WSL環境ではテストをスキップ
# os.uname()はWindowsでは利用できないため、platformモジュールを使用
import platform
import tempfile
from unittest.mock import patch

import numpy as np
import pytest

is_wsl = platform.system() == "Linux" and (
    "microsoft" in platform.release().lower() or "WSL" in os.environ.get("WSL_DISTRO_NAME", "")
)
if is_wsl:
    pytest.skip("Kindle tests require Windows environment (not WSL)", allow_module_level=True)

from pdftexter.kindle.screenshot import KindleScreenshot, KindleScreenshotConfig


class TestKindleScreenshotUnit:
    """KindleScreenshotクラスのユニットテスト（X11不要）"""

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
                        with patch("pyautogui.press"):
                            # 画面サイズをモック
                            mock_size.return_value = (1920, 1080)

                            # 常に同じ画像を返す（変化しない）
                            same_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
                            mock_grab.return_value = same_image

                            # save_imageは成功を返す
                            mock_save.return_value = True

                            # キャプチャを実行
                            page_count = screenshot.capture_pages(
                                left=100, right=1820, title="test", save_folder=tmpdir
                            )

                            # 1枚目は保存されるため、ページ数1が返ることを確認
                            assert page_count == 1

                            # ディレクトリが元に戻ることを確認
                            assert os.getcwd() == original_dir

    def test_capture_pages_key_press_sequence(self):
        """ページ送りキーが正しく押下・解放されることを確認（pag.press使用）"""
        screenshot = KindleScreenshot()

        with tempfile.TemporaryDirectory() as tmpdir:
            # モックを設定
            with patch("pdftexter.kindle.screenshot.grab_screen") as mock_grab:
                with patch("pdftexter.kindle.screenshot.save_image") as mock_save:
                    with patch("pdftexter.kindle.screenshot.get_screen_size") as mock_size:
                        with patch("pyautogui.press") as mock_press:
                            mock_size.return_value = (1920, 1080)

                            # 最初は異なる画像、以降は同じ画像（ページが変わらない）
                            first = np.zeros((1080, 1920, 3), dtype=np.uint8)
                            second = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
                            mock_grab.side_effect = [first, second] + [second] * 10
                            mock_save.return_value = True

                            # キャプチャを実行（タイムアウトを短く設定）
                            config = KindleScreenshotConfig(timeout_seconds=0.1)
                            screenshot.config = config

                            screenshot.capture_pages(
                                left=100, right=1820, title="test", save_folder=tmpdir
                            )

                            # pag.pressが呼ばれていることを確認
                            assert mock_press.called
                            # 呼び出し回数を確認（ページ送り + タイムアウト再試行）
                            assert mock_press.call_count >= 1
                            # pag.pressが正しいキーで呼ばれていることを確認
                            mock_press.assert_called_with("right")  # デフォルトのpage_change_key

    def test_capture_pages_saves_trimmed_images(self):
        """トリミングされた画像が保存されることを確認"""
        screenshot = KindleScreenshot()

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("pdftexter.kindle.screenshot.grab_screen") as mock_grab:
                with patch("pdftexter.kindle.screenshot.save_image") as mock_save:
                    with patch("pdftexter.kindle.screenshot.get_screen_size") as mock_size:
                        with patch("pyautogui.press"):
                            mock_size.return_value = (1920, 1080)

                            # テスト用画像（左100、右1820でトリミング）
                            full_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
                            full_image[:, 100:1820] = 255  # 中央部分を白に

                            images = [
                                full_image,
                                full_image + 1,  # 少し異なる画像
                            ] + [
                                full_image + 1
                            ] * 10  # 同じ画像（タイムアウト）
                            mock_grab.side_effect = images
                            mock_save.return_value = True

                            config = KindleScreenshotConfig(timeout_seconds=0.1)
                            screenshot.config = config

                            screenshot.capture_pages(
                                left=100, right=1820, title="test", save_folder=tmpdir
                            )

                            # save_imageが呼ばれていることを確認
                            assert mock_save.called
                            # 保存された画像の形状を確認（トリミング後のサイズ）
                            if mock_save.call_args_list:
                                saved_image = mock_save.call_args_list[0][0][0]
                                saved_path = mock_save.call_args_list[0][0][1]
                                # トリミング後のサイズであることを確認
                                assert saved_image.shape[1] == 1720  # right - left = 1820 - 100
                                # ファイル名が正しい形式であることを確認
                                assert saved_path.endswith(".png")
                                assert "001" in saved_path or "test" in saved_path

    def test_run_with_params_uses_window_selection(self):
        """run_with_paramsがウィンドウ選択ダイアログを使用することを確認"""
        screenshot = KindleScreenshot()

        with patch("pdftexter.kindle.screenshot._load_page_key") as mock_load_key:
            with patch("pdftexter.kindle.screenshot.select_window_handle") as mock_select:
                with patch("pdftexter.kindle.screenshot.setup_kindle_window") as mock_setup:
                    with patch("pdftexter.kindle.screenshot.get_window_client_rect") as mock_rect:
                        with patch("pdftexter.kindle.screenshot.grab_screen") as mock_grab:
                            with patch(
                                "pdftexter.kindle.screenshot.find_content_boundaries"
                            ) as mock_boundaries:
                                with patch(
                                    "pdftexter.kindle.screenshot.get_screen_size"
                                ) as mock_size:
                                    with patch("pyautogui.moveTo"):
                                        with patch("time.sleep"):
                                            with patch("pdftexter.kindle.screenshot.show_info"):
                                                with patch.object(
                                                    KindleScreenshot,
                                                    "capture_pages",
                                                    return_value=1,
                                                ) as mock_capture:
                                                    mock_load_key.return_value = "right"
                                                    mock_select.return_value = 123
                                                    mock_rect.return_value = (0, 0, 100, 100)
                                                    mock_grab.return_value = np.zeros(
                                                        (100, 100, 3), dtype=np.uint8
                                                    )
                                                    mock_boundaries.return_value = (0, 100)
                                                    mock_size.return_value = (1920, 1080)

                                                    result = screenshot.run_with_params("test")

                                                    assert result == 1
                                                    assert mock_select.called
                                                    assert mock_setup.called
                                                    assert mock_capture.called
