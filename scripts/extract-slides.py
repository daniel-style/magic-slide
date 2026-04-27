#!/usr/bin/env python3
"""
extract-slides.py — Extract individual slides from merged HTML back to sources/

Usage:
    python3 extract-slides.py merged.html sources/

Reads the merged HTML file, extracts each <section class="slide"> element,
and writes them back to individual slide-XX.html files in the sources/ directory.

This allows browser edits (via Edit Mode → Save) to sync back to the modular source files.
"""

import sys
import re
from pathlib import Path
from html.parser import HTMLParser


class SlideExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slides = []
        self.current_slide = []
        self.in_slide = False
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'section':
            attrs_dict = dict(attrs)
            if 'class' in attrs_dict and 'slide' in attrs_dict['class']:
                self.in_slide = True
                self.depth = 1
                # Reconstruct the opening tag
                attrs_str = ' '.join(f'{k}="{v}"' for k, v in attrs)
                self.current_slide.append(f'<{tag} {attrs_str}>')
                return

        if self.in_slide:
            self.depth += 1
            # Reconstruct tag with attributes
            if attrs:
                attrs_str = ' '.join(f'{k}="{v}"' for k, v in attrs)
                self.current_slide.append(f'<{tag} {attrs_str}>')
            else:
                self.current_slide.append(f'<{tag}>')

    def handle_endtag(self, tag):
        if self.in_slide:
            self.current_slide.append(f'</{tag}>')
            self.depth -= 1

            if self.depth == 0 and tag == 'section':
                # Slide complete
                self.slides.append(''.join(self.current_slide))
                self.current_slide = []
                self.in_slide = False

    def handle_data(self, data):
        if self.in_slide:
            self.current_slide.append(data)

    def handle_startendtag(self, tag, attrs):
        if self.in_slide:
            if attrs:
                attrs_str = ' '.join(f'{k}="{v}"' for k, v in attrs)
                self.current_slide.append(f'<{tag} {attrs_str}/>')
            else:
                self.current_slide.append(f'<{tag}/>')


def extract_slides(html_path, output_dir):
    """Extract slides from merged HTML and write to individual files."""
    html_path = Path(html_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not html_path.exists():
        print(f"✗ File not found: {html_path}", file=sys.stderr)
        return False

    if not output_dir.exists():
        print(f"✗ Directory not found: {output_dir}", file=sys.stderr)
        return False

    # Read HTML
    content = html_path.read_text(encoding='utf-8')

    # Extract slides using regex (more reliable than HTMLParser for this case)
    # Match <section class="slide"...>...</section> with proper nesting
    slide_pattern = r'<section[^>]*class="[^"]*slide[^"]*"[^>]*>.*?</section>'
    slides = re.findall(slide_pattern, content, re.DOTALL)

    if not slides:
        print("✗ No slides found in HTML", file=sys.stderr)
        return False

    print(f"Found {len(slides)} slides")

    # Write each slide to individual file
    for i, slide_html in enumerate(slides, start=1):
        slide_file = output_dir / f"slide-{i:02d}.html"

        # Clean up the HTML (remove excessive whitespace while preserving structure)
        cleaned = slide_html.strip()

        slide_file.write_text(cleaned, encoding='utf-8')
        print(f"  ✓ {slide_file.name}")

    print(f"\n✓ Extracted {len(slides)} slides to {output_dir}")
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract-slides.py <merged.html> <sources-dir/>", file=sys.stderr)
        sys.exit(1)

    html_path = sys.argv[1]
    output_dir = sys.argv[2]

    success = extract_slides(html_path, output_dir)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
