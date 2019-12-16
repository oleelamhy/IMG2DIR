# -*- mode: python -*-

block_cipher = None


a = Analysis(['IMG2DIR.py'],
             pathex=['C:\\Users\\LH\\Nextcloud\\SPECTORS-Object_Recognition\\Software_Developed\\IMG2DIR'],
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
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
a.datas += [('img\\IMG2DIR.ico', 'C:\\Users\\LH\\Nextcloud\\SPECTORS-Object_Recognition\\Software_Developed\\IMG2DIR\\img\\IMG2DIR.ico','DATA')]
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='IMG2DIR_v1.2.0',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='img\\img2dir.ico')
