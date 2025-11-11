# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Bot 2 (RECEIVER)

block_cipher = None

a = Analysis(
    ['../SYNS_Bot_PY/sync2_data_receiver.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../SYNS_Bot_PY/bot_config.json', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'requests',
        'werkzeug',
        'jinja2',
        'click',
        'itsdangerous',
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
    name='SYNS_Bot2_Receiver',
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
    icon=None,
)
