"""
最終GUI動作確認テスト
"""

import sys
sys.path.insert(0, 'src')

from pdftexter.utils.gui import get_title_and_direction

print("=" * 50)
print("GUIテスト開始")
print("ウィンドウが表示されるはずです...")
print("=" * 50)

title, direction = get_title_and_direction()

print("\n" + "=" * 50)
print("入力結果:")
print(f"  タイトル: {title}")
print(f"  方向: {direction}")
print("=" * 50)
print("\nテスト成功！")
