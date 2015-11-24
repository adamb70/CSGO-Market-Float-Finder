# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
import webbrowser
import FloatUI
import time
from collections import OrderedDict
from decimal import Decimal
import sys

sys.setrecursionlimit(5000)

class Ui_MainWindow(QtCore.QObject):
    processItems = QtCore.Signal(object)
    getMarketData = QtCore.Signal(object)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.WorkerThread = WorkerThread(self)
        self.t = QtCore.QThread(self, objectName='workerThread')
        self.WorkerThread.moveToThread(self.t)
        self.t.start()
        self.PassedHere = False
        self.WorkerThread.SetStatus.connect(lambda x: self.StatusLabel.setText(x))
        self.currency = None
        self.soldcount = 0
        self.start = 0

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
        self. WorkerThread.FloatError.connect(self.FloatError)

        self.WorkerThread.ShowError.connect(self.showError)
        self.WorkerThread.ShowInfo.connect(self.showInfo)
        self.WorkerThread.SetCurrHeader.connect(self.setCurrHeader)

    def setupUi(self, MainWindow):
        global baseHex
        global initialoffset
        global offsets
        baseHex = None

        self.WorkerThread.progresscount = 0

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
        self.DelaySpinner.setProperty("value", 2.7)
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
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(5)
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
                    if line.startswith('initialoffset='):
                        initialoffset = eval(line.replace('initialoffset=', ''))
                    if line.startswith('offsets='):
                        offsets = eval(line.replace('offsets=', ''))
                    if line.startswith('defaultcurrency='):
                        self.CurrencySelector.setCurrentIndex(eval(line.replace('defaultcurrency=', '')))
                    if line.startswith('defaultmarketcount='):
                        self.CountSpinner.setValue(eval(line.replace('defaultmarketcount=', '')))
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
        self.tableWidget.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("MainWindow", "Javascript Market Link", None, QtGui.QApplication.UnicodeUTF8))
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
        self.popup = MyPopupDialog()
        self.popup.setupUi(self.popup)

        # For Modal dialogs
        self.popup.exec_()

    def ExportCSV(self):
        outname, _ = QtGui.QFileDialog.getSaveFileName(MainWindow, 'Open file', '', 'Comma Separated Values (*.csv)')
        with open(outname, 'w') as outfile:
            outfile.write('Position,Float Value,Price (%s),MarketID,Javascript Market Link\n' % self.currency)
            for row in xrange(0, self.tableWidget.rowCount()):
                col0 = self.tableWidget.item(row, 0)
                col1 = self.tableWidget.item(row, 1)
                col2 = self.tableWidget.item(row, 2)
                col3 = self.tableWidget.item(row, 3)
                col4 = self.tableWidget.item(row, 4)
                outfile.write('%s,%s,%s,%s,"%s"\n' % (col0.text(), col1.text(), col2.text(), col3.text(), col4.text()))

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
            self.WorkerThread.WorkerThread.currencysym = u'R$'
        else:
            self.WorkerThread.currencysym = u'$'

        self.WorkerThread.count = self.CountSpinner.value()
        self.WorkerThread.delay = self.DelaySpinner.value()

        if url == '':
            QtGui.QMessageBox.warning(MainWindow, 'Error', "Please enter a market URL.", QtGui.QMessageBox.Close)
        else:
            self.getMarketData.emit(url)

    def SetTable(self, data):
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, data[0], QCustomTableWidgetItem(data[1]))

    def ProcessItems(self):
        self.WorkerThread.PID = FloatUI.getpid('csgo.exe')
        if not self.WorkerThread.PID:
            QtGui.QMessageBox.warning(MainWindow, 'Error', 'Please start CS:GO and retry.', QtGui.QMessageBox.Ok)
            return

        global baseHex
        if not baseHex:
            baseHex = FloatUI.GetModuleByName('studiorender.dll', self.WorkerThread.PID)

        self.WorkerThread.delay = self.DelaySpinner.value()

        self.StartButton.setDisabled(True)
        self.PauseButton.setEnabled(True)
        self.RetrieveButton.setDisabled(True)

        self.StatusLabel.setText("Processing skins...")
        self.processItems.emit(object)

    def FloatError(self):
        QtGui.QMessageBox.warning(MainWindow, 'Error', 'Could not find float value, try restarting the game. If you get this message again contact me, a CS:GO update may have changed the memory address.', QtGui.QMessageBox.Ok)

    def Pause(self):
        self.StatusLabel.setText("Pausing...")
        self.WorkerThread.pause = True

    def showError(self, message):
        QtGui.QMessageBox.warning(MainWindow, 'Warning!', message, QtGui.QMessageBox.Close)

    def showInfo(self, NameMessage):
        QtGui.QMessageBox.information(MainWindow, NameMessage[0], NameMessage[1], QtGui.QMessageBox.Close)

    def setCurrHeader(self, header):
        self.tableWidget.horizontalHeaderItem(2).setText('Price (%s)' % header)


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
    FloatError = QtCore.Signal(bool)
    SetStatus = QtCore.Signal(str)

    ShowError = QtCore.Signal(str)
    ShowInfo = QtCore.Signal(tuple)
    SetCurrHeader = QtCore.Signal(str)


    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        parent.processItems.connect(self.ProcessItems)
        parent.getMarketData.connect(self.GetMarketData)

        self.progresscount = None
        self.PID = None
        self.delay = None
        self.marketdata = None
        self.pause = False

        self.soldcount = 0
        self.currency = None
        self.currencysym = None
        self.count = 0


    @QtCore.Slot(object)
    def ProcessItems(self):
        for n in range(self.progresscount, len(self.marketdata)):
            if not self.pause:
                self.SetStatus.emit('Processing...  %s/%s' % (self.progresscount+1, len(self.marketdata)))
                skininfo = self.marketdata.items()[n]
                webbrowser.open_new(skininfo[1][1])
                time.sleep(self.delay)

                pos = n+1
                try:
                    floatvalue = Decimal(FloatUI.getFloat(self.PID, baseHex, initialoffset, offsets)).quantize(Decimal('1.000000000000'))
                except TypeError:
                    self.FloatError.emit(True)
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
                self.SetTableItem.emit([4, javascript])

                self.TableSorting.emit(True)

                self.progresscount += 1
                self.progressSignal.emit(int(float(self.progresscount/float(len(self.marketdata)))*100))
            else:
                self.pause = False
                self.StartEn.emit(True)
                self.PauseDis.emit(True)
                self.RetrieveEn.emit(True)
                self.progressSignal.emit(0)
                self.SetStatus.emit('Processing paused. Press "Start" to continue.')
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
            tempdata, tempsold = FloatUI.getMarketItems(url, 100, self.currency, start)
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
            tempdata, tempsold = FloatUI.getMarketItems(url, self.count, self.currency, start)
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
                    message = "Found %s available skins and %s sold skins. \nThe other %s skins were likely duplicated in the search or did not exist, you may retry or just process current data (%s skins)." % (len(self.marketdata), self.soldcount, initialcount-(len(self.marketdata)+self.soldcount), len(self.marketdata))
                    self.ShowInfo.emit(('Information', message))
                    self.StartEn.emit(True)
                    self.SetStatus.emit("%s skins retrieved. Read to start processing. Estimated processing time, with %s delay, is %s seconds." % (len(self.marketdata), self.delay, self.delay*len(self.marketdata)))
                    self.SetCurrHeader.emit(self.currencysym)

                elif len(self.marketdata) < 1:
                    message = "Found %s available skins and %s sold skins. \nNo skins to process, please check market has available items." % (len(self.marketdata), self.soldcount)
                    self.ShowError(message)
                else:
                    message = "Successfully found %s available skins and %s sold skins. Any sold skins will not be processed. \nClose this message and press 'Start'." % (len(self.marketdata), self.soldcount)
                    self.ShowInfo.emit(('Success!', message))
                    self.StartEn.emit(True)
                    self.SetStatus.emit("%s skins retrieved. Read to start processing. Estimated processing time, with %s delay, is %s seconds" % (len(self.marketdata), self.delay, self.delay*len(self.marketdata)))
                    self.SetCurrHeader.emit(self.currencysym)


