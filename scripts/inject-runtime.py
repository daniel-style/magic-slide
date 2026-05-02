#!/usr/bin/env python3
"""
inject-runtime.py — Post-process Magic Slide HTML to add common CSS,
progress bar, counter, Lucide CDN, FLIP engine, and keyboard/click navigation.

Usage:
    python3 inject-runtime.py presentation.html [--lang <language>]

    --lang   UI language for injected strings (default: zh).
             Examples: "zh", "en", "ja", "fr", "de", "ko"

The AI only needs to generate:
  1. <style> block with :root CSS variables (+ any presentation-specific overrides)
  2. <div id="deck"> with all <section class="slide"> elements
  3. Standard HTML boilerplate (DOCTYPE, head, body)

This script injects everything else.
"""

import re
import sys
import subprocess
import tempfile
import os

# ── UI string localizations ────────────────────────────────────────────────
UI_STRINGS = {
    'zh': {
        'save':          '保存 HTML',
        'saving':        '处理中…',
        'saved':         '✓ 已保存',
        'close':         '关闭预览',
        'closing':       '保存中…',
        'toast_saved':   '✓ 已保存',
        'toast_closing': '✓ 已保存到 {name}，服务器即将关闭…',
        'toast_no_server': '⚠️ 未连接服务器，请手动保存',
        'done_title':    '✓ 幻灯片已保存',
        'done_file':     '文件：{name}',
        'done_hint':     '预览服务器已关闭，可以关闭此标签页',
        'edit':          '编辑模式',
        'editing':       '✓ 编辑中',
        'unsaved':       '● 未保存',
        'loading_preview': '载入预览中…',
    },
    'en': {
        'save':          'Save HTML',
        'saving':        'Processing…',
        'saved':         '✓ Saved',
        'close':         'Close Preview',
        'closing':       'Saving…',
        'toast_saved':   '✓ Saved',
        'toast_closing': '✓ Saved to {name}, shutting down…',
        'toast_no_server': '⚠️ No server connection — please download manually',
        'done_title':    '✓ Presentation saved',
        'done_file':     'File: {name}',
        'done_hint':     'Preview server stopped. You can close this tab.',
        'edit':          'Edit Mode',
        'editing':       '✓ Editing',
        'unsaved':       '● Unsaved',
        'loading_preview': 'Loading preview…',
    },
}

def get_ui(lang: str) -> dict:
    """Return UI strings for the given language, falling back to English."""
    key = lang.lower()[:2] if lang else 'zh'
    return UI_STRINGS.get(key, UI_STRINGS['en'])


def strip(html: str) -> str:
    """Remove all previously injected runtime from HTML."""
    h = html
    # Remove injected CSS block (handles multiple accumulated copies)
    h = re.sub(r'\n?/\* === injected by inject-runtime\.py === \*/.*?/\* === end injected CSS === \*/\n?', '', h, flags=re.DOTALL)
    # Remove Lucide CDN tag
    h = re.sub(r'<script src="https://unpkg\.com/lucide@[^"]*"></script>\n?', '', h)
    # Remove complex injected blocks as whole regions. These contain nested
    # controls, so a generic "first closing tag" regex leaves button fragments
    # behind on reinjection.
    h = re.sub(
        r'<div id="dock-hover-preview"[\s\S]*?(?=<button id="nav-prev"|<div id="slide-overview"|<div id="ms-toolbar"|<script>|</body>)',
        '',
        h,
        flags=re.DOTALL
    )
    h = re.sub(
        r'<div id="slide-overview"[\s\S]*?(?=<div id="ms-toolbar"|<div id="ms-rich-toolbar"|<div id="ms-toast"|<script>|</body>)',
        '',
        h,
        flags=re.DOTALL
    )
    h = re.sub(
        r'<div id="qa-overview"[\s\S]*?(?=<div id="ms-toolbar"|<div id="ms-rich-toolbar"|<div id="ms-toast"|<script>|</body>)',
        '',
        h,
        flags=re.DOTALL
    )
    h = re.sub(
        r'<div id="ms-toolbar"[\s\S]*?(?=<div id="ms-rich-toolbar"|<div id="ms-toast"|<script>|</body>)',
        '',
        h,
        flags=re.DOTALL
    )
    h = re.sub(
        r'<div id="ms-rich-toolbar"[\s\S]*?(?=<div id="ms-toast"|<script>|</body>)',
        '',
        h,
        flags=re.DOTALL
    )
    # Remove any injected elements by ID — use a generic tag pattern to handle
    # whatever the browser serializes (div, button, label, etc.)
    for el_id in ['ms-toolbar', 'ms-deck-badge', 'ms-rich-toolbar', 'ms-toast', 'ms-cursor', 'ms-cursor-trail-\\d+', 'ms-save-btn', 'ms-edit-btn', 'ms-close-btn',
                  'progress', 'counter', 'slide-dock', 'dock-tip', 'dock-hover-preview', 'nav-prev', 'nav-next', 'qa-overview']:
        # Block elements with matching id (greedy within the element)
        h = re.sub(r'<[a-z]+[^>]*\bid="' + el_id + r'"[^>]*>.*?</[a-z]+>\n?', '', h, flags=re.DOTALL)
        # Self-closing elements
        h = re.sub(r'<[a-z]+[^>]*\bid="' + el_id + r'"[^>]*/>\n?', '', h)
    # Remove runtime script block (handles old and current formats).
    h = re.sub(
        r'<script>\n(?:var MS_UI=.*?;\n)?(?:document\.body\.classList\.remove\([\'"]ms-edit-mode[\'"]\);|var slides=document\.querySelectorAll).*?</script>\n?',
        '',
        h,
        flags=re.DOTALL
    )
    # Strip source-generated animation classes (animate-*, delay-*) — the runtime
    # stagger system is the single source of truth for entrance animations.
    # Leaving these causes double-animation: source CSS fires first, then stagger fires again.
    # Use a loop to remove all occurrences within class attributes
    while True:
        new_h = re.sub(r'(class="[^"]*?)\s*\b(?:animate-[\w-]+|delay-\d+)\b\s*([^"]*?")', r'\1 \2', h)
        if new_h == h:
            break
        h = new_h
    # Clean up leftover empty class attributes or double spaces in class values
    h = re.sub(r' class="(\s*)"', '', h)
    h = re.sub(r' class="([^"]*?)\s{2,}([^"]*?)"', r' class="\1 \2"', h)  # collapse multiple spaces
    h = re.sub(r' class="\s+([^"]*?)"', r' class="\1"', h)  # leading spaces
    h = re.sub(r' class="([^"]*?)\s+"', r' class="\1"', h)  # trailing spaces
    return h


def sanitize_editor_state(html: str) -> str:
    """Remove any persisted edit-mode state before reinjecting runtime."""
    h = html
    h = re.sub(r'\scontenteditable="(?:true|false)"', '', h)

    def _clean_body_class(match):
        before = match.group(1) or ''
        classes = match.group(2).split()
        after = match.group(3) or ''
        kept = [cls for cls in classes if cls != 'ms-edit-mode']
        if kept:
            return f'<body{before} class="{" ".join(kept)}"{after}>'
        return f'<body{before}{after}>'

    h = re.sub(r'<body([^>]*) class="([^"]*)"([^>]*)>', _clean_body_class, h, flags=re.IGNORECASE)
    return h


def normalize_slide_stagger(html: str) -> str:
    """Keep source decks from accidentally disabling runtime stagger effects."""

    def _normalize(match):
        tag = match.group(0)
        disabled = re.search(
            r'\bdata-stagger-disabled=(["\'])true\1',
            tag,
            flags=re.IGNORECASE,
        )
        if disabled:
            return tag
        if re.search(r'\bdata-stagger=(["\'])none\1', tag, flags=re.IGNORECASE):
            return re.sub(
                r'\bdata-stagger=(["\'])none\1',
                'data-stagger="cascade"',
                tag,
                count=1,
                flags=re.IGNORECASE,
            )
        if not re.search(r'\bdata-stagger=', tag, flags=re.IGNORECASE):
            return re.sub(r'\s*/?>$', ' data-stagger="cascade">', tag, count=1)
        return tag

    return re.sub(
        r'<section\b(?=[^>]*\bclass=(["\'])[^"\']*\bslide\b[^"\']*\1)[^>]*>',
        _normalize,
        html,
        flags=re.IGNORECASE,
    )


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

    style_attr = _tag_attr(tag, "style").lower()
    additions = []
    if tag_name in {"path", "line", "polyline"} and not _tag_has_attr(tag, "fill"):
        additions.append(("fill", "none"))
    if not _tag_has_attr(tag, "stroke") and "stroke:" not in style_attr:
        additions.append(("stroke", "currentColor"))
    if not _tag_has_attr(tag, "stroke-width") and "stroke-width:" not in style_attr:
        additions.append(("stroke-width", "2"))
    if not _tag_has_attr(tag, "stroke-linecap"):
        additions.append(("stroke-linecap", "round"))
    if not _tag_has_attr(tag, "stroke-linejoin"):
        additions.append(("stroke-linejoin", "round"))
    return _append_attrs(tag, additions)


def harden_inline_svg(html: str) -> str:
    """Add fallback presentation attrs to SVG connector paths."""

    def _harden_svg_block(match: re.Match) -> str:
        block = match.group(0)
        return re.sub(
            r'<(?:path|line|polyline)\b[^>]*>',
            _harden_svg_stroke_tag,
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )

    return re.sub(r'<svg\b[\s\S]*?</svg>', _harden_svg_block, html, flags=re.IGNORECASE)

