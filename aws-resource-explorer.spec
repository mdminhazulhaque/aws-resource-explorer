# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import botocore

block_cipher = None

# Use appropriate icon format for each platform
if sys.platform == 'win32':
    icon_file = 'icon.ico'
else:
    icon_file = 'icon.png'

# Get botocore and boto3 data directories
botocore_dir = os.path.dirname(botocore.__file__)
botocore_data = os.path.join(botocore_dir, 'data')

import boto3
boto3_dir = os.path.dirname(boto3.__file__)
boto3_data = os.path.join(boto3_dir, 'data')

a = Analysis(
    ['window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.png', '.'),
        ('icon.ico', '.'),
        ('resources_rc.py', '.'),
        (botocore_data, 'botocore/data'),
        (boto3_data, 'boto3/data'),
    ],
    hiddenimports=[
        # Application modules
        'resources_rc',
        'ui_form',
        'config',
        
        # PySide6 modules
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'shiboken6',
        
        # boto3 and AWS modules
        'boto3',
        'boto3.session',
        'boto3.resources',
        'boto3.dynamodb',
        'boto3.s3',
        'botocore',
        'botocore.client',
        'botocore.session',
        'botocore.credentials',
        'botocore.auth',
        'botocore.awsrequest',
        'botocore.endpoint',
        'botocore.response',
        'botocore.parsers',
        'botocore.hooks',
        'botocore.handlers',
        'botocore.retryhandler',
        'botocore.translate',
        'botocore.loaders',
        'botocore.regions',
        'botocore.model',
        'botocore.paginate',
        'botocore.waiter',
        'botocore.docs',
        'botocore.compat',
        'botocore.exceptions',
        'botocore.serialize',
        'botocore.validate',
        'botocore.utils',
        'botocore.configloader',
        
        # HTTP and networking
        'urllib3',
        'urllib3.util',
        'urllib3.util.connection',
        'urllib3.util.retry',
        'urllib3.util.ssl_',
        'urllib3.util.timeout',
        'urllib3.util.url',
        'urllib3.poolmanager',
        'urllib3.connectionpool',
        'urllib3.exceptions',
        
        # Date and JSON utilities
        'dateutil',
        'dateutil.parser',
        'dateutil.tz',
        'jmespath',
        'jmespath.functions',
        
        # Transfer and security
        's3transfer',
        's3transfer.manager',
        's3transfer.upload',
        's3transfer.download',
        'certifi',
        
        # Python compatibility
        'six',
        'six.moves',
        'six.moves.urllib',
        'six.moves.urllib.parse',
        
        # System modules that might be missed
        'signal',
        'sys',
        'os',
        'json',
        'logging',
        'threading',
        'queue',
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
