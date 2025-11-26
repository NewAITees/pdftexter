"""
Kindleウィンドウ操作モジュール
"""

import time
from ctypes import POINTER, WINFUNCTYPE, c_bool, c_int, create_unicode_buffer, pointer, windll
from ctypes.wintypes import RECT
from typing import Optional

import pyautogui as pag


def find_kindle_window(window_title: str = "Kindle for PC") -> Optional[int]:
    """
    Kindleウィンドウを検索してハンドルを返す
    
    Windows APIを使用して、指定されたタイトルのウィンドウを検索します。
    
    Args:
        window_title: 検索するウィンドウタイトル（デフォルト: "Kindle for PC"）
        
    Returns:
        ウィンドウハンドル、見つからない場合はNone
    """
    EnumWindows = windll.user32.EnumWindows
    GetWindowText = windll.user32.GetWindowTextW
    GetWindowTextLength = windll.user32.GetWindowTextLengthW
    WNDENUMPROC = WINFUNCTYPE(c_bool, POINTER(c_int), POINTER(c_int))
    
    found_hwnd: Optional[int] = None
    
    def enum_windows_proc(hwnd: int, l_param: int) -> bool:
        """
        ウィンドウ列挙のためのコールバック関数
        
        Args:
            hwnd: ウィンドウハンドル
            l_param: パラメータ（未使用）
            
        Returns:
            列挙を続ける場合True、停止する場合False
        """
        nonlocal found_hwnd
        length = GetWindowTextLength(hwnd)
        if length == 0:
            return True
        
        buffer = create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buffer, length + 1)
        
        if window_title in buffer.value:
            found_hwnd = hwnd
            return False  # 見つかったので列挙を停止
        
        return True  # 列挙を続ける
    
    EnumWindows(WNDENUMPROC(enum_windows_proc), 0)
    return found_hwnd


def setup_kindle_window(hwnd: int) -> None:
    """
    Kindleウィンドウを前面に表示しフォーカスを設定
    
    Args:
        hwnd: ウィンドウハンドル
    """
    SetForegroundWindow = windll.user32.SetForegroundWindow
    GetWindowRect = windll.user32.GetWindowRect
    
    # ウィンドウを前面に表示
    SetForegroundWindow(hwnd)
    
    # ウィンドウの位置とサイズを取得
    rect = RECT()
    GetWindowRect(hwnd, pointer(rect))
    
    # クリックしてフォーカスを設定（ウィンドウの左上付近をクリック）
    pag.moveTo(rect.left + 60, rect.top + 10)
    pag.click()
    time.sleep(1)  # フォーカス設定の待機時間


def get_screen_size() -> tuple[int, int]:
    """
    画面サイズを取得
    
    Returns:
        (幅, 高さ)のタプル
    """
    return pag.size()

