"""
GUI共通コンポーネントモジュール
"""

import datetime
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional

from pdftexter.kindle.window import list_windows

# 設定ファイルのパス
_SETTINGS_FILENAME = "screenshot_settings.json"

# 利用可能なページ送りキー
PAGE_KEYS = [
    ("right", "→（右矢印）"),
    ("left", "←（左矢印）"),
    ("pagedown", "Page Down"),
    ("pageup", "Page Up"),
    ("space", "スペース"),
    ("down", "↓（下矢印）"),
    ("up", "↑（上矢印）"),
]


def _get_settings_path() -> Path:
    """設定ファイルのパスを取得"""
    return Path(__file__).resolve().parents[3] / "config" / _SETTINGS_FILENAME


def _load_page_key() -> str:
    """保存済みのページ送りキーを取得（デフォルト: right）"""
    path = _get_settings_path()
    if not path.exists():
        return "right"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        key = data.get("page_key", "right")
        # 有効なキーか確認
        valid_keys = [k for k, _ in PAGE_KEYS]
        return key if key in valid_keys else "right"
    except (OSError, json.JSONDecodeError):
        return "right"


def _save_page_key(key: str) -> None:
    """ページ送りキーを保存"""
    path = _get_settings_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"page_key": key}
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


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

    title = simpledialog.askstring("タイトルを入力", "タイトルを入力して下さい(空白の場合現在の時刻)")
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


def get_title_and_key_dialog(default_prefix: str = "") -> tuple[str, str]:
    """
    タイトルとページ送りキーを取得（GUIダイアログ）

    Args:
        default_prefix: デフォルトのプレフィックス

    Returns:
        (タイトル, ページ送りキー) のタプル
    """
    root = tk.Tk()
    root.title("スクリーンショット設定")

    # 結果を保存する変数
    title_var = tk.StringVar(value="")
    saved_key = _load_page_key()
    key_var = tk.StringVar(value=saved_key)
    result = {"title": "", "key": saved_key}

    dialog = root

    # ウィンドウサイズと位置
    width = 500
    height = 350

    dialog.update_idletasks()
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    dialog.geometry(f"{width}x{height}+{x}+{y}")
    dialog.resizable(False, False)

    dialog.attributes("-topmost", True)
    dialog.lift()
    dialog.focus_force()

    # タイトル入力セクション
    title_frame = tk.Frame(dialog, pady=15)
    title_frame.pack(fill="x", padx=30)

    title_label = tk.Label(title_frame, text="本のタイトルを入力してください：", font=("", 12, "bold"))
    title_label.pack(anchor="w", pady=(0, 5))

    title_entry = tk.Entry(title_frame, textvariable=title_var, font=("", 11), width=50)
    title_entry.pack(fill="x", pady=5, ipady=3)
    title_entry.focus()

    hint_label = tk.Label(title_frame, text="※空白の場合は現在時刻が使用されます", font=("", 9), fg="gray")
    hint_label.pack(anchor="w")

    # 区切り線
    separator = tk.Frame(dialog, height=2, bg="lightgray")
    separator.pack(fill="x", padx=30, pady=10)

    # ページ送りキー選択セクション
    key_frame = tk.Frame(dialog)
    key_frame.pack(fill="x", padx=30)

    key_label = tk.Label(key_frame, text="ページ送りキーを選択：", font=("", 12, "bold"))
    key_label.pack(anchor="w", pady=(0, 5))

    # ドロップダウン（Combobox風）
    key_options = [label for _, label in PAGE_KEYS]
    key_values = [key for key, _ in PAGE_KEYS]

    # 現在の値のインデックスを取得
    try:
        current_idx = key_values.index(saved_key)
    except ValueError:
        current_idx = 0

    # OptionMenuを使用
    selected_label = tk.StringVar(value=key_options[current_idx])

    def on_key_change(*_: object) -> None:
        idx = key_options.index(selected_label.get())
        key_var.set(key_values[idx])

    key_menu = tk.OptionMenu(key_frame, selected_label, *key_options, command=on_key_change)
    key_menu.config(font=("", 11), width=20)
    key_menu.pack(anchor="w", pady=5)

    hint_key_label = tk.Label(key_frame, text="※選択したキーは次回以降も記憶されます", font=("", 9), fg="gray")
    hint_key_label.pack(anchor="w")

    # OKボタン
    def on_ok() -> None:
        title = title_var.get().strip()
        if not title:
            default_title = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            if default_prefix:
                default_title = f"{default_prefix}_{default_title}"
            result["title"] = default_title
        else:
            result["title"] = title
        result["key"] = key_var.get()
        _save_page_key(result["key"])
        dialog.quit()

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=20)

    ok_button = tk.Button(
        button_frame,
        text="OK",
        command=on_ok,
        width=15,
        font=("", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        relief="raised",
        padx=15,
        pady=8,
    )
    ok_button.pack()

    dialog.bind("<Return>", lambda e: on_ok())
    dialog.grab_set()

    try:
        dialog.mainloop()
    except Exception:
        pass
    finally:
        try:
            dialog.destroy()
        except Exception:
            pass

    return result["title"], result["key"]


def get_title_dialog(default_prefix: str = "") -> str:
    """
    タイトルのみを取得（GUIダイアログ）- 後方互換用

    Args:
        default_prefix: デフォルトのプレフィックス

    Returns:
        ユーザーが入力したタイトル（空白の場合は現在時刻）
    """
    title, _ = get_title_and_key_dialog(default_prefix)
    return title


def select_window_handle() -> Optional[int]:
    """
    対象ウィンドウを選択（GUIダイアログ）

    Returns:
        選択されたウィンドウハンドル、キャンセルの場合はNone
    """
    windows = list_windows()
    if not windows:
        show_error("エラー", "選択可能なウィンドウが見つかりません")
        return None

    root = tk.Tk()
    root.title("ウィンドウ選択")

    width = 700
    height = 500
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()

    result = {"hwnd": None}

    label = tk.Label(
        root,
        text="対象のウィンドウを選択してください：",
        font=("", 12, "bold"),
        pady=10,
    )
    label.pack()

    listbox = tk.Listbox(root, font=("", 11), selectmode=tk.SINGLE)
    for _, title in windows:
        listbox.insert(tk.END, title)
    listbox.pack(fill="both", expand=True, padx=20, pady=10)
    listbox.focus_set()

    def on_ok() -> None:
        selection = listbox.curselection()
        if not selection:
            show_warning("警告", "ウィンドウを選択してください")
            return
        index = selection[0]
        result["hwnd"] = windows[index][0]
        root.quit()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=15)

    ok_button = tk.Button(
        button_frame,
        text="OK",
        command=on_ok,
        width=12,
        font=("", 11, "bold"),
        bg="#4CAF50",
        fg="white",
    )
    ok_button.pack()

    root.bind("<Return>", lambda e: on_ok())
    root.grab_set()

    try:
        root.mainloop()
    except Exception:
        pass
    finally:
        try:
            root.destroy()
        except Exception:
            pass

    return result["hwnd"]
