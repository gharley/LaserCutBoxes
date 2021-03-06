# This Python file uses the following encoding: utf-8
import sys
import os

from enum import Enum
from typing import Optional

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QSizePolicy, QFrame
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5 import uic

from BasicBox import Box
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

        self.side_image = Optional[QSvgWidget]
        self.end_image = Optional[QSvgWidget]
        self.bottom_image = Optional[QSvgWidget]
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
        creator = SVGCreator()

        if self.chkSide.isChecked():
            box.build_long_side()
            creator.create_svg(box.outer_width, box.outer_height, box.side)
            self.side_image.renderer().load(creator.svg)
            self.side_image.show()

        if self.chkEnd.isChecked():
            box.build_short_side()
            creator.create_svg(box.outer_depth, box.outer_height, box.end)
            self.end_image.renderer().load(creator.svg)
            self.end_image.show()

        if self.chkBottom.isChecked():
            box.build_bottom()
            creator.create_svg(box.depth, box.width, box.bottom)
            self.bottom_image.renderer().load(creator.svg)
            self.bottom_image.show()

    def _load_ui(self):
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

        self.show()

        self.side_image = QSvgWidget(self.frmSide)
        self.side_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.end_image = QSvgWidget(self.frmEnd)
        self.end_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bottom_image = QSvgWidget(self.frmBottom)
        self.bottom_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # self._update_image(0)
        #
        # self.tabTypes.currentIndexChanged.connect(self._update_image)
        self.btnGenerate.clicked.connect(self._build_geometry)

    def _update_image(self, box_type):
        path = os.path.join(os.path.dirname(__file__), "images")
        box_type = BoxType(box_type)
        if box_type == BoxType.All:
            self.side_image.renderer().load(os.path.join(path, 'end_all.svg'))
        elif box_type == BoxType.SLOTS:
            self.side_image.renderer().load(os.path.join(path, 'end_slots.svg'))
        else:
            self.side_image.renderer().load(os.path.join(path, 'end_edge.svg'))

        self.side_image.show()


if __name__ == "__main__":
    app = QApplication([])
    main_window = Main()
    sys.exit(app.exec_())
