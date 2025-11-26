"""
ファイル操作ユーティリティモジュール
"""

import os
from pathlib import Path
from typing import Optional


def ensure_directory(path: str) -> None:
    """
    ディレクトリが存在しない場合は作成する
    
    Args:
        path: ディレクトリパス
    """
    os.makedirs(path, exist_ok=True)


def get_image_files(directory: str) -> list[str]:
    """
    ディレクトリ内の画像ファイルを取得してソートする
    
    Args:
        directory: 検索するディレクトリパス
        
    Returns:
        ソートされた画像ファイル名のリスト
    """
    image_extensions = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
    files = [
        f for f in os.listdir(directory)
        if f.lower().endswith(image_extensions)
    ]
    files.sort()
    return files


def join_path(*paths: str) -> str:
    """
    パスを結合する（os.path.joinのラッパー）
    
    Args:
        *paths: 結合するパス
        
    Returns:
        結合されたパス
    """
    return os.path.join(*paths)


def get_absolute_path(path: str) -> str:
    """
    絶対パスを取得する
    
    Args:
        path: パス
        
    Returns:
        絶対パス
    """
    return os.path.abspath(path)


def path_exists(path: str) -> bool:
    """
    パスが存在するか確認する
    
    Args:
        path: 確認するパス
        
    Returns:
        存在する場合True
    """
    return os.path.exists(path)


def is_file(path: str) -> bool:
    """
    パスがファイルか確認する
    
    Args:
        path: 確認するパス
        
    Returns:
        ファイルの場合True
    """
    return os.path.isfile(path)


def is_directory(path: str) -> bool:
    """
    パスがディレクトリか確認する
    
    Args:
        path: 確認するパス
        
    Returns:
        ディレクトリの場合True
    """
    return os.path.isdir(path)

