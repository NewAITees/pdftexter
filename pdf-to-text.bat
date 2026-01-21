@echo off
cd /d "%~dp0"
uv run pdf-to-text %*
