# shipyard.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/*.png', 'assets'),
        ('assets/*.ico', 'assets'),
        ('config/servers.yaml.template', 'config'),
        ('docs/help_content.py', 'docs'),
        ('pwa/*', 'pwa'),
    ],
    hiddenimports=['pystray._win32', 'PIL._tkinter_finder'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
    name='shipyard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    windowed=True,
    icon='assets/icon.ico'
)
