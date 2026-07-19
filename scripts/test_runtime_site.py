#!/usr/bin/env python3
"""Serve the packaged artifact and execute its three build-aware tools."""

from __future__ import annotations

import functools
import shutil
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
HARNESS = ROOT / "scripts" / "runtime_fetch_harness.mjs"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def main() -> int:
    if not DIST.is_dir():
        raise SystemExit("dist/ is required; run scripts/package_site.py first")
    node = shutil.which("node")
    if not node:
        raise SystemExit("node is required for the no-dependency browser-runtime harness")

    handler = functools.partial(QuietHandler, directory=DIST)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}/"
        result = subprocess.run(
            [node, str(HARNESS), base_url],
            cwd=ROOT,
            text=True,
            check=False,
        )
        return result.returncode
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    raise SystemExit(main())
