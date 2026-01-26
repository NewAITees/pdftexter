# Repository Guidelines

## Project Structure & Module Organization
- Core code lives in `src/pdftexter/` with subpackages `kindle/` (capture), `pdf/` (conversion), `ocr/` (DeepSeek OCR glue), `utils/` (shared helpers), and `cli/` (CLI entrypoints). Scripts in `scripts/` wrap the same workflows. Tests mirror modules under `tests/`, and docs sit in `docs/`. Generated artifacts belong in `output/` and should stay untracked.

## Build, Test, and Development Commands
- Install deps: `uv sync --dev` (Python 3.12+; pyproject targets 3.13).
- Run Kindle capture/PDF creation: `uv run python scripts/kindle_screenshot.py` then `uv run python scripts/kindle_pdf_convert.py`.
- Run OCR: `uv run python scripts/pdf_to_text.py --input input.pdf --output output.md`.
- Lint/format: `uv run black src tests` and `uv run isort src tests`.
- Type check: `uv run mypy src`.
- Tests: `uv run pytest`.

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints mandatory on public functions, and concise docstrings for modules/classes/functions. Prefer pure functions in `utils/`; keep side effects in CLI/scripts.
- Naming: `snake_case` for modules/functions/variables, `PascalCase` for classes, `SCREAMING_SNAKE_CASE` for constants. File names should reflect the main class or purpose (e.g., `converter.py`, `deepseek.py`).
- Formatting: run `black` and `isort` before pushes; keep imports ordered with stdlib/third-party/local blocks. Avoid committing generated PDFs/images/markdown in `output/`.

## Testing Guidelines
- Framework: `pytest`. Place tests alongside feature areas (e.g., `tests/test_pdf/test_converter.py`), name files `test_*.py`, and keep descriptive test function names (`test_converts_sorted_images`). Use fixtures/fakes instead of real Kindle/PDF files when possible; store small assets in `tests/data/` if needed.
- Quick scopes: `uv run pytest tests/test_ocr -k markdown` for selective runs. Add regression tests when fixing bugs, especially around ordering of images, OCR options, and GUI interactions.

## Commit & Pull Request Guidelines
- Commits: imperative mood, concise subject (`Fix OCR timeout handling`); group related changes and keep noise out. Include brief body when behavior changes or config defaults shift (e.g., `ocr_config.yaml` keys).
- Pull requests: include summary, repro steps, and expected/actual results. Link issues/tasks, add before/after screenshots for GUI changes, and note any manual steps (new config keys, external model downloads). Confirm `black`, `isort`, `mypy`, and `pytest` are clean before requesting review.

## Security & Configuration Tips
- Secrets/paths: never commit credentials, model paths, or proprietary PDFs/images. Keep local overrides in untracked files and avoid embedding absolute paths in code.
- Config: adjust OCR settings in `config/ocr_config.yaml`; validate new options with `uv run mypy src/pdftexter/ocr` and targeted tests before shipping. Document any required environment variables in PRs.
