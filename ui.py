# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui

import webbrowser
import FloatGetter
from totp import generateAuthCode
import time
from collections import OrderedDict
from decimal import Decimal
import sys
from errno import WSAEHOSTUNREACH
from socket import error as socket_error
import itemIndex

sys.setrecursionlimit(5000)


class Ui_MainWindow(QtCore.QObject):
    processItems = QtCore.Signal(object)
    getMarketData = QtCore.Signal(object)
    _login = QtCore.Signal(bool)
    _worker_login = QtCore.Signal(tuple)
    _disconnect_user = QtCore.Signal(bool)
    init_login = QtCore.Signal(bool)
    _process_single = QtCore.Signal(bool)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.WorkerThread = WorkerThread(self)
        self.t = QtCore.QThread(self, objectName='workerThread')
        self.WorkerThread.moveToThread(self.t)
        self.t.start()
        self.PassedHere = False
        self.currency = None
        self.soldcount = 0
        self.start = 0

        self.WorkerThread.progresscount = 0
        self.WorkerThread.SetStatus.connect(lambda x: self.StatusLabel.setText(x))
        self.WorkerThread.progressSignal.connect(lambda x: self.progressBar_2.setProperty("value", x))
        self.WorkerThread.StartEn.connect(lambda x: self.StartButton.setEnabled(x))
        self.WorkerThread.StartDis.connect(lambda x: self.StartButton.setDisabled(x))
        self.WorkerThread.PauseEn.connect(lambda x: self.PauseButton.setEnabled(x))
        self.WorkerThread.PauseDis.connect(lambda x: self.PauseButton.setDisabled(x))
        self.WorkerThread.RetrieveEn.connect(lambda x: self.RetrieveButton.setEnabled(x))
        self.WorkerThread.RetrieveDis.connect(lambda x: self.RetrieveButton.setDisabled(x))
        self.WorkerThread.TableSorting.connect(lambda x: self.tableWidget.setSortingEnabled(x))
        self.WorkerThread.NewRow.connect(lambda x: self.tableWidget.insertRow(x))
        self.WorkerThread.SetTableItem.connect(self.SetTable)

        self.WorkerThread.ShowError.connect(self.showError)
        self.WorkerThread.ShowInfo.connect(self.showInfo)
        self.WorkerThread.SetCurrHeader.connect(self.setCurrHeader)

        self.WorkerThread.display_error.connect(lambda x: self.display_error(x))
        self.WorkerThread.MainLogin.connect(self.login)

        self.init_login.emit(True)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(70, 0))
        self.label_2.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.DelaySpinner = QtGui.QDoubleSpinBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DelaySpinner.sizePolicy().hasHeightForWidth())
        self.DelaySpinner.setSizePolicy(sizePolicy)
        self.DelaySpinner.setMaximum(20.0)
        self.DelaySpinner.setSingleStep(0.05)
        self.DelaySpinner.setProperty("value", 0.7)
        self.DelaySpinner.setObjectName("DelaySpinner")
        self.horizontalLayout.addWidget(self.DelaySpinner)
        spacerItem = QtGui.QSpacerItem(5, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.PauseButton = QtGui.QPushButton(self.centralwidget)
        self.PauseButton.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PauseButton.sizePolicy().hasHeightForWidth())
        self.PauseButton.setSizePolicy(sizePolicy)
        self.PauseButton.setMinimumSize(QtCore.QSize(150, 0))
        self.PauseButton.setMaximumSize(QtCore.QSize(150, 16777215))
        self.PauseButton.setObjectName("PauseButton")
        self.horizontalLayout.addWidget(self.PauseButton)
        self.StartButton = QtGui.QPushButton(self.centralwidget)
        self.StartButton.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StartButton.sizePolicy().hasHeightForWidth())
        self.StartButton.setSizePolicy(sizePolicy)
        self.StartButton.setMinimumSize(QtCore.QSize(150, 0))
        self.StartButton.setMaximumSize(QtCore.QSize(150, 16777215))
        self.StartButton.setObjectName("StartButton")
        self.horizontalLayout.addWidget(self.StartButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.ClearButton = QtGui.QPushButton(self.centralwidget)
        self.ClearButton.setObjectName("ClearButton")
        self.horizontalLayout.addWidget(self.ClearButton)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(70, 0))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.URLBox = QtGui.QLineEdit(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.URLBox.sizePolicy().hasHeightForWidth())
        self.URLBox.setSizePolicy(sizePolicy)
        self.URLBox.setMinimumSize(QtCore.QSize(400, 0))
        self.URLBox.setMaximumSize(QtCore.QSize(600, 16777215))
        self.URLBox.setObjectName("URLBox")
        self.horizontalLayout_2.addWidget(self.URLBox)
        self.CountSpinner = QtGui.QSpinBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CountSpinner.sizePolicy().hasHeightForWidth())
        self.CountSpinner.setSizePolicy(sizePolicy)
        self.CountSpinner.setMinimumSize(QtCore.QSize(50, 0))
        self.CountSpinner.setMaximumSize(QtCore.QSize(100, 20))
        self.CountSpinner.setMinimum(1)
        self.CountSpinner.setMaximum(3000)
        self.CountSpinner.setProperty("value", 20)
        self.CountSpinner.setObjectName("CountSpinner")
        self.horizontalLayout_2.addWidget(self.CountSpinner)
        self.CurrencySelector = QtGui.QComboBox(self.centralwidget)
        self.CurrencySelector.setObjectName("CurrencySelector")
        self.CurrencySelector.addItem("")
        self.CurrencySelector.addItem("")
        self.CurrencySelector.addItem("")
        self.CurrencySelector.addItem("")
        self.CurrencySelector.addItem("")
        self.CurrencySelector.addItem("")
        self.horizontalLayout_2.addWidget(self.CurrencySelector)
        self.RetrieveButton = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RetrieveButton.sizePolicy().hasHeightForWidth())
        self.RetrieveButton.setSizePolicy(sizePolicy)
        self.RetrieveButton.setMinimumSize(QtCore.QSize(85, 0))
        self.RetrieveButton.setMaximumSize(QtCore.QSize(85, 16777215))
        self.RetrieveButton.setToolTip("")
        self.RetrieveButton.setObjectName("RetrieveButton")
        self.horizontalLayout_2.addWidget(self.RetrieveButton)
        spacerItem2 = QtGui.QSpacerItem(5, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem3, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.progressBar_2 = QtGui.QProgressBar(self.centralwidget)
        self.progressBar_2.setEnabled(True)
        self.progressBar_2.setMaximumSize(QtCore.QSize(16777215, 15))
        self.progressBar_2.setProperty("value", 0)
        self.progressBar_2.setTextVisible(False)
        self.progressBar_2.setInvertedAppearance(False)
        self.progressBar_2.setObjectName("progressBar_2")
        self.verticalLayout.addWidget(self.progressBar_2)
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setEnabled(True)
        self.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setIconSize(QtCore.QSize(0, 0))
        self.tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setCornerButtonEnabled(True)
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setObjectName("tableWidget")        
        self.tableWidget.verticalHeader().hide()
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(155)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(50)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tableWidget)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.StatusLabel = QtGui.QLabel(self.centralwidget)
        self.StatusLabel.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.StatusLabel)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 867, 21))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOption1 = QtGui.QAction(MainWindow)
        self.actionOption1.setObjectName("actionOption1")
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionExport_results_as_csv = QtGui.QAction(MainWindow)
        self.actionExport_results_as_csv.setObjectName("actionExport_results_as_csv")
        self.actionParseSingle = QtGui.QAction(MainWindow)
        self.actionParseSingle.setObjectName("actionParseSingle")
        self.changesettings = QtGui.QAction(MainWindow)
        self.changesettings.setObjectName("Settings")
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.menuHelp.addAction(self.actionAbout)
        self.menuFile.addAction(self.actionExport_results_as_csv)
        self.menuFile.addAction(self.actionParseSingle)
        self.menuFile.addAction(self.changesettings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        try:
            with open('settings.txt', 'r') as settings:
                for line in settings.readlines():
                    if line.startswith('defaultcurrency='):
                        self.CurrencySelector.setCurrentIndex(int(line.replace('defaultcurrency=', '')))
                    if line.startswith('defaultmarketcount='):
                        self.CountSpinner.setValue(int(line.replace('defaultmarketcount=', '')))
                    if line.startswith('defaultdelay='):
                        self.DelaySpinner.setValue(eval(line.replace('defaultdelay=', '')))
        except IOError:
            QtGui.QMessageBox.warning(MainWindow, 'Error', 'Could not read settings.txt file! Ensure file exists and try again.', QtGui.QMessageBox.Close)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL("activated()"), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        QtCore.QObject.connect(self.actionAbout, QtCore.SIGNAL("activated()"), self.ReadMe)
        QtCore.QObject.connect(self.changesettings, QtCore.SIGNAL("activated()"), self.ChangeSettings)
        QtCore.QObject.connect(self.actionExport_results_as_csv, QtCore.SIGNAL("activated()"), self.ExportCSV)
        QtCore.QObject.connect(self.actionParseSingle, QtCore.SIGNAL("activated()"), self.ParseSingle)
        QtCore.QObject.connect(self.RetrieveButton, QtCore.SIGNAL("clicked()"), self.RetrieveItems)
        QtCore.QObject.connect(self.StartButton, QtCore.SIGNAL("clicked()"), self.ProcessItems)
        QtCore.QObject.connect(self.PauseButton, QtCore.SIGNAL("clicked()"), self.Pause)
        QtCore.QObject.connect(self.ClearButton, QtCore.SIGNAL("clicked()"), self.ClearTable)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "CS:GO Market Float Finder", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "  Set a time delay (seconds) between getting each skin\'s float value. See README.txt for more info.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Time Delay:", None, QtGui.QApplication.UnicodeUTF8))
        self.DelaySpinner.setToolTip(QtGui.QApplication.translate("MainWindow", "Delay between loading float value (seconds)", None, QtGui.QApplication.UnicodeUTF8))
        self.PauseButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Pause processing skin floats", None, QtGui.QApplication.UnicodeUTF8))
        self.PauseButton.setText(QtGui.QApplication.translate("MainWindow", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.StartButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Start processing skin floats", None, QtGui.QApplication.UnicodeUTF8))
        self.StartButton.setText(QtGui.QApplication.translate("MainWindow", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.ClearButton.setText(QtGui.QApplication.translate("MainWindow", "Clear Table", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Market URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.URLBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Steam Market URL", None, QtGui.QApplication.UnicodeUTF8))
        self.CountSpinner.setToolTip(QtGui.QApplication.translate("MainWindow", "Number of skins to retrieve (1 - 100)", None, QtGui.QApplication.UnicodeUTF8))
        self.CurrencySelector.setToolTip(QtGui.QApplication.translate("MainWindow", "Desired currency of skins", None, QtGui.QApplication.UnicodeUTF8))
        self.CurrencySelector.setItemText(0, QtGui.QApplication.translate("MainWindow", "USD", None, QtGui.QApplication.UnicodeUTF8))
        self.CurrencySelector.setItemText(1, QtGui.QApplication.translate("MainWindow", "GBP", None, QtGui.QApplication.UnicodeUTF8))
        self.CurrencySelector.setItemText(2, QtGui.QApplication.translate("MainWindow", "EUR", None, QtGui.QApplication.UnicodeUTF8))
        self.CurrencySelector.setItemText(3, QtGui.QApplication.translate("MainWindow", "RUB", None, QtGui.QApplication.UnicodeUTF8))
        self.CurrencySelector.setItemText(4, QtGui.QApplication.translate("MainWindow", "CAD", None, QtGui.QApplication.UnicodeUTF8))
        self.CurrencySelector.setItemText(5, QtGui.QApplication.translate("MainWindow", "BRL", None, QtGui.QApplication.UnicodeUTF8))
        self.RetrieveButton.setText(QtGui.QApplication.translate("MainWindow", "Retrieve Items", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "  Paste Steam Market item URL, then choose number of results to grab. Finally, choose a currency.", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MainWindow", "Position", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MainWindow", "Float Value", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("MainWindow", "Price", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("MainWindow", "Listing ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("MainWindow", "Skin Type/Index", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("MainWindow", "Skin Seed", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("MainWindow", "Javascript Market Link", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(7).setText(QtGui.QApplication.translate("MainWindow", "Inspect Link", None, QtGui.QApplication.UnicodeUTF8))
        self.StatusLabel.setText(QtGui.QApplication.translate("MainWindow", "", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOption1.setText(QtGui.QApplication.translate("MainWindow", "Option1", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "Readme", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExport_results_as_csv.setText(QtGui.QApplication.translate("MainWindow", "Export results as .csv", None, QtGui.QApplication.UnicodeUTF8))
        self.actionParseSingle.setText(QtGui.QApplication.translate("MainWindow", "Parse Single Item", None, QtGui.QApplication.UnicodeUTF8))
        self.changesettings.setText(QtGui.QApplication.translate("MainWindow", "Settings...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))

    def ReadMe(self):
        webbrowser.open('README.txt')

    def ChangeSettings(self):
        webbrowser.open('settings.txt')

    def ParseSingle(self):
        self.popup = PopupDialog(self)
        self.popup.setupUi(self.popup)
        self.popup._get_single.connect(self.process_single)
        self.popup.exec_()

    def process_single(self):
        self._process_single.emit(True)

    def ExportCSV(self):
        outname, _ = QtGui.QFileDialog.getSaveFileName(MainWindow, 'Open file', '', 'Comma Separated Values (*.csv)')
        with open(outname, 'w') as outfile:
            outfile.write('Position,Float Value,Price (%s),MarketID,Skin Type/Index,Skin Seed,Javascript Market Link\n' % self.currency)
            for row in xrange(0, self.tableWidget.rowCount()):
                col0 = self.tableWidget.item(row, 0)
                col1 = self.tableWidget.item(row, 1)
                col2 = self.tableWidget.item(row, 2)
                col3 = self.tableWidget.item(row, 3)
                col4 = self.tableWidget.item(row, 4)
                col5 = self.tableWidget.item(row, 5)
                col6 = self.tableWidget.item(row, 6)
                col7 = self.tableWidget.item(row, 7)
                outfile.write('%s,%s,%s,%s,%s,%s,"%s",%s\n' % (col0.text(), col1.text(), col2.text(), col3.text(), col4.text(), col5.text(), col6.text(), col7.text()))

    def ClearTable(self):
        caution = QtGui.QMessageBox.warning(MainWindow, 'Are you sure?', 'Clearing the table will remove all table data and cancel the skin processing. \nAre you sure you wish to continue?', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        if caution == QtGui.QMessageBox.StandardButton.Yes:
            self.WorkerThread.pause = True
            time.sleep(2.5)
            while self.tableWidget.rowCount() > 0:
                self.tableWidget.removeRow(0)
            self.PauseButton.setDisabled(True)
            self.StartButton.setEnabled(True)
            self.StatusLabel.setText("Table Cleared. Ready to process.")
            self.WorkerThread.progresscount = 0
            self.WorkerThread.pause = False

    def RetrieveItems(self):
        url = self.URLBox.displayText()
        self.WorkerThread.marketdata = None
        self.WorkerThread.soldcount = 0
        self.WorkerThread.currency = self.CurrencySelector.currentText()
        if self.WorkerThread.currency == 'GBP':
            self.WorkerThread.currencysym = u'£'
        elif self.WorkerThread.currency == 'RUB':
            self.WorkerThread.currencysym = u'руб '
        elif self.WorkerThread.currency == 'CAD':
            self.WorkerThread.currencysym = u'$'
        elif self.WorkerThread.currency == 'EUR':
            self.WorkerThread.currencysym = u'€'
        elif self.WorkerThread.currency == 'BRL':
            self.WorkerThread.currencysym = u'R$'
        else:
            self.WorkerThread.currencysym = u'$'

        self.WorkerThread.count = self.CountSpinner.value()
        self.WorkerThread.delay = self.DelaySpinner.value()

        if url == '':
            QtGui.QMessageBox.warning(MainWindow, 'Error', "Please enter a market URL", QtGui.QMessageBox.Close)
        else:
            self.getMarketData.emit(url)

    def SetTable(self, data):
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, data[0], QCustomTableWidgetItem(data[1]))

    def ProcessItems(self):
        self.WorkerThread.delay = self.DelaySpinner.value()
        self.StartButton.setDisabled(True)
        self.PauseButton.setEnabled(True)
        self.RetrieveButton.setDisabled(True)

        self.StatusLabel.setText("Processing skins...")
        self.processItems.emit(object)

    def Pause(self):
        self.StatusLabel.setText("Pausing...")
        self.WorkerThread.pause = True

    def showError(self, message):
        QtGui.QMessageBox.warning(MainWindow, 'Warning!', message, QtGui.QMessageBox.Close)

    def showInfo(self, NameMessage):
        QtGui.QMessageBox.information(MainWindow, NameMessage[0], NameMessage[1], QtGui.QMessageBox.Close)

    def setCurrHeader(self, header):
        self.tableWidget.horizontalHeaderItem(2).setText('Price (%s)' % header)

    def login(self):
        loginPopup = LoginUI(self)

        loginPopup._login.connect(self.worker_login)
        loginPopup._disconnect_user.connect(self.disconnect_user)

        loginPopup.setupUi(loginPopup)
        loginPopup.exec_()

    def worker_login(self):
        self._worker_login.emit(True)

    def disconnect_user(self):
        self._disconnect_user.emit(True)

    def display_error(self, msg):
        QtGui.QMessageBox.warning(QtGui.QWidget(), 'Error', msg, QtGui.QMessageBox.Close)


class WorkerThread(QtCore.QObject):
    taskDone = QtCore.Signal(str)
    progressSignal = QtCore.Signal(int)
    StartEn = QtCore.Signal(bool)
    PauseEn = QtCore.Signal(bool)
    RetrieveEn = QtCore.Signal(bool)
    StartDis = QtCore.Signal(bool)
    PauseDis = QtCore.Signal(bool)
    RetrieveDis = QtCore.Signal(bool)
    NewRow = QtCore.Signal(int)
    SetTableItem = QtCore.Signal(list)
    TableSorting = QtCore.Signal(bool)
    SetStatus = QtCore.Signal(str)

    ShowError = QtCore.Signal(str)
    ShowInfo = QtCore.Signal(tuple)
    SetCurrHeader = QtCore.Signal(str)

    display_error = QtCore.Signal(str)
    MainLogin = QtCore.Signal(bool)

    single_post_float = QtCore.Signal(str)
    single_post_type = QtCore.Signal(str)
    single_post_seed = QtCore.Signal(str)

    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.parent = parent
        self.parent.processItems.connect(self.ProcessItems)
        self.parent.getMarketData.connect(self.GetMarketData)
        self.parent._process_single.connect(self.process_single)

        self.parent._worker_login.connect(self.login)
        self.parent._disconnect_user.connect(self.disconnect_user)
        self.parent.init_login.connect(self.init_login)

        self.progresscount = None
        self.marketdata = None
        self.singlelink = None
        self.delay = None
        self.pause = False

        self.soldcount = 0
        self.currency = None
        self.currencysym = None
        self.count = 0

        self.UserObject = None
        self.username = None
        self.password = None
        self.sharedsecret = None
        self.auth_code = None
        self.auth_type = None

        self.loggedin = False
        self.loginstatus = None

    def init_login(self):
        self.MainLogin.emit(True)

    def login(self):
        if self.UserObject:
            self.UserObject.disconnect()

        self.UserObject = FloatGetter.User()

        if self.auth_type == '2fa':
            self.loginstatus = self.UserObject.login(self.username, self.password, two_factor_code=self.auth_code)
        elif self.auth_type == 'email':
            self.loginstatus = self.UserObject.login(self.username, self.password, authcode=self.auth_code)
        else:
            self.loginstatus = self.UserObject.login(self.username, self.password)

        if self.UserObject.client.connection.connected:
            self.UserObject.csgo.launch()

    def disconnect_user(self):
        self.UserObject.disconnect()

    def ProcessItems(self):
        if not self.username and not self.password:
            self.display_error.emit('You must sign in first. Please restart the program.')
            return

        if not self.UserObject.client.connection.connected:
            self.display_error.emit('You are not connected to Steam. Please restart the program.')
            return

        for n in range(self.progresscount, len(self.marketdata)):
            time.sleep(self.delay)
            if not self.pause:
                self.SetStatus.emit('Processing...  %s/%s' % (self.progresscount+1, len(self.marketdata)))
                skininfo = self.marketdata.items()[n]
                inspectlink = skininfo[1][1]
                itemcode = inspectlink.replace('steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20' ,'').split('A')
                # If Market item or Inventory item
                if itemcode[0].startswith('S'):
                    param_s = int(itemcode[0].replace('S',''))
                    param_m = None
                else:
                    param_m = int(itemcode[0].replace('M',''))
                    param_s = None

                itemAD = itemcode[1].split('D')
                param_a = int(itemAD[0])
                param_d = int(itemAD[1])

                pos = n+1
                try:
                    if param_s:
                        data = self.UserObject.csgo.requestEconData(param_a, param_d, param_s=param_s)
                    elif param_m:
                        data = self.UserObject.csgo.requestEconData(param_a, param_d, param_m=param_m)

                    if type(data) == str:
                        self.pause = True
                        self.display_error.emit(data)
                        continue

                    paintseed = data.iteminfo.paintseed
                    paintindex = data.iteminfo.paintindex
                    paintwear = data.iteminfo.paintwear

                    skinFloat = FloatGetter.getfloat(paintwear)
                    floatvalue = Decimal(skinFloat).quantize(Decimal('1.000000000000'))

                    try:
                        skinid = 'ID' + str(paintindex)
                        paintindex = itemIndex.index[skinid]
                    except KeyError:
                        pass

                except TypeError:
                    self.PauseDis.emit(True)
                    self.StartEn.emit(True)
                    self.RetrieveEn.emit(True)
                    return

                price = Decimal(skininfo[1][2])
                listingid = skininfo[1][0]
                assetid = skininfo[0]

                javascript = "javascript:BuyMarketListing('listing', '%s', 730, '2', '%s')" % (listingid, assetid)

                self.TableSorting.emit(False)
                self.NewRow.emit(n)
                self.SetTableItem.emit([0, pos])
                self.SetTableItem.emit([1, floatvalue])
                self.SetTableItem.emit([2, price])
                self.SetTableItem.emit([3, listingid])
                self.SetTableItem.emit([4, paintindex])
                self.SetTableItem.emit([5, paintseed])
                self.SetTableItem.emit([6, javascript])
                self.SetTableItem.emit([7, inspectlink])

                self.TableSorting.emit(True)

                self.progresscount += 1
                self.progressSignal.emit(int(float(self.progresscount/float(len(self.marketdata)))*100))
            else:
                self.pause = False
                self.StartEn.emit(True)
                self.PauseDis.emit(True)
                self.RetrieveEn.emit(True)
                self.progressSignal.emit(0)
                self.SetStatus.emit('Processing paused, press "Start" to continue. If you want to process a different set of data, clear the table first.')
                return

        self.SetStatus.emit('Processing Finished. Clear table before starting a new process.')
        self.StartEn.emit(True)
        self.PauseDis.emit(True)
        self.RetrieveEn.emit(True)

    @QtCore.Slot(str)
    def GetMarketData(self, url):
        initialcount = self.count
        start = 0
        iteration = 1
        self.SetStatus.emit('Gathering Data...')
        while self.count > 100:
            self.count -= 100
            tempdata, tempsold = FloatGetter.getMarketItems(url, 100, self.currency, start)
            if type(tempdata) != str:
                if self.marketdata:
                    newtempdict = OrderedDict()
                    for k,e in self.marketdata.items()+tempdata.items():
                        if k in tempdata.keys() and k in self.marketdata.keys():
                            pass
                        else:
                            newtempdict.setdefault(k,e)
                        self.marketdata = newtempdict
                else:
                    self.marketdata = tempdata
                self.soldcount += int(tempsold)
                iteration += 1
                start += 100
                if initialcount > 2000:
                    time.sleep(1)

        else:
            tempdata, tempsold = FloatGetter.getMarketItems(url, self.count, self.currency, start)
            if type(tempdata) != str:
                if self.marketdata:
                    newtempdict = OrderedDict()
                    for k,e in self.marketdata.items()+tempdata.items():
                        if k in tempdata.keys() and k in self.marketdata.keys():
                            pass
                        else:
                            newtempdict.setdefault(k,e)
                        self.marketdata = newtempdict
                else:
                    self.marketdata = tempdata
                self.soldcount += int(tempsold)

            if type(self.marketdata) != OrderedDict:
                self.ShowError.emit(tempdata)
                return
            else:
                if len(self.marketdata) + self.soldcount < initialcount:
                    message = "Found %s available skins and %s sold skins. \nThe other %s skins did not exist, you may retry or just process current data (%s skins)." % (len(self.marketdata), self.soldcount, initialcount-(len(self.marketdata)+self.soldcount), len(self.marketdata))
                    self.ShowInfo.emit(('Information', message))
                    self.StartEn.emit(True)
                    self.SetStatus.emit("%s skins retrieved. Read to start processing. Estimated processing time, with %s delay, is %s seconds." % (len(self.marketdata), self.delay, self.delay*len(self.marketdata)))
                    self.SetCurrHeader.emit(self.currencysym)

                elif len(self.marketdata) < 1:
                    message = "Found %s available skins and %s sold skins. \nNo skins to process, please check market has available items." % (len(self.marketdata), self.soldcount)
                    self.ShowError.emit(message)
                    self.SetStatus.emit('Ready')
                else:
                    message = "Successfully found %s available skins and %s sold skins. Any sold skins will not be processed. \nClose this message and press 'Start'." % (len(self.marketdata), self.soldcount)
                    self.ShowInfo.emit(('Success!', message))
                    self.StartEn.emit(True)
                    self.SetCurrHeader.emit(self.currencysym)
                    self.SetStatus.emit("%s skins retrieved. Read to start processing. Estimated processing time, with %s delay, is %s seconds." % (len(self.marketdata), self.delay, self.delay*len(self.marketdata)))

    def process_single(self):
        if str(self.singlelink).startswith('steam://rungame/730/'):
            if not self.username and not self.password:
                self.display_error.emit('You must sign in first. Please restart the program.')
                return

            if not self.UserObject.client.connection.connected:
                self.display_error.emit('You are not connected to Steam. Please restart the program.')
                return

            itemcode = self.singlelink.replace('steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20' ,'').split('A')
            # If Market item or Inventory item
            if itemcode[0].startswith('S'):
                param_s = int(itemcode[0].replace('S',''))
                param_m = None
            else:
                param_m = int(itemcode[0].replace('M',''))
                param_s = None

            itemAD = itemcode[1].split('D')
            param_a = int(itemAD[0])
            param_d = int(itemAD[1])

            try:
                if param_s:
                    data = self.UserObject.csgo.requestEconData(param_a, param_d, param_s=param_s)
                elif param_m:
                    data = self.UserObject.csgo.requestEconData(param_a, param_d, param_m=param_m)

                paintseed = data.iteminfo.paintseed
                paintindex = data.iteminfo.paintindex
                paintwear = data.iteminfo.paintwear

                skinFloat = FloatGetter.getfloat(paintwear)
                floatvalue = Decimal(skinFloat).quantize(Decimal('1.000000000000'))

                try:
                    skinid = 'ID' + str(paintindex)
                    paintindex = itemIndex.index[skinid]
                except KeyError:
                    pass

                self.single_post_float.emit(str(floatvalue))
                self.single_post_type.emit(str(floatvalue))
                self.single_post_seed.emit(str(paintseed))

            except TypeError:
                return

        else:
            QtGui.QMessageBox.warning(self, 'Error', 'Please enter a inspect in game link.', QtGui.QMessageBox.Close)


class QCustomTableWidgetItem(QtGui.QTableWidgetItem):
    def __init__(self, value):
        super(QCustomTableWidgetItem, self).__init__(str('%s' % value))

    def __lt__(self, other):
        if isinstance(other, QCustomTableWidgetItem):
            try:
                selfDataValue = float(self.data(QtCore.Qt.EditRole))
                otherDataValue = float(other.data(QtCore.Qt.EditRole))
                return selfDataValue < otherDataValue
            except ValueError:
                # Can not be converted to float, so probably does not need to be (str, unicode)
                selfDataValue = self.data(QtCore.Qt.EditRole)
                otherDataValue = other.data(QtCore.Qt.EditRole)
                return selfDataValue < otherDataValue
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)


class PopupDialog(QtGui.QDialog):
    _get_single = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(PopupDialog, self).__init__()
        self.callback = parent
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint)
        self.callback.WorkerThread.single_post_float.connect(lambda x: self.post_float(x))
        self.callback.WorkerThread.single_post_type.connect(lambda x: self.post_type(x))
        self.callback.WorkerThread.single_post_seed.connect(lambda x: self.post_seed(x))

    def setupUi(self, Form):
        Form.setObjectName("Parse Single Item")
        Form.resize(600, 71)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMaximumSize(QtCore.QSize(800, 71))
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.InspectLinkBox = QtGui.QLineEdit(Form)
        self.InspectLinkBox.setObjectName("InspectLinkBox")
        self.horizontalLayout.addWidget(self.InspectLinkBox)
        self.GetValue = QtGui.QPushButton(Form)
        self.GetValue.setObjectName("GetValue")
        self.horizontalLayout.addWidget(self.GetValue)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.ResultBox = QtGui.QLineEdit(Form)
        self.ResultBox.setText("")
        self.ResultBox.setAlignment(QtCore.Qt.AlignCenter)
        self.ResultBox.setReadOnly(True)
        self.ResultBox.setObjectName("ResultBox")
        self.horizontalLayout_2.addWidget(self.ResultBox)
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.SkinTypeBox = QtGui.QLineEdit(Form)
        self.SkinTypeBox.setText("")
        self.SkinTypeBox.setAlignment(QtCore.Qt.AlignCenter)
        self.SkinTypeBox.setReadOnly(True)
        self.SkinTypeBox.setObjectName("SkinTypeBox")
        self.horizontalLayout_2.addWidget(self.SkinTypeBox)
        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.SkinSeedBox = QtGui.QLineEdit(Form)
        self.SkinSeedBox.setText("")
        self.SkinSeedBox.setAlignment(QtCore.Qt.AlignCenter)
        self.SkinSeedBox.setReadOnly(True)
        self.SkinSeedBox.setObjectName("SkinSeedBox")
        self.horizontalLayout_2.addWidget(self.SkinSeedBox)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        QtCore.QObject.connect(self.GetValue, QtCore.SIGNAL("clicked()"), self.GetSingle)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Parse Single Item", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Inspect Link", None, QtGui.QApplication.UnicodeUTF8))
        self.GetValue.setText(QtGui.QApplication.translate("Form", "Get Value", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Skin Float Value:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Skin Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Skin Seed:", None, QtGui.QApplication.UnicodeUTF8))

    def GetSingle(self):
        self.callback.WorkerThread.singlelink = self.InspectLinkBox.displayText()
        self._get_single.emit(True)

    def post_float(self, float):
        self.ResultBox.setText(float)

    def post_type(self, type):
        self.SkinTypeBox.setText(type)

    def post_seed(self, seed):
        self.SkinSeedBox.setText(seed)


class LoginUI(QtGui.QDialog):
    _login = QtCore.Signal(bool)
    _disconnect_user = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(LoginUI, self).__init__()
        self.callback = parent
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint)
        self.overwritten = False
        self.sharedsecret = None

    def setupUi(self, Form):
        Form.setObjectName("Login to Steam")
        Form.resize(255, 150)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(255, 150))
        Form.setMaximumSize(QtCore.QSize(255, 150))
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.UsernameBox = QtGui.QLineEdit(Form)
        self.UsernameBox.setObjectName("UsernameBox")
        self.horizontalLayout.addWidget(self.UsernameBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setMargin(1)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.PasswordBox = QtGui.QLineEdit(Form)
        self.PasswordBox.setInputMask("")
        self.PasswordBox.setText("")
        self.PasswordBox.setFrame(True)
        self.PasswordBox.setEchoMode(QtGui.QLineEdit.Password)
        self.PasswordBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.PasswordBox.setReadOnly(False)
        self.PasswordBox.setPlaceholderText("")
        self.PasswordBox.setObjectName("PasswordBox")
        self.horizontalLayout_2.addWidget(self.PasswordBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtGui.QSpacerItem(59, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.RememberBox = QtGui.QCheckBox(Form)
        self.RememberBox.setObjectName("RememberBox")
        self.horizontalLayout_3.addWidget(self.RememberBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.LoginButton = QtGui.QPushButton(Form)
        self.LoginButton.setObjectName("LoginButton")
        self.horizontalLayout_4.addWidget(self.LoginButton)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        try:
            with open('settings.txt', 'r') as settings:
                for line in settings.readlines():
                    if line.startswith('username='):
                        self.UsernameBox.setText(line.replace('username=', '').replace('\n',''))
                        self.RememberBox.setChecked(True)
                    if line.startswith('password='):
                        self.PasswordBox.setText(line.replace('password=', ''))
                    if line.startswith('sharedsecret='):
                        self.sharedsecret = line.replace('sharedsecret=', '')
                        self.callback.sharedsecret = self.sharedsecret
        except IOError:
            QtGui.QMessageBox.warning(MainWindow, 'Error', 'Could not read settings.txt file! Ensure file exists and try again.', QtGui.QMessageBox.Close)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        QtCore.QObject.connect(self.LoginButton, QtCore.SIGNAL("clicked()"), self.login)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Login to Steam", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Sign in to Steam", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.RememberBox.setText(QtGui.QApplication.translate("Form", "Remember details", None, QtGui.QApplication.UnicodeUTF8))
        self.LoginButton.setText(QtGui.QApplication.translate("Form", "Login", None, QtGui.QApplication.UnicodeUTF8))

    def callback_login(self):
        self._login.emit(True)

    def login(self):
        username = self.UsernameBox.text().encode('ascii')
        password = self.PasswordBox.text().encode('ascii')
        remember = self.RememberBox.isChecked()

        if remember:
            try:
                with open('settings.txt', 'r') as settings:
                    data = settings.readlines()

                for num, line in enumerate(data):
                    if line.startswith('username='):
                        data[num] = line.replace(line, 'username='+username+'\n')
                    if line.startswith('password='):
                        data[num] = line.replace(line, 'password='+password)
                        self.overwritten = True

                with open('settings.txt', 'w') as settings:
                    settings.writelines(data)
                    if not self.overwritten:
                        settings.seek(0, 2)
                        settings.writelines(['\nusername='+username, '\npassword='+password])

            except IOError:
                QtGui.QMessageBox.warning(MainWindow, 'Error', 'Could not read settings.txt file! Ensure file exists and try again.', QtGui.QMessageBox.Close)

        if username and password:
            try:
                if self.sharedsecret:
                    self.callback.WorkerThread.username = username
                    self.callback.WorkerThread.password = password
                    self.callback.WorkerThread.auth_code = generateAuthCode(self.sharedsecret)
                    self.callback.WorkerThread.auth_type = '2fa'

                    self._login.emit(True)
                else:
                    self.callback.WorkerThread.username = username
                    self.callback.WorkerThread.password = password
                    self.callback.WorkerThread.auth_code = None
                    self.callback.WorkerThread.auth_type = None

                    self._login.emit(True)

                time.sleep(1.7)
                loginstatus = self.callback.WorkerThread.loginstatus

                if loginstatus != True:
                    if loginstatus == 5:
                        QtGui.QMessageBox.warning(self, 'Error', 'Incorrect password or username, or too many login attempts.', QtGui.QMessageBox.Close)
                    elif loginstatus == 63 or loginstatus == 85 or loginstatus == 88:
                        self._disconnect_user.emit(True)

                        authPopup = AuthUI(parent=self, authstatus=loginstatus)
                        authPopup.setupUi(authPopup)
                        authPopup._login.connect(self.callback_login)
                        authPopup.exec_()
                        self.close()
                else:
                    self.close()
                    QtGui.QMessageBox.information(self, 'Success!', 'Signed in to Steam.', QtGui.QMessageBox.Close)

            except socket_error as serr:
                if serr.errno == WSAEHOSTUNREACH:
                    QtGui.QMessageBox.warning(self, 'Error', 'Could not connect to Steam.', QtGui.QMessageBox.Close)
                else:
                    QtGui.QMessageBox.warning(self, 'Error', 'Socket error ' + str(serr.errno), QtGui.QMessageBox.Close)

        else:
            QtGui.QMessageBox.warning(self, 'Error', 'Please enter your username and password.', QtGui.QMessageBox.Close)


class AuthUI(QtGui.QDialog):
    _login = QtCore.Signal(bool)

    def __init__(self, parent=None, authstatus=0):
        self.callback = parent
        self.authstatus = authstatus  # 63 = auth_code, 85 = 2fa code
        super(AuthUI, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint)

    def setupUi(self, Form):
        Form.setObjectName("Authenticate")
        Form.resize(220, 105)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(220, 105))
        Form.setMaximumSize(QtCore.QSize(220, 105))
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.AuthBox = QtGui.QLineEdit(Form)
        self.AuthBox.setObjectName("AuthBox")
        self.horizontalLayout.addWidget(self.AuthBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.AuthButton = QtGui.QPushButton(Form)
        self.AuthButton.setObjectName("AuthButton")
        self.horizontalLayout_2.addWidget(self.AuthButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        QtCore.QObject.connect(self.AuthButton, QtCore.SIGNAL("clicked()"), self.auth)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Authenticate", None, QtGui.QApplication.UnicodeUTF8))
        if self.authstatus == 63:
            self.label_3.setText(QtGui.QApplication.translate("Form", "Steam has sent an authentication code to your email, please enter it below.", None, QtGui.QApplication.UnicodeUTF8))
        elif self.authstatus == 85:
            self.label_3.setText(QtGui.QApplication.translate("Form", "Please enter your Steam Guard mobile 2FA code.", None, QtGui.QApplication.UnicodeUTF8))
        elif self.authstatus == 88:
            self.label_3.setText(QtGui.QApplication.translate("Form", "2FA code incorrect, try again.", None, QtGui.QApplication.UnicodeUTF8))

        self.label.setText(QtGui.QApplication.translate("Form", "Auth Code:", None, QtGui.QApplication.UnicodeUTF8))
        self.AuthButton.setText(QtGui.QApplication.translate("Form", "OK", None, QtGui.QApplication.UnicodeUTF8))

    def auth(self):
        authcode = self.AuthBox.text().encode('ascii')

        if self.authstatus == 85 or self.authstatus == 88:
            self.callback.callback.WorkerThread.auth_code = authcode
            self.callback.callback.WorkerThread.auth_type = '2fa'

            self._login.emit(True)
        else:
            self.callback.callback.WorkerThread.auth_code = authcode
            self.callback.callback.WorkerThread.auth_type = 'email'

            self._login.emit(True)

        time.sleep(1.7)
        loginstatus = self.callback.callback.WorkerThread.loginstatus

        if loginstatus == True:
            self.close()
        elif loginstatus == 65 or loginstatus == 88:
            QtGui.QMessageBox.warning(self, 'Error', 'Incorrect auth code.', QtGui.QMessageBox.Close)
        elif loginstatus == 63:
            QtGui.QMessageBox.warning(self, 'Error', 'Please enter auth code.', QtGui.QMessageBox.Close)
        elif loginstatus == 85:
            QtGui.QMessageBox.warning(self, 'Error', 'Please enter your mobile 2FA code.', QtGui.QMessageBox.Close)
        elif loginstatus == 5:
            QtGui.QMessageBox.warning(self, 'Error', 'Auth failed: InvalidPassword. Maybe too many login attempts recently, try later.', QtGui.QMessageBox.Close)
        else:
            QtGui.QMessageBox.warning(self, 'Error', 'Auth failed with error %s.' % str(loginstatus), QtGui.QMessageBox.Close)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    QtCore.QThread.currentThread().setObjectName('main')
    MainWindow.show()
    sys.exit(app.exec_())
