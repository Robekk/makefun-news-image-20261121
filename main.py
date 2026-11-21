#!/usr/bin/env python3
"""make.fun news-image-20261121 entry program.

Copies the pre-rendered poster (entry.png, sitting next to this file)
into the output directory as entry.png. Python 3 standard library only.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def main():
    if not os.path.isfile(SOURCE):
        print(f"error: source poster not found: {SOURCE}", file=sys.stderr)
        return 1
    with open(SOURCE, "rb") as fh:
        magic = fh.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        print("error: source poster is not a PNG file", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    src_size = os.path.getsize(SOURCE)
    if os.path.getsize(dest) != src_size:
        print("error: copied file size does not match source", file=sys.stderr)
        return 1
    print(f"Copied {src_size} bytes to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