# ── Common CSS (inserted before </style>) ─────────────────────────────────
# Only functional CSS — visual styling is handled by the generated design system
COMMON_CSS = """
/* === injected by inject-runtime.py === */
/* Reset & Base — fallback values ensure text is always visible even if generated
   uses non-standard CSS variable names (e.g. --text-primary instead of --text) */
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
body{background-color:var(--bg, var(--field, #0a0c16));color:var(--text, var(--ink, var(--fg, var(--foreground, #e8eaf0))));font-family:var(--font-body, system-ui, -apple-system, sans-serif);overflow:hidden;user-select:none;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none}
#deck{position:relative;width:100vw;height:100vh;overflow:hidden}

/* Slide visibility & positioning (FLIP engine requirement) */
.slide{position:absolute;top:0;left:0;width:100%;height:100%;display:flex;flex-direction:column;justify-content:center;align-items:stretch;padding:0;opacity:0;pointer-events:none;visibility:hidden}
.slide>.slide-content,.slide>[data-ms-content-root="true"]{width:100%}
.slide>.slide-content.ms-fit-top,.slide>[data-ms-content-root="true"].ms-fit-top{justify-content:flex-start!important;padding-top:clamp(1.5rem,3vh,3rem)!important;padding-bottom:clamp(1.5rem,3vh,3rem)!important}
.slide>.slide-content.ms-fit-scale,.slide>[data-ms-content-root="true"].ms-fit-scale{transform:scale(var(--ms-fit-scale,1));transform-origin:top center;will-change:transform}
.slide>.slide-content.ms-hero-balance,.slide>[data-ms-content-root="true"].ms-hero-balance{justify-content:center!important;align-items:center!important;text-align:center!important}
.slide>.slide-content.ms-sparse-balance,.slide>[data-ms-content-root="true"].ms-sparse-balance{justify-content:center!important}
.slide.active{opacity:1;pointer-events:auto;visibility:visible}
.slide-center{justify-content:center}
svg path:not([fill])[class*="route"],svg path:not([fill])[class*="connector"],svg path:not([fill])[class*="edge"],svg path:not([fill])[class*="flow"],svg path:not([fill])[class*="arc"],svg path:not([fill])[class*="curve"],svg path:not([fill])[class*="rail"],svg path:not([fill])[class*="trace"],svg path:not([fill])[class*="arrow"],svg path:not([fill])[class*="link"],svg line:not([fill]),svg polyline:not([fill]){fill:none}
svg path[fill="none"],svg line,svg polyline{vector-effect:non-scaling-stroke}
.ms-nowrap,.ms-cjk-token{display:inline-block;white-space:nowrap}
.deck-mark[data-magic-id],.kicker[data-magic-id],.section-tag[data-magic-id],.chip[data-magic-id],.tag[data-magic-id],.badge[data-magic-id],.pill[data-magic-id],.label[data-magic-id],.eyebrow[data-magic-id],.mini-label[data-magic-id],.small-label[data-magic-id],.mini[data-magic-id],.endpoint[data-magic-id],[data-magic-id][data-magic-nowrap="true"]{white-space:nowrap!important;inline-size:max-content;max-inline-size:none;flex-shrink:0}
.ms-cjk-balance{text-wrap:balance}
.card,.stat-item,.compare-panel,.metric-poster,.time-card,.timeline-card,.phase-card,.step-card,.lane-card{min-width:0;overflow:visible;container-type:inline-size}
.card-title{max-inline-size:100%;font-size:clamp(1.45rem,2.2vw,2.45rem);font-size:clamp(1.45rem,18cqw,2.45rem);line-height:1.02;overflow-wrap:break-word;word-break:normal;text-wrap:balance}
.card-subtitle{max-inline-size:100%;font-size:clamp(.92rem,1.15vw,1.2rem);font-size:clamp(.92rem,9cqw,1.2rem);line-height:1.15;overflow-wrap:break-word;word-break:normal}
.card-body,.card-desc{max-inline-size:100%;font-size:clamp(.95rem,1.25vw,1.25rem);font-size:clamp(.95rem,9cqw,1.25rem);line-height:1.42;overflow-wrap:break-word;word-break:normal}
.time-card .year,.timeline-card .year,.phase-card .phase-title,.step-card .step-title,.lane-card .lane-title{max-inline-size:100%;font-size:clamp(1.6rem,20cqw,3.25rem);line-height:.94;overflow-wrap:break-word;word-break:normal;text-wrap:balance}
.card .stat-value,.stat-item .stat-value,.compare-panel .stat-value,.metric-poster .stat-value{max-width:100%;font-size:clamp(2.4rem,4.6vw,5.2rem);font-size:clamp(2.4rem,30cqw,5.2rem);line-height:.9;letter-spacing:-.04em;overflow-wrap:normal;word-break:keep-all;white-space:nowrap}
.stat-value+.stat-label{display:block;margin-top:.75rem}
.stat-item .stat-label,.card .stat-label,.compare-panel .stat-label,.metric-poster .stat-label{max-inline-size:100%;font-size:clamp(.82rem,1.05vw,1.08rem);font-size:clamp(.82rem,8cqw,1.08rem);line-height:1.22;overflow-wrap:break-word;word-break:normal}
.stat-grid.card-grid-4 .stat-item .stat-value,.card-grid-4 .stat-item .stat-value{font-size:clamp(2.35rem,4vw,4.5rem);font-size:clamp(2.35rem,28cqw,4.5rem)}

/* Background image positioning */
.slide-with-bg{background-size:cover;background-position:center;position:relative}
.slide-with-bg::before{content:'';position:absolute;inset:0;background:linear-gradient(to right,rgba(0,0,0,0.92) 0%,rgba(0,0,0,0.82) 35%,rgba(0,0,0,0.50) 65%,rgba(0,0,0,0.25) 100%);z-index:0}
.slide-center.slide-with-bg::before{background:radial-gradient(ellipse at center,rgba(0,0,0,0.60) 0%,rgba(0,0,0,0.88) 100%)}
.slide-with-bg>*{position:relative;z-index:1}

/* Progress bar & counter */
.progress{position:fixed;bottom:0;left:0;height:3px;background:var(--accent, #3ba3ff);z-index:100;transition:width 0.2s ease}
.counter{position:fixed;bottom:1rem;right:2rem;font-size:0.85rem;color:var(--subtext, var(--muted, #9ca3af));z-index:100;font-family:var(--font-mono, ui-monospace, monospace);font-variant-numeric:tabular-nums}

/* Slide dock navigation */
#slide-dock{--dock-bg-left:0px;--dock-bg-right:0px;position:fixed;bottom:0;left:50%;transform:translateX(-50%) translateY(calc(100% + 4px));display:flex;align-items:flex-end;gap:9px;padding:10px 18px 15px;background:transparent;border:0;z-index:300;isolation:isolate;transition:transform 0.32s cubic-bezier(0.4,0,0.2,1)}
#slide-dock::before{content:'';position:absolute;top:0;bottom:0;left:var(--dock-bg-left);right:var(--dock-bg-right);background:rgba(10,12,22,0.72);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.08);border-bottom:none;border-radius:14px 14px 0 0;z-index:0;pointer-events:none;transition:left 0.12s cubic-bezier(0.22,1,0.36,1),right 0.12s cubic-bezier(0.22,1,0.36,1)}
#slide-dock.dock-up{transform:translateX(-50%) translateY(0)}
.dock-item{position:relative;z-index:1;width:11px;height:11px;border-radius:50%;background:rgba(255,255,255,0.25);cursor:pointer;flex-shrink:0;transform:scale(1);transform-origin:bottom center;transition:transform 0.12s cubic-bezier(0.22,1,0.36,1),background 0.15s;will-change:transform}
.dock-item.dock-on{background:var(--accent,#7fc8ff);box-shadow:none}
.dock-preview-btn{position:relative;z-index:1;width:20px;height:11px;border-radius:6px;background:rgba(255,255,255,0.25);cursor:pointer;flex-shrink:0;transition:transform 0.12s cubic-bezier(0.22,1,0.36,1),background 0.15s;margin-left:8px;will-change:transform}
.dock-preview-btn::before{content:'';position:absolute;inset:3px;border-radius:3px;border:1px solid rgba(255,255,255,0.4);transition:border-color 0.15s}
.dock-preview-btn:hover,.dock-preview-btn.active{background:var(--accent,#7fc8ff)}
.dock-preview-btn:hover::before,.dock-preview-btn.active::before{border-color:rgba(255,255,255,0.8)}
#dock-tip{position:fixed;bottom:72px;transform:translateX(-50%);background:rgba(10,12,22,0.92);color:#e8edf7;font-size:11px;font-weight:500;padding:4px 9px;border-radius:6px;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity 0.12s;border:1px solid rgba(255,255,255,0.1);font-family:var(--font-body,system-ui);z-index:301}
#dock-hover-preview{position:fixed;left:50%;bottom:86px;width:min(360px,26vw);min-width:240px;max-width:360px;aspect-ratio:16/9;pointer-events:none;opacity:0;transform:translateX(-50%) translateY(14px) scale(0.965);transform-origin:50% 100%;transition:opacity 0.18s ease,transform 0.28s cubic-bezier(0.22,1,0.36,1);z-index:302}
#dock-hover-preview.show{opacity:1;transform:translateX(-50%) translateY(0) scale(1)}
.dock-hover-preview-frame{position:absolute;inset:0;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.16);background:linear-gradient(180deg, rgba(18,20,30,0.96), rgba(8,10,18,0.98));box-shadow:0 18px 48px rgba(0,0,0,0.42),0 0 0 1px rgba(255,255,255,0.04) inset}
.dock-hover-preview-frame::after{content:'';position:absolute;inset:auto 0 0 0;height:34%;background:linear-gradient(180deg, rgba(10,12,22,0) 0%, rgba(10,12,22,0.1) 24%, rgba(10,12,22,0.78) 100%);pointer-events:none;z-index:1}
.dock-hover-preview-content{position:absolute;top:0;left:0;width:1920px;height:1080px;transform-origin:top left;pointer-events:none;opacity:0;transition:opacity 0.18s ease}
.dock-hover-preview-content iframe{width:1920px;height:1080px;border:0;display:block;pointer-events:none;background:transparent}
.dock-hover-preview-loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:0.55rem;background:linear-gradient(180deg, rgba(12,14,24,0.76), rgba(10,12,22,0.9));color:rgba(232,237,247,0.82);font-size:0.86rem;font-weight:600;letter-spacing:0.02em;opacity:0;transition:opacity 0.16s ease;z-index:2}
.dock-hover-preview-loading::before{content:'';width:0.7rem;height:0.7rem;border-radius:50%;background:rgba(127,200,255,0.9);box-shadow:0 0 0 0 rgba(127,200,255,0.45);animation:dock-preview-pulse 1.15s ease-in-out infinite}
.dock-hover-preview-meta{position:absolute;left:50%;bottom:12px;transform:translateX(-50%);max-width:calc(100% - 28px);padding:5px 10px;border-radius:999px;background:rgba(10,12,22,0.86);border:1px solid rgba(255,255,255,0.1);color:#e8edf7;font-size:11px;font-weight:600;line-height:1.2;white-space:nowrap;text-overflow:ellipsis;overflow:hidden;font-family:var(--font-body,system-ui);z-index:3}
#dock-hover-preview.ready .dock-hover-preview-content{opacity:1}
#dock-hover-preview.loading .dock-hover-preview-loading{opacity:1}
.dock-item,.dock-item:hover,.dock-preview-btn,.dock-preview-btn:hover{cursor:pointer!important}
#slide-dock,#slide-dock:hover,#dock-tip,#dock-tip:hover{cursor:default!important}
@keyframes dock-preview-pulse{0%,100%{transform:scale(0.9);box-shadow:0 0 0 0 rgba(127,200,255,0.32)}50%{transform:scale(1.08);box-shadow:0 0 0 10px rgba(127,200,255,0)}}

/* Slide overview panel */
#slide-overview{position:fixed;inset:0;background:rgba(10,12,22,0.95);backdrop-filter:blur(32px);-webkit-backdrop-filter:blur(32px);z-index:1200;display:none;opacity:0;visibility:hidden;pointer-events:none;transition:opacity 0.28s ease,backdrop-filter 0.28s ease,-webkit-backdrop-filter 0.28s ease;--overview-pad-x:clamp(28px,5vw,96px);--overview-pad-y:clamp(24px,3.5vh,44px);--overview-feather-h:clamp(28px,5vh,52px)}
#slide-overview.showing{display:block}
#slide-overview.show{opacity:1;visibility:visible;pointer-events:auto}
#slide-overview::before,#slide-overview::after{content:'';position:absolute;left:0;right:0;height:var(--overview-feather-h);pointer-events:none;opacity:0;transition:opacity 0.18s ease;z-index:2}
#slide-overview::before{top:0;background:linear-gradient(180deg, rgba(10,12,22,0.98) 0%, rgba(10,12,22,0.78) 42%, rgba(10,12,22,0) 100%)}
#slide-overview::after{bottom:0;background:linear-gradient(0deg, rgba(10,12,22,0.98) 0%, rgba(10,12,22,0.78) 42%, rgba(10,12,22,0) 100%)}
#slide-overview.show.has-top-overflow::before,#slide-overview.show.has-bottom-overflow::after{opacity:1}
.overview-grid{position:absolute;inset:0;overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:clamp(16px,2vw,28px);padding:var(--overview-pad-y) var(--overview-pad-x);align-content:start;opacity:0;transform:translateY(24px) scale(0.985);transform-origin:50% 10%;transition:opacity 0.26s ease,transform 0.42s cubic-bezier(0.22,1,0.36,1);overscroll-behavior:contain;-webkit-overflow-scrolling:touch;scroll-padding-block:var(--overview-pad-y);scrollbar-width:thin;scrollbar-color:rgba(232,237,247,0.34) transparent}
#slide-overview.show .overview-grid{opacity:1;transform:translateY(0) scale(1)}
.overview-grid::-webkit-scrollbar{width:14px}
.overview-grid::-webkit-scrollbar-track{background:transparent}
.overview-grid::-webkit-scrollbar-thumb{background:rgba(232,237,247,0.3);border:4px solid transparent;border-radius:999px;background-clip:padding-box;min-height:48px}
.overview-grid::-webkit-scrollbar-thumb:hover{background:rgba(232,237,247,0.45);border:4px solid transparent;background-clip:padding-box}
.overview-grid::-webkit-scrollbar-corner{background:transparent}
.overview-item{aspect-ratio:16/9;background:rgba(20,22,32,0.8);background-size:cover;background-position:center;background-repeat:no-repeat;border:0;border-radius:10px;cursor:pointer;overflow:hidden;position:relative;isolation:isolate;box-shadow:0 0 0 1px rgba(255,255,255,0.10);transition:transform 0.2s ease,box-shadow 0.2s ease}
.overview-item:hover{transform:translateY(-6px);box-shadow:0 12px 32px rgba(0,0,0,0.5),0 0 0 2px var(--accent,#7fc8ff)}
.overview-item.current{box-shadow:0 0 0 2px var(--accent,#7fc8ff),0 0 0 5px rgba(127,200,255,0.3)}
.overview-item-content{position:absolute;top:0;left:0;width:1920px;height:1080px;transform-origin:top left;pointer-events:none}
.overview-item-content iframe{width:1920px;height:1080px;border:0;display:block;pointer-events:none;background:transparent}
.overview-item-number{position:absolute;top:10px;right:10px;background:rgba(10,12,22,0.85);color:#9ca3af;font-size:11px;font-weight:600;padding:5px 10px;border-radius:6px;font-family:var(--font-mono,ui-monospace,monospace);z-index:1}
.overview-close{position:fixed;top:2.5rem;right:2.5rem;width:44px;height:44px;border-radius:50%;background:rgba(10,12,22,0.85);border:1px solid rgba(255,255,255,0.15);color:#e8edf7;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:20px;line-height:1;z-index:1201;opacity:0;transform:translateY(-10px) scale(0.92);transition:opacity 0.22s ease,background 0.2s ease,border-color 0.2s ease,transform 0.32s cubic-bezier(0.22,1,0.36,1)}
#slide-overview.show .overview-close{opacity:1;transform:translateY(0) scale(1)}
.overview-close:hover{background:rgba(10,12,22,0.95);transform:scale(1.1);border-color:var(--accent,#7fc8ff)}

/* QA overview panel */
#qa-overview{position:fixed;inset:0;background:rgba(9,10,13,0.96);backdrop-filter:blur(28px);-webkit-backdrop-filter:blur(28px);z-index:1300;display:none;opacity:0;visibility:hidden;pointer-events:none;transition:opacity 0.24s ease,backdrop-filter 0.24s ease,-webkit-backdrop-filter 0.24s ease;font-family:var(--font-body,system-ui,-apple-system,sans-serif);color:#edf1f7}
#qa-overview.showing{display:block}
#qa-overview.show{opacity:1;visibility:visible;pointer-events:auto}
.qa-shell{position:absolute;inset:0;display:flex;flex-direction:column;min-width:0}
.qa-toolbar{height:74px;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:18px clamp(24px,4vw,72px);border-bottom:1px solid rgba(237,241,247,0.12);background:linear-gradient(180deg,rgba(12,13,17,0.96),rgba(12,13,17,0.84));box-shadow:0 16px 44px rgba(0,0,0,0.28);z-index:2}
.qa-title{display:flex;align-items:baseline;gap:12px;min-width:0}
.qa-title strong{font-size:15px;line-height:1;text-transform:uppercase;letter-spacing:0.14em;font-weight:800;color:#f8fafc;white-space:nowrap}
#qa-summary{font-size:12px;line-height:1.35;color:rgba(237,241,247,0.64);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.qa-actions{display:flex;align-items:center;gap:8px;flex-shrink:0}
.qa-close{height:34px;border:1px solid rgba(237,241,247,0.14);background:rgba(255,255,255,0.045);color:rgba(237,241,247,0.82);border-radius:8px;font-size:18px;font-weight:750;line-height:1;cursor:pointer;transition:background 0.16s ease,border-color 0.16s ease,color 0.16s ease,transform 0.16s ease}
.qa-close{width:34px;padding:0;font-size:18px}
.qa-close:hover{background:rgba(255,255,255,0.09);border-color:rgba(237,241,247,0.28);color:#fff;transform:translateY(-1px)}
.qa-grid{position:absolute;top:74px;right:0;bottom:0;left:0;overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,520px),1fr));gap:clamp(18px,2vw,30px);padding:clamp(22px,3vw,46px) clamp(24px,4vw,72px) clamp(34px,5vw,80px);align-content:start;scrollbar-width:thin;scrollbar-color:rgba(237,241,247,0.32) transparent}
.qa-grid::-webkit-scrollbar{width:14px}
.qa-grid::-webkit-scrollbar-track{background:transparent}
.qa-grid::-webkit-scrollbar-thumb{background:rgba(237,241,247,0.28);border:4px solid transparent;border-radius:999px;background-clip:padding-box}
.qa-card{min-width:0;border:1px solid rgba(237,241,247,0.12);border-radius:10px;background:rgba(255,255,255,0.035);overflow:hidden;cursor:pointer;box-shadow:0 18px 50px rgba(0,0,0,0.26);transition:transform 0.18s ease,border-color 0.18s ease,box-shadow 0.18s ease,opacity 0.18s ease}
.qa-card:hover{transform:translateY(-4px);border-color:rgba(237,241,247,0.28);box-shadow:0 24px 70px rgba(0,0,0,0.34)}
.qa-card.current{box-shadow:0 0 0 2px rgba(127,200,255,0.72),0 18px 52px rgba(0,0,0,0.34)}
.qa-thumb{position:relative;aspect-ratio:16/9;background:rgba(24,25,31,0.86);overflow:hidden;isolation:isolate}
.qa-frame-content{position:absolute;top:0;left:0;width:1920px;height:1080px;transform-origin:top left;pointer-events:none;background:transparent}
.qa-frame-content iframe{width:1920px;height:1080px;border:0;display:block;pointer-events:none;background:transparent}
.qa-card.has-issue{border-color:rgba(251,191,36,0.56);box-shadow:0 0 0 1px rgba(251,191,36,0.26),0 18px 50px rgba(0,0,0,0.28)}
.qa-card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:12px 14px 13px;border-top:1px solid rgba(237,241,247,0.10);background:rgba(11,12,16,0.92)}
.qa-page{display:flex;flex-direction:column;gap:6px;min-width:0}
.qa-page strong{font-size:12px;line-height:1;font-weight:800;letter-spacing:0.09em;text-transform:uppercase;color:#f8fafc}
.qa-note-preview{display:none;max-width:44ch;color:rgba(237,241,247,0.66);font-size:11px;line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.qa-card.has-issue .qa-note-preview{display:block}
.qa-issue-btn{flex-shrink:0;max-width:10rem;border:1px solid rgba(237,241,247,0.14);background:rgba(255,255,255,0.055);color:rgba(237,241,247,0.82);border-radius:8px;padding:7px 9px;font-size:10px;font-weight:900;line-height:1;letter-spacing:0.08em;text-transform:uppercase;white-space:nowrap;cursor:pointer;transition:background 0.16s ease,border-color 0.16s ease,color 0.16s ease,transform 0.16s ease}
.qa-issue-btn:hover{background:rgba(255,255,255,0.10);border-color:rgba(237,241,247,0.30);color:#fff;transform:translateY(-1px)}
.qa-card.has-issue .qa-issue-btn{background:rgba(251,191,36,0.18);border-color:rgba(251,191,36,0.46);color:#fde68a}
.qa-issue-editor[hidden]{display:none}
.qa-issue-editor{position:absolute;inset:0;z-index:4;display:grid;place-items:center;padding:22px;background:rgba(9,10,13,0.56);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.qa-issue-dialog{width:min(560px,100%);border:1px solid rgba(237,241,247,0.16);border-radius:14px;background:rgba(16,18,24,0.98);box-shadow:0 30px 90px rgba(0,0,0,0.48);padding:20px;display:grid;gap:14px}
.qa-issue-dialog h3{margin:0;color:#f8fafc;font-size:16px;line-height:1.2;font-weight:850}
.qa-issue-dialog p{margin:0;color:rgba(237,241,247,0.62);font-size:12px;line-height:1.45}
.qa-issue-dialog textarea{width:100%;min-height:132px;resize:vertical;box-sizing:border-box;border:1px solid rgba(237,241,247,0.16);border-radius:10px;background:rgba(255,255,255,0.055);color:#f8fafc;font:inherit;font-size:13px;line-height:1.45;padding:12px;outline:none}
.qa-issue-dialog textarea:focus{border-color:rgba(127,200,255,0.68);box-shadow:0 0 0 3px rgba(127,200,255,0.12)}
.qa-issue-actions{display:flex;justify-content:flex-end;gap:8px}
.qa-issue-actions button{height:34px;border:1px solid rgba(237,241,247,0.14);border-radius:8px;padding:0 12px;background:rgba(255,255,255,0.055);color:rgba(237,241,247,0.84);font-size:12px;font-weight:800;cursor:pointer}
.qa-issue-actions button:hover{background:rgba(255,255,255,0.10);color:#fff}
.qa-issue-actions .qa-issue-save{background:rgba(251,191,36,0.18);border-color:rgba(251,191,36,0.44);color:#fde68a}
.qa-issue-error{min-height:1em;color:#fca5a5;font-size:12px;line-height:1.3}
body.ms-qa-capture{overflow:auto;user-select:auto;-webkit-user-select:auto;-moz-user-select:auto;-ms-user-select:auto;background:#090a0d}
body.ms-qa-capture #deck,body.ms-qa-capture #ms-toolbar,body.ms-qa-capture #ms-rich-toolbar,body.ms-qa-capture #slide-dock,body.ms-qa-capture #dock-tip,body.ms-qa-capture #dock-hover-preview,body.ms-qa-capture .nav-btn,body.ms-qa-capture .progress,body.ms-qa-capture .counter,body.ms-qa-capture #slide-overview{display:none!important}
body.ms-qa-capture #qa-overview{position:relative;inset:auto;display:block!important;opacity:1!important;visibility:visible!important;pointer-events:auto;min-height:100vh;background:#090a0d;backdrop-filter:none;-webkit-backdrop-filter:none;transition:none}
body.ms-qa-capture .qa-shell{position:relative;inset:auto;display:block;min-height:100vh}
body.ms-qa-capture .qa-toolbar{position:sticky;top:0;height:74px;background:rgba(12,13,17,0.98);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
body.ms-qa-capture .qa-close{display:none}
body.ms-qa-capture .qa-grid{position:relative;top:auto;right:auto;bottom:auto;left:auto;overflow:visible;grid-template-columns:repeat(auto-fill,minmax(min(100%,520px),1fr));padding:clamp(22px,3vw,46px) clamp(24px,4vw,72px) clamp(34px,5vw,80px)}
body.ms-qa-capture .qa-card{break-inside:avoid;page-break-inside:avoid}
body.ms-qa-capture .qa-card:hover{transform:none}
body.ms-qa-capture .qa-issue-editor{position:fixed}
@media(max-width:720px){.qa-toolbar{height:auto;min-height:74px;align-items:flex-start;flex-direction:column;padding:16px 18px}.qa-actions{width:100%;justify-content:space-between}.qa-grid{top:128px;grid-template-columns:1fr;padding:18px}.qa-title{width:100%;justify-content:space-between}#qa-summary{white-space:normal;text-align:right}.qa-card-head{align-items:stretch;flex-direction:column}.qa-issue-btn{max-width:none;width:100%}}

/* Navigation buttons */
.nav-btn{position:fixed;top:50%;width:44px;height:44px;border-radius:50%;background:rgba(10,12,22,0.72);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.1);color:#e8edf7;cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:300;opacity:0;pointer-events:none;transition:opacity 0.25s ease,transform 0.25s ease}
.nav-btn.nav-show{opacity:1;pointer-events:auto}
#nav-prev{left:20px;transform:translateY(-50%) translateX(-64px)}
#nav-next{right:20px;transform:translateY(-50%) translateX(64px)}
#nav-prev.nav-show{transform:translateY(-50%) translateX(0)}
#nav-next.nav-show{transform:translateY(-50%) translateX(0)}
.nav-btn:hover{background:rgba(10,12,22,0.9);border-color:var(--accent, #3ba3ff);transform:translateY(-50%) scale(1.1)}
#nav-prev:hover{transform:translateY(-50%) translateX(0) scale(1.1)}
#nav-next:hover{transform:translateY(-50%) translateX(0) scale(1.1)}

/* Top-right utility toolbar */
#ms-toolbar{position:fixed;top:0;right:0;z-index:500;display:flex;align-items:center;gap:6px;padding:14px 16px 18px 28px;opacity:0;transform:translateY(-8px) scale(0.985);transform-origin:100% 0;pointer-events:auto;transition:opacity 0.18s ease,transform 0.26s cubic-bezier(0.22,1,0.36,1);font-family:var(--font-body,system-ui,-apple-system,sans-serif)}
#ms-toolbar:hover,#ms-toolbar:focus-within{opacity:1;transform:translateY(0) scale(1)}
#ms-toolbar::before{content:'';position:absolute;inset:8px 10px 12px 22px;border-radius:12px;background:rgba(8,11,18,0.64);backdrop-filter:blur(18px) saturate(1.25);-webkit-backdrop-filter:blur(18px) saturate(1.25);border:1px solid rgba(232,237,247,0.14);box-shadow:0 14px 44px rgba(0,0,0,0.28),0 1px 0 rgba(255,255,255,0.06) inset;z-index:-1}
#ms-toolbar>*{position:relative}
#ms-deck-badge,#ms-toolbar button{height:30px;min-width:0;display:inline-flex;align-items:center;justify-content:center;padding:0 10px;border-radius:8px;border:1px solid rgba(232,237,247,0.12);background:rgba(255,255,255,0.035);color:rgba(232,237,247,0.92);font-size:12px;font-weight:650;line-height:1;letter-spacing:0.01em;box-shadow:none}
#ms-deck-badge{display:none;max-width:min(34vw,220px);color:rgba(232,237,247,0.68);font-weight:600;letter-spacing:0.055em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:default}
#ms-toolbar button{appearance:none;-webkit-appearance:none;cursor:pointer;background:rgba(255,255,255,0.05);transition:background 0.16s ease,border-color 0.16s ease,color 0.16s ease,transform 0.16s ease}
#ms-toolbar button:hover{background:color-mix(in srgb,var(--accent,#7fc8ff) 18%,rgba(255,255,255,0.055));border-color:color-mix(in srgb,var(--accent,#7fc8ff) 52%,rgba(255,255,255,0.18));color:#fff;transform:translateY(-1px)}
#ms-toolbar button:active{transform:translateY(0) scale(0.98)}
#ms-toolbar button:focus-visible{outline:2px solid color-mix(in srgb,var(--accent,#7fc8ff) 72%,white);outline-offset:2px}
#ms-toolbar,#ms-toolbar:hover{cursor:default!important}
#ms-toolbar button,#ms-toolbar button:hover{cursor:pointer!important}
#ms-save-btn.ms-dirty{border-color:rgba(245,158,11,0.55)!important;background:rgba(245,158,11,0.12)!important}
.ms-dirty-dot{display:none;width:6px;height:6px;border-radius:50%;background:#f59e0b;flex-shrink:0;box-shadow:0 0 12px rgba(245,158,11,0.55)}
#ms-save-btn.ms-dirty .ms-dirty-dot{display:inline-block}

/* Edit mode */
[contenteditable="true"]{outline:1px dashed rgba(118,185,0,0.3);outline-offset:4px;cursor:text;border-radius:2px}
[contenteditable="true"]:hover{outline-color:rgba(118,185,0,0.5)}
[contenteditable="true"]:focus{outline:2px solid rgba(118,185,0,0.6)!important;outline-offset:4px;background:rgba(118,185,0,0.03);border-radius:2px}
.uploadable-wrap .upload-btn{display:none!important}
.ms-edit-mode .uploadable-wrap .upload-btn{display:flex!important}
.ms-edit-mode .uploadable-wrap{cursor:pointer}
.ms-edit-mode body,.ms-edit-mode *{user-select:text!important;-webkit-user-select:text!important;-moz-user-select:text!important;-ms-user-select:text!important}
#ms-rich-toolbar{position:fixed;top:4rem;left:1rem;z-index:520;display:none;align-items:center;flex-wrap:wrap;gap:0.45rem;max-width:min(92vw,36rem);padding:0.55rem 0.6rem;background:rgba(10,12,22,0.78);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.12);border-radius:12px;box-shadow:0 18px 50px rgba(0,0,0,0.28)}
.ms-rich-group{display:flex;align-items:center;gap:0.35rem;padding-right:0.5rem;margin-right:0.15rem;border-right:1px solid rgba(255,255,255,0.08)}
.ms-rich-group:last-child{padding-right:0;margin-right:0;border-right:none}
.ms-rich-btn{min-width:30px;height:30px;padding:0 0.5rem;border-radius:8px;border:1px solid rgba(255,255,255,0.10);background:rgba(255,255,255,0.03);color:#e8edf7;font-size:0.74rem;font-weight:700;letter-spacing:0.01em;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;transition:background 0.18s ease,border-color 0.18s ease,color 0.18s ease}
.ms-rich-btn:hover{background:rgba(255,255,255,0.08);border-color:rgba(255,255,255,0.22)}
.ms-rich-btn.ms-rich-active{background:rgba(118,185,0,0.16);border-color:rgba(118,185,0,0.45);color:#f4f8ee}
.ms-rich-btn[data-format="italic"]{font-style:italic}
.ms-rich-btn[data-format="underline"]{text-decoration:underline}

/* FLIP animation support */
.magic-fade-sibling{opacity:0.15!important;transition:none!important}
.slide{overflow:hidden!important}

/* Transition animations — @keyframes are defined by the deck CSS in <style>, not here.
   Runtime JS reads --ms-dur and --ms-ease from :root, then triggers ms-{name} animations.
   'fade' and legacy 'crossfade' are built in as pure opacity transitions;
   all other transitions need deck-defined keyframes. */

/* === Stagger entrance animations === */
@keyframes ms-fade-in{from{opacity:0}to{opacity:var(--ms-stagger-final-opacity,1)}}
@keyframes ms-fade-in-up{from{opacity:0;transform:var(--ms-stagger-base-transform,translateZ(0)) translateY(var(--ms-stagger-y,30px))}to{opacity:var(--ms-stagger-final-opacity,1);transform:var(--ms-stagger-base-transform,translateZ(0)) translateY(0)}}
@keyframes ms-fade-in-down{from{opacity:0;transform:var(--ms-stagger-base-transform,translateZ(0)) translateY(calc(var(--ms-stagger-y,30px) * -1))}to{opacity:var(--ms-stagger-final-opacity,1);transform:var(--ms-stagger-base-transform,translateZ(0)) translateY(0)}}
@keyframes ms-fade-in-left{from{opacity:0;transform:var(--ms-stagger-base-transform,translateZ(0)) translateX(calc(var(--ms-stagger-x,30px) * -1))}to{opacity:var(--ms-stagger-final-opacity,1);transform:var(--ms-stagger-base-transform,translateZ(0)) translateX(0)}}
@keyframes ms-fade-in-right{from{opacity:0;transform:var(--ms-stagger-base-transform,translateZ(0)) translateX(var(--ms-stagger-x,30px))}to{opacity:var(--ms-stagger-final-opacity,1);transform:var(--ms-stagger-base-transform,translateZ(0)) translateX(0)}}
@keyframes ms-zoom-in{from{opacity:0;transform:var(--ms-stagger-base-transform,translateZ(0)) scale(0.8)}to{opacity:var(--ms-stagger-final-opacity,1);transform:var(--ms-stagger-base-transform,translateZ(0)) scale(1)}}

/* Apply to JS-marked stagger elements */
.ms-stagger-item{animation:ms-fade-in-up var(--ms-stagger-duration,0.5s) var(--ms-ease,cubic-bezier(0.25,1,0.5,1)) both;animation-delay:calc(var(--ms-stagger-base-delay,110ms) + var(--stagger-index,0) * 80ms)}
.ms-stagger-text{--ms-stagger-y:58px;--ms-stagger-duration:0.72s}
.slide[data-stagger="fade-in"] .ms-stagger-item{animation-name:ms-fade-in}
.slide[data-stagger="fade-in-down"] .ms-stagger-item{animation-name:ms-fade-in-down}
.slide[data-stagger="fade-in-left"] .ms-stagger-item{animation-name:ms-fade-in-left}
.slide[data-stagger="fade-in-right"] .ms-stagger-item{animation-name:ms-fade-in-right}
.slide[data-stagger="zoom-in"] .ms-stagger-item{animation-name:ms-zoom-in}

/* Custom cursor with trailing effect */
@keyframes cursor-glow{0%,100%{box-shadow:0 0 16px 4px var(--cursor-glow,rgba(255,255,255,0.8)),0 0 32px 8px var(--cursor-glow,rgba(255,255,255,0.4)),0 0 48px 12px var(--cursor-glow,rgba(255,255,255,0.2))}50%{box-shadow:0 0 24px 6px var(--cursor-glow,rgba(255,255,255,0.9)),0 0 48px 12px var(--cursor-glow,rgba(255,255,255,0.6)),0 0 72px 18px var(--cursor-glow,rgba(255,255,255,0.3))}}
body{cursor:none}
#ms-cursor{position:fixed;width:14px;height:14px;margin-left:-7px;margin-top:-7px;border-radius:50%;background:var(--cursor-color,#fff);border:2px solid var(--cursor-border,rgba(0,0,0,0.3));pointer-events:none;z-index:10000;opacity:0.95;animation:cursor-glow 1.8s ease-in-out infinite;transition:transform 0.15s ease,opacity 0.15s ease}
#ms-cursor.cursor-click{transform:scale(0.7)}
.ms-cursor-trail{position:fixed;width:10px;height:10px;margin-left:-5px;margin-top:-5px;border-radius:50%;background:var(--cursor-color,#fff);pointer-events:none;z-index:9999;transition:transform 0.15s ease,opacity 0.15s ease;opacity:0.6}
.ms-cursor-trail.cursor-click{transform:scale(0.7)}

/* Accessibility */
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:0.01ms!important;transition-duration:0.01ms!important}#ms-cursor{animation:none}}
body.ms-overview-embed{cursor:default!important}
body.ms-overview-embed #ms-toolbar,
body.ms-overview-embed #ms-rich-toolbar,
body.ms-overview-embed #slide-dock,
body.ms-overview-embed #dock-hover-preview,
body.ms-overview-embed #slide-overview,
body.ms-overview-embed #qa-overview,
body.ms-overview-embed .nav-btn,
body.ms-overview-embed .progress,
body.ms-overview-embed .counter,
body.ms-overview-embed #ms-cursor,
body.ms-overview-embed .ms-cursor-trail{display:none!important}
/* === end injected CSS === */
"""

