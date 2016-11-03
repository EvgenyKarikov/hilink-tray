# -*- mode: python -*-

block_cipher = None


a = Analysis(['hilink-tray\\hilink-tray.py'],
             pathex=['Z:\\home\\ilya\\hilink-tray'],
             binaries=[('C:\\Python27\\lib\\site-packages\\PySide\\plugins\\phonon_backend\\phonon_ds94.dll', 'qt4_plugins\\phonon_backend')],
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='hilink-tray',
          debug=False,
          strip=False,
          upx=False,
          console=False , icon='hilink-tray.ico')
