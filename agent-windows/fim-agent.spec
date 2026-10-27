# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['F:/srirampst/DCP/FIM/agent-windows/src/main.py'],
    pathex=['F:/srirampst/DCP/FIM/agent-windows/src'],
    binaries=[],
    datas=[],
    hiddenimports=['win32timezone', 'servicemanager', 'win32service', 'win32serviceutil'],
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
    name='fim-agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
