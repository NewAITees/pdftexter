@echo off
cd /d "%~dp0"
uv run pdf-to-text %*
if errorlevel 1 pause
