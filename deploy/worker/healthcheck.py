"""Read-only worker liveness check; no database or provider access."""
from __future__ import annotations

import pathlib


TARGETS = (
    b"python\x00-m\x00rag_app\x00worker\x00",
    b"/opt/venv/bin/python\x00-m\x00rag_app\x00worker\x00",
)
STOPPED_STATES = {"Z", "T", "t"}


def main() -> int:
    for entry in pathlib.Path("/proc").glob("[0-9]*/cmdline"):
        try:
            if entry.read_bytes() not in TARGETS:
                continue
            text = (entry.parent / "stat").read_text(encoding="ascii")
            close = text.rfind(")")
            if close < 0 or close + 2 >= len(text):
                continue
            state = text[close + 2]
        except OSError:
            continue
        if state not in STOPPED_STATES:
            return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
