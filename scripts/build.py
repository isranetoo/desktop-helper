#!/usr/bin/env python3
"""Build multiplataforma do Sortify.

Uso:
  python scripts/build.py              # Detecta SO automaticamente
  python scripts/build.py --target macos
  python scripts/build.py --target linux
  python scripts/build.py --target windows
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist"
ICO_HEADER = b"\x00\x00\x01\x00"
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


TARGET_HOSTS = {
    "windows": "Windows",
    "macos": "Darwin",
    "linux": "Linux",
}


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print("[build]", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT, env=env)


def install_base_deps() -> None:
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def has_file_signature(path: Path, signature: bytes) -> bool:
    if not path.exists() or not path.is_file():
        return False

    with path.open("rb") as file_obj:
        return file_obj.read(len(signature)) == signature


def resolve_windows_icon() -> str:
    ico_icon = ROOT / "icons" / "sortify.ico"
    png_icon = ROOT / "icons" / "sortify.png"

    if has_file_signature(ico_icon, ICO_HEADER):
        return "icons/sortify.ico"

    if has_file_signature(png_icon, PNG_HEADER):
        if ico_icon.exists():
            print(
                "[build] icons/sortify.ico n\u00e3o \u00e9 um arquivo ICO v\u00e1lido. "
                "Usando icons/sortify.png com convers\u00e3o via Pillow."
            )
        return "icons/sortify.png"

    raise FileNotFoundError(
        "[build] Nenhum \u00edcone v\u00e1lido encontrado em icons/sortify.ico "
        "ou icons/sortify.png."
    )


def validate_target_host(target: str) -> None:
    current_host = platform.system()
    expected_host = TARGET_HOSTS[target]
    if current_host == expected_host:
        return

    raise SystemExit(
        "[build] O alvo '{}' precisa ser gerado em '{}'. "
        "Host atual: '{}'. Use a máquina/runner correspondente ou o workflow "
        "de release em .github/workflows/release.yml.".format(
            target, expected_host, current_host
        )
    )


def build_windows() -> None:
    print("[build] Empacotando para Windows (PyInstaller)...")
    icon_path = resolve_windows_icon()
    run([sys.executable, "-m", "pip", "install", "pyinstaller", "Pillow"])
    sep = ";"
    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--windowed",
            "--name",
            "sortify-windows",
            "--icon",
            icon_path,
            "--add-data",
            f"config.json{sep}.",
            "--add-data",
            f"icons{sep}icons",
            "organizador_gui.py",
        ]
    )


def build_macos() -> None:
    print("[build] Empacotando para macOS (py2app)...")
    run([sys.executable, "-m", "pip", "install", "py2app"])

    with tempfile.TemporaryDirectory() as tmp:
        setup_file = Path(tmp) / "setup.py"
        setup_file.write_text(
            """
from setuptools import setup

APP = ['organizador_gui.py']
DATA_FILES = [('', ['config.json'])]
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleName': 'Sortify',
        'CFBundleDisplayName': 'Sortify',
    }
}

setup(
    app=APP,
    name='Sortify',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
""".strip()
        )
        run([sys.executable, str(setup_file), "py2app"])

    app_source = ROOT / "dist" / "Sortify.app"
    if app_source.exists():
        final_app = DIST_DIR / "Sortify-macos.app"
        if final_app.exists():
            shutil.rmtree(final_app)
        shutil.move(str(app_source), str(final_app))
        print(f"[build] App gerado em: {final_app}")


def build_linux() -> None:
    print("[build] Empacotando para Linux (AppImage via PyInstaller)...")
    run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--windowed",
            "--name",
            "sortify-linux",
            "--icon",
            "icons/sortify.png",
            "--add-data",
            "config.json:.",
            "--add-data",
            "icons:icons",
            "organizador_gui.py",
        ]
    )

    appimagetool = shutil.which("appimagetool")
    if not appimagetool:
        print(
            "[build] appimagetool não encontrado. "
            "Instale-o para gerar .AppImage ou publique o binário dist/sortify-linux."
        )
        return

    appdir = ROOT / "Sortify.AppDir"
    if appdir.exists():
        shutil.rmtree(appdir)

    (appdir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
    (appdir / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)

    shutil.copy2(DIST_DIR / "sortify-linux", appdir / "usr" / "bin" / "sortify")

    desktop_entry = appdir / "sortify.desktop"
    desktop_entry.write_text(
        """[Desktop Entry]
Type=Application
Name=Sortify
Exec=sortify
Icon=sortify
Categories=Utility;
Terminal=false
"""
    )

    if (ROOT / "icons" / "sortify.png").exists():
        shutil.copy2(ROOT / "icons" / "sortify.png", appdir / "sortify.png")

    apprun = appdir / "AppRun"
    apprun.write_text("#!/bin/sh\nexec \"$APPDIR/usr/bin/sortify\" \"$@\"\n")
    os.chmod(apprun, 0o755)

    run([appimagetool, str(appdir), str(DIST_DIR / "sortify-linux.AppImage")])


def detect_target() -> str:
    sys_name = platform.system().lower()
    if "windows" in sys_name:
        return "windows"
    if "darwin" in sys_name:
        return "macos"
    return "linux"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build multiplataforma do Sortify")
    parser.add_argument(
        "--target",
        choices=["windows", "macos", "linux", "auto"],
        default="auto",
        help="Plataforma alvo para empacotamento.",
    )
    args = parser.parse_args()

    target = detect_target() if args.target == "auto" else args.target
    print(f"[build] Plataforma alvo: {target}")

    validate_target_host(target)
    install_base_deps()

    if target == "windows":
        build_windows()
    elif target == "macos":
        build_macos()
    else:
        build_linux()

    print("[build] Concluído. Artefatos disponíveis em dist/.")


if __name__ == "__main__":
    main()
