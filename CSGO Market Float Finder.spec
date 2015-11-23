# -*- mode: python -*-
import os
import inspect 

filename = inspect.getframeinfo(inspect.currentframe()).filename
specdir = os.path.dirname(os.path.abspath(filename))


a = Analysis(['ui.py'],
             pathex=[os.path.join(specdir,)],
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
          console=False , icon=os.path.join(specdir, 'logo.ico'))