"""
Kindleウィンドウ操作モジュール
"""

import time
from ctypes import POINTER, WINFUNCTYPE, c_bool, c_int, create_unicode_buffer, pointer, windll
from ctypes.wintypes import POINT, RECT
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


def list_windows() -> list[tuple[int, str]]:
    """
    ウィンドウの一覧を取得

    Returns:
        (ウィンドウハンドル, タイトル) のリスト
    """
    EnumWindows = windll.user32.EnumWindows
    GetWindowText = windll.user32.GetWindowTextW
    GetWindowTextLength = windll.user32.GetWindowTextLengthW
    IsWindowVisible = windll.user32.IsWindowVisible
    WNDENUMPROC = WINFUNCTYPE(c_bool, POINTER(c_int), POINTER(c_int))

    windows: list[tuple[int, str]] = []

    def enum_windows_proc(hwnd: int, l_param: int) -> bool:
        if not IsWindowVisible(hwnd):
            return True

        length = GetWindowTextLength(hwnd)
        if length == 0:
            return True

        buffer = create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buffer, length + 1)
        title = buffer.value.strip()
        if title:
            windows.append((hwnd, title))
        return True

    EnumWindows(WNDENUMPROC(enum_windows_proc), 0)
    return windows


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


def get_window_client_rect(hwnd: int) -> tuple[int, int, int, int]:
    """
    Kindleウィンドウのクライアント領域を取得

    Args:
        hwnd: ウィンドウハンドル

    Returns:
        (left, top, right, bottom) のタプル
    """
    GetClientRect = windll.user32.GetClientRect
    ClientToScreen = windll.user32.ClientToScreen

    rect = RECT()
    if not GetClientRect(hwnd, pointer(rect)):
        raise RuntimeError("Failed to get window client rect")

    pt = POINT(rect.left, rect.top)
    if not ClientToScreen(hwnd, pointer(pt)):
        raise RuntimeError("Failed to translate client coords to screen coords")

    left = pt.x
    top = pt.y
    right = left + (rect.right - rect.left)
    bottom = top + (rect.bottom - rect.top)
    return (left, top, right, bottom)
