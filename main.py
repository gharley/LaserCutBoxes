# This Python file uses the following encoding: utf-8
import sys
import os

from enum import Enum

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox
from PyQt5.QtCore import QFile, Qt
from PyQt5 import uic

from BasicBox import Box
from SVGScene import SVGScene
from SVGCreator import SVGCreator


# Handle high res monitors
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


# DotDict - easy dictionary access
class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Box type enums
class BoxType(Enum):
    All = 0
    SLOTS = 1
    TABS = 2


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.props = DotDict()
        self.box_type = BoxType.All
        self.scnSide = None
        self.scnEnd = None
        self.scnBottom = None

        self._load_ui()

    def _init_properties(self):
        for obj in self.findChildren(QLabel):
            buddy = obj.buddy()
            if buddy is not None:
                buddy_name = buddy.objectName()

                if isinstance(buddy, QComboBox):
                    self.props.box_type = BoxType(buddy.currentIndex())
                else:
                    self.props[buddy_name] = int(buddy.text()) if buddy_name.startswith('num') else float(buddy.text())

    def _build_geometry(self):
        self._init_properties()
        box = Box(self.props)

        if self.chkSide.isChecked():
            box.build_long_side()
            self.scnSide.add_lines(box.side)

        if self.chkEnd.isChecked():
            box.build_short_side()
            self.scnEnd.add_lines(box.end)

        if self.chkBottom.isChecked():
            box.build_bottom()
            self.scnBottom.add_lines(box.bottom)

    def _load_ui(self):
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

        self.show()

        self.scnSide = SVGScene(self.imgSide)
        self.scnEnd = SVGScene(self.imgEnd)
        self.scnBottom = SVGScene(self.imgBottom)

        self.btnGenerate.clicked.connect(self._build_geometry)


if __name__ == "__main__":
    app = QApplication([])
    main_window = Main()
    sys.exit(app.exec_())