# ── (Lucide removed — nav arrows are pure CSS) ────────────────────────────

# ── Progress bar + counter HTML (inserted after closing </div> of deck) ───
def make_runtime_html(ui: dict) -> str:
    return """<div class="progress" id="progress"></div>
<div class="counter" id="counter"></div>
<div id="slide-dock"></div>
<div id="dock-tip"></div>
<div id="dock-hover-preview" aria-hidden="true">
  <div class="dock-hover-preview-frame">
    <div class="dock-hover-preview-content"></div>
    <div class="dock-hover-preview-loading">{loading_preview}</div>
    <div class="dock-hover-preview-meta"></div>
  </div>
</div>
<button id="nav-prev" class="nav-btn"><span style="display:inline-block;width:10px;height:10px;border-left:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg);margin-left:2px"></span></button>
<button id="nav-next" class="nav-btn"><span style="display:inline-block;width:10px;height:10px;border-right:2px solid currentColor;border-top:2px solid currentColor;transform:rotate(45deg);margin-right:2px"></span></button>
<div id="slide-overview">
  <div class="overview-grid"></div>
  <button class="overview-close">✕</button>
</div>
<div id="qa-overview" aria-hidden="true">
  <div class="qa-shell">
    <div class="qa-toolbar">
      <div class="qa-title"><strong>QA Overview</strong><span id="qa-summary">Scanning slides...</span></div>
      <div class="qa-actions">
        <button class="qa-close" type="button" aria-label="Close QA overview">×</button>
      </div>
    </div>
    <div class="qa-grid"></div>
    <div class="qa-issue-editor" hidden>
      <form class="qa-issue-dialog">
        <div>
          <h3 id="qa-issue-title">Request slide revision</h3>
          <p>Describe what feels off or what should change. Ask for regeneration, a different layout, or visual fixes.</p>
        </div>
        <textarea id="qa-issue-note" required placeholder="What should change on this slide?"></textarea>
        <div class="qa-issue-error" aria-live="polite"></div>
        <div class="qa-issue-actions">
          <button class="qa-issue-cancel" type="button">Cancel</button>
          <button class="qa-issue-save" type="submit">Save request</button>
        </div>
      </form>
    </div>
  </div>
</div>
<div id="ms-toolbar" aria-label="Preview controls">
  <div id="ms-deck-badge"></div>
  <button id="ms-save-btn" type="button"><span class="ms-save-text">{save}</span><span class="ms-dirty-dot"></span></button>
  <button id="ms-edit-btn" type="button" title="{edit} (E)"><span>{edit}</span></button>
  <button id="ms-close-btn" type="button">{close}</button>
</div>
<div id="ms-rich-toolbar" aria-hidden="true">
  <div class="ms-rich-group">
    <button class="ms-rich-btn" data-format="font-size-step" data-value="-1" title="Decrease font size">-</button>
    <button class="ms-rich-btn" data-format="font-size-step" data-value="1" title="Increase font size">+</button>
  </div>
  <div class="ms-rich-group">
    <button class="ms-rich-btn" data-format="bold" title="Bold">B</button>
    <button class="ms-rich-btn" data-format="italic" title="Italic">I</button>
    <button class="ms-rich-btn" data-format="underline" title="Underline">U</button>
    <button class="ms-rich-btn" data-format="clear" title="Clear formatting">Clr</button>
  </div>
</div>
<div id="ms-toast" style="position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);background:rgba(10,12,22,0.92);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.12);color:#e8edf7;font-size:0.9rem;font-weight:500;padding:0.75rem 1.5rem;border-radius:10px;z-index:600;opacity:0;transition:opacity 0.3s;pointer-events:none"></div>""".format(**ui)

