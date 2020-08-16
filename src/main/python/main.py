#!/usr/bin/python3

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import QDateTime, Qt, QTimer, QUrl
import PyQt5.QtCore
import PyQt5.QtGui
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFileDialog, QDateEdit, QMessageBox)

import localization.de as de
import sys
import datetime as dt

import input_backend
import plot_main
import config_parse as cp

class WidgetGallery(QDialog):

    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.localization     = de
        self.srcFileString    = ""
        self.targetFileString = ""
        self.truePath = None

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        self.createStartSection()
        self.createFileSelection()
        self.createDateSelection()
        self.createCheckboxArea()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.fileSelectionGroup, 1, 0)
        mainLayout.addWidget(self.dateSelectionGroupBox, 2, 0)
        mainLayout.addWidget(self.checkboxGroup, 3, 0)
        mainLayout.addWidget(self.startSection, 4, 0)

        self.setLayout(mainLayout)

        self.setWindowTitle(self.localization.window_title)

    def createStartSection(self):
        '''Generate Aread containing the start button'''

        self.startSection = QGroupBox(self.localization.start_section)
        self.buttonGo = QPushButton(self.localization.button_go)
        self.buttonGo.setDisabled(True)
        self.buttonGo.clicked.connect(self.run)

        layout = QVBoxLayout()
        layout.addWidget(self.buttonGo)

        self.startSection.setLayout(layout)

    def createFileSelection(self):
        '''Generate the area containing the file selectors and go button'''

        self.fileSelectionGroup = QGroupBox(self.localization.file_selection)

        # basic object #
        self.buttonSrcFile = QPushButton(self.localization.button_set_src_file)
        self.srcFileName   = QLabel(self.localization.output_file)

        self.buttonTargetFile = QPushButton(self.localization.output_file_placeholder)
        self.boxUseSrcDir  = QCheckBox(self.localization.button_use_src_dir)

        # connectors #
        self.buttonSrcFile.clicked.connect(self.selectSrcFile)
        self.buttonTargetFile.clicked.connect(self.selectTargetFile)
        self.boxUseSrcDir.stateChanged.connect(self.useSrcDir)
        self.boxUseSrcDir.setChecked(True)

        # layout #
        layout = QVBoxLayout()

        layout.addWidget(self.buttonSrcFile)
        layout.addWidget(self.srcFileName)

        layout.addWidget(self.buttonTargetFile)
        layout.addWidget(self.boxUseSrcDir)

        layout.addStretch(1)
        self.fileSelectionGroup.setLayout(layout)

    def createDateSelection(self):
        '''Generate the area containing the date selectors'''

        self.dateSelectionGroupBox = QGroupBox(self.localization.date_selection)

        layout = QGridLayout()

        self.startDateEdit = QDateEdit(calendarPopup=True)
        self.startDateEdit.setDisplayFormat("dd.MM.yyyy")
        self.startDateEdit.setReadOnly(True)
        self.startDateEdit.lineEdit().setDisabled(True)

        self.endDateEdit = QDateEdit(calendarPopup=True)
        self.endDateEdit.setDisplayFormat("dd.MM.yyyy")
        self.endDateEdit.setReadOnly(True)
        self.endDateEdit.lineEdit().setDisabled(True)

        self.startTimeEdit = QLineEdit("00:00")
        self.endTimeEdit   = QLineEdit("23:59")
        self.startTimeEdit.setDisabled(True)
        self.endTimeEdit.setDisabled(True)

        layout.addWidget(self.startDateEdit, 0, 0)
        layout.addWidget(self.startTimeEdit, 0, 1)

        layout.addWidget(self.endDateEdit, 1, 0)
        layout.addWidget(self.endTimeEdit, 1, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.dateSelectionGroupBox.setLayout(layout)

    def createCheckboxArea(self):
        '''Generate area  with configuration options'''

        self.checkboxGroup = QGroupBox(self.localization.options)

        self.boxOTemp     = QCheckBox(self.localization.button_otemp)
        self.boxOHumidity = QCheckBox(self.localization.button_ohumidity)

        layout = QVBoxLayout()
        layout.addWidget(self.boxOTemp)
        layout.addWidget(self.boxOHumidity)
        layout.addStretch(1)
        self.checkboxGroup.setLayout(layout)

    def run(self):
        '''Run generation with selected file and options'''

        # set save target if nessesary #
        self.buttonGo.setText(self.localization.button_go_wait)
        self.buttonGo.setDisabled(True)
        self.repaint()

        if self.boxUseSrcDir.isChecked():
            target = self.srcFileString
            forcePath = False
        else:
            target = self.targetFileString
            forcePath = True

        # workaround for checkboxes changed #
        self.datapoints = input_backend.read_in_file(self.srcFileString, 
                                                outsideData=True,
                                                plotOutsideTemp=self.boxOTemp.isChecked(),
                                                plotOutsideHum=self.boxOHumidity.isChecked())

        # build dates #
        try:
            startTimeHelper = dt.datetime.strptime(self.startTimeEdit.text(),"%H:%M")
            endTimeHelper   = dt.datetime.strptime(self.endTimeEdit.text(),"%H:%M")
        except ValueError as e:
            errorBox = QMessageBox(self)
            errorBox.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
            errorBox.setText(self.localization.bad_time)
            errorBox.setDetailedText(str(e))
            errorBox.show()
            self.buttonGo.setText(self.localization.button_go)
            self.buttonGo.setDisabled(False)
            return
            
        startTimeOffset = dt.timedelta(hours=startTimeHelper.hour, minutes=startTimeHelper.minute)
        endTimeOffset   = dt.timedelta(hours=endTimeHelper.hour, minutes=endTimeHelper.minute)

        zeroTime = dt.time(0, 0)
        startDateTime = dt.datetime.combine(self.startDateEdit.date().toPyDate(), zeroTime)
        startDateTime += startTimeOffset
        endDateTime   = dt.datetime.combine(self.endDateEdit.date().toPyDate(), zeroTime)
        endDateTime += endTimeOffset

        self.truePath = plot_main.plot(self.datapoints, path=target,
                            date1=startDateTime,
                            date2=endDateTime,
                            forcePath=forcePath)

        self.buttonGo.setText(self.localization.button_go)
        self.buttonGo.setDisabled(False)

        doneDialog = QMessageBox(self)
        doneDialog.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
        doneDialog.setText(self.localization.done_text)
        doneDialog.addButton(self.localization.open_pic, QMessageBox.YesRole)
        doneDialog.addButton(self.localization.close, QMessageBox.NoRole)
        doneDialog.buttonClicked.connect(self.openFile)
        doneDialog.show()

    def selectSrcFile(self):
        '''Function to select a src-file'''

        self.srcFileString = QFileDialog.getOpenFileName(self, self.localization.src_file_dialog, 
                        "", "Data-Files (*.txt *.csv *.dbf)")[0]
        self.srcFileName.setText(self.srcFileString)

        if not self.srcFileString:
            return

        waitDialog = QMessageBox(self)
        waitDialog.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
        waitDialog.setText(self.localization.wait_dialog_text)
        waitDialog.show()
        try:
            self.datapoints = input_backend.read_in_file(self.srcFileString, 
                                                    outsideData=False,
                                                    plotOutsideTemp=False,
                                                    plotOutsideHum=False)
        except Exception as e:
            waitDialog.close()
            errorBox = QMessageBox(self)
            errorBox.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
            errorBox.setText(self.localization.error_read_in)
            errorBox.setDetailedText(str(e))
            errorBox.show()
            return

        waitDialog.close()

        start = self.datapoints[cp.CFG("plot_temperatur_key")].getFirstTime()
        self.startDateEdit.setDateTime(start)

        end = self.datapoints[cp.CFG("plot_temperatur_key")].getLastTime()
        self.endDateEdit.setDateTime(end)

        self.buttonGo.setDisabled(False)
        self.endDateEdit.setReadOnly(False)
        self.startDateEdit.setReadOnly(False)
        self.startDateEdit.lineEdit().setDisabled(False)
        self.endDateEdit.lineEdit().setDisabled(False)
        self.startTimeEdit.setDisabled(False)
        self.endTimeEdit.setDisabled(False)

    def selectTargetFile(self):
        '''Function to select a target-file'''
        self.targetFileString = QFileDialog.getSaveFileName(self, 
                                                self.localization.save_file_dialog)[0]
        if not self.targetFileString:
            return

        self.buttonTargetFile.setText(self.targetFileString)
        self.buttonGo.setDisabled(False)

    def useSrcDir(self):
        '''Function to handle use src dir checkbox'''
        if self.boxUseSrcDir.isChecked():
            self.buttonTargetFile.setDisabled(True)
            if self.srcFileString:
                self.buttonGo.setDisabled(False)
                self.srcFileName.setText(self.srcFileString)
        else:
            self.buttonTargetFile.setDisabled(False)
            if self.targetFileString:
                self.buttonTargetFile.setText(self.targetFileString)
            else:
                self.buttonGo.setDisabled(True)

    def openFile(self, button):
        if button.text() == self.localization.open_pic and self.truePath:
            print("JES")
            PyQt5.QtGui.QDesktopServices.openUrl(QUrl.fromLocalFile(self.truePath));
        else:
            pass

if __name__ == '__main__':
    appctxt = ApplicationContext()
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(appctxt.app.exec_())