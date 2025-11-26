"""
GUI動作テスト用スクリプト
"""

import sys
sys.path.insert(0, 'src')

from pdftexter.utils.gui import get_title_and_direction

print("統合GUI テスト...")
print("ダイアログが表示されます。タイトルを入力して方向を選択してください。")

title, direction = get_title_and_direction()

print(f"\n入力されたタイトル: {title}")
print(f"選択された方向: {direction}")
print("\nテスト完了！")
