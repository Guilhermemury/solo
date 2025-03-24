# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.api import PYZ, EXE
from PyInstaller.building.build_main import Analysis
import os

block_cipher = None

# Hook para resolver caminhos
def get_data_files():
    data_files = []
    # Assets principais
    for root, dirs, files in os.walk('assets'):
        for file in files:
            source = os.path.join(root, file)
            dest = os.path.join('assets', os.path.relpath(source, 'assets'))
            data_files.append((source, os.path.dirname(dest)))
    # Arquivos src
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                source = os.path.join(root, file)
                dest = os.path.join('src', os.path.relpath(source, 'src'))
                data_files.append((source, os.path.dirname(dest)))
    return data_files

a = Analysis(
    ['src/game/main.py'],
    pathex=['src', '.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('src/menus', 'src/menus'),
        ('src/sprites', 'src/sprites'),
        ('src/utils', 'src/utils'),
        ('src/game', 'src/game'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Adicionar arquivos manualmente se necessário
a.datas += [
    ('assets/enemy/Idle.png', 'assets/enemy/Idle.png', 'DATA'),
    ('assets/enemy/Walk.png', 'assets/enemy/Walk.png', 'DATA'),
    ('assets/enemy/Run.png', 'assets/enemy/Run.png', 'DATA'),
    ('assets/enemy/Jump.png', 'assets/enemy/Jump.png', 'DATA'),
    ('assets/enemy/Attack_1.png', 'assets/enemy/Attack_1.png', 'DATA'),
    ('assets/enemy/Attack_2.png', 'assets/enemy/Attack_2.png', 'DATA'),
    ('assets/enemy/Attack_3.png', 'assets/enemy/Attack_3.png', 'DATA'),
    ('assets/enemy/Hurt.png', 'assets/enemy/Hurt.png', 'DATA'),
    ('assets/enemy/Dead.png', 'assets/enemy/Dead.png', 'DATA')
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SoloLeveling',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,  # Importante: isso faz com que os recursos sejam empacotados no executável
    console=False,  # False para não mostrar o console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

# Criar o pacote completo
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SoloLeveling'
) 