#!/usr/bin/env python3
"""
PDF→Text変換スクリプト

DeepSeek-OCRを使用してPDFファイルをテキスト（Markdown）に変換します。
"""

from pdftexter.cli.pdf_to_text import main

if __name__ == "__main__":
    exit(main())

