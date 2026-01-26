@echo off
cd /d "%~dp0"
uv run pdftexter kindle-to-markdown %*
if errorlevel 1 pause