class QCustomTableWidgetItem (QtGui.QTableWidgetItem):
    def __init__(self, value):
        super(QCustomTableWidgetItem, self).__init__(str('%s' % value))

    def __lt__(self, other):
        if isinstance(other, QCustomTableWidgetItem):
            selfDataValue = float(self.data(QtCore.Qt.EditRole))
            otherDataValue = float(other.data(QtCore.Qt.EditRole))
            return selfDataValue < otherDataValue
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)



class MyPopupDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(MyPopupDialog, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint)


    def setupUi(self, Form):
        Form.setObjectName("Parse Single Item")
        Form.resize(435, 71)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMaximumSize(QtCore.QSize(431, 71))
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


    def GetSingle(self):
        link = self.InspectLinkBox.displayText()
        PID = FloatUI.getpid('csgo.exe')

        global baseHex
        if not baseHex:
            'geting bvasekgsmk'
            baseHex = FloatUI.GetModuleByName('studiorender.dll', PID)

        try:
            with open('settings.txt', 'r') as settings:
                for line in settings.readlines():
                    if line.startswith('initialoffset='):
                        initialoffset = eval(line.replace('initialoffset=', ''))
                    if line.startswith('offsets='):
                        offsets = eval(line.replace('offsets=', ''))
                    if line.startswith('defaultdelay='):
                        delay = (eval(line.replace('defaultdelay=', '')))
        except IOError:
            QtGui.QMessageBox.warning(self, 'Error', 'Could not read settings.txt file! Ensure file exists and try again.', QtGui.QMessageBox.Close)

        if str(link).startswith('steam://rungame/730/'):
            if not PID:
                QtGui.QMessageBox.warning(self, 'Error', 'Please start CS:GO and retry.', QtGui.QMessageBox.Ok)
                return

            webbrowser.open_new(link)
            time.sleep(float(delay))

            floatvalue = Decimal(FloatUI.getFloat(PID, baseHex, initialoffset, offsets)).quantize(Decimal('1.000000000000'))
            self.ResultBox.setText(str(floatvalue))

        else:
            QtGui.QMessageBox.warning(self, 'Error', 'Please enter a inspect in game link.', QtGui.QMessageBox.Close)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    QtCore.QThread.currentThread().setObjectName('main')
    MainWindow.show()
    sys.exit(app.exec_())

