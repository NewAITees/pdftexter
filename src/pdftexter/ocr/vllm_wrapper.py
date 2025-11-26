"""
vLLM版DeepSeek-OCRラッパーモジュール
"""

import base64
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests


class VLLMWrapper:
    """vLLMサーバーとの通信を管理するラッパークラス"""
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        model_name: str = "deepseek-ocr",
        timeout: int = 300,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        """
        初期化
        
        Args:
            server_url: vLLMサーバーのURL（Noneの場合はローカル実行を想定）
            model_name: モデル名（vLLM APIで使用）
            timeout: タイムアウト時間（秒）
            max_retries: 最大リトライ回数
            retry_delay: リトライ間隔（秒）
        """
        self.server_url = server_url or "http://localhost:8000"
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def encode_image(self, image_path: str) -> str:
        """
        画像ファイルをbase64エンコードする
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            base64エンコードされた画像データ
        """
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded
    
    def create_request(
        self,
        image_path: str,
        prompt: str = "<image>\n<|grounding|>Convert the document to markdown.",
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """
        vLLMリクエストを作成する
        
        Args:
            image_path: 画像ファイルのパス
            prompt: プロンプトテキスト
            max_tokens: 最大トークン数
            temperature: 温度パラメータ
            
        Returns:
            リクエストデータの辞書
        """
        # 画像をbase64エンコード
        image_data = self.encode_image(image_path)
        
        # vLLM APIリクエスト形式
        request_data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        return request_data
    
    def call_vllm_api(
        self,
        image_path: str,
        prompt: str = "<image>\n<|grounding|>Convert the document to markdown.",
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> str:
        """
        vLLM APIを呼び出してOCR処理を実行する
        
        Args:
            image_path: 画像ファイルのパス
            prompt: プロンプトテキスト
            max_tokens: 最大トークン数
            temperature: 温度パラメータ
            
        Returns:
            OCR結果のテキスト
            
        Raises:
            requests.RequestException: API呼び出しに失敗した場合
            TimeoutError: タイムアウトした場合
        """
        request_data = self.create_request(image_path, prompt, max_tokens, temperature)
        
        # APIエンドポイント
        api_url = f"{self.server_url}/v1/chat/completions"
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    api_url,
                    json=request_data,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                
                # レスポンスからテキストを抽出
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    return content
                else:
                    raise ValueError("Invalid response format from vLLM API")
                    
            except requests.Timeout:
                last_exception = TimeoutError(f"Request timeout after {self.timeout} seconds")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise last_exception
                
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise last_exception
        
        raise last_exception or Exception("Failed to call vLLM API")
    
    def process_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> str:
        """
        PDFファイルを処理してOCR結果を取得する
        
        注意: このメソッドはPDFを画像に変換する必要があります。
        実際の実装では、PDFを画像に変換してから各ページを処理します。
        
        Args:
            pdf_path: PDFファイルのパス
            output_dir: 出力ディレクトリ
            prompt: プロンプトテキスト（Noneの場合はデフォルト）
            max_tokens: 最大トークン数
            temperature: 温度パラメータ
            
        Returns:
            OCR結果のテキスト（全ページ結合）
            
        Raises:
            NotImplementedError: PDF処理は別モジュールで実装する必要があります
        """
        raise NotImplementedError(
            "PDF処理はpdftexter.pdf.processorモジュールを使用してください"
        )

