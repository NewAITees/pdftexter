"""
Ollama OCR APIラッパーモジュール
"""

import base64
import time
from typing import Any, Dict

import requests


class OllamaWrapper:
    """Ollama APIとの通信を管理するラッパークラス"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "openbmb/minicpm-v4.5",
        timeout: int = 300,
        max_retries: int = 3,
        retry_delay: int = 5,
    ) -> None:
        """
        初期化

        Args:
            base_url: Ollama APIのベースURL
            model_name: 使用するモデル名
            timeout: タイムアウト時間（秒）
            max_retries: 最大リトライ回数
            retry_delay: リトライ間隔（秒）
        """
        self.base_url = base_url.rstrip("/")
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
            return base64.b64encode(image_file.read()).decode("utf-8")

    def create_request(
        self,
        image_path: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """
        Ollama chat APIリクエストを作成する

        Args:
            image_path: 画像ファイルのパス
            prompt: プロンプトテキスト
            max_tokens: 最大トークン数
            temperature: 温度パラメータ

        Returns:
            リクエストデータの辞書
        """
        image_data = self.encode_image(image_path)

        return {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_data],
                }
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

    def call_ollama_api(
        self,
        image_path: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """
        Ollama APIを呼び出してOCR処理を実行する

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
        api_url = f"{self.base_url}/api/chat"

        last_exception: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    api_url,
                    json=request_data,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                result = response.json()
                message = result.get("message", {})
                content = message.get("content", "")
                if not content:
                    raise ValueError("Invalid response format from Ollama API")
                return content
            except requests.Timeout:
                last_exception = TimeoutError(f"Request timeout after {self.timeout} seconds")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise last_exception
            except requests.RequestException as exc:
                last_exception = exc
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise last_exception

        raise last_exception or Exception("Failed to call Ollama API")
