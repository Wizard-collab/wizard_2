# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
import os

a = Analysis([os.path.abspath('installer.py')],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [ ('__wizard__.zip', '.\\__wizard__.zip', 'DATA')]
a.datas += [ ('version.yaml', '.\\version.yaml', 'DATA')]
a.datas += [ ('ressources\\icons\\wizard_setup.png', '.\\ressources\\icons\\wizard_setup.png', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='__installer_temp__',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon=os.path.abspath('ressources\\icons\\wizard_setup.ico'))
