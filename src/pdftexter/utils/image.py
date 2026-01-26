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
    color_diff_threshold: int = 30,
) -> Tuple[int, int]:
    """
    画像内のコンテンツ境界を自動検出

    Kindleの余白とコンテンツの色の境界を自動的に検出します。
    これにより、余白を削除してコンテンツ部分のみを切り出すことができます。

    検出方法：
    複数の行をサンプリングし、左端・右端の余白色と大きく異なる色が
    現れる位置を境界として検出します。複数行の結果から最も安全な
    （文字が切れない）境界を採用します。

    Args:
        img: 画像データ（NumPy配列、BGR形式）
        left_margin: 左側マージン（境界検出の開始位置）
        right_margin: 右側マージン（境界検出の終了位置）
        color_diff_threshold: 色差の閾値（RGB合計値、デフォルト30）

    Returns:
        (左端の位置, 右端の位置)のタプル
        この値は、trim_image()関数で使用して画像をトリミングします

    Raises:
        ValueError: 画像の高さが不足している場合
    """
    height, width = img.shape[:2]

    if left_margin < 0 or right_margin < 0:
        raise ValueError("left_margin/right_margin must be non-negative")
    if width <= 0:
        raise ValueError("画像の幅が不正です")
    if left_margin >= width or right_margin >= width:
        raise ValueError("left_margin/right_marginが画像幅以上です")
    if left_margin >= width - right_margin:
        raise ValueError("left_margin/right_marginの合計が画像幅以上です")

    # 画像の高さをチェック（サンプリングに最低限必要）
    min_height = 10
    if height < min_height:
        raise ValueError(
            f"画像の高さが不足しています（{height}px < {min_height}px）。" f"境界検出には最低{min_height}pxの高さが必要です。"
        )

    # 複数行をサンプリング（画像高さの20%, 40%, 60%, 80%）
    sample_ratios = [0.2, 0.4, 0.6, 0.8]
    sample_indices = [int(height * r) for r in sample_ratios]

    left_candidates: list[int] = []
    right_candidates: list[int] = []

    for row_idx in sample_indices:
        row = img[row_idx]

        # 左端の色（余白色）を取得
        left_margin_color = row[left_margin].astype(np.int32)
        # 右端の色（余白色）を取得
        right_margin_color = row[width - right_margin - 1].astype(np.int32)

        # 左から走査：余白色と大きく異なる色が現れる位置
        for i in range(left_margin, width - right_margin):
            pixel = row[i].astype(np.int32)
            diff = int(np.abs(pixel - left_margin_color).sum())
            if diff >= color_diff_threshold:
                left_candidates.append(i)
                break

        # 右から走査：余白色と大きく異なる色が現れる位置
        for i in range(width - right_margin - 1, left_margin, -1):
            pixel = row[i].astype(np.int32)
            diff = int(np.abs(pixel - right_margin_color).sum())
            if diff >= color_diff_threshold:
                right_candidates.append(i + 1)  # 境界の外側を含める
                break

    # 安全マージンとして最も内側の境界を採用（文字が切れないように）
    left = max(left_candidates) if left_candidates else left_margin
    right = min(right_candidates) if right_candidates else width - right_margin

    if right <= left:
        raise ValueError("境界検出に失敗しました。マージン設定を見直してください")

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
