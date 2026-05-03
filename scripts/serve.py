#!/usr/bin/env python3
"""
serve.py — Single-service preview server for Magic Slide presentations.

Usage:
    python3 scripts/serve.py deck/index.html

- Runs one local HTTP service for all deck previews
- Registers each deck under its own route: /deck/<deck-id>/<file.html>
- Provides deck-scoped save / heartbeat / shutdown endpoints
- Opens the browser automatically
- Press Ctrl+C to stop the service if this invocation started it
"""

import hashlib
import json
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import quote, unquote
import sys

BASE_PORT = 8765
MAX_PORT = 8865
HEARTBEAT_TIMEOUT = 120
INITIAL_DECK_GRACE_TIMEOUT = 300
SERVICE_KIND = "magic-slide-preview"
QA_ISSUES_FILENAME = "visual-issues.json"


@dataclass
class Deck:
    deck_id: str
    html_path: Path
    serve_dir: Path
    filename: str
    html_lang: str
    inject_script: Path
    extract_script: Path
    sources_dir: Path
    created_at: float
    last_heartbeat: float
    has_client_contact: bool

    def url_path(self) -> str:
        return f"/deck/{quote(self.deck_id)}/{quote(self.filename)}"


def detect_lang(html_path: Path) -> str:
    try:
        content = html_path.read_text(encoding="utf-8")
        m = re.search(r'<html[^>]*\blang="([^"]+)"', content)
        if m:
            code = m.group(1).lower()
            if code.startswith("zh"):
                return "zh"
            if code.startswith("ja"):
                return "ja"
            if code.startswith("ko"):
                return "ko"
            if code.startswith("fr"):
                return "fr"
            if code.startswith("de"):
                return "de"
            return "en"
    except Exception:
        pass
    return "en"


def sanitize_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "deck"


def make_deck_id(html_path: Path, registry: Dict[str, Deck]) -> str:
    for deck in registry.values():
        if deck.html_path == html_path:
            return deck.deck_id

    base = sanitize_slug(html_path.parent.name or html_path.stem)
    if base not in registry:
        return base

    suffix = hashlib.sha1(str(html_path).encode("utf-8")).hexdigest()[:6]
    candidate = f"{base}-{suffix}"
    if candidate not in registry:
        return candidate

    idx = 2
    while f"{candidate}-{idx}" in registry:
        idx += 1
    return f"{candidate}-{idx}"


def build_deck(html_path: Path, registry: Dict[str, Deck]) -> Deck:
    html_path = html_path.resolve()
    serve_dir = html_path.parent
    now = time.time()
    return Deck(
        deck_id=make_deck_id(html_path, registry),
        html_path=html_path,
        serve_dir=serve_dir,
        filename=html_path.name,
        html_lang=detect_lang(html_path),
        inject_script=Path(__file__).resolve().parent / "inject-runtime.py",
        extract_script=Path(__file__).resolve().parent / "extract-slides.py",
        sources_dir=serve_dir / "sources",
        created_at=now,
        last_heartbeat=now,
        has_client_contact=False,
    )


