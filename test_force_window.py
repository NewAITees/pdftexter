"""
Windows APIを使って強制的に最前面に表示するテスト
"""

import sys
sys.path.insert(0, 'src')

import tkinter as tk
from ctypes import windll
import time

print("強制最前面表示テスト...")

root = tk.Tk()
root.withdraw()

dialog = tk.Toplevel(root)
dialog.title("テストウィンドウ")
dialog.geometry("400x200")

# ラベルを追加
label = tk.Label(
    dialog,
    text="このウィンドウが見えますか？\n\n見えたらOKボタンを押してください",
    font=("", 12),
    pady=30
)
label.pack()

# OKボタン
ok_button = tk.Button(
    dialog,
    text="OK",
    command=dialog.destroy,
    width=10,
    font=("", 10)
)
ok_button.pack(pady=20)

# 画面の中央に配置
dialog.update_idletasks()
width = 400
height = 200
screen_width = dialog.winfo_screenwidth()
screen_height = dialog.winfo_screenheight()
x = (screen_width - width) // 2
y = (screen_height - height) // 2
dialog.geometry(f"{width}x{height}+{x}+{y}")

# 最前面表示の設定
dialog.attributes('-topmost', True)
dialog.lift()
dialog.focus_force()

# Windows API を使ってさらに強制的に前面に
try:
    hwnd = int(dialog.wm_frame(), 16)  # ウィンドウハンドルを取得
    windll.user32.SetForegroundWindow(hwnd)
    windll.user32.BringWindowToTop(hwnd)
    print(f"ウィンドウハンドル: {hwnd}")
except Exception as e:
    print(f"Windows API 呼び出し失敗: {e}")

print("ウィンドウを表示しました。画面を確認してください...")
print(f"位置: x={x}, y={y}")
print(f"サイズ: {width}x{height}")

dialog.transient(root)
dialog.grab_set()

root.wait_window(dialog)
root.destroy()

print("\nテスト完了！")
