@echo off
cd /d "%~dp0"
uv run kindle-screenshot %*
if errorlevel 1 pause
