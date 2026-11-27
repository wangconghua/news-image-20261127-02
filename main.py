#!/usr/bin/env python3
"""Copy entry.png to the output directory, verifying the copy byte-for-byte.

Standard library only. The output directory comes from the
MAKEFUN_OUTPUT_DIR environment variable and defaults to /output.
"""

import hashlib
import os
import sys
from pathlib import Path

SOURCE_NAME = "entry.png"

# Competition cap: the entry image must be at most 1 MiB.
MAX_BYTES = 1_048_576


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main() -> int:
    source = Path(__file__).resolve().parent / SOURCE_NAME
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

    if not source.is_file():
        return fail(
            f"source image not found (expected a file at this path): {source}"
        )

    try:
        data = source.read_bytes()
    except OSError as exc:
        return fail(f"cannot read {source}: {exc}")

    if not data:
        return fail(f"source image is empty, refusing to copy: {source}")

    if len(data) > MAX_BYTES:
        return fail(
            f"source image is {len(data)} bytes, over the "
            f"{MAX_BYTES} byte limit: {source}"
        )

    source_hash = sha256_hex(data)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return fail(f"cannot create output directory {output_dir}: {exc}")

    dest = output_dir / SOURCE_NAME
    try:
        dest.write_bytes(data)
    except OSError as exc:
        return fail(f"cannot write {dest}: {exc}")

    try:
        copied = dest.read_bytes()
    except OSError as exc:
        return fail(f"cannot read back {dest}: {exc}")

    if sha256_hex(copied) != source_hash:
        return fail(
            "SHA-256 mismatch after copy: "
            f"source {source_hash} != dest {sha256_hex(copied)}"
        )

    print(
        f"copied {SOURCE_NAME} ({len(data)} bytes) "
        f"to {dest} (sha256 {source_hash})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
