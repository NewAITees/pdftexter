"""
GUI共通コンポーネントモジュール
"""

import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional


def get_title(default_prefix: str = "") -> str:
    """
    保存用のタイトルを取得（GUIダイアログ）
    
    Args:
        default_prefix: デフォルトのプレフィックス
        
    Returns:
        ユーザーが入力したタイトル、空白の場合は現在時刻
    """
    default_title = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    if default_prefix:
        default_title = f"{default_prefix}_{default_title}"
    
    title = simpledialog.askstring(
        'タイトルを入力',
        'タイトルを入力して下さい(空白の場合現在の時刻)'
    )
    return title if title and title.strip() else default_title


def get_save_folder(title: str = "保存するフォルダを選択してください") -> Optional[str]:
    """
    保存先フォルダを選択（GUIダイアログ）
    
    Args:
        title: ダイアログのタイトル
        
    Returns:
        選択されたフォルダパス、キャンセルの場合はNone
    """
    return filedialog.askdirectory(title=title)


def select_folder(title: str = "フォルダを選択") -> Optional[str]:
    """
    フォルダ選択ダイアログを表示する
    
    Args:
        title: ダイアログのタイトル
        
    Returns:
        選択されたフォルダパス、キャンセルの場合はNone
    """
    return filedialog.askdirectory(title=title)


def show_error(title: str, message: str) -> None:
    """
    エラーメッセージを表示する
    
    Args:
        title: エラーダイアログのタイトル
        message: エラーメッセージ
    """
    messagebox.showerror(title, message)


def show_info(title: str, message: str) -> None:
    """
    情報メッセージを表示する
    
    Args:
        title: 情報ダイアログのタイトル
        message: 情報メッセージ
    """
    messagebox.showinfo(title, message)


def show_warning(title: str, message: str) -> None:
    """
    警告メッセージを表示する
    
    Args:
        title: 警告ダイアログのタイトル
        message: 警告メッセージ
    """
    messagebox.showwarning(title, message)