# ── FLIP engine + navigation script ───────────────────────────────────────
# Uses a single-clone inverse-FLIP approach.
# Key runtime properties:
#   - FROM slide is hidden instantly so originals never overlap the animated clone
#   - Each shared element gets exactly one animated TO clone during motion
#   - The previous dual-clone crossfade path was removed to eliminate ghosting
#   - Non-shared elements are detected recursively up to content div, not just direct children
#   - z-index management prevents stacking issues
RUNTIME_SCRIPT = """<script>
document.body.classList.remove('ms-edit-mode');
document.querySelectorAll('[contenteditable]').forEach(function(el){el.removeAttribute('contenteditable');});
var slides=document.querySelectorAll('.slide');
var progress=document.getElementById('progress');
var counter=document.getElementById('counter');
var cur=0,animating=false;
var MS_VIEW_PARAMS=new URLSearchParams(window.location.search);
var MS_EMBED_MODE=MS_VIEW_PARAMS.get('ms_embed')||'';
var MS_IS_OVERVIEW_EMBED=MS_EMBED_MODE==='overview';
var MS_IS_MAGIC_SLIDE_PREVIEW=window.location.protocol==='http:'&&window.location.hostname==='localhost'&&/^\/deck\/[^/]+\//.test(window.location.pathname);
var MS_QA_ALLOWED=MS_IS_MAGIC_SLIDE_PREVIEW;
var MS_QA_MODE=MS_QA_ALLOWED&&MS_VIEW_PARAMS.get('ms_qa')==='overview';
var MS_QA_CAPTURE_MODE=MS_QA_MODE&&MS_VIEW_PARAMS.get('ms_qa_capture')==='1';
document.body.classList.toggle('ms-qa-capture',MS_QA_CAPTURE_MODE);
function isCjkTokenProtectionCandidate(el){
  if(!el||el.dataset.cjkWrap==='off'||el.classList.contains('ms-cjk-protected'))return false;
  if(el.closest('[contenteditable="true"]'))return false;
  if(!el.matches('[data-cjk-wrap="smart"],.heading-hero,.heading-xl,.heading-lg,.heading-md,h1,h2,h3,.body-lg,.body-text-lg,p,li'))return false;
  if(el.querySelector('img,video,canvas,svg,.ms-nowrap,.ms-cjk-token'))return false;
  if(Array.from(el.children).some(function(ch){return !ch.matches('br')}))return false;
  var text=el.textContent||'';
  if(!/[\\u3400-\\u9fff\\uf900-\\ufaff]/.test(text))return false;
  if(!findCjkProtectedRanges(text).length)return false;
  var cs=getComputedStyle(el);
  if(cs.whiteSpace.indexOf('nowrap')>-1)return false;
  return true;
}
function findCjkProtectedRanges(text){
  var ranges=[];
  function addMatches(re){
    var match;
    re.lastIndex=0;
    while((match=re.exec(text))!==null){
      if(match[0])ranges.push({start:match.index,end:match.index+match[0].length});
      if(match.index===re.lastIndex)re.lastIndex+=1;
    }
  }
  addMatches(/《[^》]+》/g);
  addMatches(/[A-Za-z][A-Za-z0-9+.#/_-]{1,}(?:\\s+[A-Za-z0-9+.#/_-]{2,})*/g);
  addMatches(/\\d+(?:\\.\\d+)?\\s*(?:年|月|日|世纪|页|张|个|次|倍|%|％|px|rem|vw|vh|MB|GB|TB|ms|s)/g);
  ranges.sort(function(a,b){return a.start-b.start||b.end-a.end});
  var merged=[];
  ranges.forEach(function(range){
    var last=merged[merged.length-1];
    if(last&&range.start<=last.end){
      last.end=Math.max(last.end,range.end);
    }else{
      merged.push({start:range.start,end:range.end});
    }
  });
  return merged;
}
function applyCjkTokenProtection(root){
  (root||document).querySelectorAll('[data-cjk-wrap="smart"],.heading-hero,.heading-xl,.heading-lg,.heading-md,h1,h2,h3,.body-lg,.body-text-lg,p,li').forEach(function(el){
    if(!isCjkTokenProtectionCandidate(el))return;
    var text=el.textContent;
    var ranges=findCjkProtectedRanges(text);
    if(!ranges.length)return;
    var frag=document.createDocumentFragment();
    var cursor=0;
    ranges.forEach(function(range){
      if(range.start>cursor)frag.appendChild(document.createTextNode(text.slice(cursor,range.start)));
      var span=document.createElement('span');
      span.className='ms-nowrap';
      span.dataset.msNowrapToken='1';
      span.textContent=text.slice(range.start,range.end);
      frag.appendChild(span);
      cursor=range.end;
    });
    if(cursor<text.length)frag.appendChild(document.createTextNode(text.slice(cursor)));
    el.textContent='';
    el.appendChild(frag);
    el.classList.add('ms-cjk-protected');
  });
}
function cjkTextLines(el){
  var lines=[];
  if(!el)return lines;
  var walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,{
    acceptNode:function(node){
      return node.textContent.trim()?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;
    }
  });
  while(walker.nextNode()){
    var text=walker.currentNode;
    for(var i=0;i<text.length;i+=1){
      var range=document.createRange();
      range.setStart(text,i);
      range.setEnd(text,i+1);
      var rect=range.getBoundingClientRect();
      range.detach();
      if(rect.width<0.5&&rect.height<0.5)continue;
      var line=lines.find(function(item){return Math.abs(item.y-rect.y)<Math.max(4,rect.height*0.22)});
      if(!line){
        line={y:rect.y,text:''};
        lines.push(line);
      }
      line.text+=text.data[i];
    }
  }
  return lines.sort(function(a,b){return a.y-b.y}).map(function(line){return line.text.trim()}).filter(Boolean);
}
function hasCjkWidowLine(el){
  var lines=cjkTextLines(el);
  if(lines.length<2)return false;
  var last=lines[lines.length-1].replace(/[\\s\\u00a0]+/g,'');
  var cjk=(last.match(/[\\u3400-\\u9fff\\uf900-\\ufaff]/g)||[]).length;
  var nonPunctuation=last.replace(/[，。！？；：、,.!?;:’”》〉）\\]\\)}]/g,'');
  return cjk===1&&nonPunctuation.length<=1;
}
function applyCjkWidowGuard(root){
  (root||document).querySelectorAll('[data-cjk-wrap="balance"],.heading-hero,.heading-xl,.heading-lg,.heading-md,.body-lg,.body-text-lg,p,li').forEach(function(el){
    if(!el||el.dataset.cjkWrap==='off')return;
    if(el.closest('[contenteditable="true"]'))return;
    if(el.querySelector('img,video,canvas,svg'))return;
    if(!/[\\u3400-\\u9fff\\uf900-\\ufaff]/.test(el.textContent||''))return;
    var cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||cs.whiteSpace.indexOf('nowrap')>-1)return;
    el.classList.remove('ms-cjk-balance');
    if(hasCjkWidowLine(el)){
      el.classList.add('ms-cjk-balance');
      if(hasCjkWidowLine(el))el.classList.remove('ms-cjk-balance');
    }
  });
}
function isMagicNoWrapLabel(el){
  if(!el||!el.hasAttribute('data-magic-id')||el.dataset.magicWrap==='allow')return false;
  if(el.closest('[contenteditable="true"]'))return false;
  if(el.querySelector&&el.querySelector('img,video,canvas,svg,br'))return false;
  if(Array.from(el.children||[]).some(function(ch){return ch.textContent&&ch.textContent.trim()}))return false;
  var text=(el.textContent||'').replace(/\s+/g,' ').trim();
  if(!text||text.length>52)return false;
  if(el.matches('[data-magic-nowrap="true"]'))return true;
  if(el.matches('h1,h2,h3,h4,h5,h6,p,.heading-hero,.heading-xl,.heading-lg,.heading-md'))return false;
  if(el.matches('.deck-mark,.small-mono,.kicker,.section-tag,.chip,.tag,.badge,.pill,.label,.eyebrow,.mini-label,.small-label,.mini,.endpoint,.feature-plate'))return true;
  var cs=getComputedStyle(el);
  var display=(cs.display||'').replace(/\s+/g,'-');
  if((display==='inline-flex'||display==='inline-block'||display==='inline'||display==='inline-grid')&&text.length<=52&&/^(SPAN|SMALL|LI|BUTTON|A|DIV|STRONG|B|EM)$/.test(el.tagName))return true;
  return /^(SPAN|SMALL|LI|BUTTON|A|DIV|STRONG|B|EM)$/.test(el.tagName)&&text.length<=36;
}
function stabilizeMagicText(root){
  (root||document).querySelectorAll('[data-magic-id]').forEach(function(el){
    if(!isMagicNoWrapLabel(el))return;
    el.style.whiteSpace='nowrap';
    el.style.width='max-content';
    el.style.maxWidth='none';
    el.style.maxInlineSize='none';
    el.style.flexShrink='0';
  });
}
slides[0].classList.add('active');
if(MS_IS_OVERVIEW_EMBED)document.body.classList.add('ms-overview-embed');
var msSlideParam=parseInt(MS_VIEW_PARAMS.get('ms_slide')||'',10);
if(msSlideParam>=1&&msSlideParam<=slides.length){
  cur=msSlideParam-1;
  slides[0].classList.remove('active');
  slides[cur].classList.add('active');
}
applyCjkTokenProtection(MS_IS_OVERVIEW_EMBED?slides[cur]:document);
function getMagic(s){var e={};s.querySelectorAll('[data-magic-id]').forEach(function(el){e[el.dataset.magicId]=el});return e}
function parseColorValue(color){
  if(!color)return null;
  var m=color.match(/rgba?\(([^)]+)\)/i);
  if(!m)return null;
  var parts=m[1].split(',').map(function(part){return parseFloat(part.trim())});
  if(parts.length<3||parts.slice(0,3).some(function(v){return isNaN(v)}))return null;
  return {r:parts[0],g:parts[1],b:parts[2],a:(parts.length>3&&!isNaN(parts[3]))?parts[3]:1};
}
function luminanceFromColor(color){
  var parsed=parseColorValue(color);
  if(!parsed||parsed.a<=0.05)return null;
  return (0.299*parsed.r+0.587*parsed.g+0.114*parsed.b)/255;
}
function getSlideTone(slide){
  if(!slide)return 'dark';
  var bgMode=(slide.getAttribute('data-bg')||'').toLowerCase();
  if(bgMode==='white'||bgMode==='light')return 'light';
  if(bgMode==='dark')return 'dark';
  if(slide.classList.contains('theme-dark'))return 'dark';
  if(slide.classList.contains('theme-light'))return 'light';
  var slideLuminance=luminanceFromColor(getComputedStyle(slide).backgroundColor);
  if(slideLuminance!==null)return slideLuminance>0.52?'light':'dark';
  var bodyLuminance=luminanceFromColor(getComputedStyle(document.body).backgroundColor);
  if(bodyLuminance!==null)return bodyLuminance>0.52?'light':'dark';
  return 'dark';
}
function copyComputedBackground(fromEl,toEl){
  if(!fromEl||!toEl)return;
  var cs=getComputedStyle(fromEl);
  toEl.style.backgroundColor=cs.backgroundColor;
  toEl.style.backgroundImage=cs.backgroundImage;
  toEl.style.backgroundPosition=cs.backgroundPosition;
  toEl.style.backgroundSize=cs.backgroundSize;
  toEl.style.backgroundRepeat=cs.backgroundRepeat;
  toEl.style.backgroundOrigin=cs.backgroundOrigin;
  toEl.style.backgroundClip=cs.backgroundClip;
  toEl.style.backgroundBlendMode=cs.backgroundBlendMode;
}
function resolveOverviewBackgroundSource(slide){
  if(!slide)return document.body;
  var cs=getComputedStyle(slide);
  if(luminanceFromColor(cs.backgroundColor)!==null)return slide;
  if(cs.backgroundImage&&cs.backgroundImage!=='none')return slide;
  return document.body;
}
function updateUI(){
  progress.style.width=((cur+1)/slides.length*100)+'%';
  counter.textContent=(cur+1)+' / '+slides.length;
  var items=document.querySelectorAll('.dock-item');
  items.forEach(function(d,i){d.classList.toggle('dock-on',i===cur)});
  updateCursorColor();
}
function updateCursorColor(){
  var activeSlide=slides[cur];
  if(!activeSlide)return;
  var tone=getSlideTone(activeSlide);
  var cursorColor=tone==='light'?'rgba(20,22,17,0.92)':'rgba(255,255,255,0.96)';
  var glowColor=tone==='light'?'rgba(20,22,17,0.24)':'rgba(255,255,255,0.78)';
  var borderColor=tone==='light'?'rgba(255,255,255,0.72)':'rgba(20,22,17,0.35)';
  document.documentElement.style.setProperty('--cursor-color',cursorColor);
  document.documentElement.style.setProperty('--cursor-glow',glowColor);
  document.documentElement.style.setProperty('--cursor-border',borderColor);
}
function isRuntimeContentFallback(el){
  if(!el||!el.classList)return false;
  if(el.classList.contains('bg')||el.classList.contains('brand-mark')||el.classList.contains('section-no'))return false;
  if(el.getAttribute('aria-hidden')==='true')return false;
  if(el.dataset&&(el.dataset.slideChrome==='true'||el.dataset.msChrome==='true'))return false;
  return true;
}
function getSlideWrappers(slide){
  if(!slide)return [];
  var primary=slide.querySelector(':scope > .slide-content');
  if(primary)return [primary];
  var fallback=Array.from(slide.children).find(isRuntimeContentFallback);
  if(fallback)fallback.setAttribute('data-ms-content-root','true');
  return fallback?[fallback]:[];
}
function getSlideContent(slide){
  if(!slide)return null;
  var primary=slide.querySelector(':scope > .slide-content')||slide.querySelector('.slide-content');
  if(primary)return primary;
  var fallback=Array.from(slide.children).find(isRuntimeContentFallback);
  if(fallback)fallback.setAttribute('data-ms-content-root','true');
  return fallback||slide;
}
function isFadeTransition(name){
  name=(name||'fade').toLowerCase();
  return name==='fade'||name==='crossfade';
}
function resetSlideLayoutFit(slide){
  getSlideWrappers(slide).forEach(function(wrapper){
    wrapper.classList.remove('ms-fit-top','ms-fit-scale','ms-hero-balance','ms-sparse-balance');
    wrapper.style.removeProperty('--ms-fit-scale');
  });
}
function measureWrapperBudget(wrapper){
  if(!wrapper)return {availableHeight:0,contentHeight:0,availableWidth:0,contentWidth:0};
  var cs=getComputedStyle(wrapper);
  var padLeft=parseFloat(cs.paddingLeft)||0;
  var padRight=parseFloat(cs.paddingRight)||0;
  var padTop=parseFloat(cs.paddingTop)||0;
  var padBottom=parseFloat(cs.paddingBottom)||0;
  var availableWidth=Math.max(0,wrapper.clientWidth-padLeft-padRight);
  var availableHeight=Math.max(0,wrapper.clientHeight-padTop-padBottom);
  var wrapperRect=wrapper.getBoundingClientRect();
  var minLeft=Infinity,minTop=Infinity,maxRight=-Infinity,maxBottom=-Infinity;
  Array.from(wrapper.children).forEach(function(ch){
    var chCS=getComputedStyle(ch);
    if(chCS.display==='none'||chCS.position==='absolute')return;
    var r=ch.getBoundingClientRect();
    if(!r.width&&!r.height)return;
    minLeft=Math.min(minLeft,r.left-wrapperRect.left);
    minTop=Math.min(minTop,r.top-wrapperRect.top);
    maxRight=Math.max(maxRight,r.right-wrapperRect.left);
    maxBottom=Math.max(maxBottom,r.bottom-wrapperRect.top);
  });
  var rectWidth=minLeft===Infinity?0:Math.max(0,maxRight-minLeft);
  var rectHeight=minTop===Infinity?0:Math.max(0,maxBottom-minTop);
  // Deliberately do not use wrapper.scrollWidth/scrollHeight here:
  // scroll metrics include absolutely positioned decorative motifs such as
  // watermarks, rings, arcs, and background numbers. Counting those as content
  // makes otherwise centered slides receive `.ms-fit-top`, pushing the real
  // content into the upper half of the viewport.
  return {
    availableWidth:availableWidth,
    availableHeight:availableHeight,
    contentWidth:rectWidth,
    contentHeight:rectHeight,
    contentTop:minTop===Infinity?0:minTop,
    contentBottom:maxBottom===-Infinity?0:maxBottom,
    topGap:minTop===Infinity?0:Math.max(0,minTop-padTop),
    bottomGap:maxBottom===-Infinity?0:Math.max(0,wrapper.clientHeight-padBottom-maxBottom)
  };
}
function shouldBalanceSparseWrapper(slide,wrapper,budget){
  if(!slide||!wrapper||!budget||!budget.availableHeight||!budget.contentHeight)return false;
  if(!wrapper.classList.contains('slide-content'))return false;
  if(slide.classList.contains('slide-top'))return false;
  if(wrapper.dataset&&/^(top|start)$/.test((wrapper.dataset.msAlign||wrapper.dataset.align||'').toLowerCase()))return false;
  var cs=getComputedStyle(wrapper);
  var jc=(cs.justifyContent||'').toLowerCase();
  var isTopAligned=jc==='flex-start'||jc==='start'||jc==='normal';
  if(!isTopAligned&&!slide.classList.contains('slide-dense'))return false;
  var contentRatio=budget.contentHeight/Math.max(1,budget.availableHeight);
  if(contentRatio>0.86)return false;
  var imbalance=budget.bottomGap-budget.topGap;
  if(imbalance<Math.max(40,budget.availableHeight*0.10))return false;
  return true;
}
function fitSlideLayout(slide){
  if(!slide)return;
  resetSlideLayoutFit(slide);
  stabilizeMagicText(slide);
  applyCjkTokenProtection(slide);
  applyCjkWidowGuard(slide);
  getSlideWrappers(slide).forEach(function(wrapper){
    if(slide===slides[0]&&wrapper.classList.contains('slide-content')&&getComputedStyle(wrapper).justifyContent==='flex-end'){
      wrapper.classList.add('ms-hero-balance');
    }
    var budget=measureWrapperBudget(wrapper);
    var heightOverflow=budget.availableHeight&&budget.contentHeight>budget.availableHeight+4;
    var widthOverflow=budget.availableWidth&&budget.contentWidth>budget.availableWidth+4;
    if(!heightOverflow&&!widthOverflow&&shouldBalanceSparseWrapper(slide,wrapper,budget)){
      wrapper.classList.add('ms-sparse-balance');
      budget=measureWrapperBudget(wrapper);
      heightOverflow=budget.availableHeight&&budget.contentHeight>budget.availableHeight+4;
      widthOverflow=budget.availableWidth&&budget.contentWidth>budget.availableWidth+4;
    }
    if(heightOverflow){
      wrapper.classList.add('ms-fit-top');
      budget=measureWrapperBudget(wrapper);
      heightOverflow=budget.availableHeight&&budget.contentHeight>budget.availableHeight+4;
      widthOverflow=budget.availableWidth&&budget.contentWidth>budget.availableWidth+4;
    }
    if(!heightOverflow&&!widthOverflow)return;
    var widthScale=budget.availableWidth&&budget.contentWidth?budget.availableWidth/budget.contentWidth:1;
    var heightScale=budget.availableHeight&&budget.contentHeight?budget.availableHeight/budget.contentHeight:1;
    var scale=Math.min(1,widthScale,heightScale);
    if(scale<0.995){
      wrapper.classList.add('ms-fit-scale');
      wrapper.style.setProperty('--ms-fit-scale',Math.max(0.72,scale).toFixed(3));
    }
  });
}
function snapStyles(el){var cs=getComputedStyle(el);var snap={display:cs.display,boxSizing:cs.boxSizing,minWidth:cs.minWidth,minHeight:cs.minHeight,maxWidth:cs.maxWidth,maxHeight:cs.maxHeight,minInlineSize:cs.minInlineSize,maxInlineSize:cs.maxInlineSize,alignItems:cs.alignItems,justifyContent:cs.justifyContent,gap:cs.gap,rowGap:cs.rowGap,columnGap:cs.columnGap,flexDirection:cs.flexDirection,flexWrap:cs.flexWrap,fontSize:cs.fontSize,fontWeight:cs.fontWeight,fontStyle:cs.fontStyle,fontFamily:cs.fontFamily,color:cs.color,letterSpacing:cs.letterSpacing,lineHeight:cs.lineHeight,background:cs.background,padding:cs.padding,borderRadius:cs.borderRadius,border:cs.border,boxShadow:cs.boxShadow,textAlign:cs.textAlign,textTransform:cs.textTransform,textDecoration:cs.textDecoration,textShadow:cs.textShadow,whiteSpace:cs.whiteSpace,wordBreak:cs.wordBreak,overflowWrap:cs.overflowWrap,textWrap:cs.textWrap,opacity:cs.opacity,children:[]};Array.from(el.children).forEach(function(ch){snap.children.push(snapStyles(ch))});return snap}
function applySnap(el,s){el.style.display=s.display;el.style.boxSizing='border-box';el.style.minWidth=s.minWidth;el.style.minHeight=s.minHeight;el.style.maxWidth=s.maxWidth;el.style.maxHeight=s.maxHeight;el.style.minInlineSize=s.minInlineSize;el.style.maxInlineSize=s.maxInlineSize;el.style.alignItems=s.alignItems;el.style.justifyContent=s.justifyContent;el.style.gap=s.gap;el.style.rowGap=s.rowGap;el.style.columnGap=s.columnGap;el.style.flexDirection=s.flexDirection;el.style.flexWrap=s.flexWrap;el.style.fontSize=s.fontSize;el.style.fontWeight=s.fontWeight;el.style.fontStyle=s.fontStyle;el.style.fontFamily=s.fontFamily;el.style.color=s.color;el.style.letterSpacing=s.letterSpacing;el.style.lineHeight=s.lineHeight;el.style.background=s.background;el.style.padding=s.padding;el.style.borderRadius=s.borderRadius;el.style.border=s.border;el.style.boxShadow=s.boxShadow;el.style.textAlign=s.textAlign;el.style.textTransform=s.textTransform;el.style.textDecoration=s.textDecoration;el.style.textShadow=s.textShadow;el.style.whiteSpace=s.whiteSpace;el.style.wordBreak=s.wordBreak;el.style.overflowWrap=s.overflowWrap;el.style.textWrap=s.textWrap||'';el.style.opacity=s.opacity;if(s.children&&s.children.length>0){Array.from(el.children).forEach(function(ch,i){if(s.children[i])applySnap(ch,s.children[i])})}}
function cssPx(v,scale){
  var n=parseFloat(v);
  return Number.isFinite(n)?(n*scale)+'px':v;
}
function visualScale(el,rect){
  return {
    x:rect.width/Math.max(1,(el&&el.offsetWidth)||rect.width||1),
    y:rect.height/Math.max(1,(el&&el.offsetHeight)||rect.height||1)
  };
}
function visualLabelSnap(el,rect){
  var cs=getComputedStyle(el),sc=visualScale(el,rect),avg=(sc.x+sc.y)/2;
  var labelDisplay=cs.display;
  return {
    left:rect.left+'px',top:rect.top+'px',width:rect.width+'px',height:rect.height+'px',
    display:labelDisplay,boxSizing:'border-box',alignItems:cs.alignItems==='normal'?'center':cs.alignItems,justifyContent:cs.justifyContent,
    gap:cssPx(cs.gap,sc.x),rowGap:cssPx(cs.rowGap,sc.y),columnGap:cssPx(cs.columnGap,sc.x),flexDirection:cs.flexDirection,flexWrap:'nowrap',
    fontSize:cssPx(cs.fontSize,sc.y),fontWeight:cs.fontWeight,fontStyle:cs.fontStyle,fontFamily:cs.fontFamily,color:cs.color,
    letterSpacing:cssPx(cs.letterSpacing,sc.x),lineHeight:cssPx(cs.lineHeight,sc.y),
    background:cs.background,boxShadow:cs.boxShadow,textAlign:cs.textAlign,textTransform:cs.textTransform,textDecoration:cs.textDecoration,textShadow:cs.textShadow,
    whiteSpace:'nowrap',wordBreak:'normal',overflowWrap:'normal',textWrap:cs.textWrap,opacity:cs.opacity,
    minWidth:cssPx(cs.minWidth,sc.x),minHeight:cssPx(cs.minHeight,sc.y),maxWidth:cssPx(cs.maxWidth,sc.x),maxHeight:cssPx(cs.maxHeight,sc.y),minInlineSize:cssPx(cs.minInlineSize,sc.x),maxInlineSize:cssPx(cs.maxInlineSize,sc.x),
    paddingTop:cssPx(cs.paddingTop,sc.y),paddingRight:cssPx(cs.paddingRight,sc.x),paddingBottom:cssPx(cs.paddingBottom,sc.y),paddingLeft:cssPx(cs.paddingLeft,sc.x),
    borderTopWidth:cssPx(cs.borderTopWidth,avg),borderRightWidth:cssPx(cs.borderRightWidth,avg),borderBottomWidth:cssPx(cs.borderBottomWidth,avg),borderLeftWidth:cssPx(cs.borderLeftWidth,avg),
    borderTopStyle:cs.borderTopStyle,borderRightStyle:cs.borderRightStyle,borderBottomStyle:cs.borderBottomStyle,borderLeftStyle:cs.borderLeftStyle,
    borderTopColor:cs.borderTopColor,borderRightColor:cs.borderRightColor,borderBottomColor:cs.borderBottomColor,borderLeftColor:cs.borderLeftColor,
    borderRadius:cs.borderRadius
  };
}
function applyVisualLabelSnap(el,s){
  el.style.position='fixed';el.style.zIndex='9999';el.style.pointerEvents='none';el.style.margin='0';el.style.overflow='visible';el.style.transform='none';el.style.transformOrigin='0 0';el.style.willChange='left,top,width,height,font-size,padding';
  Object.keys(s).forEach(function(k){el.style[k]=s[k]});
}
function visualLabelTransition(dur,ease){
  return ['left','top','width','height','min-width','min-height','max-width','max-height','font-size','letter-spacing','line-height','padding-top','padding-right','padding-bottom','padding-left','border-top-width','border-right-width','border-bottom-width','border-left-width'].map(function(p){return p+' '+dur+'ms '+ease}).join(',');
}
function magicLayoutBox(el,tr){
  var ow=el&&el.offsetWidth?el.offsetWidth:0;
  var oh=el&&el.offsetHeight?el.offsetHeight:0;
  return {
    width:Math.max(1,ow||tr.width||1),
    height:Math.max(1,oh||tr.height||1)
  };
}
function placeMagicClone(c,tr,box){
  c.style.position='fixed';
  c.style.zIndex='9999';
  c.style.pointerEvents='none';
  c.style.margin='0';
  c.style.overflow='visible';
  c.style.left='0';
  c.style.top='0';
  c.style.width=box.width+'px';
  c.style.height=box.height+'px';
  c.style.transformOrigin='0 0';
  c.style.willChange='transform,opacity';
}
function matrixIdentity(){return {a:1,b:0,c:0,d:1,e:0,f:0}}
function matrixTranslate(x,y){return {a:1,b:0,c:0,d:1,e:x||0,f:y||0}}
function matrixScale(x,y){return {a:x,b:0,c:0,d:y,e:0,f:0}}
function matrixMultiply(m,n){
  return {
    a:m.a*n.a+m.c*n.b,
    b:m.b*n.a+m.d*n.b,
    c:m.a*n.c+m.c*n.d,
    d:m.b*n.c+m.d*n.d,
    e:m.a*n.e+m.c*n.f+m.e,
    f:m.b*n.e+m.d*n.f+m.f
  };
}
function matrixCss(m){
  function fmt(n){
    if(!Number.isFinite(n))return '0';
    if(Math.abs(n)<0.000001)n=0;
    return String(Math.round(n*1000000)/1000000);
  }
  return 'matrix('+[m.a,m.b,m.c,m.d,m.e,m.f].map(fmt).join(',')+')';
}
function parseCssMatrix(t){
  if(!t||t==='none')return matrixIdentity();
  try{
    var M=window.DOMMatrix?new DOMMatrix(t):(window.WebKitCSSMatrix?new WebKitCSSMatrix(t):null);
    if(M&&(!('is2D' in M)||M.is2D!==false))return {a:M.a,b:M.b,c:M.c,d:M.d,e:M.e,f:M.f};
  }catch(e){}
  var m=t.match(/^matrix\\(([^)]+)\\)$/);
  if(m){
    var p=m[1].split(',').map(function(v){return parseFloat(v)});
    if(p.length>=6&&p.every(Number.isFinite))return {a:p[0],b:p[1],c:p[2],d:p[3],e:p[4],f:p[5]};
  }
  m=t.match(/^matrix3d\\(([^)]+)\\)$/);
  if(m){
    var q=m[1].split(',').map(function(v){return parseFloat(v)});
    if(q.length>=16&&q.every(Number.isFinite))return {a:q[0],b:q[1],c:q[4],d:q[5],e:q[12],f:q[13]};
  }
  return matrixIdentity();
}
function readMagicQuadMatrix(el,box){
  if(!el||!el.getBoxQuads)return null;
  try{
    var qs=el.getBoxQuads({box:'border'});
    if(!qs||!qs[0])return null;
    var q=qs[0],p1=q.p1,p2=q.p2,p4=q.p4;
    var w=Math.max(1,box.width||1),h=Math.max(1,box.height||1);
    if(!p1||!p2||!p4)return null;
    return {a:(p2.x-p1.x)/w,b:(p2.y-p1.y)/w,c:(p4.x-p1.x)/h,d:(p4.y-p1.y)/h,e:p1.x,f:p1.y};
  }catch(e){return null}
}
function readRectWithoutOwnTransform(el,cs){
  if(!cs||!cs.transform||cs.transform==='none')return el.getBoundingClientRect();
  var oldTransform=el.style.getPropertyValue('transform');
  var oldTransformPriority=el.style.getPropertyPriority('transform');
  var oldTransition=el.style.getPropertyValue('transition');
  var oldTransitionPriority=el.style.getPropertyPriority('transition');
  el.style.setProperty('transition','none','important');
  el.style.setProperty('transform','none','important');
  var rect=el.getBoundingClientRect();
  if(oldTransform)el.style.setProperty('transform',oldTransform,oldTransformPriority);
  else el.style.removeProperty('transform');
  if(oldTransition)el.style.setProperty('transition',oldTransition,oldTransitionPriority);
  else el.style.removeProperty('transition');
  return rect;
}
function readMagicMatrix(el,rect,box){
  var quad=readMagicQuadMatrix(el,box);
  if(quad)return quad;
  var w=Math.max(1,box.width||1),h=Math.max(1,box.height||1);
  var cs=getComputedStyle(el);
  if(!cs.transform||cs.transform==='none')return {a:rect.width/w,b:0,c:0,d:rect.height/h,e:rect.left,f:rect.top};
  var layoutRect=readRectWithoutOwnTransform(el,cs);
  var ew=Math.max(1,el.offsetWidth||w),eh=Math.max(1,el.offsetHeight||h);
  var origin=(cs.transformOrigin||'0 0').split(/\\s+/);
  var ox=parseFloat(origin[0])||0,oy=parseFloat(origin[1])||0;
  var base=matrixMultiply(matrixTranslate(layoutRect.left,layoutRect.top),matrixScale(layoutRect.width/ew,layoutRect.height/eh));
  var own=matrixMultiply(matrixMultiply(matrixTranslate(ox,oy),parseCssMatrix(cs.transform)),matrixTranslate(-ox,-oy));
  var boxScale=matrixScale(ew/w,eh/h);
  return matrixMultiply(matrixMultiply(base,own),boxScale);
}
function hasMagicTransform(el){
  if(!el)return false;
  var cs=getComputedStyle(el);
  if(cs.transform&&cs.transform!=='none')return true;
  var r=el.getBoundingClientRect();
  var q=readMagicQuadMatrix(el,{width:Math.max(1,el.offsetWidth||r.width||1),height:Math.max(1,el.offsetHeight||r.height||1)});
  return !!(q&&(Math.abs(q.b)>0.001||Math.abs(q.c)>0.001));
}
function safeRatio(a,b){return Math.max(a,b)/Math.max(1,Math.min(a,b))}
function lineHeightPx(cs){
  var lh=parseFloat(cs.lineHeight);
  if(Number.isFinite(lh))return lh;
  var fs=parseFloat(cs.fontSize);
  if(Number.isFinite(fs))return fs*1.2;
  return 19.2;
}
function approxLineCount(rect,cs){
  if(!rect||!rect.height)return 1;
  return Math.max(1,Math.round(rect.height/Math.max(1,lineHeightPx(cs))));
}
function isTextLike(el){
  if(!el||!el.textContent)return false;
  if(el.querySelector&&el.querySelector('img,video,canvas,svg'))return false;
  return /^(SPAN|P|H1|H2|H3|H4|H5|H6|LI|SMALL|STRONG|EM|DIV)$/.test(el.tagName);
}
function parentWidthSignature(el){
  if(!el||!el.parentElement)return '';
  var parent=el.parentElement;
  var rect=parent.getBoundingClientRect();
  var cs=getComputedStyle(parent);
  return [
    Math.round(rect.width),
    cs.maxWidth,
    cs.width,
    cs.display,
    cs.gridTemplateColumns,
    cs.flexBasis,
    cs.justifySelf,
    cs.alignSelf
  ].join('|');
}
function hasDiscreteTextLayoutShift(fromEl,toEl,fr,tr,fCS,tCS){
  if(fCS.textTransform!==tCS.textTransform||fCS.whiteSpace!==tCS.whiteSpace||fCS.wordBreak!==tCS.wordBreak||fCS.overflowWrap!==tCS.overflowWrap)return true;
  if(!isTextLike(fromEl)||!isTextLike(toEl)||!fr||!tr)return false;
  var fromLines=approxLineCount(fr,fCS),toLines=approxLineCount(tr,tCS);
  if(fromLines!==toLines)return true;
  var widthRatio=safeRatio(fr.width,tr.width);
  var heightRatio=safeRatio(fr.height,tr.height);
  var aspectRatio=safeRatio(fr.width/Math.max(1,fr.height),tr.width/Math.max(1,tr.height));
  if(parentWidthSignature(fromEl)!==parentWidthSignature(toEl)&&heightRatio>1.15&&widthRatio>1.15)return true;
  if(aspectRatio>1.75&&heightRatio>1.15)return true;
  return false;
}
function isComplexMagicNode(el){
  if(!el)return false;
  if(el.children.length>1)return true;
  if(el.children.length===1&&el.children[0].children&&el.children[0].children.length>0)return true;
  if(el.querySelector&&el.querySelector('img,svg,canvas,video,ul,ol,.card,.stat-item,.timeline-item'))return true;
  return false;
}
function hasResponsiveContainerShift(fromEl,toEl,fr,tr){
  if(!fromEl||!toEl||!fr||!tr)return false;
  var widthRatio=safeRatio(fr.width,tr.width);
  var heightRatio=safeRatio(fr.height,tr.height);
  if(parentWidthSignature(fromEl)!==parentWidthSignature(toEl)&&widthRatio>1.08)return true;
  if(isComplexMagicNode(fromEl)||isComplexMagicNode(toEl)){
    if(widthRatio>1.08||heightRatio>1.08)return true;
  }
  return false;
}
function normalizedMagicText(el){
  return el&&el.textContent?el.textContent.replace(/\s+/g,' ').trim():'';
}
function shouldCrossfadeIdentical(fromEl,toEl,fr,tr,fCS,tCS){
  if(!fromEl||!toEl||!fr||!tr)return true;
  if(hasDiscreteTextLayoutShift(fromEl,toEl,fr,tr,fCS,tCS))return true;
  if(hasResponsiveContainerShift(fromEl,toEl,fr,tr))return true;
  if(isComplexMagicNode(fromEl)||isComplexMagicNode(toEl))return true;
  if(isTextLike(fromEl)&&isTextLike(toEl)){
    var widthRatio=safeRatio(fr.width,tr.width);
    var heightRatio=safeRatio(fr.height,tr.height);
    if(parentWidthSignature(fromEl)!==parentWidthSignature(toEl))return true;
    if(normalizedMagicText(fromEl).length>20)return true;
    if(widthRatio>1.08||heightRatio>1.08)return true;
  }
  return false;
}
function go(from,to){
  if(animating||from===to||to<0||to>=slides.length)return;
  animating=true;
  var rs=getComputedStyle(document.documentElement);var dur=parseInt(rs.getPropertyValue('--ms-dur')||'600',10);var ease=rs.getPropertyValue('--ms-ease').trim()||'cubic-bezier(0.25,1,0.5,1)';
  var fromSlide=slides[from],toSlide=slides[to];
  var fromEls=getMagic(fromSlide);
  var toEls=getMagic(toSlide);
  var sharedIds=[];
  Object.keys(fromEls).forEach(function(id){if(toEls[id])sharedIds.push(id)});
  Object.keys(toEls).forEach(function(id){if(fromEls[id]&&sharedIds.indexOf(id)===-1)sharedIds.push(id)});

  // Shared stagger marking function — returns stagger count for cleanup timing
  function applyStagger(slide){
    var staggerMode=(slide.getAttribute('data-stagger')||'cascade').toLowerCase();
    if(staggerMode==='none'||staggerMode==='off')return 0;
    var toContent=getSlideContent(slide);
    var staggerIndex=0;
    // During FLIP transitions, build a set of "already visible" content from FROM slide
    // Elements with same tag+text on FROM slide don't need stagger (they're already on screen)
    var fromTexts={};
    if(sharedIds.length>0){
      var fc=getSlideContent(fromSlide);
      fc.querySelectorAll('h1,h2,h3,h4,h5,h6,p').forEach(function(el){
        fromTexts[el.tagName+'|'+el.textContent.trim()]=true;
      });
    }
    function isLayoutContainer(el){
      if(!el.children.length)return false;
      var d=getComputedStyle(el).display;
      return d==='flex'||d==='grid'||d==='inline-flex'||d==='inline-grid';
    }
    function hasVisualChrome(el){
      var cs=getComputedStyle(el);
      var hasBg=cs.backgroundColor&&cs.backgroundColor!=='rgba(0, 0, 0, 0)'&&cs.backgroundColor!=='transparent';
      var hasBorder=cs.borderStyle&&cs.borderStyle!=='none';
      var hasShadow=cs.boxShadow&&cs.boxShadow!=='none';
      return hasBg||hasBorder||hasShadow;
    }
    function hasSharedMagicDescendants(el){
      if(!el.querySelectorAll)return false;
      return Array.from(el.querySelectorAll('[data-magic-id]')).some(function(node){
        return sharedIds.indexOf(node.getAttribute('data-magic-id'))!==-1;
      });
    }
    function isTextBlock(el){
      if(!el||!el.matches)return false;
      return el.matches('h1,h2,h3,h4,h5,h6,p,blockquote,figcaption,.lead,.section-title,.hero-copy');
    }
    function markLeaf(el){
      if(sharedIds.length>0&&fromTexts[el.tagName+'|'+el.textContent.trim()])return;
      var cs=getComputedStyle(el);
      el.style.setProperty('--ms-stagger-final-opacity',cs.opacity||'1');
      el.style.setProperty('--ms-stagger-base-transform',cs.transform&&cs.transform!=='none'?cs.transform:'translateZ(0)');
      el.classList.add('ms-stagger-item');
      if(isTextBlock(el))el.classList.add('ms-stagger-text');
      el.style.setProperty('--stagger-index',staggerIndex);
      staggerIndex++;
    }
    function markStagger(parent){
      Array.from(parent.children).forEach(function(ch){
        if(ch.hasAttribute('data-magic-id'))return;
        if(ch.classList.contains('bg'))return;
        if(ch.hasAttribute('data-stagger-skip'))return;

        // Text blocks often contain inline language spans. Animate the block,
        // not the inline span, because transform does not apply to normal
        // inline text nodes and the stagger becomes visually invisible.
        if(isTextBlock(ch)&&!hasSharedMagicDescendants(ch)){
          markLeaf(ch);
          return;
        }

        // Layout containers (flex/grid): check if this is a FLIP transition or card grid
        if(isLayoutContainer(ch)){
          // FLIP groups stay untouched, but transparent layout wrappers should
          // recurse so nested timeline/list/stat items still stagger individually.
          var hasSharedChild=hasSharedMagicDescendants(ch);
          var isCardGrid=ch.classList.contains('card-grid');
          Array.from(ch.children).forEach(function(item){
            if(item.classList.contains('card-highlight')||item.classList.contains('card-dimmed'))isCardGrid=true;
          });
          if(isCardGrid&&sharedIds.length>0){
            return;
          }
          // Mixed layout wrapper: recurse into it. Shared descendants will be
          // skipped at the leaf level, while ordinary content still gets stagger.
          markStagger(ch);
          return;
        }

        // Non-layout wrapper with magic descendants: recurse deeper
        var hasMagicDescendants=hasSharedMagicDescendants(ch);
        if(hasMagicDescendants){
          markStagger(ch);
        } else if(ch.tagName==='UL'||ch.tagName==='OL'){
          Array.from(ch.children).forEach(function(li){
            if(li.tagName==='LI'){
              markLeaf(li);
            }
          });
        } else if(ch.children.length>0){
          // Has child elements — check if it's a visual component or a pure wrapper
          if(hasVisualChrome(ch)){
            // Visual component (card, stat-card) — animate as one unit
            markLeaf(ch);
          } else {
            // Transparent wrapper div — recurse into children so real content
            // (timeline rows, list items, headings) can stagger individually.
            markStagger(ch);
          }
        } else {
          // Leaf element (text node, image, etc.)
          markLeaf(ch);
        }
      });
    }
    markStagger(toContent);
    return staggerIndex;
  }

  if(sharedIds.length===0){
    var txName=toSlide.dataset.transition||'fade';
    toSlide.classList.add('active');
    toSlide.style.transition='none';toSlide.style.opacity='0';toSlide.style.visibility='visible';toSlide.style.zIndex='2';
    fitSlideLayout(toSlide);
    var staggerN=applyStagger(toSlide);
    void toSlide.offsetHeight;
    if(isFadeTransition(txName)){
      toSlide.style.transition='opacity '+dur+'ms '+ease;toSlide.style.opacity='1';
    } else {
      toSlide.style.opacity='';
      toSlide.style.animation='ms-'+txName+' '+dur+'ms '+ease+' both';
    }
    fromSlide.style.transition='opacity '+dur+'ms '+ease;fromSlide.style.opacity='0';
    setTimeout(function(){
      fromSlide.classList.remove('active');
      fromSlide.style.opacity='';fromSlide.style.visibility='';fromSlide.style.transition='';
      toSlide.style.zIndex='';toSlide.style.transition='';toSlide.style.animation='';
      toSlide.querySelectorAll('.ms-stagger-item').forEach(function(el){
        el.classList.remove('ms-stagger-item');
        el.classList.remove('ms-stagger-text');
        el.style.removeProperty('--ms-stagger-final-opacity');
        el.style.removeProperty('--ms-stagger-base-transform');
      });
      animating=false;
    },Math.max(dur+50,staggerN*80+550));
    cur=to;updateUI();updateHash();return;
  }

  // === PHASE 1: Measure FROM rects (FROM slide visible, no DOM changes yet) ===
  var fromRects={},fromStyles={};
  sharedIds.forEach(function(id){
    fromRects[id]=fromEls[id].getBoundingClientRect();
    fromStyles[id]=snapStyles(fromEls[id]);
  });

  // === PHASE 2: Measure TO rects (TO slide shown at opacity:0) ===
  toSlide.style.transition='none';toSlide.style.opacity='0';toSlide.style.visibility='visible';
  toSlide.classList.add('active');fitSlideLayout(toSlide);void toSlide.offsetHeight;
  var toRects={},toStyles={};
  sharedIds.forEach(function(id){
    toRects[id]=toEls[id].getBoundingClientRect();
    toStyles[id]=snapStyles(toEls[id]);
  });
  // Hide TO again immediately
  toSlide.style.visibility='hidden';toSlide.classList.remove('active');

  // === PHASE 3: Create one self-contained TO clone per shared element ===
  // Previous runtime used a dual-clone crossfade path for "similar" nodes
  // (FROM clone + TO clone). That strategy produces visible ghosting in real
  // decks because both versions of the same semantic object are on screen at
  // once. The fix is architectural: always animate a single TO clone with an
  // inverse FLIP transform, then swap back to the real TO element at the end.
  //
  // Tradeoff:
  // - We lose the old dual-version crossfade for complex matches
  // - We gain a hard guarantee that a shared element has only one animated
  //   visual instance during motion, which removes the "ghost" artifact
  //   entirely at the runtime layer.
  var pairs=[];
  sharedIds.forEach(function(id){
    var ft=fromEls[id].textContent.replace(/\s+/g,' ').trim(),tt=toEls[id].textContent.replace(/\s+/g,' ').trim();
    var sameText=ft===tt;
    var mode=sameText?'identical':'similar';
    // Keep the classification for future heuristics/debugging, but both paths
    // now render through the same single-clone inverse FLIP strategy.
    if(mode==='identical'){
      var fCS=getComputedStyle(fromEls[id]),tCS=getComputedStyle(toEls[id]);
      if(shouldCrossfadeIdentical(fromEls[id],toEls[id],fromRects[id],toRects[id],fCS,tCS))mode='similar';
    }
    var fr=fromRects[id],tr=toRects[id];
    var c=toEls[id].cloneNode(true);
    c.removeAttribute('data-magic-id');
    var labelMode=sameText&&isMagicNoWrapLabel(fromEls[id])&&isMagicNoWrapLabel(toEls[id])&&!hasMagicTransform(fromEls[id])&&!hasMagicTransform(toEls[id]);
    var p;
    if(labelMode){
      var fromLabel=visualLabelSnap(fromEls[id],fr),toLabel=visualLabelSnap(toEls[id],tr);
      applyVisualLabelSnap(c,fromLabel);
      document.body.appendChild(c);
      p={id:id,mode:mode,fr:fr,tr:tr,clone:c,label:true,finalLabel:toLabel};
    }else{
      var box=magicLayoutBox(toEls[id],tr);
      var fromMatrix=readMagicMatrix(fromEls[id],fr,box);
      var toMatrix=readMagicMatrix(toEls[id],tr,box);
      applySnap(c,toStyles[id]);
      placeMagicClone(c,tr,box);
      c.style.transform=matrixCss(fromMatrix);
      document.body.appendChild(c);
      p={id:id,mode:mode,fr:fr,tr:tr,clone:c,finalTransform:matrixCss(toMatrix)};
    }
    // Hide FROM element immediately after clone is appended to prevent double-display
    fromEls[id].style.visibility='hidden';
    pairs.push(p);
  });

  // === PHASE 4: Hide TO magic originals BEFORE making TO slide visible ===
  sharedIds.forEach(function(id){
    toEls[id].style.visibility='hidden';
  });

  // === PHASE 5: Slide swap with target-page transition ===
  // Show TO slide
  var txName=toSlide.dataset.transition||'fade';
  toSlide.style.transition='none';toSlide.style.animation='';toSlide.style.opacity='0';toSlide.style.visibility='visible';
  toSlide.style.zIndex='2';toSlide.classList.add('active');
  // CRITICAL: Hide FROM slide BEFORE forcing reflow — prevents one-frame double-display
  fromSlide.style.transition='none';fromSlide.style.opacity='0';fromSlide.style.visibility='hidden';fromSlide.classList.remove('active');
  void toSlide.offsetHeight;
  // Trigger stagger only after the visible slide swap has committed. If we add
  // stagger classes while the FROM slide is still on top, the entrance animation
  // can finish under the old slide and appear to be missing.
  var staggerN=applyStagger(toSlide);
  void toSlide.offsetHeight;

  // === PHASE 6: Animate (double rAF to ensure styles are committed) ===
  requestAnimationFrame(function(){requestAnimationFrame(function(){
    if(isFadeTransition(txName)){
      toSlide.style.transition='opacity '+dur+'ms '+ease;
      toSlide.style.opacity='1';
    }else{
      toSlide.style.opacity='';
      toSlide.style.animation='ms-'+txName+' '+dur+'ms '+ease+' both';
    }
    pairs.forEach(function(p){
      if(p.label){
        p.clone.style.transition=visualLabelTransition(dur,ease);
        applyVisualLabelSnap(p.clone,p.finalLabel);
      }else{
        p.clone.style.transition='transform '+dur+'ms '+ease;
        p.clone.style.transform=p.finalTransform;
      }
    });
    // Non-magic content entrance handled by CSS stagger animations
  })});

  // === PHASE 7: Swap clones back to the real TO originals with no overlap ===
  setTimeout(function(){
    sharedIds.forEach(function(id){
      toEls[id].style.visibility='visible';
    });
    pairs.forEach(function(p){p.clone.remove()});
    sharedIds.forEach(function(id){fromEls[id].style.visibility='';toEls[id].style.visibility=''});
    fromSlide.style.opacity='';fromSlide.style.visibility='';fromSlide.style.transition='';
    toSlide.style.zIndex='';toSlide.style.transition='';toSlide.style.animation='';
  },dur+20);
  // Clean up stagger after all animations finish
  setTimeout(function(){
    toSlide.querySelectorAll('.ms-stagger-item').forEach(function(el){
      el.classList.remove('ms-stagger-item');
      el.classList.remove('ms-stagger-text');
      el.style.removeProperty('--ms-stagger-final-opacity');
      el.style.removeProperty('--ms-stagger-base-transform');
      });
      animating=false;
  },Math.max(dur+40,staggerN*80+550));

  cur=to;updateUI();updateHash();
}
// ── URL hash sync ─────────────────────────────────────────────────────────
function updateHash(){
  if(history.replaceState){
    history.replaceState(null,null,'#'+(cur+1));
  }else{
    location.hash='#'+(cur+1);
  }
}
function restoreFromHash(){
  var h=location.hash.slice(1);
  var n=parseInt(h,10);
  if(n>=1&&n<=slides.length){
    cur=n-1;
    slides.forEach(function(s,i){
      s.classList.toggle('active',i===cur);
      if(i===cur){s.style.opacity='1';s.style.visibility='visible';}
      else{s.style.opacity='0';s.style.visibility='hidden';}
    });
    if(!MS_IS_OVERVIEW_EMBED)updateUI();
    fitSlideLayout(slides[cur]);
  }
}
if(location.hash)restoreFromHash();
else if(MS_IS_OVERVIEW_EMBED){
  fitSlideLayout(slides[cur]);
}
window.addEventListener('resize',function(){
  fitSlideLayout(slides[cur]);
});
if(!MS_IS_OVERVIEW_EMBED){
window.addEventListener('hashchange',restoreFromHash);
// ──────────────────────────────────────────────────────────────────────────
var cursorVisible=true;
function isMsTextEntryTarget(target){
  if(!target)return false;
  var el=target.nodeType===1?target:(target.parentElement||null);
  if(!el)return false;
  if(el.isContentEditable||el.closest('[contenteditable="true"]'))return true;
  return !!el.closest('input,textarea,select,[role="textbox"]');
}
function isMsContentEditableTarget(target){
  if(!target)return false;
  var el=target.nodeType===1?target:(target.parentElement||null);
  return !!(el&&(el.isContentEditable||el.closest('[contenteditable="true"]')));
}
function shouldIgnorePresentationShortcut(e){
  return isMsTextEntryTarget(e.target);
}
document.addEventListener('keydown',function(e){
  if(shouldIgnorePresentationShortcut(e))return;
  var overlayOpen=document.querySelector('#slide-overview.show,#qa-overview.show');
  if(overlayOpen&&['ArrowRight','ArrowDown','Space','ArrowLeft','ArrowUp'].indexOf(e.code)>-1){
    e.preventDefault();
    return;
  }
  if(e.code==='ArrowRight'||e.code==='ArrowDown'||e.code==='Space'){e.preventDefault();go(cur,cur+1);}
  if(e.code==='ArrowLeft'||e.code==='ArrowUp'){e.preventDefault();go(cur,cur-1);}
  if(e.code==='KeyC'&&!e.ctrlKey&&!e.metaKey&&!e.altKey){
    e.preventDefault();
    cursorVisible=!cursorVisible;
    var cursor=document.getElementById('ms-cursor');
    var trails=document.querySelectorAll('.ms-cursor-trail');
    if(cursor)cursor.style.display=cursorVisible?'':'none';
    trails.forEach(function(t){t.style.display=cursorVisible?'':'none';});
    document.body.style.cursor=cursorVisible?'none':'default';
  }
});
var _ct=null;
document.addEventListener('click',function(e){
  if(document.body.classList.contains('ms-edit-mode'))return;
  if(_ct){clearTimeout(_ct);_ct=null;
    e.preventDefault();
    if(window.getSelection)window.getSelection().removeAllRanges();
    if(!document.fullscreenElement)document.documentElement.requestFullscreen().catch(function(){});
    else document.exitFullscreen().catch(function(){});}
  else _ct=setTimeout(function(){_ct=null;go(cur,cur+1);},220);
});
updateUI();updateHash();
fitSlideLayout(slides[cur]);
  (function(){
  var dock=document.getElementById('slide-dock');
  var tip=document.getElementById('dock-tip');
  var hoverPreview=document.getElementById('dock-hover-preview');
  var hoverPreviewContent=hoverPreview?hoverPreview.querySelector('.dock-hover-preview-content'):null;
  var hoverPreviewMeta=hoverPreview?hoverPreview.querySelector('.dock-hover-preview-meta'):null;
  var navP=document.getElementById('nav-prev');
  var navN=document.getElementById('nav-next');
  if(!dock)return;
  var dockItems=[];
  var hoverPreviewFrame=null;
  var hoverPreviewLoadedIdx=-1;
  var hoverPreviewRequestedIdx=-1;
  var hoverPreviewPendingIdx=-1;
  var hoverPreviewPendingItem=null;
  var hoverPreviewTimer=null;
  var hoverPreviewVisible=false;
  function buildDockPreviewUrl(idx){
    var url=new URL(window.location.href);
    url.searchParams.set('ms_embed','overview');
    url.searchParams.set('ms_slide',String(idx+1));
    url.hash='#'+(idx+1);
    return url.toString();
  }
  function ensureDockPreviewFrame(){
    if(!hoverPreviewContent)return null;
    if(hoverPreviewFrame)return hoverPreviewFrame;
    hoverPreviewFrame=document.createElement('iframe');
    hoverPreviewFrame.loading='eager';
    hoverPreviewFrame.tabIndex=-1;
    hoverPreviewFrame.setAttribute('aria-hidden','true');
    hoverPreviewFrame.setAttribute('title','Dock preview');
    hoverPreviewFrame.addEventListener('load',function(){
      if(!hoverPreview)return;
      if(hoverPreviewRequestedIdx<0)return;
      hoverPreviewLoadedIdx=hoverPreviewRequestedIdx;
      hoverPreview.classList.remove('loading');
      hoverPreview.classList.add('ready');
      if(hoverPreviewPendingItem)positionDockPreview(hoverPreviewPendingItem);
    });
    hoverPreviewContent.appendChild(hoverPreviewFrame);
    return hoverPreviewFrame;
  }
  function refreshDockPreviewScale(){
    if(!hoverPreview||!hoverPreviewContent)return;
    var previewWidth=hoverPreview.clientWidth;
    if(!previewWidth)return;
    hoverPreviewContent.style.transform='scale('+(previewWidth/1920)+')';
  }
  function positionDockPreview(item){
    if(!hoverPreview||!item)return;
    var r=item.getBoundingClientRect();
    var dockRect=dock.getBoundingClientRect();
    var previewWidth=hoverPreview.offsetWidth||320;
    var left=r.left+r.width/2;
    var pad=Math.min(24,window.innerWidth*0.04);
    left=Math.max((previewWidth/2)+pad,Math.min(window.innerWidth-(previewWidth/2)-pad,left));
    hoverPreview.style.left=left+'px';
    hoverPreview.style.bottom=(window.innerHeight-dockRect.top+16)+'px';
    refreshDockPreviewScale();
  }
  function hideDockPreview(immediate){
    hoverPreviewPendingItem=null;
    hoverPreviewPendingIdx=-1;
    hoverPreviewRequestedIdx=-1;
    if(hoverPreviewTimer){
      clearTimeout(hoverPreviewTimer);
      hoverPreviewTimer=null;
    }
    if(!hoverPreview)return;
    hoverPreview.classList.remove('show','loading','ready');
    hoverPreviewVisible=false;
    if(immediate){
      hoverPreview.style.transition='none';
      hoverPreview.offsetHeight;
      hoverPreview.style.transition='';
    }
  }
  function beginDockPreviewLoading(item,idx){
    if(!hoverPreview||!item)return false;
    hoverPreviewRequestedIdx=idx;
    if(hoverPreviewMeta)hoverPreviewMeta.textContent=(idx+1)+' \u00b7 '+(item.dataset.label||('slide '+(idx+1)));
    positionDockPreview(item);
    if(hoverPreviewLoadedIdx===idx){
      hoverPreview.classList.remove('loading');
      hoverPreview.classList.add('ready','show');
      hoverPreviewVisible=true;
      return false;
    }
    hoverPreview.classList.add('show','loading');
    hoverPreview.classList.remove('ready');
    hoverPreviewVisible=true;
    return true;
  }
  function showDockPreviewNow(item){
    if(!hoverPreview||!item)return;
    var idx=parseInt(item.dataset.idx,10);
    if(!(idx>=0))return;
    var frame=ensureDockPreviewFrame();
    if(!beginDockPreviewLoading(item,idx))return;
    if(frame)frame.src=buildDockPreviewUrl(idx);
  }
  function scheduleDockPreview(item){
    if(!item||!hoverPreview)return;
    var idx=parseInt(item.dataset.idx,10);
    if(!(idx>=0))return;
    if(hoverPreviewPendingIdx===idx&&hoverPreviewTimer){
      hoverPreviewPendingItem=item;
      positionDockPreview(item);
      return;
    }
    hoverPreviewPendingItem=item;
    hoverPreviewPendingIdx=idx;
    if(!beginDockPreviewLoading(item,idx)){
      return;
    }
    if(hoverPreviewTimer)clearTimeout(hoverPreviewTimer);
    hoverPreviewTimer=setTimeout(function(){
      hoverPreviewTimer=null;
      if(hoverPreviewPendingItem)showDockPreviewNow(hoverPreviewPendingItem);
    },90);
  }
  slides.forEach(function(s,i){
    var d=document.createElement('div');
    d.className='dock-item';
    var heading=s.querySelector('h1,h2,h3');
    var label=heading?heading.textContent.trim():(s.dataset.id||'').replace(/-/g,' ');
    d.dataset.label=label||'slide '+(i+1);
    d.dataset.idx=i;
    d.addEventListener('click',function(e){e.stopPropagation();if(_ct){clearTimeout(_ct);_ct=null;}if(i!==cur)go(cur,i)});
    dock.appendChild(d);
    dockItems.push(d);
  });
  // Add preview button
  var previewBtn=document.createElement('div');
  previewBtn.className='dock-preview-btn';
  previewBtn.title='Overview (O)';
  previewBtn.addEventListener('click',function(e){e.stopPropagation();if(_ct){clearTimeout(_ct);_ct=null;}toggleOverview();});
  dock.appendChild(previewBtn);
  updateUI();
  // Auto-shrink dots + gap if dock would overflow screen width
  (function(){
    var maxW=window.innerWidth*0.88,n=dockItems.length,pad=40;
    // Try progressively smaller sizes until it fits
    var sizes=[{s:10,g:7},{s:8,g:5},{s:6,g:4},{s:5,g:3},{s:4,g:2}];
    for(var i=0;i<sizes.length;i++){
      var sz=sizes[i];
      if(n*sz.s+(n-1)*sz.g+pad<=maxW){
        if(i>0){
          dockItems.forEach(function(d){d.style.width=sz.s+'px';d.style.height=sz.s+'px';});
          dock.style.gap=sz.g+'px';
        }
        break;
      }
    }
  })();
  function setDockRest(){
    dock.style.setProperty('--dock-bg-left','0px');
    dock.style.setProperty('--dock-bg-right','0px');
    dockItems.forEach(function(d){
      if(d.classList.contains('dock-on')){
        d.style.transform='translate3d(0,0,0) scale(1.5)';
      }else{
        d.style.transform='translate3d(0,0,0) scale(1)';
      }
    });
    if(previewBtn)previewBtn.style.transform='translate3d(0,0,0) scale(1)';
  }
  var _raf=null,_lmx=0,_lmy=0;
  function mag(mx,my){
    _lmx=mx;
    _lmy=my;
    if(_raf)return;
    _raf=requestAnimationFrame(function(){
      _raf=null;
      if(_lmy<window.innerHeight-56){
        setDockRest();
        if(tip)tip.style.opacity='0';
        hideDockPreview();
        return;
      }
      var layoutItems=dockItems.slice();
      if(previewBtn)layoutItems.push(previewBtn);
      var bestD=null,bestDist=Infinity,bestIdx=0;
      var n=dockItems.length,layoutN=layoutItems.length,activeMin=1.5,maxScale=n>15?2.15:2.6;
      var centers=[],scales=[],baseSizes=[],gaps=[];
      var dockRect=dock.getBoundingClientRect();
      layoutItems.forEach(function(d,i){
        var base=d.offsetWidth||11,cx=dockRect.left+d.offsetLeft+base/2;
        var dist=Math.abs(_lmx-cx);
        centers[i]=cx;
        scales[i]=1;
        baseSizes[i]=base;
        if(i<n&&dist<bestDist){bestDist=dist;bestD=d;bestIdx=i;}
      });
      var pitch=n>1?Math.max(1,Math.abs(centers[Math.min(n-1,bestIdx+1)]-centers[Math.max(0,bestIdx-1)])/(bestIdx>0&&bestIdx<n-1?2:1)):24;
      var radius=pitch*2.35,previewHitRadius=Math.max(14,pitch*0.52);
      if(bestDist>radius){
        setDockRest();
        if(tip)tip.style.opacity='0';
        hideDockPreview();
        return;
      }
      dockItems.forEach(function(d,i){
        var dist=Math.abs(_lmx-centers[i]);
        if(dist<radius){
          var wave=Math.cos(dist/radius*Math.PI/2);
          var eased=Math.pow(Math.max(0,wave),1.35);
          scales[i]=1+(maxScale-1)*eased;
        }
        if(d.classList.contains('dock-on'))scales[i]=Math.max(activeMin,scales[i]);
      });
      for(var gi=0;gi<layoutN-1;gi++){
        gaps[gi]=Math.max(3,centers[gi+1]-centers[gi]-(baseSizes[gi]+baseSizes[gi+1])/2);
      }
      var baseLeft=centers[0]-baseSizes[0]/2;
      var baseRight=centers[layoutN-1]+baseSizes[layoutN-1]/2;
      var baseWidth=Math.max(1,baseRight-baseLeft);
      var scaledWidth=0;
      for(var wi=0;wi<layoutN;wi++){
        scaledWidth+=baseSizes[wi]*scales[wi];
        if(wi<layoutN-1)scaledWidth+=gaps[wi];
      }
      var anchor=Math.max(0,Math.min(1,(_lmx-baseLeft)/baseWidth));
      var targetLeft=baseLeft-(scaledWidth-baseWidth)*anchor;
      var cursor=targetLeft,visualLeft=Infinity,visualRight=-Infinity;
      layoutItems.forEach(function(d,i){
        var width=baseSizes[i]*scales[i];
        var targetCenter=cursor+width/2;
        var dx=targetCenter-centers[i];
        d.style.transform='translateX('+dx.toFixed(1)+'px) scale('+scales[i].toFixed(3)+')';
        visualLeft=Math.min(visualLeft,cursor);
        visualRight=Math.max(visualRight,cursor+width);
        cursor+=width+(i<layoutN-1?gaps[i]:0);
      });
      var bgPad=10;
      var leftOutset=Math.max(0,dockRect.left-visualLeft+bgPad);
      var rightOutset=Math.max(0,visualRight-dockRect.right+bgPad);
      dock.style.setProperty('--dock-bg-left',(-leftOutset).toFixed(1)+'px');
      dock.style.setProperty('--dock-bg-right',(-rightOutset).toFixed(1)+'px');
      if(bestD&&bestDist<=previewHitRadius&&tip){
        var r=bestD.getBoundingClientRect();
        tip.style.left=(r.left+r.width/2)+'px';
        tip.textContent=(parseInt(bestD.dataset.idx)+1)+' · '+bestD.dataset.label;
        tip.style.opacity='0';
        scheduleDockPreview(bestD);
      }else{
        if(tip)tip.style.opacity='0';
        hideDockPreview();
      }
    });
  }
  function reset(){
    setDockRest();
    if(tip)tip.style.opacity='0';
    hideDockPreview();
  }
  setDockRest();
  if(navP)navP.addEventListener('click',function(e){e.stopPropagation();if(_ct){clearTimeout(_ct);_ct=null;}go(cur,cur-1)});
  if(navN)navN.addEventListener('click',function(e){e.stopPropagation();if(_ct){clearTimeout(_ct);_ct=null;}go(cur,cur+1)});
  document.addEventListener('mousemove',function(e){
    var x=e.clientX,y=e.clientY,W=window.innerWidth,H=window.innerHeight;
    if(y>H-80){dock.classList.add('dock-up');mag(x,y);}
    else{dock.classList.remove('dock-up');reset();}
    if(navP)navP.classList.toggle('nav-show',x<100);
    if(navN)navN.classList.toggle('nav-show',x>W-100);
  });
  dock.addEventListener('mouseleave',reset);
  window.addEventListener('resize',function(){
    refreshDockPreviewScale();
    if(hoverPreviewPendingItem)positionDockPreview(hoverPreviewPendingItem);
  });
})();

// ── Slide overview panel ──────────────────────────────────────────────────
(function(){
  var overview=document.getElementById('slide-overview');
  var grid=overview?overview.querySelector('.overview-grid'):null;
  var closeBtn=overview?overview.querySelector('.overview-close'):null;
  var previewBtn=document.querySelector('.dock-preview-btn');
  var overviewCache=null;
  var overviewObserver=null;
  var overviewLoadQueue=[];
  var overviewQueueScheduled=false;
  var overviewHideTimer=null;
  function updateOverviewOverflow(){
    if(!overview||!grid)return;
    var maxScroll=Math.max(0,grid.scrollHeight-grid.clientHeight);
    overview.classList.toggle('has-top-overflow',grid.scrollTop>1);
    overview.classList.toggle('has-bottom-overflow',grid.scrollTop<maxScroll-1);
  }
  function buildOverviewFrameUrl(idx){
    var url=new URL(window.location.href);
    url.searchParams.set('ms_embed','overview');
    url.searchParams.set('ms_slide',String(idx+1));
    url.hash='#'+(idx+1);
    return url.toString();
  }
  function refreshOverviewScales(){
    if(!grid)return;
    var items=grid.querySelectorAll('.overview-item');
    items.forEach(function(item){
      var itemWidth=item.offsetWidth;
      if(!itemWidth)return;
      var itemHeight=Math.round(itemWidth*1080/1920);
      item.style.height=itemHeight+'px';
      var scale=itemWidth/1920;
      var content=item.querySelector('.overview-item-content');
      if(content)content.style.transform='scale('+scale+')';
    });
    updateOverviewOverflow();
  }
  function mountOverviewFrame(item){
    if(!item||item.dataset.frameMounted==='1')return;
    var idx=parseInt(item.dataset.idx,10);
    if(!(idx>=0))return;
    var content=item.querySelector('.overview-item-content');
    if(!content)return;
    var frame=document.createElement('iframe');
    frame.loading='lazy';
    frame.tabIndex=-1;
    frame.setAttribute('aria-hidden','true');
    frame.setAttribute('title','Slide '+(idx+1));
    frame.src=buildOverviewFrameUrl(idx);
    content.appendChild(frame);
    item.dataset.frameMounted='1';
    item.dataset.frameQueued='0';
  }
  function flushOverviewLoadQueue(deadline){
    overviewQueueScheduled=false;
    var start=performance.now();
    while(overviewLoadQueue.length){
      var item=overviewLoadQueue.shift();
      if(item&&item.isConnected)mountOverviewFrame(item);
      if(deadline&&typeof deadline.timeRemaining==='function'){
        if(deadline.timeRemaining()<4)break;
      }else if(performance.now()-start>12){
        break;
      }
    }
    if(overviewLoadQueue.length)scheduleOverviewLoadQueue();
  }
  function scheduleOverviewLoadQueue(){
    if(overviewQueueScheduled)return;
    overviewQueueScheduled=true;
    if('requestIdleCallback' in window){
      window.requestIdleCallback(flushOverviewLoadQueue,{timeout:120});
    }else{
      setTimeout(function(){flushOverviewLoadQueue();},16);
    }
  }
  function queueOverviewFrame(item){
    if(!item||item.dataset.frameMounted==='1'||item.dataset.frameQueued==='1')return;
    item.dataset.frameQueued='1';
    overviewLoadQueue.push(item);
    scheduleOverviewLoadQueue();
  }
  function ensureOverviewObserver(){
    if(overviewObserver||!grid||!('IntersectionObserver' in window))return;
    overviewObserver=new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting)queueOverviewFrame(entry.target);
      });
    },{
      root:grid,
      rootMargin:'260px 0px',
      threshold:0.01
    });
  }
  function observeOverviewItems(){
    if(!grid)return;
    var items=grid.querySelectorAll('.overview-item');
    if(overviewObserver){
      items.forEach(function(item){overviewObserver.observe(item);});
    }else{
      items.forEach(function(item,idx){
        if(idx<8||idx===cur)queueOverviewFrame(item);
      });
    }
  }
  function primeOverviewFrames(){
    if(!grid)return;
    var items=Array.from(grid.querySelectorAll('.overview-item'));
    if(items[cur])queueOverviewFrame(items[cur]);
    items.slice(0,6).forEach(function(item){queueOverviewFrame(item);});
  }

  function toggleOverview(){
    if(!overview)return;
    var isShown=overview.classList.contains('show');
    if(isShown){
      closeOverview();
    }else{
      openOverview();
    }
  }

  function openOverview(){
    if(!overview||!grid)return;
    var qaOverview=document.getElementById('qa-overview');
    if(qaOverview&&qaOverview.classList.contains('show')&&typeof window.closeQaOverview==='function'){
      window.closeQaOverview();
    }
    if(overviewHideTimer){
      clearTimeout(overviewHideTimer);
      overviewHideTimer=null;
    }
    overview.classList.add('showing');
    requestAnimationFrame(function(){
      requestAnimationFrame(function(){
        overview.classList.add('show');
      });
    });
    if(previewBtn)previewBtn.classList.add('active');

    // Generate thumbnails only if not cached
    if(!overviewCache){
      grid.innerHTML='';
      slides.forEach(function(slide,idx){
        var item=document.createElement('div');
        item.className='overview-item';
        if(idx===cur)item.classList.add('current');
        item.dataset.idx=idx;
        item.dataset.frameMounted='0';
        item.dataset.frameQueued='0';
        copyComputedBackground(resolveOverviewBackgroundSource(slide),item);

        var number=document.createElement('div');
        number.className='overview-item-number';
        number.textContent=(idx+1)+' / '+slides.length;
        item.appendChild(number);

        var content=document.createElement('div');
        content.className='overview-item-content';
        // Calculate scale based on actual item width (accounting for grid auto-fill)
        // Use a temporary measurement after item is added to grid
        var tempScale=0.16667; // fallback: 320/1920
        content.style.transform='scale('+tempScale+')';
        item.appendChild(content);

        item.addEventListener('click',function(){
          closeOverview();
          if(idx!==cur)go(cur,idx);
        });

        grid.appendChild(item);
      });

      overviewCache=true;
      ensureOverviewObserver();
      observeOverviewItems();
    }

    // Update current marker + scale every time the overview opens so cached
    // thumbnails stay aligned after resizes or content edits.
    var items=grid.querySelectorAll('.overview-item');
    items.forEach(function(item,idx){
      item.classList.toggle('current',idx===cur);
    });
    primeOverviewFrames();
    requestAnimationFrame(refreshOverviewScales);
  }

  function closeOverview(){
    if(!overview)return;
    overview.classList.remove('show');
    overview.classList.remove('has-top-overflow','has-bottom-overflow');
    if(previewBtn)previewBtn.classList.remove('active');
    if(overviewHideTimer)clearTimeout(overviewHideTimer);
    overviewHideTimer=setTimeout(function(){
      overview.classList.remove('showing');
      overviewHideTimer=null;
    },320);
  }

  if(closeBtn)closeBtn.addEventListener('click',function(e){
    e.stopPropagation();
    if(_ct){clearTimeout(_ct);_ct=null;}
    closeOverview();
  });
  window.addEventListener('resize',function(){
    if(overviewCache)requestAnimationFrame(refreshOverviewScales);
  });
  if(grid)grid.addEventListener('scroll',updateOverviewOverflow,{passive:true});

  if(overview)overview.addEventListener('click',function(e){
    if(e.target===overview||e.target===grid){
      e.stopPropagation();
      if(_ct){clearTimeout(_ct);_ct=null;}
      closeOverview();
    }
  });

  // Keyboard shortcut: O key
  document.addEventListener('keydown',function(e){
    if(e.code==='Escape'&&overview.classList.contains('show')){
      e.preventDefault();
      closeOverview();
      return;
    }
    if(shouldIgnorePresentationShortcut(e))return;
    if(e.code==='KeyO'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!document.body.classList.contains('ms-edit-mode')){
      e.preventDefault();
      toggleOverview();
    }
  });

  window.closeOverview=closeOverview;
  window.toggleOverview=toggleOverview;
})();

// ── QA overview panel ─────────────────────────────────────────────────────
(function(){
  if(!MS_QA_ALLOWED){
    window.closeQaOverview=function(){};
    window.openQaOverview=function(){};
    window.toggleQaOverview=function(){};
    return;
  }
  var qa=document.getElementById('qa-overview');
  var grid=qa?qa.querySelector('.qa-grid'):null;
  var closeBtn=qa?qa.querySelector('.qa-close'):null;
  var summary=document.getElementById('qa-summary');
  var issueEditor=qa?qa.querySelector('.qa-issue-editor'):null;
  var issueForm=qa?qa.querySelector('.qa-issue-dialog'):null;
  var issueTitle=document.getElementById('qa-issue-title');
  var issueTextarea=document.getElementById('qa-issue-note');
  var issueError=qa?qa.querySelector('.qa-issue-error'):null;
  var issueCancel=qa?qa.querySelector('.qa-issue-cancel'):null;
  var issueSave=qa?qa.querySelector('.qa-issue-save'):null;
  var qaCache=false;
  var qaObserver=null;
  var qaLoadQueue=[];
  var qaQueueScheduled=false;
  var qaHideTimer=null;
  var qaIssues=emptyQaIssues();
  var qaIssuesLoaded=false;
  var qaIssuesLoading=null;
  var editingIssueIdx=null;

  function emptyQaIssues(){
    return {schemaVersion:1,qaRevision:0,updatedAt:null,issues:[]};
  }
  function qaIssueApiUrl(){
    var m=window.location.pathname.match(/^\/deck\/[^/]+/);
    return m?m[0]+'/qa-issues':'';
  }
  function normalizeQaIssues(data){
    var doc=emptyQaIssues();
    if(data&&typeof data==='object'){
      doc.schemaVersion=Number.isInteger(data.schemaVersion)?data.schemaVersion:1;
      doc.qaRevision=Number.isInteger(data.qaRevision)?data.qaRevision:0;
      doc.updatedAt=typeof data.updatedAt==='string'?data.updatedAt:null;
      if(Array.isArray(data.issues)){
        doc.issues=data.issues.filter(function(issue){return issue&&typeof issue==='object';}).map(function(issue){
          return {
            id:String(issue.id||''),
            slide:parseInt(issue.slide,10)||0,
            slideId:typeof issue.slideId==='string'?issue.slideId:'',
            note:typeof issue.note==='string'?issue.note:'',
            resolved:issue.resolved===true,
            createdAt:typeof issue.createdAt==='string'?issue.createdAt:'',
            updatedAt:typeof issue.updatedAt==='string'?issue.updatedAt:'',
            resolvedAt:typeof issue.resolvedAt==='string'?issue.resolvedAt:null,
            resolvedInRevision:Number.isInteger(issue.resolvedInRevision)?issue.resolvedInRevision:null,
            resolution:typeof issue.resolution==='string'?issue.resolution:null,
            changedFiles:Array.isArray(issue.changedFiles)?issue.changedFiles.filter(function(file){return typeof file==='string';}):[]
          };
        });
      }
    }
    return doc;
  }
  function loadQaIssues(force){
    if(!force&&qaIssuesLoaded)return Promise.resolve(qaIssues);
    if(qaIssuesLoading)return qaIssuesLoading;
    var url=qaIssueApiUrl();
    if(!url){
      qaIssuesLoaded=true;
      return Promise.resolve(qaIssues);
    }
    qaIssuesLoading=fetch(url,{headers:{'Accept':'application/json'}})
      .then(function(r){return r.ok?r.json():Promise.reject(new Error('QA issue load failed'));})
      .then(function(data){
        qaIssues=normalizeQaIssues(data);
        qaIssuesLoaded=true;
        qaIssuesLoading=null;
        applyQaIssuesToCards();
        updateQaSummary();
        return qaIssues;
      })
      .catch(function(err){
        console.warn(err);
        qaIssuesLoaded=true;
        qaIssuesLoading=null;
        updateQaSummary();
        return qaIssues;
      });
    return qaIssuesLoading;
  }
  function saveQaIssues(){
    var url=qaIssueApiUrl();
    if(!url)return Promise.reject(new Error('QA issue API is unavailable'));
    return fetch(url,{
      method:'POST',
      headers:{'Content-Type':'application/json','Accept':'application/json'},
      body:JSON.stringify(qaIssues)
    })
      .then(function(r){return r.ok?r.json():Promise.reject(new Error('QA issue save failed'));})
      .then(function(data){
        qaIssues=normalizeQaIssues(data);
        qaIssuesLoaded=true;
        applyQaIssuesToCards();
        updateQaSummary();
        return qaIssues;
      });
  }
  function activeIssueForSlide(idx){
    var slideNo=idx+1;
    return qaIssues.issues.find(function(issue){return issue.slide===slideNo&&!issue.resolved;})||null;
  }
  function unresolvedIssueCount(){
    return qaIssues.issues.filter(function(issue){return !issue.resolved;}).length;
  }
  function slideIdForIndex(idx){
    var slide=slides[idx];
    return slide?(slide.getAttribute('data-id')||''):'';
  }
  function nowIso(){
    return new Date().toISOString();
  }
  function issueIdForSlide(idx){
    var stamp=nowIso().replace(/[-:.TZ]/g,'').slice(0,14);
    return 'slide-'+String(idx+1).padStart(2,'0')+'-'+stamp;
  }
  function setIssueError(text){
    if(issueError)issueError.textContent=text||'';
  }
  function closeIssueEditor(){
    editingIssueIdx=null;
    setIssueError('');
    if(issueEditor)issueEditor.hidden=true;
    if(issueTextarea)issueTextarea.value='';
  }
  function openIssueEditor(idx){
    if(!issueEditor||!issueTextarea)return;
    editingIssueIdx=idx;
    var issue=activeIssueForSlide(idx);
    if(issueTitle)issueTitle.textContent='Slide '+(idx+1)+' revision request';
    issueTextarea.value=issue?issue.note:'';
    setIssueError('');
    issueEditor.hidden=false;
    setTimeout(function(){issueTextarea.focus();},0);
  }
  function saveIssueFromEditor(){
    if(editingIssueIdx===null||!issueTextarea)return;
    var note=issueTextarea.value.trim();
    if(!note){
      setIssueError('Please describe what should change before saving.');
      issueTextarea.focus();
      return;
    }
    var idx=editingIssueIdx;
    var now=nowIso();
    var issue=activeIssueForSlide(idx);
    if(issue){
      issue.note=note;
      issue.slideId=slideIdForIndex(idx);
      issue.updatedAt=now;
    }else{
      qaIssues.issues.push({
        id:issueIdForSlide(idx),
        slide:idx+1,
        slideId:slideIdForIndex(idx),
        note:note,
        resolved:false,
        createdAt:now,
        updatedAt:now,
        resolvedAt:null,
        resolvedInRevision:null,
        resolution:null,
        changedFiles:[]
      });
    }
    qaIssues.updatedAt=now;
    if(issueSave)issueSave.disabled=true;
    saveQaIssues()
      .then(function(){
        closeIssueEditor();
      })
      .catch(function(err){
        console.warn(err);
        setIssueError('Could not save the revision request. Confirm the preview server is running.');
      })
      .finally(function(){
        if(issueSave)issueSave.disabled=false;
      });
  }
  function applyQaIssuesToCards(){
    if(!grid)return;
    grid.querySelectorAll('.qa-card').forEach(function(item){
      var idx=parseInt(item.dataset.idx,10);
      var issue=activeIssueForSlide(idx);
      var hasIssue=!!issue;
      item.classList.toggle('has-issue',hasIssue);
      item.dataset.issueId=hasIssue?issue.id:'';
      var note=item.querySelector('.qa-note-preview');
      if(note){
        note.textContent=hasIssue?issue.note:'';
        note.title=hasIssue?issue.note:'';
      }
      var btn=item.querySelector('.qa-issue-btn');
      if(btn){
        btn.textContent=hasIssue?'Revision saved':'Revise slide';
        btn.setAttribute('aria-label',(hasIssue?'Edit revision request for slide ':'Request revision for slide ')+(idx+1));
      }
    });
  }

  function buildQaFrameUrl(idx){
    var url=new URL(window.location.href);
    url.searchParams.delete('ms_qa');
    url.searchParams.delete('ms_qa_capture');
    url.searchParams.set('ms_embed','overview');
    url.searchParams.set('ms_slide',String(idx+1));
    url.hash='#'+(idx+1);
    return url.toString();
  }
  function markQaFrameReady(item,status){
    if(!item)return;
    item.dataset.scanned='1';
    item.dataset.status=status||'ready';
    updateQaSummary();
    requestAnimationFrame(refreshQaScales);
  }
  function waitForQaFrameRendered(frame){
    function settleEmbeddedDocument(status){
      try{
        var doc=frame.contentDocument;
        var win=frame.contentWindow;
        if(!doc)return Promise.resolve(status||'ready');
        var fontsReady=(doc.fonts&&doc.fonts.ready)?doc.fonts.ready.catch(function(){return null;}):Promise.resolve();
        var imagesReady=Promise.all(Array.from(doc.images||[]).map(function(img){
          if(img.complete)return Promise.resolve();
          return new Promise(function(resolve){
            function done(){
              img.removeEventListener('load',done);
              img.removeEventListener('error',done);
              resolve();
            }
            img.addEventListener('load',done,{once:true});
            img.addEventListener('error',done,{once:true});
            if(img.decode)img.decode().then(done).catch(done);
          });
        })).catch(function(){return null;});
        return Promise.all([fontsReady,imagesReady]).then(function(){
          return new Promise(function(resolve){
            var raf=(win&&win.requestAnimationFrame)?win.requestAnimationFrame.bind(win):window.requestAnimationFrame.bind(window);
            raf(function(){
              raf(function(){
                setTimeout(function(){resolve(status||'ready');},MS_QA_CAPTURE_MODE?260:120);
              });
            });
          });
        });
      }catch(err){
        return new Promise(function(resolve){
          setTimeout(function(){resolve(status||'ready');},MS_QA_CAPTURE_MODE?320:160);
        });
      }
    }
    return new Promise(function(resolve){
      var done=false;
      function afterLoad(status){
        if(done)return;
        done=true;
        settleEmbeddedDocument(status).then(resolve,function(){resolve(status||'ready');});
      }
      frame.addEventListener('load',function(){afterLoad('ready');},{once:true});
      frame.addEventListener('error',function(){afterLoad('error');},{once:true});
      setTimeout(function(){
        try{
          var doc=frame.contentDocument;
          if(doc&&doc.readyState==='complete'&&frame.contentWindow&&frame.contentWindow.location.href!=='about:blank'){
            afterLoad('ready');
          }
        }catch(err){}
      },0);
    });
  }
  function refreshQaScales(){
    if(!grid)return;
    grid.querySelectorAll('.qa-card').forEach(function(item){
      var thumb=item.querySelector('.qa-thumb');
      var content=item.querySelector('.qa-frame-content');
      var head=item.querySelector('.qa-card-head');
      if(!thumb||!content)return;
      var width=thumb.offsetWidth;
      if(!width)return;
      var thumbHeight=Math.round(width*1080/1920);
      thumb.style.height=thumbHeight+'px';
      content.style.transform='scale('+(width/1920)+')';
      var headHeight=head?Math.ceil(head.getBoundingClientRect().height||head.offsetHeight||0):0;
      item.style.minHeight=(thumbHeight+headHeight)+'px';
    });
  }
  function mountQaFrame(item){
    if(!item||item.dataset.frameMounted==='1')return;
    var idx=parseInt(item.dataset.idx,10);
    if(!(idx>=0))return;
    var content=item.querySelector('.qa-frame-content');
    if(!content)return;
    var frame=document.createElement('iframe');
    frame.loading=MS_QA_CAPTURE_MODE?'eager':(idx<6?'eager':'lazy');
    frame.tabIndex=-1;
    frame.setAttribute('aria-hidden','true');
    frame.setAttribute('title','QA slide '+(idx+1));
    var timeoutMs=MS_QA_CAPTURE_MODE?30000:9000;
    var timeout=setTimeout(function(){
      if(item.dataset.scanned==='1')return;
      item.dataset.status='timeout';
      if(MS_QA_CAPTURE_MODE)updateQaSummary();
      else markQaFrameReady(item,'timeout');
    },timeoutMs);
    frame.src=buildQaFrameUrl(idx);
    content.appendChild(frame);
    waitForQaFrameRendered(frame).then(function(status){
      clearTimeout(timeout);
      if(item.dataset.scanned!=='1')markQaFrameReady(item,status);
    });
    item.dataset.frameMounted='1';
    item.dataset.frameQueued='0';
  }
  function flushQaLoadQueue(deadline){
    qaQueueScheduled=false;
    var start=performance.now();
    while(qaLoadQueue.length){
      var item=qaLoadQueue.shift();
      if(item&&item.isConnected)mountQaFrame(item);
      if(deadline&&typeof deadline.timeRemaining==='function'){
        if(deadline.timeRemaining()<4)break;
      }else if(performance.now()-start>16){
        break;
      }
    }
    if(qaLoadQueue.length)scheduleQaLoadQueue();
  }
  function scheduleQaLoadQueue(){
    if(qaQueueScheduled)return;
    qaQueueScheduled=true;
    if('requestIdleCallback' in window){
      window.requestIdleCallback(flushQaLoadQueue,{timeout:160});
    }else{
      setTimeout(function(){flushQaLoadQueue();},16);
    }
  }
  function queueQaFrame(item){
    if(!item||item.dataset.frameMounted==='1'||item.dataset.frameQueued==='1')return;
    item.dataset.frameQueued='1';
    qaLoadQueue.push(item);
    scheduleQaLoadQueue();
  }
  function ensureQaObserver(){
    if(MS_QA_CAPTURE_MODE)return;
    if(qaObserver||!grid||!('IntersectionObserver' in window))return;
    qaObserver=new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting)queueQaFrame(entry.target);
      });
    },{
      root:grid,
      rootMargin:'420px 0px',
      threshold:0.01
    });
  }
  function observeQaItems(){
    if(!grid)return;
    var items=grid.querySelectorAll('.qa-card');
    if(MS_QA_CAPTURE_MODE){
      items.forEach(function(item){queueQaFrame(item);});
      return;
    }
    if(qaObserver){
      items.forEach(function(item){qaObserver.observe(item);});
    }else{
      items.forEach(function(item,idx){if(idx<8||idx===cur)queueQaFrame(item);});
    }
  }
  function primeQaFrames(){
    if(!grid)return;
    var items=Array.from(grid.querySelectorAll('.qa-card'));
    if(MS_QA_CAPTURE_MODE){
      items.forEach(function(item){queueQaFrame(item);});
      return;
    }
    if(items[cur])queueQaFrame(items[cur]);
    items.slice(0,6).forEach(function(item){queueQaFrame(item);});
  }
  function updateQaSummary(){
    if(!summary||!grid)return;
    var cards=Array.from(grid.querySelectorAll('.qa-card'));
    var pending=cards.filter(function(item){return item.dataset.scanned!=='1';}).length;
    var timedOut=cards.filter(function(item){return item.dataset.status==='timeout'&&item.dataset.scanned!=='1';}).length;
    var errored=cards.filter(function(item){return item.dataset.status==='error';}).length;
    var issueCount=unresolvedIssueCount();
    summary.textContent=slides.length+' slides'+(issueCount?' - '+issueCount+' revision request'+(issueCount===1?'':'s'):'')+(pending?' - '+pending+' loading frames'+(timedOut?' ('+timedOut+' timed out)':''):' - ready for visual review')+(errored?' - '+errored+' frame error'+(errored===1?'':'s'):'');
    document.body.dataset.msQaSlides=String(slides.length);
    document.body.dataset.msQaPending=String(pending);
    document.body.dataset.msQaTimeouts=String(timedOut);
    document.body.dataset.msQaErrors=String(errored);
    document.body.classList.toggle('ms-qa-ready',pending===0&&timedOut===0&&errored===0);
  }
  function applyQaFilter(){
    if(!grid)return;
    grid.querySelectorAll('.qa-card').forEach(function(item){
      item.dataset.hidden='false';
    });
  }
  function buildQaCards(){
    if(!grid||qaCache)return;
    grid.querySelectorAll('.qa-card').forEach(function(card){card.remove();});
    slides.forEach(function(slide,idx){
      var item=document.createElement('div');
      item.className='qa-card';
      if(idx===cur)item.classList.add('current');
      item.dataset.idx=idx;
      item.dataset.status='pending';
      item.dataset.scanned='0';
      item.dataset.frameMounted='0';
      item.dataset.frameQueued='0';

      var thumb=document.createElement('div');
      thumb.className='qa-thumb';
      copyComputedBackground(resolveOverviewBackgroundSource(slide),thumb);
      var content=document.createElement('div');
      content.className='qa-frame-content';
      content.style.transform='scale(0.2708)';
      thumb.appendChild(content);
      item.appendChild(thumb);

      var head=document.createElement('div');
      head.className='qa-card-head';
      var page=document.createElement('div');
      page.className='qa-page';
      var title=document.createElement('strong');
      title.textContent='Slide '+(idx+1)+' / '+slides.length;
      page.appendChild(title);
      var note=document.createElement('div');
      note.className='qa-note-preview';
      page.appendChild(note);
      var issueBtn=document.createElement('button');
      issueBtn.type='button';
      issueBtn.className='qa-issue-btn';
      issueBtn.textContent='Revise slide';
      issueBtn.addEventListener('click',function(e){
        e.preventDefault();
        e.stopPropagation();
        openIssueEditor(idx);
      });
      head.appendChild(page);
      head.appendChild(issueBtn);
      item.appendChild(head);

      item.addEventListener('click',function(e){
        e.stopPropagation();
        closeQaOverview();
        if(idx!==cur)go(cur,idx);
      });
      grid.appendChild(item);
    });
    qaCache=true;
    ensureQaObserver();
    observeQaItems();
    applyQaIssuesToCards();
  }
  function openQaOverview(){
    if(!qa||!grid)return;
    var regularOverview=document.getElementById('slide-overview');
    if(regularOverview&&regularOverview.classList.contains('show')&&typeof window.closeOverview==='function')window.closeOverview();
    if(qaHideTimer){
      clearTimeout(qaHideTimer);
      qaHideTimer=null;
    }
    buildQaCards();
    qa.classList.add('showing');
    qa.setAttribute('aria-hidden','false');
    requestAnimationFrame(function(){
      requestAnimationFrame(function(){
        qa.classList.add('show');
        refreshQaScales();
      });
    });
    grid.querySelectorAll('.qa-card').forEach(function(item,idx){
      item.classList.toggle('current',idx===cur);
    });
    updateQaSummary();
    applyQaFilter();
    loadQaIssues(true);
    primeQaFrames();
  }
  function closeQaOverview(){
    if(!qa)return;
    qa.classList.remove('show');
    qa.setAttribute('aria-hidden','true');
    if(qaHideTimer)clearTimeout(qaHideTimer);
    qaHideTimer=setTimeout(function(){
      qa.classList.remove('showing');
      qaHideTimer=null;
    },280);
  }
  function toggleQaOverview(){
    if(!qa)return;
    if(qa.classList.contains('show'))closeQaOverview();
    else openQaOverview();
  }

  if(qa)qa.addEventListener('click',function(e){
    e.stopPropagation();
  });
  if(issueForm)issueForm.addEventListener('keydown',function(e){
    if(e.code!=='Escape')e.stopPropagation();
  },true);
  if(issueForm)issueForm.addEventListener('submit',function(e){
    e.preventDefault();
    e.stopPropagation();
    saveIssueFromEditor();
  });
  if(issueCancel)issueCancel.addEventListener('click',function(e){
    e.preventDefault();
    e.stopPropagation();
    closeIssueEditor();
  });
  if(issueEditor)issueEditor.addEventListener('click',function(e){
    if(e.target===issueEditor)closeIssueEditor();
  });
  if(closeBtn)closeBtn.addEventListener('click',function(e){
    e.stopPropagation();
    closeQaOverview();
  });
  window.addEventListener('resize',function(){
    if(qaCache)requestAnimationFrame(refreshQaScales);
  });
  document.addEventListener('keydown',function(e){
    if(e.code==='Escape'&&issueEditor&&!issueEditor.hidden){
      e.preventDefault();
      closeIssueEditor();
      return;
    }
    if(e.code==='Escape'&&qa&&qa.classList.contains('show')){
      e.preventDefault();
      closeQaOverview();
      return;
    }
    if(shouldIgnorePresentationShortcut(e))return;
    if(e.code==='KeyQ'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!document.body.classList.contains('ms-edit-mode')){
      e.preventDefault();
      toggleQaOverview();
    }
  });
  window.closeQaOverview=closeQaOverview;
  window.openQaOverview=openQaOverview;
  window.toggleQaOverview=toggleQaOverview;
  if(MS_QA_MODE)setTimeout(openQaOverview,80);
})();
}

// ── Uploadable image placeholders ─────────────────────────────────────────
(function(){
  if(MS_IS_OVERVIEW_EMBED)return;
  // Hide toolbar when opened as a local file (no server available)
  var toolbar=document.getElementById('ms-toolbar');
  if(toolbar){
    if(window.location.protocol==='file:')toolbar.style.display='none';
    else toolbar.addEventListener('click',function(e){e.stopPropagation();if(_ct){clearTimeout(_ct);_ct=null;}});
  }

  // Show upload overlay on hover for any .uploadable-wrap
  document.querySelectorAll('.uploadable-wrap').forEach(function(wrap){
    var btn=wrap.querySelector('.upload-btn');
    if(!btn)return;
    wrap.addEventListener('mouseenter',function(){btn.style.opacity='1';});
    wrap.addEventListener('mouseleave',function(){btn.style.opacity='0';});
    wrap.addEventListener('click',function(e){e.stopPropagation();if(_ct){clearTimeout(_ct);_ct=null;}});
  });

  // Handle file selection → base64 inline
  window.msHandleImageUpload=function(input,id){
    var file=input.files[0];
    if(!file)return;
    var reader=new FileReader();
    reader.onload=function(e){
      var wrap=input.closest('.uploadable-wrap');
      var img=wrap.querySelector('img[data-uploadable="'+id+'"]');
      var placeholder=wrap.querySelector('.upload-placeholder');
      if(img){img.src=e.target.result;img.style.display='block';}
      if(placeholder){placeholder.style.display='none';}
      // Mark dirty after upload
      if(typeof markDirty==='function')markDirty();
    };
    reader.readAsDataURL(file);
  };

  // Toast helper
  function showToast(msg,duration){
    var t=document.getElementById('ms-toast');
    if(!t)return;
    t.textContent=msg;t.style.opacity='1';
    clearTimeout(t._tid);
    t._tid=setTimeout(function(){t.style.opacity='0';},duration||3000);
  }

  // Build self-contained HTML (inline all local images as base64)
  function buildHTML(callback){
    var urls=[];
    document.querySelectorAll('[style*="background-image"]').forEach(function(el){
      var m=el.style.backgroundImage.match(/url\(["']?([^"')]+)["']?\)/);
      if(m&&!m[1].startsWith('data:')&&!m[1].startsWith('http'))urls.push(m[1]);
    });
    document.querySelectorAll('img[src]').forEach(function(el){
      if(!el.src.startsWith('data:')&&!el.src.startsWith('http')&&!el.src.startsWith('blob:'))urls.push(el.getAttribute('src'));
    });
    urls=[...new Set(urls)];
    Promise.all(urls.map(function(url){
      return fetch(url).then(function(r){return r.blob();}).then(function(blob){
        return new Promise(function(res){var fr=new FileReader();fr.onload=function(){res({url:url,data:fr.result});};fr.readAsDataURL(blob);});
      }).catch(function(){return{url:url,data:null};});
    })).then(function(results){
      var map={};results.forEach(function(r){if(r.data)map[r.url]=r.data;});
      var clone=document.documentElement.cloneNode(true);
      if(clone.body)clone.body.classList.remove('ms-edit-mode');
      clone.querySelectorAll('.slide').forEach(function(s){
        s.classList.remove('active');
        ['transform','opacity','visibility'].forEach(function(p){s.style.removeProperty(p);});
      });
      clone.querySelectorAll('[contenteditable]').forEach(function(el){
        el.removeAttribute('contenteditable');
      });
      clone.querySelectorAll('[data-magic-id]').forEach(function(el){
        ['transform','transition','position','top','left','width','height'].forEach(function(p){el.style.removeProperty(p);});
      });
      clone.querySelectorAll('.ms-nowrap[data-ms-nowrap-token],.ms-cjk-token[data-ms-cjk-token]').forEach(function(span){
        span.replaceWith(document.createTextNode(span.textContent||''));
      });
      clone.querySelectorAll('.ms-cjk-protected,.ms-cjk-wrapped').forEach(function(el){
        el.classList.remove('ms-cjk-protected','ms-cjk-wrapped');
      });
      clone.querySelectorAll('.ms-cjk-balance').forEach(function(el){
        el.classList.remove('ms-cjk-balance');
      });
      clone.querySelectorAll('[style*="background-image"]').forEach(function(el){
        var m=el.style.backgroundImage.match(/url\(["']?([^"')]+)["']?\)/);
        if(m&&map[m[1]])el.style.backgroundImage='url('+map[m[1]]+')';
      });
      clone.querySelectorAll('img[src]').forEach(function(el){
        var s=el.getAttribute('src');if(map[s])el.src=map[s];
      });
      // Strip runtime so saved file is a clean skeleton
      ['ms-toolbar','ms-deck-badge','ms-rich-toolbar','ms-toast','ms-cursor','ms-cursor-trail-0','ms-cursor-trail-1','ms-cursor-trail-2','ms-cursor-trail-3','ms-cursor-trail-4','progress','counter','slide-dock','dock-tip','dock-hover-preview','nav-prev','nav-next','slide-overview','qa-overview'].forEach(function(id){
        var el=clone.querySelector('#'+id);if(el)el.remove();
      });
      clone.querySelectorAll('style').forEach(function(s){
        s.textContent=s.textContent.replace(/\\/\\* === injected by inject-runtime\\.py === \\*\\/[\\s\\S]*?\\/\\* === end injected CSS === \\*\\//g,'');
      });
      clone.querySelectorAll('script[src*="lucide"]').forEach(function(s){s.remove();});
      clone.querySelectorAll('script:not([src])').forEach(function(s){
        if(s.textContent.indexOf('var slides=document.querySelectorAll')>-1)s.remove();
      });
      callback('<!DOCTYPE html>\\n'+clone.outerHTML);
    });
  }

  // ── Dirty state tracking ─────────────────────────────────────────────────
  var dirty=false,saving=false;
  var saveBtn=document.getElementById('ms-save-btn');
  var saveBtnText=saveBtn?saveBtn.querySelector('.ms-save-text'):null;
  function getDeckBase(){
    if(window.location.protocol==='file:')return '';
    var m=window.location.pathname.match(/^\/deck\/[^/]+/);
    return m?m[0]:'';
  }
  function getDeckLabel(){
    var m=window.location.pathname.match(/^\/deck\/([^/]+)/);
    return m?decodeURIComponent(m[1]):'';
  }
  function apiUrl(path){
    var base=getDeckBase();
    return (base||'')+path;
  }
  var deckBadge=document.getElementById('ms-deck-badge');
  if(deckBadge&&window.location.protocol!=='file:'){
    var deckLabel=getDeckLabel();
    if(deckLabel){
      deckBadge.textContent='Deck: '+deckLabel;
      deckBadge.style.display='inline-flex';
    }
  }

  function markDirty(){
    if(dirty)return;
    dirty=true;
    if(saveBtn){saveBtn.classList.add('ms-dirty');}
    if(saveBtnText){saveBtnText.textContent=MS_UI.unsaved;}
  }
  window.markDirty=markDirty; // expose for image upload handler

  function clearDirty(){
    dirty=false;
    if(saveBtn){saveBtn.classList.remove('ms-dirty');}
    if(saveBtnText){saveBtnText.textContent=MS_UI.save;}
  }

  // Warn before unload if there are unsaved edits
  window.addEventListener('beforeunload',function(e){
    if(dirty){e.preventDefault();e.returnValue='';}
  });

  // Save button — save in place or download
  if(saveBtn){
    saveBtn.addEventListener('click',function(e){
      e.stopPropagation();
      saving=true;
      if(saveBtnText)saveBtnText.textContent=MS_UI.saving;
      saveBtn.style.pointerEvents='none';
      buildHTML(function(html){
        fetch(apiUrl('/save'),{method:'POST',headers:{'Content-Type':'text/html'},body:html})
          .then(function(r){
            if(r.ok){
              clearDirty();
              if(saveBtnText)saveBtnText.textContent=MS_UI.saved;
              showToast(MS_UI.toast_saved);
              setTimeout(function(){
                if(saveBtnText)saveBtnText.textContent=MS_UI.save;
                saveBtn.style.pointerEvents='auto';
                saveBtn.style.display='none';
                var cb=document.getElementById('ms-close-btn');
                if(cb)cb.style.display='';
                saving=false;
              },1500);
            } else throw new Error();
          })
          .catch(function(){
            var blob=new Blob([html],{type:'text/html'});
            var a=document.createElement('a');
            a.href=URL.createObjectURL(blob);
            a.download=document.title.replace(/[^a-z0-9\u4e00-\u9fff]+/gi,'-').replace(/^-|-$/g,'')+'.html';
            a.click();URL.revokeObjectURL(a.href);
            clearDirty();
            if(saveBtnText)saveBtnText.textContent=MS_UI.save;
            saveBtn.style.pointerEvents='auto';
            saving=false;
          });
      });
    });
  }

  document.addEventListener('keydown',function(e){
    if(isMsTextEntryTarget(e.target)&&!isMsContentEditableTarget(e.target))return;
    var isSaveShortcut=(e.key==='s'||e.key==='S')&&(e.metaKey||e.ctrlKey)&&!e.altKey;
    if(!isSaveShortcut)return;
    if(!saveBtn||saving)return;
    e.preventDefault();
    e.stopPropagation();
    saveBtn.click();
  },true);

  // Close button — save + shutdown server + show final message
  var closeBtn=document.getElementById('ms-close-btn');
  if(closeBtn){
    closeBtn.addEventListener('click',function(e){
      e.stopPropagation();
      closeBtn.textContent=MS_UI.closing;closeBtn.style.pointerEvents='none';
      dirty=false; // prevent beforeunload from blocking
      buildHTML(function(html){
        fetch(apiUrl('/save'),{method:'POST',headers:{'Content-Type':'text/html'},body:html})
          .then(function(r){return r.ok?r.text():Promise.reject();})
          .then(function(filename){
            var name=filename.trim()||document.title;
            showToast(MS_UI.toast_closing.replace('{name}',name),4000);
            setTimeout(function(){fetch(apiUrl('/shutdown'),{method:'POST'}).catch(function(){});},1500);
            setTimeout(function(){document.body.innerHTML='<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;background:#0a0c0e;color:#e8edf7;font-family:system-ui;gap:1rem"><p style="font-size:1.5rem;font-weight:700">'+MS_UI.done_title+'</p><p style="color:#6b7280;font-size:0.95rem">'+MS_UI.done_file.replace('{name}',name)+'</p><p style="color:#6b7280;font-size:0.85rem">'+MS_UI.done_hint+'</p></div>';},2500);
          })
          .catch(function(){
            showToast(MS_UI.toast_no_server,3000);
            closeBtn.textContent=MS_UI.close;closeBtn.style.pointerEvents='auto';
          });
      });
    });
  }

  // ── Auto-save (on load + every 30s) + heartbeat (every 5s) ───────────────
  if(window.location.protocol!=='file:'){
    function autoSave(){
      if(saving||!dirty)return;
      buildHTML(function(html){
        fetch(apiUrl('/save'),{method:'POST',headers:{'Content-Type':'text/html'},body:html})
          .then(function(r){if(r.ok){clearDirty();}})
          .catch(function(){});
      });
    }
    // Only auto-save when dirty (every 30s)
    setInterval(autoSave,30000);
    // Heartbeat every 5s — the preview service removes inactive decks after the server-side timeout
    setInterval(function(){fetch(apiUrl('/heartbeat'),{method:'POST'}).catch(function(){});},5000);
  }

  // ── Edit Mode ───────────────────────────────────────────────────────────
  var editBtn=document.getElementById('ms-edit-btn');
  if(editBtn && window.location.protocol!=='file:'){
    var editMode=false;
    var editBtnText=editBtn.querySelector('span');
    var dock=document.getElementById('slide-dock');
    var navP=document.getElementById('nav-prev');
    var navN=document.getElementById('nav-next');
    var closeBtn=document.getElementById('ms-close-btn');
    var richToolbar=document.getElementById('ms-rich-toolbar');
    var richButtons=richToolbar?Array.from(richToolbar.querySelectorAll('.ms-rich-btn')):[];
    var activeEditable=null;
    var savedRange=null;
    var INLINE_RICH_TAGS=['SPAN','STRONG','EM','U','B','I','A','BR'];

    // Default state: hide save, show close
    if(saveBtn)saveBtn.style.display='none';
    if(closeBtn)closeBtn.style.display='';
    if(richToolbar)richToolbar.style.display='none';

    function isInlineRichTag(el){
      return !!el && el.nodeType===1 && INLINE_RICH_TAGS.indexOf(el.tagName)>-1;
    }

    function hasRichAttrs(el){
      return !!el && el.nodeType===1 && (el.hasAttribute('data-rt-color')||el.hasAttribute('data-rt-size')||el.hasAttribute('data-rt-mark'));
    }

    function getEditableHost(node){
      var el=node&&node.nodeType===1?node:(node&&node.parentElement?node.parentElement:null);
      return el?el.closest('[contenteditable="true"]'):null;
    }

    function getSelectionNode(){
      var range=getEditableRange();
      if(range){
        return range.startContainer.nodeType===1?range.startContainer:range.startContainer.parentElement;
      }
      return activeEditable;
    }

    function getCurrentFormatState(){
      var node=getSelectionNode()||activeEditable;
      if(!node)node=activeEditable;
      return {
        bold: !!closestFormattingNode(node,function(el){return el.tagName==='STRONG'||el.tagName==='B';}),
        italic: !!closestFormattingNode(node,function(el){return el.tagName==='EM'||el.tagName==='I';}),
        underline: !!closestFormattingNode(node,function(el){return el.tagName==='U';})
      };
    }

    function getToolbarAnchorRect(){
      var range=getEditableRange();
      if(range){
        var rect=range.getBoundingClientRect();
        if(rect&&(rect.width||rect.height))return rect;
      }
      return activeEditable?activeEditable.getBoundingClientRect():null;
    }

    function positionRichToolbar(){
      if(!richToolbar||richToolbar.style.display==='none'||!editMode||!activeEditable)return;
      var rect=getToolbarAnchorRect();
      if(!rect)return;
      var margin=12;
      var toolbarWidth=richToolbar.offsetWidth||320;
      var toolbarHeight=richToolbar.offsetHeight||44;
      var left=rect.left+(rect.width/2)-(toolbarWidth/2);
      left=Math.max(12,Math.min(left,window.innerWidth-toolbarWidth-12));
      var top=rect.top-toolbarHeight-margin;
      if(top<12)top=rect.bottom+margin;
      if(top+toolbarHeight>window.innerHeight-12){
        top=Math.max(12,rect.top-toolbarHeight-margin);
      }
      richToolbar.style.left=left+'px';
      richToolbar.style.top=top+'px';
    }

    function showRichToolbar(){
      if(!richToolbar)return;
      richToolbar.style.display='flex';
      richToolbar.setAttribute('aria-hidden','false');
      positionRichToolbar();
    }

    function hideRichToolbar(){
      if(!richToolbar)return;
      richToolbar.style.display='none';
      richToolbar.setAttribute('aria-hidden','true');
      richButtons.forEach(function(btn){btn.classList.remove('ms-rich-active');});
    }

    function unwrapNode(node){
      if(!node||!node.parentNode)return;
      while(node.firstChild)node.parentNode.insertBefore(node.firstChild,node);
      node.remove();
    }

    function replaceTag(node,tagName){
      if(!node||!node.parentNode)return node;
      var repl=document.createElement(tagName);
      Array.from(node.attributes||[]).forEach(function(attr){repl.setAttribute(attr.name,attr.value);});
      while(node.firstChild)repl.appendChild(node.firstChild);
      node.parentNode.replaceChild(repl,node);
      return repl;
    }

    function cleanupSpan(node){
      if(node&&node.nodeType===1&&node.tagName==='SPAN'&&!node.attributes.length)unwrapNode(node);
    }

    function cleanupInlineStyle(node){
      if(!node||node.nodeType!==1)return;
      var styleAttr=node.getAttribute('style');
      if(styleAttr!==null&&!styleAttr.trim())node.removeAttribute('style');
    }

    function normalizeRichContent(root){
      if(!root)return;
      Array.from(root.querySelectorAll('b')).forEach(function(node){replaceTag(node,'strong');});
      Array.from(root.querySelectorAll('i')).forEach(function(node){replaceTag(node,'em');});
      Array.from(root.querySelectorAll('font')).reverse().forEach(function(node){unwrapNode(node);});
      Array.from(root.querySelectorAll('span,strong,em,u')).reverse().forEach(function(node){
        if(node.tagName==='SPAN'&&!hasRichAttrs(node)&&!node.attributes.length){
          unwrapNode(node);
          return;
        }
        if((node.tagName==='STRONG'||node.tagName==='EM'||node.tagName==='U'||(node.tagName==='SPAN'&&hasRichAttrs(node)))&&!node.textContent.trim()){
          node.remove();
        }
      });
      root.normalize();
    }

    function clearRichAttr(root,attrName){
      if(!root)return;
      if(root.nodeType===1&&root.hasAttribute(attrName)){
        root.removeAttribute(attrName);
        if(attrName==='data-rt-size'){
          root.style.removeProperty('font-size');
          cleanupInlineStyle(root);
        }
        cleanupSpan(root);
      }
      Array.from(root.querySelectorAll('['+attrName+']')).forEach(function(node){
        node.removeAttribute(attrName);
        if(attrName==='data-rt-size'){
          node.style.removeProperty('font-size');
          cleanupInlineStyle(node);
        }
        cleanupSpan(node);
      });
    }

    function clearAllFormatting(root){
      if(!root)return;
      if(root.nodeType===1){
        ['data-rt-color','data-rt-size','data-rt-mark'].forEach(function(attr){root.removeAttribute(attr);});
        root.style.removeProperty('font-size');
        cleanupInlineStyle(root);
      }
      Array.from(root.querySelectorAll('[data-rt-color],[data-rt-size],[data-rt-mark]')).forEach(function(node){
        ['data-rt-color','data-rt-size','data-rt-mark'].forEach(function(attr){node.removeAttribute(attr);});
        node.style.removeProperty('font-size');
        cleanupInlineStyle(node);
        cleanupSpan(node);
      });
      Array.from(root.querySelectorAll('strong,em,u,b,i,font')).reverse().forEach(function(node){unwrapNode(node);});
      normalizeRichContent(root);
    }

    function getSelectionStyleNode(){
      return getSelectionNode()||activeEditable;
    }

    function getComputedFontSizePx(node){
      var el=node&&node.nodeType===1?node:(node&&node.parentElement?node.parentElement:null);
      if(!el)return null;
      var px=parseFloat(window.getComputedStyle(el).fontSize);
      return Number.isFinite(px)?px:null;
    }

    function clampFontSizePx(sizePx){
      if(!Number.isFinite(sizePx))return null;
      return Math.max(8,Math.min(240,Math.round(sizePx)));
    }

    function applyNodeFontSize(node,sizePx){
      if(!node||node.nodeType!==1)return false;
      var clamped=clampFontSizePx(sizePx);
      if(!Number.isFinite(clamped))return false;
      node.setAttribute('data-rt-size',clamped+'px');
      node.style.fontSize=clamped+'px';
      return true;
    }

    function applyFontSizeStep(step){
      if(!activeEditable)return false;
      var numericStep=parseFloat(step);
      if(!Number.isFinite(numericStep)||numericStep===0)return false;
      var styleNode=getSelectionStyleNode();
      var currentSize=getComputedFontSizePx(styleNode);
      if(!Number.isFinite(currentSize))return false;
      var nextSize=clampFontSizePx(currentSize+numericStep);
      if(!Number.isFinite(nextSize))return false;
      var applied=wrapSelection(
        'span',
        {'data-rt-size':nextSize+'px','style':'font-size:'+nextSize+'px;'},
        ['data-rt-size']
      );
      if(!applied){
        applied=applyNodeFontSize(activeEditable,nextSize);
        if(applied)selectNodeContents(activeEditable);
      }
      return applied;
    }

    function captureSelection(){
      if(!editMode)return;
      var sel=window.getSelection();
      if(!sel||!sel.rangeCount){
        savedRange=null;
        updateRichToolbarState();
        return;
      }
      var anchorHost=getEditableHost(sel.anchorNode);
      var focusHost=getEditableHost(sel.focusNode);
      if(anchorHost&&anchorHost===focusHost){
        activeEditable=anchorHost;
        savedRange=sel.getRangeAt(0).cloneRange();
        showRichToolbar();
        positionRichToolbar();
      }else{
        savedRange=null;
      }
      updateRichToolbarState();
    }

    function restoreSelection(){
      if(!savedRange)return false;
      var sel=window.getSelection();
      if(!sel)return false;
      sel.removeAllRanges();
      sel.addRange(savedRange);
      return true;
    }

    function getEditableRange(){
      var sel=window.getSelection();
      if((!sel||!sel.rangeCount)&&savedRange){
        restoreSelection();
        sel=window.getSelection();
      }
      if(!sel||!sel.rangeCount||!activeEditable)return null;
      var range=sel.getRangeAt(0);
      if(!activeEditable.contains(range.commonAncestorContainer))return null;
      return range;
    }

    function collapseSelectionToEnd(node){
      if(!node)return;
      var range=document.createRange();
      range.selectNodeContents(node);
      range.collapse(false);
      var sel=window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      savedRange=range.cloneRange();
    }

    function selectNodeContents(node){
      if(!node)return;
      var range=document.createRange();
      range.selectNodeContents(node);
      var sel=window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      savedRange=range.cloneRange();
    }

    function transformSelection(transformer){
      var range=getEditableRange();
      if(!range||range.collapsed)return false;
      var fragment=range.extractContents();
      var box=document.createElement('div');
      box.appendChild(fragment);
      transformer(box);
      normalizeRichContent(box);
      var out=document.createDocumentFragment();
      while(box.firstChild)out.appendChild(box.firstChild);
      range.insertNode(out);
      collapseSelectionToEnd(activeEditable);
      return true;
    }

    function wrapSelection(tagName,attrs,attrsToClear){
      var range=getEditableRange();
      if(!range||range.collapsed)return false;
      var fragment=range.extractContents();
      var box=document.createElement('div');
      box.appendChild(fragment);
      (attrsToClear||[]).forEach(function(attr){clearRichAttr(box,attr);});
      normalizeRichContent(box);
      var wrapper=document.createElement(tagName);
      Object.keys(attrs||{}).forEach(function(name){wrapper.setAttribute(name,attrs[name]);});
      while(box.firstChild)wrapper.appendChild(box.firstChild);
      range.insertNode(wrapper);
      selectNodeContents(wrapper);
      return true;
    }

    function toggleRootTag(tagName){
      if(!activeEditable)return;
      var children=Array.from(activeEditable.childNodes).filter(function(node){
        return !(node.nodeType===3&&!node.textContent.trim());
      });
      if(children.length===1&&children[0].nodeType===1&&children[0].tagName===tagName){
        unwrapNode(children[0]);
      }else{
        var wrapper=document.createElement(tagName);
        while(activeEditable.firstChild)wrapper.appendChild(activeEditable.firstChild);
        activeEditable.appendChild(wrapper);
        selectNodeContents(wrapper);
      }
    }

    function removeNearestTag(tagName){
      if(!activeEditable)return false;
      var node=closestFormattingNode(getSelectionNode(),function(el){return el.tagName===tagName;});
      if(!node||node===activeEditable)return false;
      var parent=node.parentElement||activeEditable;
      unwrapNode(node);
      normalizeRichContent(activeEditable);
      selectNodeContents(parent&&activeEditable.contains(parent)?parent:activeEditable);
      return true;
    }

    function closestFormattingNode(node,predicate){
      var current=node&&node.nodeType===1?node:(node&&node.parentElement?node.parentElement:null);
      while(current&&current!==activeEditable){
        if(predicate(current))return current;
        current=current.parentElement;
      }
      if(activeEditable&&predicate(activeEditable))return activeEditable;
      return null;
    }

    function updateRichToolbarState(){
      if(!richToolbar)return;
      if(!editMode||!activeEditable){
        hideRichToolbar();
        return;
      }
      showRichToolbar();
      positionRichToolbar();
      richButtons.forEach(function(btn){btn.classList.remove('ms-rich-active');});
      var state=getCurrentFormatState();
      function markActive(match){
        richButtons.forEach(function(btn){
          if(btn.dataset.format===match.format&&String(btn.dataset.value||'')===String(match.value||'')){
            btn.classList.add('ms-rich-active');
          }
        });
      }
      if(state.bold)markActive({format:'bold'});
      if(state.italic)markActive({format:'italic'});
      if(state.underline)markActive({format:'underline'});
    }

    function applyRichFormat(format,value){
      if(!activeEditable)return;
      var applied=false;
      var state=getCurrentFormatState();
      if(format==='bold'){
        if(state.bold){
          applied=removeNearestTag('STRONG');
        }else{
          applied=wrapSelection('strong',null,null);
          if(!applied){
            toggleRootTag('STRONG');
            applied=true;
          }
        }
      }else if(format==='italic'){
        if(state.italic){
          applied=removeNearestTag('EM');
        }else{
          applied=wrapSelection('em',null,null);
          if(!applied){
            toggleRootTag('EM');
            applied=true;
          }
        }
      }else if(format==='underline'){
        if(state.underline){
          applied=removeNearestTag('U');
        }else{
          applied=wrapSelection('u',null,null);
          if(!applied){
            toggleRootTag('U');
            applied=true;
          }
        }
      }else if(format==='clear'){
        applied=transformSelection(function(box){clearAllFormatting(box);});
        if(!applied){
          clearAllFormatting(activeEditable);
          applied=true;
        }
      }else if(format==='font-size-step'){
        applied=applyFontSizeStep(value);
      }
      if(!applied)return;
      normalizeRichContent(activeEditable);
      markDirty();
      activeEditable.focus();
      captureSelection();
    }

    // Block navigation keys in edit mode (capture phase beats existing handlers)
    document.addEventListener('keydown',function(e){
      if(!editMode)return;
      if(['ArrowRight','ArrowDown','ArrowLeft','ArrowUp','Space'].indexOf(e.code)>-1){
        e.stopPropagation(); // prevent the go() handler from firing
      }
    },true);

    // Block click-to-advance in edit mode (but allow uploads and toolbar)
    document.addEventListener('click',function(e){
      if(!editMode)return;
      if(e.target.isContentEditable||e.target.closest('[contenteditable="true"]'))return;
      if(e.target.closest('#ms-toolbar'))return;
      if(e.target.closest('#ms-rich-toolbar'))return;
      if(e.target.closest('.uploadable-wrap'))return;
      // Stop the click→go(cur,cur+1) handler
      e.stopPropagation();
    },true);

    function enableEditing(){
      // Walk all elements in active slide, find leaf text nodes
      var active=document.querySelector('.slide.active');
      if(!active)return;
      active.querySelectorAll('*').forEach(function(el){
        // Skip non-content elements
        if(el.closest('#ms-toolbar')||el.closest('.nav-btn'))return;
        if(el.classList.contains('bg')||el.classList.contains('ghost')||el.classList.contains('progress'))return;
        if(el.tagName==='I'||el.tagName==='SVG'||el.tagName==='PATH'||el.tagName==='INPUT'||el.tagName==='BUTTON')return;
        if(isInlineRichTag(el))return;
        if(!el.textContent.trim())return;
        // Skip if this element contains a structured child with its own text.
        // Inline rich-text wrappers still belong to the same editable leaf.
        var hasStructuredTextChild=false;
        for(var i=0;i<el.children.length;i++){
          var child=el.children[i];
          if(!child.textContent.trim())continue;
          if(isInlineRichTag(child))continue;
          hasStructuredTextChild=true;
          break;
        }
        if(hasStructuredTextChild)return;

        el.contentEditable='true';
        el.addEventListener('input',markDirty);
        el.addEventListener('mouseup',captureSelection);
        el.addEventListener('keyup',captureSelection);
        el.addEventListener('focus',captureSelection);
        if(el.tagName.match(/^H[1-6]$/))el.addEventListener('keydown',_preventBr);
      });
    }

    function disableEditing(){
      document.querySelectorAll('[contenteditable="true"]').forEach(function(el){
        el.removeAttribute('contenteditable');
        el.removeEventListener('input',markDirty);
        el.removeEventListener('mouseup',captureSelection);
        el.removeEventListener('keyup',captureSelection);
        el.removeEventListener('focus',captureSelection);
        el.removeEventListener('keydown',_preventBr);
      });
      activeEditable=null;
      savedRange=null;
      hideRichToolbar();
    }

    function _preventBr(e){
      if(e.key==='Enter'){e.preventDefault();e.target.blur();}
    }

    function isTextEntryTarget(target){
      if(!target)return false;
      if(target.isContentEditable||target.closest('[contenteditable="true"]'))return true;
      return !!target.closest('input,textarea,select');
    }

    function toggleEditMode(){
      editMode=!editMode;
      document.body.classList.toggle('ms-edit-mode',editMode);
      if(editMode){
        animating=true;
        enableEditing();
        editBtn.style.background='rgba(118,185,0,0.15)';
        editBtn.style.borderColor='rgba(118,185,0,0.5)';
        if(editBtnText)editBtnText.textContent=MS_UI.editing;
        if(dock){dock.style.opacity='0.3';dock.style.pointerEvents='none';}
        if(navP){navP.style.opacity='0';navP.style.pointerEvents='none';}
        if(navN){navN.style.opacity='0';navN.style.pointerEvents='none';}
        if(saveBtn)saveBtn.style.display='';
        if(closeBtn)closeBtn.style.display='none';
        showRichToolbar();
        updateRichToolbarState();
      } else {
        disableEditing();
        animating=false;
        editBtn.style.background='rgba(10,12,22,0.72)';
        editBtn.style.borderColor='rgba(255,255,255,0.12)';
        if(editBtnText)editBtnText.textContent=MS_UI.edit;
        if(dock){dock.style.opacity='';dock.style.pointerEvents='';}
        if(navP){navP.style.opacity='';navP.style.pointerEvents='';}
        if(navN){navN.style.opacity='';navN.style.pointerEvents='';}
        // Keep save button visible if dirty so user can still save
        if(saveBtn)saveBtn.style.display=dirty?'':'none';
        if(closeBtn)closeBtn.style.display=dirty?'none':'';
      }
    }

    editBtn.addEventListener('click',function(e){e.stopPropagation();if(_ct){clearTimeout(_ct);_ct=null;}toggleEditMode();});

    document.addEventListener('keydown',function(e){
      if(e.code!=='KeyE'||e.ctrlKey||e.metaKey||e.altKey||isTextEntryTarget(e.target))return;
      e.preventDefault();
      e.stopPropagation();
      if(_ct){clearTimeout(_ct);_ct=null;}
      toggleEditMode();
    },true);

    document.addEventListener('selectionchange',captureSelection);

    if(richToolbar){
      richToolbar.addEventListener('mousedown',function(e){
        e.preventDefault();
        e.stopPropagation();
      });
      richToolbar.addEventListener('click',function(e){
        var btn=e.target.closest('[data-format]');
        if(!btn||!editMode)return;
        e.preventDefault();
        e.stopPropagation();
        if(_ct){clearTimeout(_ct);_ct=null;}
        restoreSelection();
        applyRichFormat(btn.dataset.format,btn.dataset.value||'');
      });
    }

    // Sanitize paste — plain text only
    document.addEventListener('paste',function(e){
      if(!editMode)return;
      var target=e.target;
      if(!target.isContentEditable)return;
      e.preventDefault();
      var text=(e.clipboardData||window.clipboardData).getData('text/plain');
      document.execCommand('insertText',false,text);
    });

    // Exit edit mode when save button is clicked (capture phase)
    // We only exit editing state, but keep save button visible during the save operation
    if(saveBtn){
      saveBtn.addEventListener('click',function(){
        if(editMode){
          disableEditing();
          editMode=false;
          document.body.classList.remove('ms-edit-mode');
          animating=false;
          editBtn.style.background='rgba(10,12,22,0.72)';
          editBtn.style.borderColor='rgba(255,255,255,0.12)';
          if(editBtnText)editBtnText.textContent=MS_UI.edit;
          if(dock){dock.style.opacity='';dock.style.pointerEvents='';}
          if(navP){navP.style.opacity='';navP.style.pointerEvents='';}
          if(navN){navN.style.opacity='';navN.style.pointerEvents='';}
          hideRichToolbar();
          // Don't hide save button or show close — the save handler will do that after save completes
        }
      },true);
    }
  } else if(editBtn && window.location.protocol==='file:'){
    editBtn.style.display='none';
  }
})();
// Custom cursor with trailing effect
(function(){
  if(MS_IS_OVERVIEW_EMBED)return;
  var old=document.getElementById('ms-cursor');if(old)old.remove();
  var cursor=document.createElement('div');
  cursor.id='ms-cursor';
  document.body.appendChild(cursor);
  // Create 5 trailing dots
  var trails=[];
  var trailCount=5;
  for(var i=0;i<trailCount;i++){
    var trail=document.createElement('div');
    trail.id='ms-cursor-trail-'+i;
    trail.className='ms-cursor-trail';
    document.body.appendChild(trail);
    trails.push({el:trail,x:0,y:0,cx:0,cy:0});
  }
  var x=0,y=0,cx=0,cy=0;
  var cursorSuppressed=false;
  function isCursorSuppressedTarget(target){
    return !!(target&&target.closest&&target.closest('#ms-toolbar,#ms-rich-toolbar,#slide-dock,.nav-btn,.overview-close,.overview-item,#qa-overview'));
  }
  function setCursorSuppressed(next){
    if(cursorSuppressed===next)return;
    cursorSuppressed=next;
    if(cursorSuppressed){
      cursor.style.display='none';
      cursor.style.opacity='0';
      trails.forEach(function(t){t.el.style.display='none';t.el.style.opacity='0'});
    }else{
      var shouldShow=(typeof cursorVisible==='undefined')||cursorVisible;
      cursor.style.display=shouldShow?'':'none';
      cursor.style.opacity='1';
      trails.forEach(function(t,i){
        t.el.style.display=shouldShow?'':'none';
        t.el.style.opacity=(0.65-i*0.1);
      });
    }
  }
  document.addEventListener('mousemove',function(e){
    x=e.clientX;y=e.clientY;
    setCursorSuppressed(isCursorSuppressedTarget(e.target));
  });
  function updateCursor(){
    if(cursorSuppressed){
      requestAnimationFrame(updateCursor);
      return;
    }
    // Update main cursor
    cx+=(x-cx)*0.2;cy+=(y-cy)*0.2;
    cursor.style.left=cx+'px';cursor.style.top=cy+'px';
    // Update trails - each follows the previous one
    var prevX=cx,prevY=cy;
    for(var i=0;i<trails.length;i++){
      var t=trails[i];
      var lag=0.35-i*0.05; // Faster lag for tighter trail
      t.cx+=(prevX-t.cx)*lag;
      t.cy+=(prevY-t.cy)*lag;
      t.el.style.left=t.cx+'px';
      t.el.style.top=t.cy+'px';
      // Fade out trailing dots
      var opacity=0.65-i*0.1;
      t.el.style.opacity=opacity;
      prevX=t.cx;prevY=t.cy;
    }
    requestAnimationFrame(updateCursor);
  }
  updateCursor();
  document.addEventListener('mousedown',function(){
    cursor.classList.add('cursor-click');
    trails.forEach(function(t){t.el.classList.add('cursor-click')});
  });
  document.addEventListener('mouseup',function(){
    cursor.classList.remove('cursor-click');
    trails.forEach(function(t){t.el.classList.remove('cursor-click')});
  });
  document.addEventListener('mouseleave',function(){
    cursor.style.opacity='0';
    trails.forEach(function(t){t.el.style.opacity='0'});
  });
  document.addEventListener('mouseenter',function(){
    cursor.style.opacity='1';
    trails.forEach(function(t,i){t.el.style.opacity=(0.65-i*0.1)});
  });
})();
</script>"""


