# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/mediaLibrary.ui'
#
# Created: Sat Jan 24 10:10:59 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MediaLibrary(object):
    def setupUi(self, MediaLibrary):
        MediaLibrary.setObjectName(_fromUtf8("MediaLibrary"))
        MediaLibrary.resize(400, 300)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.filterLabel = QtGui.QLabel(self.dockWidgetContents)
        self.filterLabel.setObjectName(_fromUtf8("filterLabel"))
        self.horizontalLayout.addWidget(self.filterLabel)
        self.filterLineEdit = QtGui.QLineEdit(self.dockWidgetContents)
        self.filterLineEdit.setObjectName(_fromUtf8("filterLineEdit"))
        self.horizontalLayout.addWidget(self.filterLineEdit)
        self.filterPushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.filterPushButton.setObjectName(_fromUtf8("filterPushButton"))
        self.horizontalLayout.addWidget(self.filterPushButton)
        self.advFilterPushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.advFilterPushButton.setEnabled(False)
        self.advFilterPushButton.setObjectName(_fromUtf8("advFilterPushButton"))
        self.horizontalLayout.addWidget(self.advFilterPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.mediaLibraryView = MediaLibraryView(self.dockWidgetContents)
        self.mediaLibraryView.setAlternatingRowColors(True)
        self.mediaLibraryView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.mediaLibraryView.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.mediaLibraryView.setSortingEnabled(True)
        self.mediaLibraryView.setObjectName(_fromUtf8("mediaLibraryView"))
        self.verticalLayout.addWidget(self.mediaLibraryView)
        MediaLibrary.setWidget(self.dockWidgetContents)
        self.filterLabel.setBuddy(self.filterLineEdit)

        self.retranslateUi(MediaLibrary)
        QtCore.QObject.connect(self.filterLineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), MediaLibrary.setFilter)
        QtCore.QObject.connect(self.filterPushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MediaLibrary.setFilter)
        QtCore.QObject.connect(self.mediaLibraryView, QtCore.SIGNAL(_fromUtf8("customContextMenuRequested(QPoint)")), self.mediaLibraryView.popupMenu)
        QtCore.QMetaObject.connectSlotsByName(MediaLibrary)

    def retranslateUi(self, MediaLibrary):
        MediaLibrary.setWindowTitle(_translate("MediaLibrary", "Media Library", None))
        self.filterLabel.setText(_translate("MediaLibrary", "Filter:", None))
        self.filterPushButton.setText(_translate("MediaLibrary", "filter", None))
        self.advFilterPushButton.setText(_translate("MediaLibrary", "Advanced Filter...", None))

from mediaLibrary import MediaLibraryView
