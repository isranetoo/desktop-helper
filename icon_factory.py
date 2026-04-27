"""
Geração de ícones do aplicativo sem versionar arquivos binários.
"""

from __future__ import annotations

import os
import struct
import zlib
import binascii


def _build_rgba_pixels(size: int = 64) -> list[tuple[int, int, int, int]]:
    pixels = []
    center = size // 2
    for y in range(size):
        for x in range(size):
            r, g, b, a = 14, 23, 38, 255
            dist = ((x - center) ** 2 + (y - center) ** 2) ** 0.5
            if dist < size * 0.41:
                r, g, b = 20, 56, 96
            if 10 < x < size - 10 and 10 < y < size - 10:
                if (x - center) ** 2 + (y - center) ** 2 < (size * 0.31) ** 2:
                    r, g, b = 59, 130, 246
            if (
                (size * 0.25 < y < size * 0.38 and size * 0.28 < x < size * 0.72)
                or (size * 0.38 <= y < size * 0.5 and size * 0.28 < x < size * 0.47)
                or (size * 0.5 <= y < size * 0.63 and size * 0.28 < x < size * 0.72)
                or (size * 0.63 <= y < size * 0.75 and size * 0.53 < x < size * 0.72)
            ):
                r, g, b = 241, 245, 249
            pixels.append((int(r), int(g), int(b), a))
    return pixels


def _encode_png(path: str, size: int, pixels: list[tuple[int, int, int, int]]) -> None:
    raw = b""
    for y in range(size):
        row = pixels[y * size : (y + 1) * size]
        raw += b"\x00" + b"".join(bytes(px) for px in row)
    comp = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = binascii.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", comp)
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as fp:
        fp.write(png)


def _encode_ico(path: str, size: int, pixels: list[tuple[int, int, int, int]]) -> None:
    w = h = 32
    step = size // w
    small = []
    for y in range(h):
        for x in range(w):
            small.append(pixels[(y * step) * size + (x * step)])

    xor = b""
    for y in range(h - 1, -1, -1):
        row = small[y * w : (y + 1) * w]
        xor += b"".join(bytes((b, g, r, a)) for (r, g, b, a) in row)

    and_mask = b"\x00" * (4 * h)
    bi = struct.pack("<IIIHHIIIIII", 40, w, h * 2, 1, 32, 0, len(xor) + len(and_mask), 0, 0, 0, 0)
    image = bi + xor + and_mask

    icon_dir = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(image), 22)
    with open(path, "wb") as fp:
        fp.write(icon_dir + entry + image)


def ensure_icon_assets(base_dir: str | None = None) -> tuple[str, str]:
    root = base_dir or os.path.abspath(".")
    out_dir = os.path.join(root, "generated", "icons")
    os.makedirs(out_dir, exist_ok=True)
    ico_path = os.path.join(out_dir, "sortify.ico")
    png_path = os.path.join(out_dir, "sortify.png")

    if os.path.exists(ico_path) and os.path.exists(png_path):
        return ico_path, png_path

    size = 64
    pixels = _build_rgba_pixels(size)
    _encode_png(png_path, size, pixels)
    _encode_ico(ico_path, size, pixels)
    return ico_path, png_path

