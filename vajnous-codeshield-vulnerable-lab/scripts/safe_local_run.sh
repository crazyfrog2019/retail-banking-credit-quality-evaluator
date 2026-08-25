#!/usr/bin/env bash
set -euo pipefail

echo "WARNING: This repository is intentionally vulnerable."
echo "Run only on a disposable/local lab machine."
echo "The Flask app binds to 127.0.0.1 only."
python app.py
