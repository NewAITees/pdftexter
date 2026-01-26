@echo off
cd /d "%~dp0"
uv run pdftexter %*
if errorlevel 1 pause
