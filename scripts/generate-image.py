#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate an image using Nano Banana (PipeLLM) and output base64 data or save to file.

Usage:
  python3 generate-image.py "a serene mountain landscape at sunset" [--aspect 16:9] [--model pro]
  python3 generate-image.py "prompt" --aspect 16:9 --output ./images/slide-bg.png
  python3 generate-image.py --save-key

Output:
  Without --output: prints raw base64-encoded PNG data to stdout.
  With --output: decodes base64, saves PNG to the specified path, prints the path to stdout.
  On error, prints an error message to stderr and exits with code 1.

Environment / Config:
  PIPELLM_API_KEY — API key for pipellm.ai (env var OR ~/.config/pipellm/api_key file)

Models:
  flash: gemini-3.1-flash-image-preview — fast, good for backgrounds
  pro:   gemini-3-pro-image-preview     — higher quality, up to 4K
"""

import sys
import os
import json
import argparse
import base64
import time
import getpass
import tempfile
import urllib.request
import urllib.error
from typing import List

BASE_URL = "https://api.pipellm.ai/v1beta/models"
MODELS = {
    "flash": "gemini-3.1-flash-image-preview",
    "pro": "gemini-3-pro-image-preview",
}
MAX_RETRIES = 3
RETRY_DELAYS = [10, 20, 40]
KEY_FILE = os.path.expanduser("~/.config/pipellm/api_key")
KEY_ENV = "PIPELLM_API_KEY"
REDACTION = "[REDACTED]"


def _known_secrets() -> List[str]:
    """Return locally known PipeLLM secrets for log redaction."""
    secrets = []
    env_key = os.environ.get(KEY_ENV, "").strip()
    if env_key:
        secrets.append(env_key)
    if os.path.isfile(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                file_key = f.read().strip()
            if file_key:
                secrets.append(file_key)
        except OSError:
            pass
    return sorted(set(secrets), key=len, reverse=True)


def redact_secrets(text: object) -> str:
    """Remove locally known PipeLLM secrets from text before logging."""
    redacted = str(text)
    for secret in _known_secrets():
        if len(secret) >= 8:
            redacted = redacted.replace(secret, REDACTION)
    return redacted


def get_api_key() -> str:
    """Read API key from env var first, then from config file."""
    key = os.environ.get(KEY_ENV, "").strip()
    if key:
        return key
    if os.path.isfile(KEY_FILE):
        try:
            os.chmod(KEY_FILE, 0o600)
        except OSError:
            pass
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            key = f.read().strip()
        if key:
            return key
    print("Error: PIPELLM_API_KEY not set and no key found at " + KEY_FILE, file=sys.stderr)
    sys.exit(1)


def save_api_key(key: str) -> None:
    """Persist API key to config file for future sessions."""
    key = key.strip()
    if not key:
        print("Error: API key cannot be empty.", file=sys.stderr)
        sys.exit(1)

    key_dir = os.path.dirname(KEY_FILE)
    os.makedirs(key_dir, mode=0o700, exist_ok=True)
    try:
        os.chmod(key_dir, 0o700)
    except OSError:
        pass

    fd, tmp_path = tempfile.mkstemp(prefix=".api_key.", dir=key_dir, text=True)
    try:
        os.chmod(tmp_path, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(key + "\n")
        os.replace(tmp_path, KEY_FILE)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    os.chmod(KEY_FILE, 0o600)


def read_api_key_for_save() -> str:
    """Read an API key without requiring it to appear in argv."""
    if sys.stdin.isatty():
        return getpass.getpass("PipeLLM API key: ").strip()
    return sys.stdin.read().strip()


def generate(prompt: str, aspect: str = "16:9", model: str = "flash") -> str:
    api_key = get_api_key()

    model_id = MODELS.get(model, MODELS["flash"])
    url = f"{BASE_URL}/{model_id}:generateContent"

    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"imageConfig": {"aspectRatio": aspect}},
    }

    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                    return part["inlineData"]["data"]
            print("Error: No image data in response.", file=sys.stderr)
            print(f"Response: {redact_secrets(json.dumps(data, indent=2))}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode() if e.fp else ""
            if e.code == 429 and attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt]
                print(f"Rate limited (429), retrying in {delay}s (attempt {attempt+1}/{MAX_RETRIES})...", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"Error: HTTP {e.code} — {redact_secrets(err_body)}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            if attempt < MAX_RETRIES and "timed out" in str(e).lower():
                delay = RETRY_DELAYS[attempt]
                print(f"Timeout, retrying in {delay}s (attempt {attempt+1}/{MAX_RETRIES})...", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"Error: {redact_secrets(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate image via Nano Banana")
    parser.add_argument("prompt", nargs="?", help="Image generation prompt")
    parser.add_argument("--aspect", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--model", default="flash", choices=["flash", "pro"], help="Model tier (default: flash)")
    parser.add_argument("--output", default=None, help="Save decoded PNG to this file path instead of printing base64")
    parser.add_argument("--save-key", action="store_true", help="Read API key from stdin or a hidden prompt, save it to ~/.config/pipellm/api_key, and exit")
    args = parser.parse_args()

    if args.save_key:
        if args.prompt:
            parser.error("--save-key no longer accepts a key argument; pipe the key on stdin or enter it at the hidden prompt")
        save_api_key(read_api_key_for_save())
        print("API key saved to " + KEY_FILE, file=sys.stderr)
        sys.exit(0)

    if not args.prompt:
        parser.error("prompt is required (unless using --save-key)")

    b64 = generate(args.prompt, args.aspect, args.model)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "wb") as f:
            f.write(base64.b64decode(b64))
        sys.stdout.write(os.path.abspath(args.output))
    else:
        sys.stdout.write(b64)
