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


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print("[build]", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT, env=env)


def install_base_deps() -> None:
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def build_windows() -> None:
    print("[build] Empacotando para Windows (PyInstaller)...")
    run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    sep = ";"
    run(
        [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name",
            "sortify-windows",
            "--add-data",
            f"config.json{sep}.",
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
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name",
            "sortify-linux",
            "--add-data",
            "config.json:.",
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
