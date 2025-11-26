"""
OCR設定モジュールのテスト
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from pdftexter.ocr.config import (
    DeepSeekOCRConfig,
    OCRConfig,
    OutputConfig,
    get_default_config,
    load_config,
)


class TestOCRConfig:
    """OCR設定クラスのテスト"""
    
    def test_deepseek_ocr_config_validation(self):
        """DeepSeekOCRConfigの検証が正しく動作することを確認"""
        # 正常な設定
        config = DeepSeekOCRConfig(
            model_path="/test/path",
            model_name="test-model",
            output_format="markdown",
            temperature=0.5,
        )
        assert config.model_name == "test-model"
        assert config.output_format == "markdown"
        
        # 無効な出力形式
        with pytest.raises(ValueError, match="output_format must be"):
            DeepSeekOCRConfig(
                model_path="/test/path",
                output_format="invalid",
            )
        
        # 無効な温度パラメータ
        with pytest.raises(ValueError, match="temperature must be between"):
            DeepSeekOCRConfig(
                model_path="/test/path",
                temperature=3.0,  # 範囲外
            )
    
    def test_load_config_from_file(self):
        """設定ファイルから設定を読み込めることを確認"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir, "ocr_config.yaml")
            config_data = {
                "deepseek_ocr": {
                    "model_path": "/custom/path",
                    "model_name": "custom-model",
                    "vllm_server_url": "http://custom:8000",
                    "max_tokens": 8192,
                    "temperature": 0.2,
                    "output_format": "plain",
                },
                "output": {
                    "base_dir": "/custom/output",
                },
            }
            
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)
            
            config = load_config(str(config_file))
            
            assert config.deepseek_ocr.model_path == "/custom/path"
            assert config.deepseek_ocr.model_name == "custom-model"
            assert config.deepseek_ocr.vllm_server_url == "http://custom:8000"
            assert config.deepseek_ocr.max_tokens == 8192
            assert config.deepseek_ocr.temperature == 0.2
            assert config.deepseek_ocr.output_format == "plain"
            assert config.output.base_dir == "/custom/output"
    
    def test_get_default_config(self):
        """デフォルト設定が正しく取得されることを確認"""
        config = get_default_config()
        
        assert config.deepseek_ocr.model_path is not None
        assert config.deepseek_ocr.model_name == "deepseek-ocr"
        assert config.deepseek_ocr.max_tokens == 4096
        assert config.deepseek_ocr.output_format == "markdown"
    
    def test_get_default_config_from_env(self):
        """環境変数からデフォルト設定が読み込まれることを確認"""
        original_model_path = os.environ.get("DEEPSEEK_OCR_MODEL_PATH")
        original_model_name = os.environ.get("DEEPSEEK_OCR_MODEL_NAME")
        
        try:
            os.environ["DEEPSEEK_OCR_MODEL_PATH"] = "/env/path"
            os.environ["DEEPSEEK_OCR_MODEL_NAME"] = "env-model"
            
            config = get_default_config()
            
            assert config.deepseek_ocr.model_path == "/env/path"
            assert config.deepseek_ocr.model_name == "env-model"
        finally:
            if original_model_path:
                os.environ["DEEPSEEK_OCR_MODEL_PATH"] = original_model_path
            elif "DEEPSEEK_OCR_MODEL_PATH" in os.environ:
                del os.environ["DEEPSEEK_OCR_MODEL_PATH"]
            
            if original_model_name:
                os.environ["DEEPSEEK_OCR_MODEL_NAME"] = original_model_name
            elif "DEEPSEEK_OCR_MODEL_NAME" in os.environ:
                del os.environ["DEEPSEEK_OCR_MODEL_NAME"]

