# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

# Collect hidden imports
hiddenimports = collect_submodules('pyqtgraph') + collect_submodules('OpenGL') + collect_submodules('jupyter_rfb')

a = Analysis(
    ['GUI_v1.0.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=['.'],  # Directory where custom hooks are located
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

#a = Analysis(
  #  ['GUI_v1.0.py'],
 #   pathex=[],
  #  binaries=[],
  #  datas=[],
   # hiddenimports=[],
  #  hookspath=[],
 #   hooksconfig={},
  #  runtime_hooks=[],
 #   excludes=[],
 #   noarchive=False,
 #   optimize=0,
#)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FSGUI',
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
