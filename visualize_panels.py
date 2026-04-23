#!/usr/bin/env python3
"""
Generate charts for each panel listed in pcrf_graph_suggester_output.md.

Outputs:
- charts/*.png  (one file per metric/panel)
- charts/index.md (links + embedded images)

Usage:
  . .venv/bin/activate
  python visualize_panels.py
"""

from __future__ import annotations

import csv
import glob
import os
import re
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta


PANEL_MD_DEFAULT = "pcrf_graph_suggester_output.md"
OUT_DIR_DEFAULT = "charts"
TZ_OFFSET_HOURS_DEFAULT = 5.0
CSV_DIR_DEFAULT = "csv"


@dataclass(frozen=True)
class PanelDef:
    category: str
    column: str
    file_glob: str
    dimension: str
    note: str
    calculated_as: str = ""
    requires: tuple[str, ...] = ()


PANEL_RE = re.compile(
    r"^- `(?P<column>[^`]+)` from `(?P<glob>[^`]+)` grouped by `(?P<dim>[^`]+)`(?P<note>.*)$"
)


def parse_time(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    # Typical: 2026-04-19T16:00:00Z
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def safe_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "panel"


def load_csv_series(
    paths: list[str],
    dimension: str,
    column: str,
    tz_offset_hours: float,
    *,
    calculated_columns: tuple[str, ...] = (),
) -> dict[str, list[tuple[datetime, float]]]:
    out: dict[str, list[tuple[datetime, float]]] = {}
    for path in paths:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue
            if "StartTime" not in reader.fieldnames:
                raise RuntimeError(f"{path} missing StartTime column (needed for time axis)")
            if dimension not in reader.fieldnames:
                raise RuntimeError(f"{path} missing dimension column {dimension}")
            if calculated_columns:
                missing = [c for c in calculated_columns if c not in reader.fieldnames]
                if missing:
                    raise RuntimeError(f"{path} missing metric columns {', '.join(missing)}")
            else:
                if column not in reader.fieldnames:
                    raise RuntimeError(f"{path} missing metric column {column}")

            for row in reader:
                ts = parse_time(row.get("StartTime", ""))
                if ts is None:
                    continue
                # Convert to local time by applying a fixed offset from UTC.
                # We keep the datetime "naive" for matplotlib to avoid timezone
                # surprises and because the offset is fixed by configuration.
                ts = (ts + timedelta(hours=tz_offset_hours)).replace(tzinfo=None)

                dim = (row.get(dimension) or "").strip()
                if not dim:
                    # Some exports include a cluster-total rollup row with empty dimension.
                    # User requested to remove it from charts.
                    continue

                try:
                    if calculated_columns:
                        val = 0.0
                        for c in calculated_columns:
                            raw = (row.get(c) or "").strip()
                            if raw == "":
                                continue
                            val += float(raw)
                    else:
                        raw = (row.get(column) or "").strip()
                        if raw == "":
                            continue
                        val = float(raw)
                except ValueError:
                    # Non-numeric columns are not supported by this renderer.
                    continue

                out.setdefault(dim, []).append((ts, val))

    for dim, points in out.items():
        points.sort(key=lambda x: x[0])
        out[dim] = points
    return out


def parse_panels(md_path: str) -> list[PanelDef]:
    panels: list[PanelDef] = []
    category = "Uncategorized"
    calc_re = re.compile(r"calculated as `(?P<expr>[^`]+)`")
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("### "):
                category = line[4:].strip()
                continue
            m = PANEL_RE.match(line)
            if not m:
                continue
            note = (m.group("note") or "").strip()
            calculated_as = ""
            requires: tuple[str, ...] = ()
            calc_m = calc_re.search(note)
            if calc_m:
                calculated_as = calc_m.group("expr").strip()
                # Only support simple addition: ColA+ColB+ColC
                requires = tuple(p.strip() for p in calculated_as.split("+") if p.strip())
            panels.append(
                PanelDef(
                    category=category,
                    column=m.group("column").strip(),
                    file_glob=m.group("glob").strip(),
                    dimension=m.group("dim").strip(),
                    note=note,
                    calculated_as=calculated_as,
                    requires=requires,
                )
            )
    return panels


def main() -> int:
    import matplotlib

    matplotlib.use("Agg")  # headless
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.ticker as mticker

    md_path = os.environ.get("PANEL_MD", PANEL_MD_DEFAULT)
    out_dir = os.environ.get("OUT_DIR", OUT_DIR_DEFAULT)
    tz_offset_hours = float(os.environ.get("TZ_OFFSET_HOURS", str(TZ_OFFSET_HOURS_DEFAULT)))
    csv_dir = os.environ.get("CSV_DIR", CSV_DIR_DEFAULT)

    if not os.path.exists(md_path):
        raise SystemExit(f"Missing `{md_path}` (set PANEL_MD env var if different)")

    panels = parse_panels(md_path)
    if not panels:
        raise SystemExit(f"No panels found in `{md_path}`")

    os.makedirs(out_dir, exist_ok=True)

    # Build index.md as we go.
    index_lines: list[str] = []
    index_lines.append("# PCRF Charts\n")
    index_lines.append(f"Source panels: `{md_path}`\n")

    current_category: str | None = None
    generated = 0
    skipped = 0

    class MidnightFullDateFormatter(mticker.Formatter):
        def __init__(self, full_fmt: str, time_fmt: str) -> None:
            super().__init__()
            self.full_fmt = full_fmt
            self.time_fmt = time_fmt

        def __call__(self, x: float, pos: int | None = None) -> str:
            dt = mdates.num2date(x).replace(tzinfo=None)
            if dt.hour == 0 and dt.minute == 0:
                return dt.strftime(self.full_fmt)
            return dt.strftime(self.time_fmt)

    for panel in panels:
        if panel.category != current_category:
            current_category = panel.category
            index_lines.append(f"## {current_category}\n")

        matches = sorted(glob.glob(os.path.join(csv_dir, panel.file_glob)))
        if not matches:
            index_lines.append(f"- Skipped: `{panel.column}` (no files match `{panel.file_glob}`)\n")
            skipped += 1
            continue

        try:
            series_by_dim = load_csv_series(
                matches,
                panel.dimension,
                panel.column,
                tz_offset_hours,
                calculated_columns=panel.requires,
            )
        except RuntimeError as e:
            index_lines.append(f"- Skipped: `{panel.column}` ({e})\n")
            skipped += 1
            continue

        if not series_by_dim:
            index_lines.append(f"- Skipped: `{panel.column}` (no numeric data)\n")
            skipped += 1
            continue

        # Plot.
        fig, ax = plt.subplots(figsize=(14, 5))
        for dim, pts in sorted(series_by_dim.items()):
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            ax.plot(xs, ys, label=dim, linewidth=1.2)

        title = f"{panel.category}: {panel.column}"
        if panel.note:
            title += f" {panel.note}"
        ax.set_title(title)
        tz_label = f"UTC{tz_offset_hours:+g}"
        ax.set_xlabel(f"StartTime ({tz_label})")
        ax.set_ylabel(panel.column)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left", ncol=2, fontsize=8, frameon=False)

        # Increase x-axis granularity:
        # - Major labels only at the start of each hour
        # - Minor tick marks every 5 minutes
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(MidnightFullDateFormatter("%Y-%m-%d", "%H:%M"))
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))
        ax.tick_params(axis="x", which="major", labelrotation=30)
        ax.tick_params(axis="x", which="minor", length=3)

        out_name = f"{safe_name(panel.category)}__{safe_name(panel.column)}.png"
        out_path = os.path.join(out_dir, out_name)
        fig.tight_layout()
        fig.savefig(out_path, dpi=150)
        plt.close(fig)

        # index.md lives in out_dir; reference images as if they are in the same folder.
        index_lines.append(f"- `{panel.column}` -> `{out_name}`\n")
        index_lines.append(f"![]({out_name})\n")
        generated += 1

    index_path = os.path.join(out_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines).rstrip() + "\n")

    print(f"Generated {generated} charts in `{out_dir}/` (skipped {skipped}).")
    print(f"Index: `{index_path}`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
