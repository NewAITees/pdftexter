"""
pytest設定ファイル
"""

import os
import sys
from unittest.mock import MagicMock

# X11ディスプレイがない環境でもテストが実行できるように
# pyautoguiをモック（インポート前に実行）
# 注意: DISPLAY環境変数は設定しない（テストファイル側でスキップ判定するため）
if "DISPLAY" not in os.environ or not os.environ.get("DISPLAY"):
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

