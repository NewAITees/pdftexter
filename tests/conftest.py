"""
pytest設定ファイル
"""

import os
import sys
from unittest.mock import MagicMock

# X11ディスプレイがない環境でもテストが実行できるように
# pyautoguiをモック（インポート前に実行）
# 環境変数を設定してX11エラーを回避
if "DISPLAY" not in os.environ or not os.environ.get("DISPLAY"):
    os.environ["DISPLAY"] = ":99"  # ダミーディスプレイ
    
    # pyautoguiをモック
    mock_pag = MagicMock()
    mock_pag.size = MagicMock(return_value=(1920, 1080))
    mock_pag.press = MagicMock()
    mock_pag.moveTo = MagicMock()
    mock_pag.click = MagicMock()
    mock_pag.keyDown = MagicMock()
    mock_pag.keyUp = MagicMock()
    
    # モジュールをモック（インポート前に設定）
    if "pyautogui" not in sys.modules:
        sys.modules["pyautogui"] = mock_pag
    if "mouseinfo" not in sys.modules:
        sys.modules["mouseinfo"] = MagicMock()

