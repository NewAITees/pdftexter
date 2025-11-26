"""
DeepSeek-OCRモデルのダウンロードモジュール
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
    from huggingface_hub import snapshot_download
except ImportError:
    snapshot_download = None


def download_deepseek_ocr_model(
    model_path: str,
    model_name: str = "deepseek-ai/DeepSeek-OCR",
    resume_download: bool = True,
) -> Tuple[bool, str]:
    """
    DeepSeek-OCRモデルをHuggingFaceからダウンロードする
    
    Args:
        model_path: モデルを保存するディレクトリパス
        model_name: HuggingFaceのモデル名（デフォルト: "deepseek-ai/DeepSeek-OCR"）
        resume_download: 中断されたダウンロードを再開するか
        
    Returns:
        (成功したか, メッセージ)のタプル
    """
    if snapshot_download is None:
        return False, (
            "huggingface_hubがインストールされていません。\n"
            "以下のコマンドでインストールしてください:\n"
            "  pip install huggingface_hub\n"
            "または:\n"
            "  uv pip install huggingface_hub"
        )
    
    try:
        output_path = Path(model_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"DeepSeek-OCRモデルをダウンロード中...")
        print(f"モデル: {model_name}")
        print(f"保存先: {output_path}")
        print("（モデルサイズは約6.7GBです。時間がかかる場合があります）\n")
        
        # HuggingFaceからモデルをダウンロード
        downloaded_path = snapshot_download(
            repo_id=model_name,
            local_dir=str(output_path),
            resume_download=resume_download,
        )
        
        print(f"\n✓ ダウンロード完了: {downloaded_path}")
        return True, f"モデルが正常にダウンロードされました: {downloaded_path}"
        
    except Exception as e:
        error_msg = f"モデルのダウンロード中にエラーが発生しました: {e}"
        print(f"✗ {error_msg}", file=sys.stderr)
        return False, error_msg


def check_huggingface_hub() -> bool:
    """huggingface_hubがインストールされているかチェック"""
    return snapshot_download is not None


def install_huggingface_hub() -> Tuple[bool, str]:
    """
    huggingface_hubをインストールする
    
    Returns:
        (成功したか, メッセージ)のタプル
    """
    try:
        # uvが利用可能かチェック
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
        )
        use_uv = result.returncode == 0
        
        if use_uv:
            print("uvを使用してhuggingface_hubをインストール中...")
            result = subprocess.run(
                ["uv", "pip", "install", "huggingface_hub"],
                capture_output=True,
                text=True,
            )
        else:
            print("pipを使用してhuggingface_hubをインストール中...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "huggingface_hub"],
                capture_output=True,
                text=True,
            )
        
        if result.returncode == 0:
            return True, "huggingface_hubのインストールが完了しました"
        else:
            return False, f"インストールに失敗しました: {result.stderr}"
            
    except Exception as e:
        return False, f"インストール中にエラーが発生しました: {e}"

