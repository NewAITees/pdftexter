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

_KINDLE_STATE_FILENAME = "kindle_state.json"


def _get_kindle_state_path() -> Path:
    """
    Kindle設定の保存パスを取得

    Returns:
        保存先パス
    """
    return Path(__file__).resolve().parents[3] / "config" / _KINDLE_STATE_FILENAME


def _load_kindle_direction() -> Optional[str]:
    """
    保存済みのページめくり方向を取得

    Returns:
        "left" または "right"、未設定ならNone
    """
    path = _get_kindle_state_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    direction = data.get("direction")
    return direction if direction in {"left", "right"} else None


def _save_kindle_direction(direction: str) -> None:
    """
    ページめくり方向を保存

    Args:
        direction: "left" または "right"
    """
    path = _get_kindle_state_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"direction": direction}
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
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


def get_title_and_direction(default_prefix: str = "") -> tuple[str, str]:
    """
    タイトルとページめくり方向を同時に取得（GUIダイアログ）

    Args:
        default_prefix: デフォルトのプレフィックス

    Returns:
        (タイトル, ページめくり方向) のタプル
    """
    # Tkinterウィンドウを作成
    root = tk.Tk()

    # メインウィンドウは最小化せずに、ダイアログとして使用
    root.title("Kindleスクリーンショット設定")

    # 結果を保存する変数
    title_var = tk.StringVar(value="")
    saved_direction = _load_kindle_direction()
    direction_var = tk.StringVar(value=saved_direction or "right")
    result = {"title": "", "direction": "right"}

    # rootをそのまま使用（Toplevelではなく）
    dialog = root
    dialog.title("Kindleスクリーンショット設定")

    # ウィンドウサイズと位置（大きく見やすく）
    width = 600
    height = 400

    # 画面の中央に配置
    dialog.update_idletasks()
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # ジオメトリを設定
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    dialog.resizable(False, False)

    # 最前面に表示（重要！）
    dialog.attributes("-topmost", True)
    dialog.lift()
    dialog.focus_force()

    # タイトル入力セクション
    title_frame = tk.Frame(dialog, pady=20)
    title_frame.pack(fill="x", padx=30)

    title_label = tk.Label(title_frame, text="📚 本のタイトルを入力してください：", font=("", 14, "bold"))
    title_label.pack(anchor="w", pady=(0, 10))

    title_entry = tk.Entry(title_frame, textvariable=title_var, font=("", 12), width=50)
    title_entry.pack(fill="x", pady=5, ipady=5)
    title_entry.focus()  # フォーカスを設定

    hint_label = tk.Label(title_frame, text="※空白の場合は現在時刻が使用されます", font=("", 9), fg="gray")
    hint_label.pack(anchor="w", pady=(5, 0))

    # 区切り線
    separator = tk.Frame(dialog, height=2, bg="lightgray")
    separator.pack(fill="x", padx=30, pady=15)

    # ページめくり方向セクション
    direction_frame = tk.Frame(dialog)
    direction_frame.pack(fill="x", padx=30)

    direction_label = tk.Label(direction_frame, text="📖 ページめくりの方向を選択：", font=("", 14, "bold"))
    direction_label.pack(anchor="w", pady=(0, 15))

    # ラジオボタン
    right_radio = tk.Radiobutton(
        direction_frame, text="右方向（→）  ※通常の本", variable=direction_var, value="right", font=("", 12)
    )
    right_radio.pack(anchor="w", pady=5)

    left_radio = tk.Radiobutton(
        direction_frame,
        text="左方向（←）  ※縦書きの本など",
        variable=direction_var,
        value="left",
        font=("", 12),
    )
    left_radio.pack(anchor="w", pady=5)

    # OKボタン
    def on_ok():
        title = title_var.get().strip()
        if not title:
            # 空白の場合は現在時刻を使用
            default_title = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            if default_prefix:
                default_title = f"{default_prefix}_{default_title}"
            result["title"] = default_title
        else:
            result["title"] = title
        result["direction"] = direction_var.get()
        _save_kindle_direction(result["direction"])
        dialog.quit()  # mainloop()を終了

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=25)

    ok_button = tk.Button(
        button_frame,
        text="OK",
        command=on_ok,
        width=15,
        font=("", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        relief="raised",
        padx=20,
        pady=10,
    )
    ok_button.pack()

    # Enterキーでも決定できるように
    dialog.bind("<Return>", lambda e: on_ok())

    # ダイアログを最前面に表示
    dialog.grab_set()

    # メインループを開始
    try:
        dialog.mainloop()
    except Exception:
        pass
    finally:
        # ウィンドウを破棄
        try:
            dialog.destroy()
        except Exception:
            pass

    return result["title"], result["direction"]


def get_page_direction() -> str:
    """
    ページめくり方向を選択（GUIダイアログ）

    注意: この関数は非推奨です。get_title_and_direction()を使用してください。

    Returns:
        選択されたキー（"right" または "left"）
    """
    _, direction = get_title_and_direction()
    return direction


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
