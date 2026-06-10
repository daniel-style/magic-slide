#!/usr/bin/env python3
"""Regression check for aspect-ratio slide canvases and runtime upscaling."""

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INJECT = ROOT / "scripts" / "inject-runtime.py"


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def node_env_with_playwright():
    env = dict(os.environ)
    paths = []
    pnpm_root = ROOT / "node_modules" / ".pnpm"
    if pnpm_root.exists():
        for pattern in ("playwright@*/node_modules", "playwright-core@*/node_modules"):
            paths.extend(str(path) for path in pnpm_root.glob(pattern))
    existing = env.get("NODE_PATH")
    if existing:
        paths.append(existing)
    if paths:
        env["NODE_PATH"] = os.pathsep.join(paths)
    return env


def main() -> int:
    if not shutil.which("node"):
        print("Node.js is required for the Playwright runtime canvas check.", file=sys.stderr)
        return 2

    node_env = node_env_with_playwright()
    probe = subprocess.run(
        ["node", "-e", "require.resolve('playwright')"],
        cwd=ROOT,
        env=node_env,
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        print("The Playwright npm package is required for this check.", file=sys.stderr)
        print(probe.stderr.strip(), file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="magic-slide-canvas-") as tmp:
        html_path = Path(tmp) / "aspect-canvas.html"
        html_path.write_text(
            textwrap.dedent(
                """\
                <!doctype html>
                <html>
                <head>
                  <meta charset="utf-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  <title>Aspect Canvas Regression</title>
                  <style>
                    :root {
                      --bg: #d6ff55;
                      --text: #151612;
                      --font-display: Impact, system-ui, sans-serif;
                      --font-body: system-ui, sans-serif;
                    }
                    body { margin: 0; background: var(--bg); color: var(--text); }
                    .slide {
                      position: relative;
                      width: 100vw;
                      height: 100vh;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      background: var(--bg);
                    }
                    .slide-content {
                      inline-size: min(1500px, calc(100vw - 6rem), calc((100vh - 5rem) * 16 / 9));
                      aspect-ratio: 16 / 9;
                      padding: 2.4rem;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                    }
                    .stage {
                      width: 100%;
                      height: 100%;
                      display: grid;
                      grid-template-columns: 1fr 1fr;
                      gap: 2rem;
                    }
                    .panel {
                      border: 2px solid currentColor;
                      display: grid;
                      align-content: end;
                      padding: 1.5rem;
                    }
                    h1 {
                      margin: 0;
                      font-family: var(--font-display);
                      font-size: 7rem;
                      line-height: .86;
                    }
                    p {
                      margin: 1rem 0 0;
                      font: 1.2rem/1.35 var(--font-body);
                    }
                  </style>
                </head>
                <body>
                  <div id="deck">
                    <section class="slide" data-id="cover" data-transition="fade" data-stagger="cascade" data-bg="light">
                      <div class="slide-content">
                        <div class="stage">
                          <div class="panel"><h1>Aspect Canvas</h1><p>Left panel content.</p></div>
                          <div class="panel"><h1>Runtime Fit</h1><p>Right panel content.</p></div>
                        </div>
                      </div>
                    </section>
                  </div>
                </body>
                </html>
                """
            ),
            encoding="utf-8",
        )

        run([sys.executable, str(INJECT), str(html_path), "--lang", "en"], cwd=ROOT)

        js = r"""
        const { chromium } = require('playwright');
        (async () => {
          const url = process.env.MS_CANVAS_CHECK_URL;
          const browser = await chromium.launch({ headless: true });
          try {
            const page = await browser.newPage({ viewport: { width: 3840, height: 2160 }, deviceScaleFactor: 1 });
            await page.goto(url);
            await page.waitForTimeout(250);
            const data = await page.evaluate(() => {
              const wrapper = document.querySelector('.slide.active .slide-content');
              const rect = wrapper.getBoundingClientRect();
              const style = getComputedStyle(wrapper);
              return {
                classes: wrapper.className,
                width: rect.width,
                height: rect.height,
                transform: style.transform,
                fit: parseFloat(style.getPropertyValue('--ms-fit-upscale')) || 1,
                minHeight: style.minHeight,
                aspectRatio: style.aspectRatio
              };
            });
            console.log(JSON.stringify(data, null, 2));
            if (!/\bms-aspect-canvas\b/.test(data.classes)) {
              throw new Error('runtime did not preserve the aspect-ratio canvas');
            }
            if (!/\bms-fit-upscale\b/.test(data.classes) || data.fit < 1.2) {
              throw new Error('runtime did not upscale the aspect-ratio canvas on a large viewport');
            }
            if (data.height >= 2000) {
              throw new Error('aspect canvas was stretched close to full viewport height');
            }
          } finally {
            await browser.close();
          }
        })().catch((err) => {
          console.error(err && err.stack ? err.stack : err);
          process.exit(1);
        });
        """
        node_env["MS_CANVAS_CHECK_URL"] = html_path.as_uri() + "?ms_no_presenter=1"
        run(["node", "-e", js], cwd=ROOT, env=node_env)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
