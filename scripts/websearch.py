#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Web search using PipeLLM WebSearch API.

Usage:
  python3 websearch.py "search query" [--simple]

Output:
  JSON with search results to stdout.
  Errors to stderr with exit code 1.

Environment:
  PIPELLM_API_KEY — API key for pipellm.ai (env var OR ~/.config/pipellm/api_key file)

Endpoints:
  Default: Deep Search (/v1/websearch/search) — Full retrieval + reranking + contexts
  --simple: Simple Search (/v1/websearch/simple-search) — Fast snippets only
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
import urllib.parse
import time

BASE_URL = "https://api.pipellm.ai/v1/websearch"
MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 10]
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


def search(query: str, simple: bool = False) -> dict:
    """Perform web search using PipeLLM WebSearch API.

    Args:
        query: Search query string
        simple: If True, use simple-search endpoint (faster, no contexts)

    Returns:
        dict with 'organic' key containing search results

    Raises:
        Exception: On API errors or network failures after retries
    """
    api_key = get_api_key()

    endpoint = "simple-search" if simple else "search"
    url = f"{BASE_URL}/{endpoint}?{urllib.parse.urlencode({'q': query})}"

    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {api_key}"}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                if data.get("code") == 200:
                    return data.get("data", {})
                else:
                    raise Exception(f"API error: {data.get('message', 'Unknown error')}")

        except urllib.error.HTTPError as e:
            if e.code == 503 and attempt < MAX_RETRIES:
                # Handle 503 Service Unavailable with retry
                retry_after = e.headers.get("Retry-After")
                if retry_after:
                    time.sleep(int(retry_after))
                else:
                    time.sleep(RETRY_DELAYS[attempt])
                continue
            elif e.code == 400:
                error_body = e.read().decode() if hasattr(e, 'read') else ""
                raise Exception(f"Bad request (400): {error_body}")
            elif e.code == 401:
                raise Exception("Authentication failed (401): Invalid API key")
            elif e.code == 404:
                raise Exception("No search results found (404)")
            else:
                raise Exception(f"HTTP error {e.code}: {e.reason}")

        except urllib.error.URLError as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAYS[attempt])
                continue
            raise Exception(f"Network error: {e.reason}")

        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAYS[attempt])
                continue
            raise


def main():
    parser = argparse.ArgumentParser(
        description="PipeLLM WebSearch - Search the web via PipeLLM API"
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Use simple search (faster, no deep retrieval)"
    )
    args = parser.parse_args()

    try:
        results = search(args.query, args.simple)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
