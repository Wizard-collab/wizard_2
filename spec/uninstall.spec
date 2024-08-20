# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
import os

a = Analysis([os.path.abspath('uninstall.py')],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt5'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [ ('ressources\\icons\\wizard_setup.png', '.\\ressources\\icons\\wizard_setup.png', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='uninstall',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon=os.path.abspath('ressources\\icons\\wizard_setup.ico'))
