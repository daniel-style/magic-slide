#!/usr/bin/env python3
"""
Check Magic Move text anchors during real slide transitions.

Usage:
    python3 scripts/check-magic-text-wrap.py path/to/index.html
    python3 scripts/check-magic-text-wrap.py http://localhost:8765/deck/foo/index.html

What it checks:
- Hard failure: any explicitly one-line Magic text (`data-magic-line="nowrap"`,
  `.magic-nowrap-phrase`, `data-magic-nowrap="true"`, or label-like anchors)
  wraps during final states or temporary FLIP clone motion.
- Warning: short unmarked Magic text anchors wrap during motion, because they
  are often accidental one-line phrases that should use `.magic-nowrap-phrase`
  / `data-magic-line="nowrap"` or be split into semantic fragments.

The runtime tags temporary clones with `data-ms-magic-clone-id`, so this script
can inspect the animated object, not just the final slide DOM.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


SAMPLE_DELAYS_MS = (80, 180, 320, 560, 820)


def as_url(target: str) -> str:
    if target.startswith(("http://", "https://", "file://")):
        return target
    return Path(target).resolve().as_uri()


CHECK_JS = """
() => {
  const labelSelector = [
    '.deck-mark', '.small-mono', '.kicker', '.section-tag', '.chip', '.tag',
    '.badge', '.pill', '.label', '.eyebrow', '.mini-label', '.small-label',
    '.mini', '.endpoint', '.feature-plate'
  ].join(',');

  function normalizeText(el) {
    return (el.textContent || '').replace(/\\s+/g, ' ').trim();
  }

  function hasTextChild(el) {
    return Array.from(el.children || []).some((child) => normalizeText(child));
  }

  function isVisible(el, cs, box, text) {
    return text
      && cs.display !== 'none'
      && cs.visibility !== 'hidden'
      && Number(cs.opacity || 1) !== 0
      && box.width > 0
      && box.height > 0;
  }

  function isTextLike(el) {
    if (el.querySelector && el.querySelector('img,video,canvas,svg,br')) return false;
    if (hasTextChild(el)) return false;
    const tag = el.tagName;
    if (/^(H1|H2|H3|H4|H5|H6|P|SPAN|STRONG|B|EM|I|SMALL|A|LI|BLOCKQUOTE)$/.test(tag)) return true;
    const cs = getComputedStyle(el);
    const display = (cs.display || '').replace(/\\s+/g, '-');
    return /^(DIV|BUTTON)$/.test(tag) && /^(inline|inline-block|inline-flex|inline-grid)$/.test(display);
  }

  function rectCount(el) {
    const range = document.createRange();
    range.selectNodeContents(el);
    const rects = Array.from(range.getClientRects()).filter((r) => r.width > 0 && r.height > 0);
    range.detach();
    return rects.length;
  }

  function isExplicitNoWrap(el) {
    return el.matches('[data-magic-line="nowrap"], .magic-nowrap-phrase, [data-magic-nowrap="true"], [data-magic-label="true"]')
      || el.matches(labelSelector)
      || !!el.closest(labelSelector);
  }

  function isLikelyShortPhrase(text) {
    const words = text.split(/\\s+/).filter(Boolean).length;
    return text.length <= 42 && words <= 5;
  }

  const rows = [];
  document.querySelectorAll('[data-magic-id], [data-ms-magic-clone-id]').forEach((el, index) => {
    const text = normalizeText(el);
    const cs = getComputedStyle(el);
    const box = el.getBoundingClientRect();
    if (!isVisible(el, cs, box, text) || !isTextLike(el)) return;
    const cloneId = el.getAttribute('data-ms-magic-clone-id') || '';
    const magicId = el.getAttribute('data-magic-id') || cloneId;
    const explicitNoWrap = isExplicitNoWrap(el);
    rows.push({
      index,
      text,
      tag: el.tagName,
      className: el.className || '',
      magicId,
      isClone: !!cloneId,
      explicitNoWrap,
      likelyShortPhrase: isLikelyShortPhrase(text),
      linePolicy: el.getAttribute('data-magic-line') || '',
      whiteSpace: cs.whiteSpace,
      rectCount: rectCount(el),
      width: Math.round(box.width),
      height: Math.round(box.height),
    });
  });
  return rows;
}
"""


def classify(rows: list[dict], label: str) -> tuple[list[str], list[str]]:
    failures = []
    warnings = []
    for row in rows:
        wrapped = row.get("rectCount", 0) > 1
        white_space = row.get("whiteSpace", "")
        if row.get("explicitNoWrap"):
            if "nowrap" not in white_space:
                failures.append(
                    f"{label}: {row['text']!r} ({row['magicId']}) has white-space={white_space!r}"
                )
            if wrapped:
                failures.append(
                    f"{label}: {row['text']!r} ({row['magicId']}) wrapped into {row['rectCount']} rects"
                )
        elif row.get("likelyShortPhrase") and wrapped:
            clone_note = " clone" if row.get("isClone") else ""
            warnings.append(
                f"{label}: short Magic text{clone_note} {row['text']!r} ({row['magicId']}) wrapped into {row['rectCount']} rects; consider data-magic-line=\"nowrap\"/.magic-nowrap-phrase or semantic fragments"
            )
    return failures, warnings


def sample(page, label: str) -> tuple[list[str], list[str]]:
    return classify(page.evaluate(CHECK_JS), label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Deck HTML file path or preview URL")
    parser.add_argument("--timeout", type=int, default=60000)
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Return non-zero if likely short unmarked text anchors wrap.",
    )
    args = parser.parse_args()

    url = as_url(args.target)
    failures: list[str] = []
    warnings: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page.goto(url, wait_until="networkidle", timeout=args.timeout)
        page.wait_for_selector(".slide.active", timeout=args.timeout)

        slide_count = page.evaluate("document.querySelectorAll('.slide').length")
        f, w = sample(page, "slide-1-final")
        failures.extend(f)
        warnings.extend(w)

        for i in range(1, slide_count):
            page.keyboard.press("ArrowRight")
            for delay in SAMPLE_DELAYS_MS:
                page.wait_for_timeout(delay)
                f, w = sample(page, f"slide-{i}-to-{i + 1}")
                failures.extend(f)
                warnings.extend(w)

        for i in range(slide_count, 1, -1):
            page.keyboard.press("ArrowLeft")
            for delay in SAMPLE_DELAYS_MS:
                page.wait_for_timeout(delay)
                f, w = sample(page, f"slide-{i}-to-{i - 1}")
                failures.extend(f)
                warnings.extend(w)

        browser.close()

    if warnings:
        print("Magic text wrap warnings:", file=sys.stderr)
        for warning in sorted(set(warnings)):
            print(f"- {warning}", file=sys.stderr)

    if failures:
        print("Magic text wrap check failed:", file=sys.stderr)
        for failure in sorted(set(failures)):
            print(f"- {failure}", file=sys.stderr)
        return 1

    if args.fail_on_warnings and warnings:
        return 1

    suffix = f" with {len(set(warnings))} warning(s)" if warnings else ""
    print(f"Magic text wrap check passed{suffix}: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