def make_runtime_script(ui: dict) -> str:
    """Inject UI strings as a JS variable before the runtime script."""
    ui_js = 'var MS_UI=' + repr(ui).replace("'", '"') + ';\n'
    return RUNTIME_SCRIPT.replace('<script>\n', '<script>\n' + ui_js, 1)


def inject(html: str, lang: str = 'zh') -> str:
    """Strip old runtime then inject fresh runtime into a Magic Slide HTML file."""
    ui = get_ui(lang)
    modified = sanitize_editor_state(strip(html))

    # Some decks arrive with image src attributes serialized as src="..."" after
    # runtime reinjection. Normalize that malformed pattern before we write out
    # the final HTML so uploadable images continue to render correctly.
    modified = re.sub(r'(<img\b[^>]*\bsrc="[^"]+)""', r'\1"', modified)
    modified = normalize_slide_stagger(modified)
    modified = harden_inline_svg(modified)

    # 1. Inject Lucide CDN in <head> (first occurrence only)
    # Lucide removed — nav arrows are pure CSS, no external JS needed

    # 2. Inject common CSS before </style> (first occurrence only)
    modified = modified.replace('</style>', COMMON_CSS + '\n</style>', 1)

    # 3. Insert progress/counter/dock/nav HTML before </body> (first occurrence only)
    modified = modified.replace('</body>', make_runtime_html(ui) + '\n</body>', 1)

    # 4. Inject script block before </body> (first occurrence only — </body> now follows the runtime HTML)
    modified = modified.replace('</body>', make_runtime_script(ui) + '\n</body>', 1)

    return modified


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 inject-runtime.py <file.html> [--lang <lang>]", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    lang = 'zh'
    args = sys.argv[2:]
    if '--lang' in args:
        idx = args.index('--lang')
        if idx + 1 < len(args):
            lang = args[idx + 1]

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    result = inject(html, lang=lang)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(result)

    print("Injected runtime into " + path)

    # Validate all <script> blocks for JS syntax errors
    scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', result, re.DOTALL)
    errors = []
    for i, src in enumerate(scripts):
        # Skip external scripts (empty body after stripping whitespace)
        if not src.strip():
            continue
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as tmp:
            tmp.write(src)
            tmp_path = tmp.name
        try:
            proc = subprocess.run(['node', '--check', tmp_path], capture_output=True, text=True)
            if proc.returncode != 0:
                # Map temp file line numbers back to HTML line numbers
                # Find where this script block starts in the HTML
                script_start = result.find(src)
                line_offset = result[:script_start].count('\n') + 1
                msg = proc.stderr.replace(tmp_path, path)
                # Adjust line numbers
                def adjust_line(m):
                    return path + ':' + str(int(m.group(1)) + line_offset - 1)
                msg = re.sub(r'\S+:(\d+)', adjust_line, msg)
                errors.append(f"Script block {i+1}: {msg.strip()}")
        finally:
            os.unlink(tmp_path)

    if errors:
        print("\n⚠️  JS syntax errors detected — fix before opening in browser:", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ JS syntax OK")
