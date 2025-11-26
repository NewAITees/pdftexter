"""
vLLMラッパーモジュールのテスト
"""

import base64
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from pdftexter.ocr.vllm_wrapper import VLLMWrapper


class TestVLLMWrapper:
    """VLLMWrapperクラスのテスト"""
    
    def test_create_request_uses_model_name(self):
        """リクエストに設定されたモデル名が使用されることを確認"""
        wrapper = VLLMWrapper(
            server_url="http://localhost:8000",
            model_name="custom-model-name",
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # テスト用画像を作成
            from PIL import Image
            img = Image.new('RGB', (100, 100), color=(255, 0, 0))
            img_path = Path(tmpdir, "test.png")
            img.save(img_path)
            
            request_data = wrapper.create_request(str(img_path))
            
            # モデル名が正しく設定されていることを確認
            assert request_data["model"] == "custom-model-name"
    
    def test_create_request_encodes_image(self):
        """画像がbase64エンコードされることを確認"""
        wrapper = VLLMWrapper()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color=(255, 0, 0))
            img_path = Path(tmpdir, "test.png")
            img.save(img_path)
            
            request_data = wrapper.create_request(str(img_path))
            
            # 画像がbase64エンコードされていることを確認
            content = request_data["messages"][0]["content"]
            image_url = next(
                (item["image_url"]["url"] for item in content if item["type"] == "image_url"),
                None
            )
            assert image_url is not None
            assert image_url.startswith("data:image/png;base64,")
            
            # base64データが存在することを確認
            encoded_data = image_url.split(",")[1]
            decoded = base64.b64decode(encoded_data)
            assert len(decoded) > 0
    
    def test_call_vllm_api_retries_on_failure(self):
        """API呼び出しが失敗した場合、リトライされることを確認"""
        wrapper = VLLMWrapper(max_retries=3, retry_delay=0.1)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color=(255, 0, 0))
            img_path = Path(tmpdir, "test.png")
            img.save(img_path)
            
            with patch("requests.post") as mock_post:
                # 最初の2回はエラー、3回目は成功
                mock_responses = [
                    Mock(status_code=500, raise_for_status=Mock(side_effect=requests.RequestException())),
                    Mock(status_code=500, raise_for_status=Mock(side_effect=requests.RequestException())),
                    Mock(
                        status_code=200,
                        raise_for_status=Mock(),
                        json=Mock(return_value={
                            "choices": [{
                                "message": {"content": "OCR result"}
                            }]
                        })
                    ),
                ]
                mock_post.side_effect = mock_responses
                
                result = wrapper.call_vllm_api(str(img_path))
                
                # リトライ後に成功することを確認
                assert result == "OCR result"
                assert mock_post.call_count == 3
    
    def test_call_vllm_api_raises_on_all_failures(self):
        """すべてのリトライが失敗した場合、例外が発生することを確認"""
        wrapper = VLLMWrapper(max_retries=2, retry_delay=0.1)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color=(255, 0, 0))
            img_path = Path(tmpdir, "test.png")
            img.save(img_path)
            
            with patch("requests.post") as mock_post:
                # すべて失敗
                mock_response = Mock(
                    status_code=500,
                    raise_for_status=Mock(side_effect=requests.RequestException("Server error"))
                )
                mock_post.return_value = mock_response
                
                # 例外が発生することを確認
                with pytest.raises(requests.RequestException):
                    wrapper.call_vllm_api(str(img_path))
                
                # リトライ回数分呼ばれることを確認
                assert mock_post.call_count == 2

