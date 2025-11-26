"""
OCRモデルのダウンロードとチェックモジュール
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def check_model_exists(model_path: str) -> bool:
    """
    モデルが存在するかチェックする
    
    Args:
        model_path: モデルのパス
        
    Returns:
        モデルが存在する場合True
    """
    path = Path(model_path)
    if not path.exists():
        return False
    
    # DeepSeek-OCRのディレクトリ構造をチェック
    # 一般的に、モデルファイルやconfig.jsonなどが存在する
    required_files = ["config.json", "tokenizer.json"]
    has_required = any((path / f).exists() for f in required_files)
    
    # または、run_dpsk_ocr_pdf.pyなどの実行ファイルが存在する
    has_scripts = any(
        (path / f).exists()
        for f in ["run_dpsk_ocr_pdf.py", "run_dpsk_ocr_image.py"]
    )
    
    return has_required or has_scripts


def check_vllm_server(server_url: str = "http://localhost:8000") -> Tuple[bool, str]:
    """
    vLLMサーバーが起動しているかチェックする
    
    Args:
        server_url: vLLMサーバーのURL
        
    Returns:
        (起動しているか, メッセージ)のタプル
    """
    try:
        import requests
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            return True, "vLLMサーバーは起動しています"
        else:
            return False, f"vLLMサーバーが応答しません（ステータスコード: {response.status_code}）"
    except requests.exceptions.ConnectionError:
        return False, "vLLMサーバーに接続できません。サーバーが起動しているか確認してください。"
    except Exception as e:
        return False, f"vLLMサーバーのチェック中にエラーが発生しました: {e}"


def print_setup_instructions() -> None:
    """DeepSeek-OCRのセットアップ手順を表示する"""
    print("\n" + "=" * 60)
    print("DeepSeek-OCRのセットアップが必要です")
    print("=" * 60)
    print("\n以下の手順でセットアップしてください:\n")
    print("1. DeepSeek-OCRリポジトリをクローン:")
    print("   git clone https://github.com/deepseek-ai/DeepSeek-OCR.git")
    print("   cd DeepSeek-OCR")
    print("\n2. 仮想環境を作成（Python 3.12.9推奨）:")
    print("   uv venv -p=3.12.9")
    print("   source .venv/bin/activate  # Linux/Mac")
    print("   .venv\\Scripts\\activate     # Windows")
    print("\n3. 依存関係をインストール:")
    print("   uv pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \\")
    print("       --index-url https://download.pytorch.org/whl/cu118")
    print("   wget https://github.com/vllm-project/vllm/releases/download/v0.8.5/vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl")
    print("   uv pip install vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl")
    print("   uv pip install -r requirements.txt")
    print("   uv pip install flash-attn==2.7.3 --no-build-isolation")
    print("\n4. vLLMサーバーを起動:")
    print("   # DeepSeek-OCRディレクトリで実行")
    print("   python -m vllm.entrypoints.openai.api_server \\")
    print("       --model /path/to/deepseek-ocr-model \\")
    print("       --port 8000")
    print("\n5. 設定ファイル（config/ocr_config.yaml）でモデルパスとサーバーURLを設定")
    print("=" * 60 + "\n")


def verify_ocr_setup(config_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    OCRセットアップを検証する
    
    Args:
        config_path: 設定ファイルのパス
        
    Returns:
        (セットアップが完了しているか, メッセージ)のタプル
    """
    try:
        from pdftexter.ocr.config import load_config
        
        config = load_config(config_path)
        
        # モデルのチェック
        model_path = config.deepseek_ocr.model_path
        if not check_model_exists(model_path):
            print_setup_instructions()
            return False, f"モデルが見つかりません: {model_path}"
        
        # vLLMサーバーのチェック
        server_url = config.deepseek_ocr.vllm_server_url or "http://localhost:8000"
        is_running, message = check_vllm_server(server_url)
        
        if not is_running:
            print_setup_instructions()
            return False, message
        
        return True, "OCRセットアップは完了しています"
        
    except Exception as e:
        return False, f"セットアップの検証中にエラーが発生しました: {e}"

