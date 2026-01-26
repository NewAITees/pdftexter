#!/bin/bash
cd "$(dirname "$0")"
uv run pdf-to-text "$@"
