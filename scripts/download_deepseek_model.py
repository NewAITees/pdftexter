#!/usr/bin/env python3
"""
DeepSeek-OCRモデルのダウンロードスクリプト
"""

import argparse
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from pdftexter.ocr.model_downloader import (
    check_huggingface_hub,
    download_deepseek_ocr_model,
    install_huggingface_hub,
)


def main() -> int:
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="DeepSeek-OCRモデルをHuggingFaceからダウンロードします"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="./models/DeepSeek-OCR",
        help="モデルを保存するディレクトリパス（デフォルト: ./models/DeepSeek-OCR）",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="deepseek-ai/DeepSeek-OCR",
        help="HuggingFaceのモデル名（デフォルト: deepseek-ai/DeepSeek-OCR）",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="中断されたダウンロードを再開しない",
    )
    parser.add_argument(
        "--install-hub",
        action="store_true",
        help="huggingface_hubがインストールされていない場合、自動的にインストールする",
    )
    
    args = parser.parse_args()
    
    # huggingface_hubのチェック
    if not check_huggingface_hub():
        if args.install_hub:
            print("huggingface_hubをインストール中...")
            success, message = install_huggingface_hub()
            if not success:
                print(f"エラー: {message}", file=sys.stderr)
                return 1
            print(f"✓ {message}\n")
        else:
            print(
                "エラー: huggingface_hubがインストールされていません。\n"
                "以下のいずれかの方法でインストールしてください:\n"
                "  1. --install-hub オプションを使用（自動インストール）\n"
                "  2. 手動でインストール: pip install huggingface_hub\n"
                "  3. 手動でインストール: uv pip install huggingface_hub",
                file=sys.stderr,
            )
            return 1
    
    # モデルのダウンロード
    success, message = download_deepseek_ocr_model(
        model_path=args.model_path,
        model_name=args.model_name,
        resume_download=not args.no_resume,
    )
    
    if success:
        print(f"\n✓ {message}")
        print(f"\n次のステップ:")
        print(f"1. 設定ファイル（config/ocr_config.yaml）でmodel_pathを設定:")
        print(f"   model_path: \"{Path(args.model_path).absolute()}\"")
        print(f"\n2. vLLMサーバーを起動:")
        print(f"   python -m vllm.entrypoints.openai.api_server \\")
        print(f"       --model {Path(args.model_path).absolute()} \\")
        print(f"       --port 8000")
        return 0
    else:
        print(f"\n✗ {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

