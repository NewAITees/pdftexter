"""
画像処理ユーティリティモジュール
"""

from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import ImageGrab


def find_content_boundaries(
    img: np.ndarray,
    left_margin: int = 1,
    right_margin: int = 1,
) -> Tuple[int, int]:
    """
    画像内のコンテンツ境界を自動検出（簡易的な方法）

    Kindleの余白とコンテンツの色の境界を自動的に検出します。
    これにより、余白を削除してコンテンツ部分のみを切り出すことができます。

    検出方法：
    ページ上の特定のピクセル（20行目）で、左上のピクセルと異なる色を探します。
    左から右へ、右から左へと検索して、コンテンツの境界を特定します。

    Args:
        img: 画像データ（NumPy配列、BGR形式）
        left_margin: 左側マージン（境界検出用）
        right_margin: 右側マージン（境界検出用）

    Returns:
        (左端の位置, 右端の位置)のタプル
        この値は、trim_image()関数で使用して画像をトリミングします

    Raises:
        ValueError: 画像の高さが不足している場合
    """
    # 画像の高さをチェック（20行目にアクセスするため、最低21行必要）
    min_height = 21
    if img.shape[0] < min_height:
        raise ValueError(
            f"画像の高さが不足しています（{img.shape[0]}px < {min_height}px）。" f"境界検出には最低{min_height}pxの高さが必要です。"
        )

    # 比較に使用する行インデックス（20行目を使用）
    row_idx = 20

    def compare_pixels(img: np.ndarray, rng: range, row_idx: int) -> Optional[int]:
        """
        ピクセルの色を比較して境界を検出

        Args:
            img: 画像データ
            rng: 検索範囲
            row_idx: 比較に使用する行インデックス

        Returns:
            境界位置、見つからない場合はNone
        """
        for i in rng:
            # ページ上の特定のピクセル（例：20行目）で、左上のピクセルと異なる色を探す
            if np.all(img[row_idx][i] != img[row_idx - 1][0]):
                return i
        return None

    left = compare_pixels(img, range(left_margin, img.shape[1] - right_margin), row_idx)
    right = compare_pixels(img, reversed(range(left_margin, img.shape[1] - right_margin)), row_idx)

    # デフォルト値（境界が見つからない場合）
    if left is None:
        left = left_margin
    if right is None:
        right = img.shape[1] - right_margin

    return left, right


def grab_screen(bbox: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
    """
    画面をキャプチャしてNumPy配列として取得

    Args:
        bbox: キャプチャ範囲 (left, top, right, bottom)。Noneの場合は全画面

    Returns:
        RGB形式の画像データ（NumPy配列）
    """
    img = ImageGrab.grab(bbox=bbox)
    return np.array(img)


def convert_rgb_to_bgr(img: np.ndarray) -> np.ndarray:
    """
    RGB形式の画像をBGR形式に変換

    Args:
        img: RGB形式の画像データ

    Returns:
        BGR形式の画像データ
    """
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


def trim_image(img: np.ndarray, left: int, right: int) -> np.ndarray:
    """
    画像を左右でトリミングする

    Args:
        img: 画像データ
        left: 左端の位置
        right: 右端の位置

    Returns:
        トリミングされた画像データ
    """
    return img[:, left:right]


def save_image(img: np.ndarray, filepath: str) -> bool:
    """
    画像をファイルに保存する

    Args:
        img: 画像データ（BGR形式）
        filepath: 保存先ファイルパス

    Returns:
        保存成功の場合True
    """
    try:
        cv2.imwrite(filepath, img)
        return True
    except Exception:
        return False


def images_equal(img1: np.ndarray, img2: np.ndarray) -> bool:
    """
    2つの画像が等しいか確認する

    Args:
        img1: 画像データ1
        img2: 画像データ2

    Returns:
        等しい場合True
    """
    return np.array_equal(img1, img2)


def images_changed(
    img1: np.ndarray,
    img2: np.ndarray,
    diff_threshold: int = 10,
    min_change_ratio: float = 0.01,
) -> bool:
    """
    2つの画像の変化が十分大きいか確認する

    Args:
        img1: 画像データ1
        img2: 画像データ2
        diff_threshold: 差分とみなす画素の閾値
        min_change_ratio: 変化した画素の最小割合

    Returns:
        変化が一定以上ある場合True
    """
    if img1.shape != img2.shape:
        return True

    diff = cv2.absdiff(img1, img2)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    changed = diff_gray > diff_threshold
    ratio = np.count_nonzero(changed) / changed.size
    return ratio >= min_change_ratio
