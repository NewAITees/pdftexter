"""
HuggingFace Transformers版DeepSeek-OCRラッパー
vLLMサーバー不要で直接モデルを実行できる簡単な方法
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from transformers import AutoModel, AutoTokenizer
    from PIL import Image
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    torch = None


class HuggingFaceOCRWrapper:
    """HuggingFace Transformers版DeepSeek-OCRラッパー"""
    
    def __init__(self, model_path: str):
        """
        初期化
        
        Args:
            model_path: DeepSeek-OCRモデルのパス（HuggingFaceモデルIDまたはローカルパス）
            
        Raises:
            ImportError: transformersがインストールされていない場合
            FileNotFoundError: モデルが見つからない場合
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformersがインストールされていません。\n"
                "以下のコマンドでインストールしてください:\n"
                "  pip install transformers pillow torch\n"
                "または:\n"
                "  uv pip install transformers pillow torch"
            )
        
        self.model_path = model_path
        print(f"DeepSeek-OCRモデルを読み込み中: {model_path}...", file=sys.stderr)
        
        # Flash Attention 2関連のエラーを回避するため、モンキーパッチを適用
        # DeepSeek-OCRモデルのカスタムコードがLlamaFlashAttention2をインポートしようとするのを防ぎます
        # LlamaFlashAttention2のダミークラスを定義
        class DummyLlamaFlashAttention2:
            """LlamaFlashAttention2のダミークラス（互換性のため）"""
            pass
        
        # transformers.models.llama.modeling_llamaモジュールにダミークラスを追加
        # これにより、モデルのカスタムコードがインポートエラーを起こさないようにします
        try:
            import transformers.models.llama.modeling_llama as llama_module
            if not hasattr(llama_module, 'LlamaFlashAttention2'):
                # LlamaFlashAttention2が存在しない場合、ダミークラスを追加
                llama_module.LlamaFlashAttention2 = DummyLlamaFlashAttention2
        except ImportError:
            pass
        
        try:
            # Tokenizerとモデルを読み込み（公式の推奨方法）
            # 参考: https://github.com/deepseek-ai/DeepSeek-OCR
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            
            # モデルの読み込み（公式の推奨方法に従う）
            # 公式READMEでは _attn_implementation='flash_attention_2' を推奨
            # ただし、flash-attnがインストールされていない場合はフォールバック
            use_flash_attention_2 = False
            try:
                # flash-attnがインストールされているかチェック
                import flash_attn  # noqa: F401
                use_flash_attention_2 = True
            except ImportError:
                # flash-attnがインストールされていない場合は標準実装を使用
                use_flash_attention_2 = False
            
            if use_flash_attention_2:
                # 公式の推奨方法：flash_attention_2を使用
                try:
                    self.model = AutoModel.from_pretrained(
                        model_path,
                        _attn_implementation='flash_attention_2',
                        trust_remote_code=True,
                        use_safetensors=True,
                    )
                    print("✓ モデルを読み込みました（Flash Attention 2を使用）", file=sys.stderr)
                except Exception as e:
                    # flash_attention_2が使えない場合は標準実装にフォールバック
                    error_msg = str(e)
                    print(f"⚠ Flash Attention 2の使用に失敗しました: {error_msg}", file=sys.stderr)
                    print("⚠ 標準のattention実装を使用します", file=sys.stderr)
                    self.model = AutoModel.from_pretrained(
                        model_path,
                        trust_remote_code=True,
                        use_safetensors=True,
                    )
                    print("✓ モデルを読み込みました（標準のattention実装を使用）", file=sys.stderr)
            else:
                # flash-attnがインストールされていない場合は標準実装を使用
                self.model = AutoModel.from_pretrained(
                    model_path,
                    trust_remote_code=True,
                    use_safetensors=True,
                )
                print("✓ モデルを読み込みました（標準のattention実装を使用）", file=sys.stderr)
                print("💡 ヒント: flash-attnをインストールすると、パフォーマンスが向上します", file=sys.stderr)
            
            # モデルを評価モードに設定し、GPUに移動
            self.model = self.model.eval()
            if torch is not None and torch.cuda.is_available():
                try:
                    self.model = self.model.cuda().to(torch.bfloat16)
                    print("✓ GPUを使用して推論します", file=sys.stderr)
                except Exception:
                    self.model = self.model.cuda()
                    print("✓ GPUを使用して推論します（bfloat16は使用できません）", file=sys.stderr)
            else:
                print("⚠ GPUが利用できないため、CPUで推論します", file=sys.stderr)
            
            print("✓ モデルの読み込みが完了しました", file=sys.stderr)
            
        except Exception as e:
            raise RuntimeError(
                f"モデルの読み込みに失敗しました: {e}\n"
                f"モデルパスを確認してください: {model_path}"
            )
    
    def process_image(
        self,
        image_path: str,
        prompt: str = "<image>\n<|grounding|>Convert the document to markdown.",
    ) -> str:
        """
        画像ファイルをOCR処理する
        
        Args:
            image_path: 画像ファイルのパス
            prompt: プロンプトテキスト
            
        Returns:
            OCR結果のテキスト（Markdown形式）
        """
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
        
        # DeepSeek-OCRの公式実装では`model.infer()`メソッドを使用
        # infer(self, tokenizer, prompt='', image_file='', output_path='', 
        #       base_size=1024, image_size=640, crop_mode=True, 
        #       test_compress=False, save_results=False)
        if hasattr(self.model, 'infer'):
            # 公式の推奨方法：`infer`メソッドを使用
            result = self.model.infer(
                self.tokenizer,
                prompt=prompt,
                image_file=str(image_path),
                output_path='',  # 結果を保存しない
                base_size=1024,
                image_size=640,
                crop_mode=True,
                test_compress=False,
                save_results=False,
            )
            return result
        else:
            raise RuntimeError(
                "DeepSeek-OCRモデルに`infer`メソッドが見つかりません。"
                "モデルが正しく読み込まれているか確認してください。"
            )


# torchのインポート
try:
    import torch
except ImportError:
    torch = None

