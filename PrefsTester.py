from ProjectPrefs import ProjectPrefs

prefs = ProjectPrefs()
prefs.setPref('MaskPath', '/my/crazy/dir')
prefs.saveConfig('result.ini')
