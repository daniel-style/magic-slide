#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate an image using Nano Banana (PipeLLM) and output base64 data or save to file.

Usage:
  python3 generate-image.py "a serene mountain landscape at sunset" [--aspect 16:9] [--model pro]
  python3 generate-image.py "prompt" --aspect 16:9 --output ./images/slide-bg.png

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
import urllib.request
import urllib.error

BASE_URL = "https://api.pipellm.ai/v1beta/models"
MODELS = {
    "flash": "gemini-3.1-flash-image-preview",
    "pro": "gemini-3-pro-image-preview",
}
MAX_RETRIES = 3
RETRY_DELAYS = [10, 20, 40]
KEY_FILE = os.path.expanduser("~/.config/pipellm/api_key")


def get_api_key() -> str:
    """Read API key from env var first, then from config file."""
    key = os.environ.get("PIPELLM_API_KEY", "").strip()
    if key:
        return key
    if os.path.isfile(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            key = f.read().strip()
        if key:
            return key
    print("Error: PIPELLM_API_KEY not set and no key found at " + KEY_FILE, file=sys.stderr)
    sys.exit(1)


def save_api_key(key: str) -> None:
    """Persist API key to config file for future sessions."""
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    with open(KEY_FILE, "w") as f:
        f.write(key.strip() + "\n")
    os.chmod(KEY_FILE, 0o600)


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
            print(f"Response: {json.dumps(data, indent=2)}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode() if e.fp else ""
            if e.code == 429 and attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt]
                print(f"Rate limited (429), retrying in {delay}s (attempt {attempt+1}/{MAX_RETRIES})...", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"Error: HTTP {e.code} — {err_body}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            if attempt < MAX_RETRIES and "timed out" in str(e).lower():
                delay = RETRY_DELAYS[attempt]
                print(f"Timeout, retrying in {delay}s (attempt {attempt+1}/{MAX_RETRIES})...", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate image via Nano Banana")
    parser.add_argument("prompt", nargs="?", help="Image generation prompt")
    parser.add_argument("--aspect", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--model", default="flash", choices=["flash", "pro"], help="Model tier (default: flash)")
    parser.add_argument("--output", default=None, help="Save decoded PNG to this file path instead of printing base64")
    parser.add_argument("--save-key", metavar="KEY", help="Save API key to ~/.config/pipellm/api_key and exit")
    args = parser.parse_args()

    if args.save_key:
        save_api_key(args.save_key)
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
