"""
PDF変換GUIモジュールのテスト

注意: このテストはWindows環境での実行を想定しています。
WSL環境ではスキップされます。
"""

import os
import sys
import threading
from unittest.mock import MagicMock, Mock, patch

import pytest

# WSL環境またはX11ディスプレイがない環境ではスキップ
# os.uname()はWindowsでは利用できないため、platformモジュールを使用
import platform
is_wsl = (
    platform.system() == "Linux" and
    ("microsoft" in platform.release().lower() or "WSL" in os.environ.get("WSL_DISTRO_NAME", ""))
)
if is_wsl or "DISPLAY" not in os.environ or not os.environ.get("DISPLAY"):
    pytest.skip("GUI tests require Windows environment (not WSL)", allow_module_level=True)
else:
    import tkinter as tk
    from pdftexter.pdf.converter import PDFConverterGUI


class TestPDFConverterGUI:
    """PDFConverterGUIクラスのテスト"""
    
    @pytest.fixture
    def gui(self):
        """テスト用のGUIインスタンスを作成（モック使用）"""
        with patch("pdftexter.pdf.converter.tk.Tk") as mock_tk, \
             patch("pdftexter.pdf.converter.tk.StringVar") as mock_stringvar, \
             patch("pdftexter.pdf.converter.tk.DoubleVar") as mock_doublevar, \
             patch("pdftexter.pdf.converter.tk.Label"), \
             patch("pdftexter.pdf.converter.tk.Entry"), \
             patch("pdftexter.pdf.converter.tk.Button"):
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            mock_stringvar.return_value = MagicMock()
            mock_doublevar.return_value = MagicMock()

            gui = PDFConverterGUI()
            gui.setup_gui()
            gui.root = mock_root
            return gui
    
    def test_run_conversion_starts_thread(self, gui):
        """_run_conversionでスレッドが起動されることを確認（モンキーパッチで検証）"""
        # 変数を準備（モック使用）
        folder_var = Mock()
        folder_var.get = Mock(return_value="/test/folder")
        output_folder_var = Mock()
        output_folder_var.get = Mock(return_value="/test/output")
        output_filename_var = Mock()
        output_filename_var.get = Mock(return_value="test.pdf")
        progress_var = Mock()
        status_var = Mock()
        convert_button = Mock()
        
        # スレッドが起動されることを確認（モンキーパッチ）
        thread_started = threading.Event()
        thread_target_called = False
        original_thread = threading.Thread
        
        def thread_wrapper(*args, **kwargs):
            nonlocal thread_target_called
            thread_started.set()
            # スレッドのtargetが設定されていることを確認
            if 'target' in kwargs:
                thread_target_called = True
            return original_thread(*args, **kwargs)
        
        with patch("pdftexter.pdf.converter.threading.Thread", thread_wrapper):
            with patch.object(
                gui.converter, "convert_images_to_pdf", return_value=True
            ):
                gui._run_conversion(
                    folder_var,
                    output_folder_var,
                    output_filename_var,
                    progress_var,
                    status_var,
                    convert_button,
                )
                
                # スレッドが起動されたことを確認
                assert thread_started.wait(timeout=1.0), "Thread was not started"
                # conversion_threadがtargetとして設定されていることを確認
                assert thread_target_called, "conversion_thread was not set as target"
    
    def test_run_conversion_validates_inputs(self, gui):
        """入力値の検証が正しく行われることを確認"""
        folder_var = tk.StringVar(value="")
        output_folder_var = tk.StringVar(value="/test/output")
        output_filename_var = tk.StringVar(value="test.pdf")
        progress_var = tk.DoubleVar()
        status_var = tk.StringVar()
        convert_button = Mock(spec=tk.Button)
        
        with patch("pdftexter.pdf.converter.show_error") as mock_error:
            gui._run_conversion(
                folder_var,
                output_folder_var,
                output_filename_var,
                progress_var,
                status_var,
                convert_button,
            )
            
            # エラーメッセージが表示されることを確認
            assert mock_error.called
    
    def test_post_conversion_updates_ui(self, gui):
        """変換完了後のUI更新が正しく行われることを確認"""
        convert_button = Mock(spec=tk.Button)
        
        with patch("pdftexter.pdf.converter.show_info") as mock_info:
            gui._post_conversion(True, "/test/output", "test.pdf", convert_button)
            
            # 成功メッセージが表示されることを確認
            assert mock_info.called
            # ボタンの状態が更新されることを確認
            assert convert_button.config.called

