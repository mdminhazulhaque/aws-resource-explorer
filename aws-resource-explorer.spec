# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

# Use appropriate icon format for each platform
if sys.platform == 'win32':
    icon_file = 'icon.ico'
else:
    icon_file = 'icon.png'

a = Analysis(
    ['window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.png', '.'),
        ('icon.ico', '.'),
        ('resources_rc.py', '.')
    ],
    hiddenimports=[
        'resources_rc'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='aws-resource-explorer',
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
    icon=icon_file
)
