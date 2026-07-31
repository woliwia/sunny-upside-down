#!/usr/bin/env python3
"""Sunny Upside Down — tiny zero-dependency dev server.

Why not plain `python3 -m http.server`?
  1. No-cache headers, so a reload always gives you the newest version of the app.
  2. It turns a local `.env` file into `/config.js`, so optional API keys stay
     out of the source code (and out of git).

Usage:
    python3 serve.py [port]          # default: 7777

Optional configuration — copy `.env.example` to `.env` and fill in what you need:
    SHADEMAP_API_KEY=your-free-key-from-https://shademap.app/about
"""
import http.server
import json
import os
import socketserver
import sys

DEFAULT_PORT = 7777
HERE = os.path.dirname(os.path.abspath(__file__))
# Only these keys are ever exposed to the browser. Anything else in .env stays server-side.
PUBLIC_ENV_KEYS = ("SHADEMAP_API_KEY",)


def read_env(path=".env"):
    """Parse a minimal KEY=VALUE .env file. Missing file → empty config."""
    config = {}
    if not os.path.exists(path):
        return config
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip("'\"")
            if key in PUBLIC_ENV_KEYS and value:
                config[key] = value
    return config


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        if self.path.split("?")[0].rstrip("/") == "/config.js":
            body = f"window.SUD_CONFIG = {json.dumps(read_env())};\n".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    os.chdir(HERE)
    engine = "ShadeMap (key loaded from .env)" if read_env() else "built-in (no .env key set)"
    with ReusableServer(("", port), Handler) as httpd:
        print(f"🍳☀️  Sunny Upside Down → http://localhost:{port}")
        print(f"     shadow engine: {engine}")
        print("     press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋  stopped")


if __name__ == "__main__":
    main()
