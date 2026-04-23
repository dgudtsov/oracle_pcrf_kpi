#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -d ".venv" ]]; then
  echo "Missing .venv. Create it first (python3 -m venv .venv) and install deps."
  exit 1
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"

export TZ_OFFSET_HOURS="${TZ_OFFSET_HOURS:-5}"
export PAGE_CONTENT_WIDTH_CM="${PAGE_CONTENT_WIDTH_CM:-17.0}"

python visualize_panels.py
python md_to_odt.py

echo "Done."
echo "Markdown index: charts/index.md"
echo "ODT report:     charts/charts_report.odt"

