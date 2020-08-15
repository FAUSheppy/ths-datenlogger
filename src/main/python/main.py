#!/usr/bin/python3

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

import localization.de as de

class WidgetGallery(QDialog):

    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.localization     = de
        self.srcFileString    = ""
        self.targetFileString = ""

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        self.createFileSelection()
        self.createDateSelection()
        self.createCheckboxArea()

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.fileSelectionGroup, 1, 0)
        mainLayout.addWidget(self.dateSelectionGroupBox, 1, 1)
        mainLayout.addWidget(self.checkboxGroup, 2, 0)

        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)

        self.setLayout(mainLayout)

        self.setWindowTitle(self.localization.window_title)

    def createFileSelection(self):
        '''Generate the area containing the file selectors and go button'''

        self.fileSelectionGroup = QGroupBox(self.localization.file_selection)

        # basic object #
        buttonGo      = QPushButton(self.localization.button_go)
        buttonSrcFile = QPushButton(self.localization.button_set_src_file)
        srcFileName   = QLabel(self.srcFileString)

        buttonTargetFile = QPushButton(self.targetFileString)
        buttonUseSrcDir  = QCheckBox(self.localization.button_use_src_dir)

        # connectors #
        buttonGo.connect(self.run)
        buttonSrcFile.connect(self.selectSrcFile)
        buttonTargetFile.connect(self.selectTargetFile)
        buttonUseSrcDir.connect(self.useSrcDir)

        # layout #
        layout = QVBoxLayout()

        layout.addWidget(buttonGo)
        layout.addWidget(buttonSrcFile)
        layout.addWidget(srcFileName)

        layout.addWidget(buttonTargetFile)
        layout.addWidget(buttonUseSrcDir)

        layout.addStretch(1)
        self.dateSelectionGroupBox.setLayout(layout)

    def createDateSelection(self):
        '''Generate the area containing the date selectors'''

        self.dateSelectionGroupBox = QGroupBox(self.localization.date_selection)

        layout = QVBoxLayout()
        #layout.addWidget() # TODO
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)

    def createCheckboxArea(self):
        '''Generate area  with configuration options'''

        self.checkboxGroup = QGroupBox(self.localization.options)

        buttonOTemp     = QCheckBox(self.localization.button_otemp)
        buttonOHumidity = QCheckBox(self.localization.button_ohumidity)

        layout = QVBoxLayout()
        layout.addWidget(buttonOTemp)
        layout.addWidget(buttonOHumidity)
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)


if __name__ == '__main__':
    appctxt = ApplicationContext()
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(appctxt.app.exec_())
