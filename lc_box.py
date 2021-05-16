# This Python file uses the following encoding: utf-8
import json
import sys, os

from PyQt5 import uic
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, QLineEdit, QCheckBox, QFileDialog

from BasicBox import BasicBox
from HingeBox import HingeBox

from SVGCreator import SVGCreator
from SVGScene import SVGScene
from common import DotDict, BoxType

import lc_box_rc

# Handle high res monitors
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.config = DotDict()
        self.config.export_dir = ''
        self.config.spec_dir = ''

        self.box = None

        self.scnSide = None
        self.scnEnd = None
        self.scnBottom = None

        self._load_config()
        self._load_ui()
        self._build_geometry()

    def closeEvent(self, event) -> None:
        with open('config.json', 'w') as out_file:
            json.dump(self.config, out_file)

    def _init_connections(self):
        def toggle_type():
            if self.btnHinge.isChecked():
                self.objHinge.show()
                self.imgEnd.hide()
                self.chkEnd.hide()
            else:
                self.objHinge.hide()
                self.imgEnd.show()
                self.chkEnd.show()

        self.cboBoxType.currentIndexChanged.connect(self._set_box_type)
        self.btnGenerate.clicked.connect(self._build_geometry)
        self.btnBasic.clicked.connect(toggle_type)
        self.btnHinge.clicked.connect(toggle_type)

        self.actionGenerate_Drawings.triggered.connect(self._build_geometry)
        self.actionSave_Drawings.triggered.connect(self._save_drawings)
        self.actionLoad_Specifications.triggered.connect(self._load_specs)
        self.actionSave_Specifications.triggered.connect(self._save_specs)
        self.actionExit.triggered.connect(self.close)

        toggle_type()

        for obj in self.findChildren(QLineEdit):
            if obj.objectName().startswith('num'):
                obj.setValidator(QIntValidator())
            else:
                obj.setValidator(QDoubleValidator(0.00, 99999.99, 2))

    def _init_properties(self):
        self.props = DotDict()
        for obj in self.findChildren(QLabel):
            buddy = obj.buddy()
            if buddy is not None:
                buddy_name = buddy.objectName()

                if isinstance(buddy, QComboBox):
                    self.props.box_type = BoxType(buddy.currentIndex())
                else:
                    self.props[buddy_name] = int(buddy.text()) if buddy_name.startswith('num') else float(buddy.text())

    def _load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as in_file:
                self.config = DotDict(json.load(in_file))

    def _load_ui(self):
        ui_file = QFile(':resources/form.ui')
        ui_file.open(QFile.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

        self._init_connections()

        self.show()

        style_sheet = QFile(':resources/form.qss')
        if style_sheet.exists():
            style_sheet.open(QFile.ReadOnly)
            style = str(style_sheet.readAll(), 'utf-8')
            self.setStyleSheet(style)
            style_sheet.close()

        self.setWindowIcon(QIcon(':images/end_all.svg'))

        self.scnSide = SVGScene(self.imgSide)
        self.scnEnd = SVGScene(self.imgEnd)
        self.scnBottom = SVGScene(self.imgBottom)

    # Slots and Actions
    def _build_geometry(self):
        self._init_properties()

        if self.btnHinge.isChecked():
            box = self.box = HingeBox(self.props)
        else:
            box = self.box = BasicBox(self.props)

        self.scnSide.clear()
        self.scnEnd.clear()
        self.scnBottom.clear()

        if self.chkSide.isChecked():
            box.build_long_side()
            self.scnSide.add_lines(box.outer_width, box.outer_height, box.side)

        if self.chkEnd.isChecked():
            box.build_short_side()
            self.scnEnd.add_lines(box.depth, box.outer_height, box.end)

        if self.chkBottom.isChecked():
            box.build_bottom()
            self.scnBottom.add_lines(box.outer_width, box.outer_depth, box.bottom)

    def _load_specs(self):
        dialog = QFileDialog()

        dir_name = dialog.getOpenFileName(None, 'Load Specifications', self.config.spec_dir, 'Specifications (*.spec)')
        if dir_name[0]:
            self.config.spec_dir = dir_name[0]

            with open(dir_name[0], 'r') as in_file:
                specs = DotDict(json.load(in_file))

            for key, value in specs.items():
                widget = self.findChild(QWidget, key)
                if widget is None: continue

                if key.startswith('chk'):
                    widget.setChecked(value)
                elif key.startswith('cbo'):
                    widget.setCurrentIndex(value)
                else:
                    widget.setText(value)

            self._build_geometry()

    def _save_drawings(self):
        dialog = QFileDialog()
        options = QFileDialog.options(dialog)
        options &= ~QFileDialog.ShowDirsOnly

        dir_name = dialog.getExistingDirectory(None, 'Select Destination Folder', self.config.export_dir, options)
        if dir_name:
            self.config.export_dir = dir_name

            if self.box is None:
                return

            box = self.box
            creator = SVGCreator()

            if self.chkSide.isChecked():
                creator.create_svg(box.outer_width, box.outer_height, box.side)
                creator.write_file('{0}/{1}'.format(dir_name, 'side.svg'))

            if self.chkEnd.isChecked():
                creator.create_svg(box.outer_depth, box.outer_height, box.end)
                creator.write_file('{0}/{1}'.format(dir_name, 'end.svg'))

            if self.chkBottom.isChecked():
                creator.create_svg(box.outer_width, box.outer_depth, box.bottom)
                creator.write_file('{0}/{1}'.format(dir_name, 'bottom.svg'))

    def _save_specs(self):
        dialog = QFileDialog()

        dir_name = dialog.getSaveFileName(None, 'Save Specifications', self.config.spec_dir, 'Specifications (*.spec)')
        if dir_name[0]:
            self.config.spec_dir = dir_name[0]

            specs = DotDict()
            for child in self.findChildren(QLineEdit):
                specs[child.objectName()] = child.text()

            for child in self.findChildren(QCheckBox):
                specs[child.objectName()] = child.isChecked()

            for child in self.findChildren(QComboBox):
                specs[child.objectName()] = child.currentIndex()

            with open(dir_name[0], 'w') as out_file:
                json.dump(specs, out_file)

    def _set_box_type(self, box_type):
        self.props.box_type = BoxType(box_type)

    def _set_control_states(self):
        pass


if __name__ == "__main__":
    app = QApplication([])
    main_window = Main()
    sys.exit(app.exec_())
