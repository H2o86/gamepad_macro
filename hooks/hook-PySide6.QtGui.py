import os
import PySide6

pyside6_dir = os.path.dirname(PySide6.__file__)
platforms_dir = os.path.join(pyside6_dir, "plugins", "platforms")
styles_dir = os.path.join(pyside6_dir, "plugins", "styles")

hiddenimports = ['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets']

datas = []
if os.path.exists(platforms_dir):
    datas.append((platforms_dir, 'PySide6/plugins/platforms'))
    datas.append((platforms_dir, 'PySide6/qt6/plugins/platforms'))
    datas.append((platforms_dir, 'PySide6/qtbase/plugins/platforms'))
    datas.append((platforms_dir, 'PySide6/Qt/plugins/platforms'))
    datas.append((platforms_dir, 'platforms'))

if os.path.exists(styles_dir):
    datas.append((styles_dir, 'PySide6/plugins/styles'))
    datas.append((styles_dir, 'PySide6/plugins/styles'))
    datas.append((styles_dir, 'styles'))

binaries = []
