# -*- mode: python ; coding: utf-8 -*-

from icon_factory import ensure_icon_assets

ico_path, png_path = ensure_icon_assets()

a = Analysis(
    ['organizador_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.'), (ico_path, 'generated/icons'), (png_path, 'generated/icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='organizador_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[ico_path],
)
