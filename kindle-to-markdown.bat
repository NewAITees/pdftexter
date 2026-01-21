@echo off
cd /d "%~dp0"
uv run pdftexter kindle-to-markdown %*
