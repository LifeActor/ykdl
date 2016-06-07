from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [x for x in collect_submodules('ykdl') ]
