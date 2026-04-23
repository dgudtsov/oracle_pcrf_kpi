#!/usr/bin/env python3
"""
Create an .odt document from charts/index.md with all referenced PNGs embedded.

Defaults (override via env vars):
- INDEX_MD: charts/index.md
- ODT_OUT:  charts/charts_report_%Y%m%d_%H%M.odt

Usage:
  . .venv/bin/activate
  python md_to_odt.py
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import struct


INDEX_MD_DEFAULT = Path("charts/index.md")
ODT_OUT_STEM_DEFAULT = "charts_report"
PAGE_CONTENT_WIDTH_CM_DEFAULT = 17.0


@dataclass(frozen=True)
class Block:
    kind: str  # title, h2, toc_h2, metric, image, text
    text: str
    target: str = ""


TITLE_RE = re.compile(r"^#\s+(?P<t>.+?)\s*$")
H2_RE = re.compile(r"^##\s+(?P<t>.+?)\s*$")
METRIC_RE = re.compile(r"^- `(?P<m>[^`]+)` -> `(?P<p>[^`]+)`\s*$")
IMAGE_RE = re.compile(r"^!\[[^\]]*\]\((?P<p>[^)]+)\)\s*$")


def parse_index_md(md_path: Path) -> list[Block]:
    blocks: list[Block] = []
    for raw in md_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        m = TITLE_RE.match(line)
        if m:
            blocks.append(Block("title", m.group("t")))
            continue
        m = H2_RE.match(line)
        if m:
            blocks.append(Block("h2", m.group("t")))
            continue
        m = METRIC_RE.match(line)
        if m:
            blocks.append(Block("metric", f"{m.group('m')}  ({m.group('p')})"))
            continue
        m = IMAGE_RE.match(line)
        if m:
            blocks.append(Block("image", m.group("p")))
            continue
        blocks.append(Block("text", line))
    return blocks


def default_out_path(now: datetime | None = None) -> Path:
    now = now or datetime.now()
    suffix = now.strftime("_%Y%m%d_%H%M")
    return Path("charts") / f"{ODT_OUT_STEM_DEFAULT}{suffix}.odt"


def safe_anchor(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "section"


def unique_anchor_name(used: set[str], title: str) -> str:
    base = safe_anchor(title)
    name = base
    i = 2
    while name in used:
        name = f"{base}_{i}"
        i += 1
    used.add(name)
    return name


def with_standard_contents(blocks: list[Block]) -> list[Block]:
    """
    Adds a simple "Contents" section at the beginning of the document.

    Per request, the contents consists of level-2 headers (h2), so it is
    implemented as duplicated H2 headings up-front, linking to each section.
    """

    h2_titles: list[str] = []
    seen_titles: set[str] = set()
    for blk in blocks:
        if blk.kind != "h2":
            continue
        title = blk.text.strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        h2_titles.append(title)

    if not h2_titles:
        return blocks

    used_anchors: set[str] = set()
    anchors_by_title: dict[str, str] = {t: unique_anchor_name(used_anchors, t) for t in h2_titles}

    # Attach anchors to the "real" section headings.
    anchored_blocks: list[Block] = []
    for blk in blocks:
        if blk.kind == "h2":
            title = blk.text.strip()
            anchor = anchors_by_title.get(title, "")
            anchored_blocks.append(Block("h2", blk.text, target=anchor))
        else:
            anchored_blocks.append(blk)

    out: list[Block] = []
    inserted = False
    for blk in anchored_blocks:
        out.append(blk)
        if not inserted and blk.kind == "title":
            out.append(Block("h2", "Contents"))
            for t in h2_titles:
                out.append(Block("toc_h2", t, target=anchors_by_title[t]))
            inserted = True

    if not inserted:
        # No title found: still prepend contents.
        out = [
            Block("h2", "Contents"),
            *(Block("toc_h2", t, target=anchors_by_title[t]) for t in h2_titles),
            *anchored_blocks,
        ]

    return out


def resolve_image(md_path: Path, img_ref: str) -> Path:
    rel = Path(img_ref)
    if rel.is_absolute():
        return rel.resolve()

    # index.md lives in charts/, but it references images as charts/foo.png.
    base_dir = md_path.parent
    root_dir = base_dir.parent
    candidates = [
        base_dir / rel,
        root_dir / rel,
        rel,
    ]
    chosen = next((p for p in candidates if p.exists()), candidates[0])
    return chosen.resolve()


def unique_picture_name(used: set[str], img_path: Path) -> str:
    base = img_path.name
    name = base
    i = 1
    while name in used:
        name = f"{img_path.stem}__{i}{img_path.suffix}"
        i += 1
    used.add(name)
    return name


def read_png_dimensions_and_dpi(path: Path) -> tuple[int, int, float, float]:
    """
    Returns (width_px, height_px, dpi_x, dpi_y).
    If DPI is not present in the PNG, defaults to 96 DPI.
    """

    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG file: {path}")

    width_px: int | None = None
    height_px: int | None = None
    dpi_x = 96.0
    dpi_y = 96.0

    offset = 8
    while offset + 12 <= len(data):
        (length,) = struct.unpack(">I", data[offset : offset + 4])
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        offset = offset + 12 + length  # length+type+data+crc

        if chunk_type == b"IHDR":
            if length < 8:
                raise ValueError(f"Corrupt IHDR in {path}")
            width_px, height_px = struct.unpack(">II", chunk_data[:8])
        elif chunk_type == b"pHYs":
            # pixels per unit (meter) + unit specifier
            if length >= 9:
                x_ppu, y_ppu, unit = struct.unpack(">IIB", chunk_data[:9])
                if unit == 1 and x_ppu > 0 and y_ppu > 0:
                    # 1 inch = 0.0254 meters
                    dpi_x = x_ppu * 0.0254
                    dpi_y = y_ppu * 0.0254
        elif chunk_type == b"IEND":
            break

    if width_px is None or height_px is None:
        raise ValueError(f"Missing IHDR in {path}")

    return width_px, height_px, dpi_x, dpi_y


def main() -> int:
    from odf.opendocument import OpenDocumentText
    from odf import draw, style, text

    md_path = Path(os.environ.get("INDEX_MD", str(INDEX_MD_DEFAULT)))
    out_path_env = os.environ.get("ODT_OUT")
    out_path = Path(out_path_env) if out_path_env else default_out_path()
    page_content_width_cm = float(
        os.environ.get("PAGE_CONTENT_WIDTH_CM", str(PAGE_CONTENT_WIDTH_CM_DEFAULT))
    )

    if not md_path.exists():
        raise SystemExit(f"Missing `{md_path}` (set INDEX_MD if different)")

    blocks = parse_index_md(md_path)
    if not blocks:
        raise SystemExit(f"No content found in `{md_path}`")

    blocks = with_standard_contents(blocks)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = OpenDocumentText()

    # Paragraph styles
    title_style = style.Style(name="Title", family="paragraph")
    title_style.addElement(style.TextProperties(attributes={"fontsize": "18pt", "fontweight": "bold"}))
    doc.styles.addElement(title_style)

    h2_style = style.Style(name="H2", family="paragraph")
    h2_style.addElement(style.TextProperties(attributes={"fontsize": "14pt", "fontweight": "bold"}))
    doc.styles.addElement(h2_style)

    h2_page_style = style.Style(name="H2Page", family="paragraph")
    h2_page_style.addElement(style.TextProperties(attributes={"fontsize": "14pt", "fontweight": "bold"}))
    h2_page_style.addElement(style.ParagraphProperties(attributes={"breakbefore": "page"}))
    doc.styles.addElement(h2_page_style)

    metric_style = style.Style(name="Metric", family="paragraph")
    metric_style.addElement(style.TextProperties(attributes={"fontsize": "11pt", "fontweight": "bold"}))
    doc.styles.addElement(metric_style)

    body_style = style.Style(name="Body", family="paragraph")
    body_style.addElement(style.TextProperties(attributes={"fontsize": "11pt"}))
    doc.styles.addElement(body_style)

    # Image style
    img_style = style.Style(name="ImgFrame", family="graphic")
    img_style.addElement(
        style.GraphicProperties(
            attributes={
                "wrap": "none",
                "horizontalpos": "center",
                "horizontalrel": "paragraph",
                "verticalpos": "top",
                "verticalrel": "paragraph",
            }
        )
    )
    doc.automaticstyles.addElement(img_style)

    used_picture_names: set[str] = set()

    for blk in blocks:
        if blk.kind == "title":
            doc.text.addElement(text.P(text=blk.text, stylename=title_style))
            continue
        if blk.kind == "h2":
            stylename = h2_page_style if blk.target else h2_style
            h = text.H(stylename=stylename, outlinelevel=2)
            if blk.target:
                h.addElement(text.BookmarkStart(name=blk.target))
            h.addText(blk.text)
            if blk.target:
                h.addElement(text.BookmarkEnd(name=blk.target))
            doc.text.addElement(h)
            continue
        if blk.kind == "toc_h2":
            h = text.H(stylename=h2_style, outlinelevel=2)
            a = text.A(href=f"#{blk.target}", type="simple")
            a.addText(blk.text)
            h.addElement(a)
            doc.text.addElement(h)
            continue
        if blk.kind == "metric":
            doc.text.addElement(text.P(text=blk.text, stylename=metric_style))
            continue
        if blk.kind == "text":
            doc.text.addElement(text.P(text=blk.text, stylename=body_style))
            continue
        if blk.kind == "image":
            img_path = resolve_image(md_path, blk.text)
            if not img_path.exists():
                doc.text.addElement(text.P(text=f"[missing image] {blk.text}", stylename=body_style))
                continue
            if img_path.suffix.lower() != ".png":
                doc.text.addElement(text.P(text=f"[skipped non-png image] {blk.text}", stylename=body_style))
                continue

            pic_name = unique_picture_name(used_picture_names, img_path)
            href = doc.addPicture(
                f"Pictures/{pic_name}",
                mediatype="image/png",
                content=img_path.read_bytes(),
            )

            # Fit images to page width (content width), preserve aspect ratio.
            w_px, h_px, _dpi_x, _dpi_y = read_png_dimensions_and_dpi(img_path)
            w_cm = page_content_width_cm
            h_cm = (w_cm * h_px) / w_px if w_px else w_cm
            frame = draw.Frame(
                stylename=img_style,
                anchortype="paragraph",
                width=f"{w_cm:.3f}cm",
                height=f"{h_cm:.3f}cm",
            )
            frame.addElement(draw.Image(href=href, type="simple", show="embed", actuate="onLoad"))
            p = text.P(stylename=body_style)
            p.addElement(frame)
            doc.text.addElement(p)
            continue

    doc.save(str(out_path))
    print(f"Wrote `{out_path}`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