def is_port_open(port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def request_json(url: str, method: str = "GET", payload: Optional[dict] = None) -> Optional[dict]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status != 200:
                return None
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else None
    except Exception:
        return None


def find_running_service_port() -> Optional[int]:
    for port in range(BASE_PORT, MAX_PORT + 1):
        if not is_port_open(port):
            continue
        meta = request_json(f"http://localhost:{port}/__magic_slide_meta")
        if meta and meta.get("service") == SERVICE_KIND:
            return port
    return None


def find_free_port() -> int:
    for port in range(BASE_PORT, MAX_PORT + 1):
        if not is_port_open(port):
            return port
    raise RuntimeError(f"No free port available in range {BASE_PORT}-{MAX_PORT}")


def register_with_running_service(port: int, html_path: Path) -> Optional[dict]:
    return request_json(
        f"http://localhost:{port}/__register",
        method="POST",
        payload={"html_path": str(html_path.resolve())},
    )


def deck_route(deck: Deck) -> str:
    return f"http://localhost:{server_port}/{deck.url_path().lstrip('/')}"  # type: ignore[name-defined]


def empty_qa_issues() -> dict:
    return {
        "schemaVersion": 1,
        "qaRevision": 0,
        "updatedAt": None,
        "issues": [],
    }


def qa_issues_path(deck: Deck) -> Path:
    return deck.sources_dir / "qa" / QA_ISSUES_FILENAME


def read_qa_issues(deck: Deck) -> dict:
    path = qa_issues_path(deck)
    if not path.exists():
        return empty_qa_issues()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return empty_qa_issues()
    if not isinstance(data.get("issues"), list):
        data["issues"] = []
    if not isinstance(data.get("schemaVersion"), int):
        data["schemaVersion"] = 1
    if not isinstance(data.get("qaRevision"), int):
        data["qaRevision"] = 0
    if "updatedAt" not in data:
        data["updatedAt"] = None
    return data


def write_qa_issues(deck: Deck, data: dict) -> None:
    if not isinstance(data, dict) or not isinstance(data.get("issues"), list):
        raise ValueError("qa issue payload must contain an issues array")
    existing = read_qa_issues(deck)
    existing_by_id = {
        issue.get("id"): issue
        for issue in existing.get("issues", [])
        if isinstance(issue, dict) and issue.get("id")
    }
    incoming_ids = set()
    merged_issues = []
    for issue in data["issues"]:
        if not isinstance(issue, dict):
            continue
        merged = dict(issue)
        issue_id = merged.get("id")
        if issue_id:
            incoming_ids.add(issue_id)
        existing_issue = existing_by_id.get(issue_id)
        if existing_issue and existing_issue.get("resolved") is True and merged.get("resolved") is not True:
            merged["resolved"] = True
            for key in ("resolvedAt", "resolvedInRevision", "resolution", "changedFiles"):
                if existing_issue.get(key) not in (None, "", []):
                    merged[key] = existing_issue.get(key)
        merged_issues.append(merged)

    for issue in existing.get("issues", []):
        if isinstance(issue, dict) and issue.get("id") and issue.get("id") not in incoming_ids:
            merged_issues.append(issue)

    existing_revision = existing.get("qaRevision", 0) if isinstance(existing.get("qaRevision"), int) else 0
    incoming_revision = data.get("qaRevision", 0) if isinstance(data.get("qaRevision"), int) else 0
    data = dict(data)
    data["issues"] = merged_issues
    data["schemaVersion"] = data.get("schemaVersion") if isinstance(data.get("schemaVersion"), int) else 1
    data["qaRevision"] = max(existing_revision, incoming_revision)
    if not isinstance(data.get("updatedAt"), str):
        data["updatedAt"] = existing.get("updatedAt") if isinstance(existing.get("updatedAt"), str) else None
    path = qa_issues_path(deck)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 serve.py <file.html>", file=sys.stderr)
        sys.exit(1)

    html_path = Path(sys.argv[1]).resolve()
    if not html_path.exists():
        print(f"File not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    existing_port = find_running_service_port()
    if existing_port is not None:
        registered = register_with_running_service(existing_port, html_path)
        if not registered:
            print("Failed to register deck with running Magic Slide service.", file=sys.stderr)
            sys.exit(1)
        url = registered["url"]
        print(f"  Magic Slide service already running → {url}")
        webbrowser.open(url)
        return

    registry: Dict[str, Deck] = {}
    registry_lock = threading.Lock()
    initial_deck = build_deck(html_path, registry)
    registry[initial_deck.deck_id] = initial_deck

    global server_port
    server_port = find_free_port()

    def with_lock(fn):
        def wrapped(*args, **kwargs):
            with registry_lock:
                return fn(*args, **kwargs)
        return wrapped

    @with_lock
    def get_deck(deck_id: str) -> Optional[Deck]:
        return registry.get(deck_id)

    @with_lock
    def register_deck(html_path_str: str) -> Deck:
        deck_path = Path(html_path_str).resolve()
        for existing in registry.values():
            if existing.html_path == deck_path:
                existing.created_at = time.time()
                existing.last_heartbeat = existing.created_at
                existing.has_client_contact = False
                return existing
        deck = build_deck(deck_path, registry)
        registry[deck.deck_id] = deck
        return deck

    @with_lock
    def remove_deck(deck_id: str) -> Optional[Deck]:
        return registry.pop(deck_id, None)

    @with_lock
    def list_decks():
        return [
            {
                "deck_id": deck.deck_id,
                "filename": deck.filename,
                "html_path": str(deck.html_path),
                "url": f"http://localhost:{server_port}{deck.url_path()}",
                "last_heartbeat": deck.last_heartbeat,
            }
            for deck in registry.values()
        ]

    @with_lock
    def active_count() -> int:
        return len(registry)

    def resolve_static_target(deck: Deck, rel_path: str) -> Optional[Path]:
        rel_path = rel_path.lstrip("/")
        if not rel_path or rel_path == deck.filename:
            return deck.html_path
        candidate = (deck.serve_dir / rel_path).resolve()
        try:
            candidate.relative_to(deck.serve_dir.resolve())
        except ValueError:
            return None
        return candidate

    def render_index() -> bytes:
        items = []
        for entry in list_decks():
            items.append(
                f'<li><a href="{entry["url"]}">{entry["deck_id"]}</a> '
                f'<span style="color:#9ca3af">{entry["filename"]}</span></li>'
            )
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Magic Slide Preview</title>
  <style>
    body{{margin:0;padding:40px;background:#0a0c10;color:#edf1f7;font-family:system-ui,sans-serif}}
    h1{{margin:0 0 18px;font-size:28px}}
    p{{color:#9ca3af;max-width:760px;line-height:1.6}}
    ul{{margin:28px 0 0;padding:0;list-style:none;display:grid;gap:12px}}
    li{{padding:14px 16px;border:1px solid rgba(255,255,255,0.08);border-radius:12px;background:rgba(255,255,255,0.03)}}
    a{{color:#edf1f7;text-decoration:none;font-weight:700}}
  </style>
</head>
<body>
  <h1>Magic Slide Preview Service</h1>
  <p>One local preview service can host multiple decks at once. Open a deck route below or run <code>serve.py path/to/deck.html</code> again to register another deck.</p>
  <ul>{''.join(items) if items else '<li>No active decks.</li>'}</ul>
</body>
</html>"""
        return html.encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            msg = fmt % args
            if any(token in msg for token in ("save", "shutdown", "__register")):
                print(f"  {msg}")

        def send_bytes(self, status: int, payload: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(payload)

        def send_json(self, status: int, data: dict):
            self.send_bytes(status, json.dumps(data).encode("utf-8"), "application/json; charset=utf-8")

        def parse_path(self):
            return self.path.split("?", 1)[0]

        def read_json_body(self) -> Optional[dict]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length) if length > 0 else b"{}"
                return json.loads(body.decode("utf-8"))
            except Exception:
                return None

        def do_GET(self):
            path = self.parse_path()

            if path == "/__magic_slide_meta":
                self.send_json(
                    200,
                    {
                        "service": SERVICE_KIND,
                        "port": server_port,
                        "decks": list_decks(),
                    },
                )
                return

            if path == "/":
                self.send_bytes(200, render_index(), "text/html; charset=utf-8")
                return

            match = re.match(r"^/deck/([^/]+)(?:/(.*))?$", path)
            if not match:
                self.send_response(404)
                self.end_headers()
                return

            deck_id = unquote(match.group(1))
            rel_path = unquote(match.group(2) or "")
            deck = get_deck(deck_id)
            if not deck:
                self.send_response(404)
                self.end_headers()
                return

            deck.last_heartbeat = time.time()
            deck.has_client_contact = True

            if not rel_path:
                self.send_response(302)
                self.send_header("Location", deck.url_path())
                self.end_headers()
                return

            if rel_path == "qa-issues":
                try:
                    deck.last_heartbeat = time.time()
                    deck.has_client_contact = True
                    self.send_json(200, read_qa_issues(deck))
                except Exception as ex:
                    print(f"  ✗ Failed to read QA issues for {deck.deck_id}: {ex}", file=sys.stderr)
                    self.send_json(500, {"error": "failed to read QA issues"})
                return

            target = resolve_static_target(deck, rel_path)
            if not target:
                self.send_response(404)
                self.end_headers()
                return

            try:
                data = target.read_bytes()
            except (FileNotFoundError, IsADirectoryError):
                self.send_response(404)
                self.end_headers()
                return

            ext = target.suffix.lower()
            mime = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css",
                ".js": "application/javascript",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".svg": "image/svg+xml",
                ".webp": "image/webp",
            }.get(ext, "application/octet-stream")
            self.send_bytes(200, data, mime)

        def do_POST(self):
            path = self.parse_path()

            if path == "/__register":
                payload = self.read_json_body() or {}
                html_path_str = payload.get("html_path")
                if not html_path_str:
                    self.send_json(400, {"error": "html_path required"})
                    return
                deck_path = Path(html_path_str).resolve()
                if not deck_path.exists():
                    self.send_json(404, {"error": "html file not found"})
                    return
                deck = register_deck(str(deck_path))
                self.send_json(
                    200,
                    {
                        "service": SERVICE_KIND,
                        "deck_id": deck.deck_id,
                        "url": f"http://localhost:{server_port}{deck.url_path()}",
                    },
                )
                return

            match = re.match(r"^/deck/([^/]+)/(save|heartbeat|shutdown|qa-issues)$", path)
            if not match:
                self.send_response(404)
                self.end_headers()
                return

            deck_id = unquote(match.group(1))
            action = match.group(2)
            deck = get_deck(deck_id)
            if not deck:
                self.send_response(404)
                self.end_headers()
                return

            if action == "save":
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                try:
                    deck.html_path.write_bytes(body)
                    if deck.inject_script.exists():
                        subprocess.run(
                            [sys.executable, str(deck.inject_script), str(deck.html_path), "--lang", deck.html_lang],
                            capture_output=True,
                            timeout=10,
                        )
                    if deck.sources_dir.exists() and deck.extract_script.exists():
                        result = subprocess.run(
                            [sys.executable, str(deck.extract_script), str(deck.html_path), str(deck.sources_dir)],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if result.returncode == 0:
                            print(f"  ✓ Synced to sources/ for {deck.deck_id}")
                        else:
                            print(f"  ⚠ Failed to sync to sources/ for {deck.deck_id}: {result.stderr}")
                    deck.last_heartbeat = time.time()
                    deck.has_client_contact = True
                    print(f"  ✓ Saved → {deck.html_path}")
                    self.send_bytes(200, deck.filename.encode("utf-8"), "text/plain; charset=utf-8")
                except Exception as ex:
                    print(f"  ✗ Save failed for {deck.deck_id}: {ex}", file=sys.stderr)
                    self.send_response(500)
                    self.end_headers()
                return

            if action == "qa-issues":
                payload = self.read_json_body()
                if not isinstance(payload, dict) or not isinstance(payload.get("issues"), list):
                    self.send_json(400, {"error": "invalid QA issues payload"})
                    return
                try:
                    write_qa_issues(deck, payload)
                    deck.last_heartbeat = time.time()
                    deck.has_client_contact = True
                    print(f"  ✓ QA issues saved → {qa_issues_path(deck)}")
                    self.send_json(200, read_qa_issues(deck))
                except Exception as ex:
                    print(f"  ✗ QA issue save failed for {deck.deck_id}: {ex}", file=sys.stderr)
                    self.send_json(500, {"error": "failed to save QA issues"})
                return

            if action == "heartbeat":
                deck.last_heartbeat = time.time()
                deck.has_client_contact = True
                self.send_bytes(200, b"ok", "text/plain; charset=utf-8")
                return

            if action == "shutdown":
                removed = remove_deck(deck_id)
                self.send_bytes(200, b"bye", "text/plain; charset=utf-8")
                if removed:
                    print(f"\n  ✓ Closed preview for {removed.deck_id} → {removed.html_path}")
                if active_count() == 0:
                    threading.Timer(0.3, server.shutdown).start()
                return

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

    server = HTTPServer(("localhost", server_port), Handler)

    def watchdog():
        while True:
            time.sleep(5)
            stale = []
            now = time.time()
            with registry_lock:
                for deck_id, deck in list(registry.items()):
                    timeout = HEARTBEAT_TIMEOUT if deck.has_client_contact else INITIAL_DECK_GRACE_TIMEOUT
                    if now - deck.last_heartbeat > timeout:
                        stale.append((deck_id, deck))
                        registry.pop(deck_id, None)
            for deck_id, deck in stale:
                timeout = HEARTBEAT_TIMEOUT if deck.has_client_contact else INITIAL_DECK_GRACE_TIMEOUT
                reason = "heartbeat" if deck.has_client_contact else "initial client contact"
                print(f"\n  ⏹ No {reason} for {timeout}s — removing {deck_id} ({deck.filename})")
            if active_count() == 0:
                print("\n  ⏹ No active deck previews remain — shutting down service.")
                server.shutdown()
                return

    initial_url = f"http://localhost:{server_port}{initial_deck.url_path()}"
    print(f"  Magic Slide service → http://localhost:{server_port}")
    print(f"  Initial deck:          {initial_url}")
    print(f"  Auto-stop:             {HEARTBEAT_TIMEOUT}s after the last preview tab stops sending heartbeats")
    print(f"  Press Ctrl+C to stop\n")

    threading.Timer(0.4, lambda: webbrowser.open(initial_url)).start()
    threading.Thread(target=watchdog, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")


if __name__ == "__main__":
    main()
