"""
OCR設定管理モジュール
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class DeepSeekOCRConfig(BaseModel):
    """DeepSeek-OCR設定クラス"""
    
    model_path: str = Field(..., description="DeepSeek-OCRモデルのパス（ローカル推論時）")
    model_name: str = Field("deepseek-ocr", description="vLLM APIで使用するモデル名")
    vllm_server_url: Optional[str] = Field(None, description="vLLMサーバーのURL（Noneの場合はローカル実行）")
    max_tokens: int = Field(4096, description="最大トークン数")
    temperature: float = Field(0.1, description="温度パラメータ")
    output_format: str = Field("markdown", description="出力形式（markdown or plain）")
    timeout: int = Field(300, description="タイムアウト時間（秒）")
    max_retries: int = Field(3, description="最大リトライ回数")
    retry_delay: int = Field(5, description="リトライ間隔（秒）")
    
    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """出力形式の検証"""
        if v not in ["markdown", "plain"]:
            raise ValueError("output_format must be 'markdown' or 'plain'")
        return v
    
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """温度パラメータの検証"""
        if not 0.0 <= v <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        return v


class OutputConfig(BaseModel):
    """出力設定クラス"""
    
    base_dir: str = Field("./output", description="デフォルト出力ディレクトリ")
    images_dir: str = Field("./output/images", description="画像保存先")
    pdfs_dir: str = Field("./output/pdfs", description="PDF保存先")
    texts_dir: str = Field("./output/texts", description="テキスト保存先")


class OCRConfig(BaseModel):
    """OCR設定全体を管理するクラス"""
    
    deepseek_ocr: DeepSeekOCRConfig
    output: OutputConfig


def load_config(config_path: Optional[str] = None) -> OCRConfig:
    """
    OCR設定ファイルを読み込む
    
    Args:
        config_path: 設定ファイルのパス（Noneの場合はデフォルトパスを使用）
        
    Returns:
        OCRConfigオブジェクト
        
    Raises:
        FileNotFoundError: 設定ファイルが見つからない場合
        ValueError: 設定ファイルの形式が不正な場合
    """
    if config_path is None:
        # デフォルトの設定ファイルパス
        default_paths = [
            Path("config/ocr_config.yaml"),
            Path.home() / ".pdftexter" / "ocr_config.yaml",
            Path("/etc/pdftexter/ocr_config.yaml"),
        ]
        
        for path in default_paths:
            if path.exists():
                config_path = str(path)
                break
        
        if config_path is None:
            # デフォルト設定を使用
            return get_default_config()
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")
    
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    if config_data is None:
        raise ValueError("設定ファイルが空です")
    
    try:
        return OCRConfig(**config_data)
    except Exception as e:
        raise ValueError(f"設定ファイルの形式が不正です: {e}")


def get_default_config() -> OCRConfig:
    """
    デフォルト設定を取得する
    
    Returns:
        デフォルト設定のOCRConfigオブジェクト
    """
    return OCRConfig(
        deepseek_ocr=DeepSeekOCRConfig(
            model_path=os.environ.get("DEEPSEEK_OCR_MODEL_PATH", "/path/to/DeepSeek-OCR"),
            model_name=os.environ.get("DEEPSEEK_OCR_MODEL_NAME", "deepseek-ocr"),
            vllm_server_url=os.environ.get("VLLM_SERVER_URL"),
            max_tokens=4096,
            temperature=0.1,
            output_format="markdown",
            timeout=300,
            max_retries=3,
            retry_delay=5,
        ),
        output=OutputConfig(
            base_dir="./output",
            images_dir="./output/images",
            pdfs_dir="./output/pdfs",
            texts_dir="./output/texts",
        ),
    )

