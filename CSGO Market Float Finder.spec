# -*- mode: python -*-
a = Analysis(['ui.py'],
             pathex=['\\'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='CSGO Market Float Finder.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='\\logo.ico')
