# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['TennisForTwo.py'],
             pathex=['C:\\Users\\Dustin\\Documents\\Projects\\tennisfortwo'],
             binaries=[],
             datas=[('data', 'data'), ('tennis.bmp', '.'), ('freesansbold.ttf', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['numpy', 'scipy', 'lib2to3'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='TennisForTwo',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='TennisForTwo')
