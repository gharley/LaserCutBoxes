# This Python file uses the following encoding: utf-8
import sys
import os

from enum import Enum
from typing import Optional

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QFrame
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5 import uic

from BasicBox import Box


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


# Handle high res monitors
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.image = Optional[QLabel]
        self.widget = Optional[QSvgWidget]
        self.props = DotDict()
        self.box_type = BoxType.All

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

        if self.chkEnd.isChecked():
            box.build_short_side()

        if self.chkBottom.isChecked():
            box.build_bottom()

    def _load_ui(self):
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

        self.show()
        self.image = self.findChild(QFrame, 'image')
        self._update_image(0)

        self.tabTypes.currentIndexChanged.connect(self._update_image)
        self.buttonBox.accepted.connect(self._build_geometry)

    def _update_image(self, box_type):
        if not isinstance(self.widget, QSvgWidget):
            self.widget = QSvgWidget(self)
            self.widget.setGeometry(self.image.geometry())

        path = os.path.join(os.path.dirname(__file__), "images")
        box_type = BoxType(box_type)
        if box_type == BoxType.All:
            self.widget.renderer().load(os.path.join(path, 'end_all.svg'))
        elif box_type == BoxType.SLOTS:
            self.widget.renderer().load(os.path.join(path, 'end_slots.svg'))
        else:
            self.widget.renderer().load(os.path.join(path, 'end_edge.svg'))

        self.widget.show()


if __name__ == "__main__":
    app = QApplication([])
    main_window = Main()
    sys.exit(app.exec_())
