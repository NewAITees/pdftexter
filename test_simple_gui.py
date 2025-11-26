"""
最もシンプルなGUIテスト
"""

import tkinter as tk
from tkinter import messagebox

print("シンプルなメッセージボックステスト...")

# まず最もシンプルなメッセージボックスを表示
root = tk.Tk()
root.withdraw()

result = messagebox.showinfo("テスト", "このメッセージが見えますか？")
print(f"メッセージボックスの結果: {result}")

root.destroy()

print("\n次に統合GUIをテスト...")

import sys
sys.path.insert(0, 'src')

from pdftexter.utils.gui import get_title_and_direction

title, direction = get_title_and_direction()

print(f"\nタイトル: {title}")
print(f"方向: {direction}")
print("\nテスト完了！")
