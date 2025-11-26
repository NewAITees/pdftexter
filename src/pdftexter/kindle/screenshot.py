"""
Kindleスクリーンショット撮影モジュール
"""

import os
import time
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pyautogui as pag

from pdftexter.kindle.window import find_kindle_window, get_screen_size, setup_kindle_window
from pdftexter.utils.file import ensure_directory, join_path
from pdftexter.utils.gui import get_save_folder, get_title, show_error, show_info
from pdftexter.utils.image import (
    convert_rgb_to_bgr,
    find_content_boundaries,
    grab_screen,
    images_equal,
    save_image,
    trim_image,
)


class KindleScreenshotConfig:
    """Kindleスクリーンショット設定クラス"""
    
    def __init__(
        self,
        window_title: str = "Kindle for PC",
        page_change_key: str = "right",
        fullscreen_wait: float = 5.0,
        left_margin: int = 1,
        right_margin: int = 1,
        wait_seconds: float = 0.15,
        timeout_seconds: float = 5.0,
    ):
        """
        設定を初期化
        
        Args:
            window_title: Kindleウィンドウのタイトル
            page_change_key: 次のページへ移動するキー
            fullscreen_wait: フルスクリーン後の待機時間（秒）
            left_margin: 左側マージン（境界検出用）
            right_margin: 右側マージン（境界検出用）
            wait_seconds: キー押下後の待機時間（秒）
            timeout_seconds: ページめくりのタイムアウト時間（秒）
        """
        self.window_title = window_title
        self.page_change_key = page_change_key
        self.fullscreen_wait = fullscreen_wait
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.wait_seconds = wait_seconds
        self.timeout_seconds = timeout_seconds


class KindleScreenshot:
    """Kindleスクリーンショット撮影クラス"""
    
    def __init__(self, config: Optional[KindleScreenshotConfig] = None):
        """
        初期化
        
        Args:
            config: 設定オブジェクト（Noneの場合はデフォルト設定を使用）
        """
        self.config = config or KindleScreenshotConfig()
        self.base_save_folder: Optional[str] = None
    
    def capture_pages(
        self,
        left: int,
        right: int,
        title: str,
        save_folder: str,
    ) -> int:
        """
        ページを自動的にキャプチャして保存
        
        このメソッドは以下の処理を自動的に実行します：
        1. 画面をキャプチャ
        2. 余白を自動トリミング（left, rightで指定された境界に基づく）
        3. 画像を保存
        4. 自動的に次のページへ（pag.pressでキー操作）
        5. ページが変わるまで待機
        6. 最終ページに到達するまで繰り返し
        
        Args:
            left: 左端の位置（トリミング境界）
            right: 右端の位置（トリミング境界）
            title: 保存フォルダ名
            save_folder: 保存先の親フォルダ
            
        Returns:
            保存したページ数
        """
        screen_width, screen_height = get_screen_size()
        
        # ページめくりを検知するための比較用画像
        # トリミング後の画像の高さは画面の高さと同じ
        old = np.zeros((screen_height, right - left, 3), np.uint8)
        page = 1
        
        # 保存先フォルダの設定
        current_dir = os.getcwd()
        save_path = join_path(save_folder, title)
        ensure_directory(save_path)
        os.chdir(save_path)
        
        try:
            while True:
                filename = f"{page:03d}.png"
                start_time = time.perf_counter()
                
                # ページめくりが完了するまで待機
                while True:
                    time.sleep(self.config.wait_seconds)
                    
                    # 画面をキャプチャ
                    screen = grab_screen()
                    screen_array = convert_rgb_to_bgr(screen)
                    
                    # コンテンツ境界に基づいて自動トリミング（余白を削除）
                    trimmed = trim_image(screen_array, left, right)
                    
                    # ページめくりが完了したか確認
                    if not images_equal(old, trimmed):
                        break
                    
                    # タイムアウト処理（最終ページなどで変化がなかった場合）
                    if time.perf_counter() - start_time > self.config.timeout_seconds:
                        os.chdir(current_dir)
                        return page - 1  # 最後に成功したページ数を返す
                
                # 画像保存
                if save_image(trimmed, filename):
                    old = trimmed
                    elapsed = time.perf_counter() - start_time
                    print(f'Page: {page}, {trimmed.shape}, {elapsed:.2f} sec')
                    page += 1
                    
                    # 自動的に次ページへ（キーを押してすぐに離す）
                    # ページ送りは完全に自動化されており、ユーザーの操作は不要
                    pag.press(self.config.page_change_key)
                else:
                    print(f'Failed to save page {page}')
                    break
        finally:
            os.chdir(current_dir)
        
        return page - 1
    
    def run(self) -> Optional[int]:
        """
        メイン処理を実行
        
        Returns:
            保存したページ数、エラーの場合はNone
        """
        # Kindleウィンドウを検出
        hwnd = find_kindle_window(self.config.window_title)
        if hwnd is None:
            show_error("エラー", "Kindleが見つかりません")
            return None
        
        # ウィンドウを前面に表示
        setup_kindle_window(hwnd)
        
        # 画面サイズを取得してマウスを画面外に移動
        # （フルスクリーン表示の邪魔にならないように）
        screen_width, screen_height = get_screen_size()
        pag.moveTo(screen_width - 200, screen_height - 1)
        time.sleep(self.config.fullscreen_wait)
        
        # タイトルと保存先の取得
        title = get_title()
        base_save_folder = get_save_folder()
        if not base_save_folder:
            show_error("エラー", "保存先フォルダが選択されていません")
            return None
        
        # 初期画像を取得してコンテンツ境界を自動検出
        # これにより、余白を自動的に削除してコンテンツ部分のみを切り出す
        initial_image = grab_screen()
        initial_array = convert_rgb_to_bgr(initial_image)
        left, right = find_content_boundaries(
            initial_array,
            self.config.left_margin,
            self.config.right_margin,
        )
        
        # 自動ページめくりとキャプチャを実行
        # ページは自動的にめくられ、トリミングされた画像が保存されます
        total_pages = self.capture_pages(left, right, title, base_save_folder)
        
        # 完了メッセージを表示
        if total_pages is not None and total_pages > 0:
            show_info(
                "完了",
                f"スクリーンショットの撮影が終了しました。\n"
                f"合計 {total_pages} ページを保存しました。"
            )
        
        return total_pages


def main() -> None:
    """メイン関数"""
    screenshot = KindleScreenshot()
    screenshot.run()


if __name__ == "__main__":
    main()

