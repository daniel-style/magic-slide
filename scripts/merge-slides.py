#!/usr/bin/env python3
"""
merge-slides.py — Assemble Magic Slide HTML from modular source files.

Usage:
    python3 merge-slides.py <sources-dir> [--output <path>] [--lang <code>]

Arguments:
    <sources-dir>  Directory containing style.css + slide-*.html files
    --output       Output HTML path (default: <sources-dir>/../index.html)
    --lang         HTML lang attribute (default: en)

Expected structure:
    <sources-dir>/
      style.css
      slide-01.html
      slide-02.html
      ...

Output:
    Complete HTML file with DOCTYPE, <head>, <style>, <body>, <div id="deck">,
    and all slides assembled in filename sort order.
"""

import sys
import argparse
import re
from pathlib import Path


def normalize_fragment_asset_paths(fragment: str, sources_dir: Path, output_path: Path) -> str:
    """
    Slide fragments are authored under `sources/`, but the merged HTML lives one
    directory above by default. If a fragment uses ../foo.png, that path becomes
    invalid after merge. Normalize that common case during assembly.
    """
    if output_path.parent != sources_dir.parent:
        return fragment

    def _rewrite_attr(match: re.Match) -> str:
        prefix, quote, value, suffix = match.groups()
        if value.startswith("../"):
            return f'{prefix}{quote}./{value[3:]}{suffix}'
        return match.group(0)

    def _rewrite_url(match: re.Match) -> str:
        quote = match.group(1) or ""
        value = match.group(2)
        if value.startswith("../"):
            return f"url({quote}./{value[3:]}{quote})"
        return match.group(0)

    fragment = re.sub(r'((?:src|href)=)(["\'])([^"\']+)(["\'])', _rewrite_attr, fragment)
    fragment = re.sub(r'url\((["\']?)([^)"\']+)\1\)', _rewrite_url, fragment)
    return fragment


SVG_STROKE_HINT_RE = re.compile(
    r'\b(route|connector|edge|line|flow|arc|curve|rail|trace|arrow|link)\b',
    re.IGNORECASE,
)


def _tag_has_attr(tag: str, attr: str) -> bool:
    return re.search(r'\s' + re.escape(attr) + r'\s*=', tag, re.IGNORECASE) is not None


def _tag_attr(tag: str, attr: str) -> str:
    match = re.search(
        r'\s' + re.escape(attr) + r'\s*=\s*(["\'])(.*?)\1',
        tag,
        re.IGNORECASE | re.DOTALL,
    )
    return match.group(2) if match else ""


def _append_attrs(tag: str, attrs) -> str:
    if not attrs:
        return tag
    suffix = " " + " ".join(f'{name}="{value}"' for name, value in attrs)
    if tag.endswith("/>"):
        return tag[:-2].rstrip() + suffix + " />"
    return tag[:-1].rstrip() + suffix + ">"


def _harden_svg_stroke_tag(match: re.Match) -> str:
    tag = match.group(0)
    tag_name = re.match(r'<\s*([a-zA-Z0-9:-]+)', tag).group(1).lower()
    css_class = _tag_attr(tag, "class")
    d_attr = _tag_attr(tag, "d")
    hinted = bool(SVG_STROKE_HINT_RE.search(css_class))
    open_path = tag_name in {"line", "polyline"} or (
        tag_name == "path" and (not d_attr or not re.search(r'[zZ]\s*$', d_attr.strip()))
    )
    should_harden = hinted or open_path
    if not should_harden:
        return tag

    additions = []
    if tag_name in {"path", "line", "polyline"} and not _tag_has_attr(tag, "fill"):
        additions.append(("fill", "none"))
    if not _tag_has_attr(tag, "stroke") and "stroke:" not in _tag_attr(tag, "style").lower():
        additions.append(("stroke", "currentColor"))
    if not _tag_has_attr(tag, "stroke-width") and "stroke-width:" not in _tag_attr(tag, "style").lower():
        additions.append(("stroke-width", "2"))
    if not _tag_has_attr(tag, "stroke-linecap"):
        additions.append(("stroke-linecap", "round"))
    if not _tag_has_attr(tag, "stroke-linejoin"):
        additions.append(("stroke-linejoin", "round"))
    return _append_attrs(tag, additions)


def harden_inline_svg(fragment: str) -> str:
    """Add fallback presentation attrs to SVG connector paths.

    Open SVG paths default to black fill when CSS is unavailable or scoped
    differently in preview/clone contexts. Adding attributes keeps generated
    diagrams from becoming black blobs while still allowing CSS classes to
    override stroke color and width.
    """

    def _harden_svg_block(match: re.Match) -> str:
        block = match.group(0)
        return re.sub(
            r'<(?:path|line|polyline)\b[^>]*>',
            _harden_svg_stroke_tag,
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )

    return re.sub(r'<svg\b[\s\S]*?</svg>', _harden_svg_block, fragment, flags=re.IGNORECASE)


def main():
    parser = argparse.ArgumentParser(description='Merge modular slide sources into HTML')
    parser.add_argument('sources_dir', help='Directory containing style.css + slide-*.html files')
    parser.add_argument('--output', help='Output HTML path (default: <sources-dir>/../index.html)')
    parser.add_argument('--lang', default='en', help='HTML lang attribute (default: en)')
    args = parser.parse_args()

    sources_dir = Path(args.sources_dir).resolve()
    if not sources_dir.is_dir():
        print(f"Error: Directory not found: {sources_dir}", file=sys.stderr)
        sys.exit(1)

    # Read style.css
    style_path = sources_dir / 'style.css'
    if not style_path.exists():
        print(f"Error: style.css not found: {style_path}", file=sys.stderr)
        sys.exit(1)

    css_content = style_path.read_text(encoding='utf-8')

    # Read all slide-*.html files (sorted)
    slide_files = sorted(sources_dir.glob('slide-*.html'))
    if not slide_files:
        print(f"Error: No slide-*.html files found in {sources_dir}", file=sys.stderr)
        sys.exit(1)

    # Check for numbering gaps
    expected = set()
    actual = set()
    for f in slide_files:
        num_str = f.stem.replace('slide-', '')
        try:
            actual.add(int(num_str))
        except ValueError:
            pass
    if actual:
        expected = set(range(min(actual), max(actual) + 1))
        missing = expected - actual
        if missing:
            print(f"Warning: Slide numbering gaps — missing: {sorted(missing)}", file=sys.stderr)

    slides_html = []

    for slide_file in slide_files:
        content = slide_file.read_text(encoding='utf-8').strip()
        if not content.startswith('<section'):
            print(f"Warning: {slide_file.name} does not start with <section> tag", file=sys.stderr)
        slides_html.append(content)

    # Determine output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        # Default: parent directory / index.html
        topic_dir = sources_dir.parent
        output_path = topic_dir / "index.html"

    slides_html = [
        harden_inline_svg(normalize_fragment_asset_paths(content, sources_dir, output_path))
        for content in slides_html
    ]

    # Generate complete HTML
    html = assemble(css=css_content, slides=slides_html, lang=args.lang)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Merged {len(slides_html)} slides → {output_path}")


def assemble(css: str, slides: list, lang: str) -> str:
    """Generate complete HTML document from CSS and slide fragments."""
    slides_joined = '\n'.join(slides)

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
{css}
  </style>
</head>
<body>
  <div id="deck">
{slides_joined}
  </div>
</body>
</html>
'''


if __name__ == '__main__':
    main()
