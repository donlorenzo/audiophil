# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/configDlg.ui'
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

class Ui_ConfigDlg(object):
    def setupUi(self, ConfigDlg):
        ConfigDlg.setObjectName(_fromUtf8("ConfigDlg"))
        ConfigDlg.resize(628, 493)
        self.verticalLayout_3 = QtGui.QVBoxLayout(ConfigDlg)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.tabWidget = QtGui.QTabWidget(ConfigDlg)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.savePathLineEdit = QtGui.QLineEdit(self.tab)
        self.savePathLineEdit.setFrame(True)
        self.savePathLineEdit.setReadOnly(False)
        self.savePathLineEdit.setObjectName(_fromUtf8("savePathLineEdit"))
        self.horizontalLayout_3.addWidget(self.savePathLineEdit)
        self.selectSavePathPushButton = QtGui.QPushButton(self.tab)
        self.selectSavePathPushButton.setObjectName(_fromUtf8("selectSavePathPushButton"))
        self.horizontalLayout_3.addWidget(self.selectSavePathPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.directoriesListWidget = QtGui.QListWidget(self.tab)
        self.directoriesListWidget.setObjectName(_fromUtf8("directoriesListWidget"))
        self.horizontalLayout.addWidget(self.directoriesListWidget)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.addDirectoryPushButton = QtGui.QPushButton(self.tab)
        self.addDirectoryPushButton.setObjectName(_fromUtf8("addDirectoryPushButton"))
        self.verticalLayout.addWidget(self.addDirectoryPushButton)
        self.editDirectoryPushButton = QtGui.QPushButton(self.tab)
        self.editDirectoryPushButton.setEnabled(False)
        self.editDirectoryPushButton.setObjectName(_fromUtf8("editDirectoryPushButton"))
        self.verticalLayout.addWidget(self.editDirectoryPushButton)
        self.removeDirectoryPushButton = QtGui.QPushButton(self.tab)
        self.removeDirectoryPushButton.setEnabled(False)
        self.removeDirectoryPushButton.setObjectName(_fromUtf8("removeDirectoryPushButton"))
        self.verticalLayout.addWidget(self.removeDirectoryPushButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.groupBox = QtGui.QGroupBox(self.tab)
        self.groupBox.setEnabled(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setChecked(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.checkBox = QtGui.QCheckBox(self.groupBox)
        self.checkBox.setEnabled(False)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.spinBox = QtGui.QSpinBox(self.groupBox)
        self.spinBox.setEnabled(False)
        self.spinBox.setMinimum(1)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.horizontalLayout_2.addWidget(self.spinBox)
        self.pushButton_4 = QtGui.QPushButton(self.groupBox)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_2 = QtGui.QLabel(self.tab_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_4.addWidget(self.label_2)
        self.formatTemplateLineEdit = QtGui.QLineEdit(self.tab_2)
        self.formatTemplateLineEdit.setObjectName(_fromUtf8("formatTemplateLineEdit"))
        self.horizontalLayout_4.addWidget(self.formatTemplateLineEdit)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.placeholderArtistButton = QtGui.QPushButton(self.tab_2)
        self.placeholderArtistButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.placeholderArtistButton.setObjectName(_fromUtf8("placeholderArtistButton"))
        self.gridLayout.addWidget(self.placeholderArtistButton, 0, 0, 1, 1)
        self.placeholderAlbumButton = QtGui.QPushButton(self.tab_2)
        self.placeholderAlbumButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.placeholderAlbumButton.setObjectName(_fromUtf8("placeholderAlbumButton"))
        self.gridLayout.addWidget(self.placeholderAlbumButton, 0, 1, 1, 1)
        self.placeholderTitleButton = QtGui.QPushButton(self.tab_2)
        self.placeholderTitleButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.placeholderTitleButton.setObjectName(_fromUtf8("placeholderTitleButton"))
        self.gridLayout.addWidget(self.placeholderTitleButton, 0, 2, 1, 1)
        self.placeholderTracknumberButton = QtGui.QPushButton(self.tab_2)
        self.placeholderTracknumberButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.placeholderTracknumberButton.setObjectName(_fromUtf8("placeholderTracknumberButton"))
        self.gridLayout.addWidget(self.placeholderTracknumberButton, 0, 3, 1, 1)
        self.placeholderDurationButton = QtGui.QPushButton(self.tab_2)
        self.placeholderDurationButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.placeholderDurationButton.setObjectName(_fromUtf8("placeholderDurationButton"))
        self.gridLayout.addWidget(self.placeholderDurationButton, 0, 4, 1, 1)
        self.placeholderFilePathButton = QtGui.QPushButton(self.tab_2)
        self.placeholderFilePathButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.placeholderFilePathButton.setObjectName(_fromUtf8("placeholderFilePathButton"))
        self.gridLayout.addWidget(self.placeholderFilePathButton, 1, 0, 1, 1)
        self.placeholderFileNameButton = QtGui.QPushButton(self.tab_2)
        self.placeholderFileNameButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.placeholderFileNameButton.setObjectName(_fromUtf8("placeholderFileNameButton"))
        self.gridLayout.addWidget(self.placeholderFileNameButton, 1, 1, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 248, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout_3.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(ConfigDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.label.setBuddy(self.savePathLineEdit)

        self.retranslateUi(ConfigDlg)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConfigDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConfigDlg.reject)
        QtCore.QObject.connect(self.selectSavePathPushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), ConfigDlg.selectSavePath)
        QtCore.QObject.connect(self.addDirectoryPushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), ConfigDlg.selectDirectory)
        QtCore.QObject.connect(self.editDirectoryPushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), ConfigDlg.editDirectory)
        QtCore.QObject.connect(self.removeDirectoryPushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), ConfigDlg.removeDirectory)
        QtCore.QObject.connect(self.directoriesListWidget, QtCore.SIGNAL(_fromUtf8("currentItemChanged(QListWidgetItem*,QListWidgetItem*)")), ConfigDlg.updateButtonActivity)
        QtCore.QMetaObject.connectSlotsByName(ConfigDlg)

    def retranslateUi(self, ConfigDlg):
        ConfigDlg.setWindowTitle(_translate("ConfigDlg", "Dialog", None))
        self.label.setText(_translate("ConfigDlg", "save path:", None))
        self.selectSavePathPushButton.setText(_translate("ConfigDlg", "select Path...", None))
        self.addDirectoryPushButton.setText(_translate("ConfigDlg", "add directory...", None))
        self.editDirectoryPushButton.setText(_translate("ConfigDlg", "edit directory...", None))
        self.removeDirectoryPushButton.setText(_translate("ConfigDlg", "remove directory", None))
        self.groupBox.setTitle(_translate("ConfigDlg", "re-scanning", None))
        self.checkBox.setText(_translate("ConfigDlg", "auto re-scan interval", None))
        self.spinBox.setSuffix(_translate("ConfigDlg", " hours", None))
        self.pushButton_4.setText(_translate("ConfigDlg", "rescan now", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ConfigDlg", "Media Library", None))
        self.label_2.setText(_translate("ConfigDlg", "Format Template:", None))
        self.placeholderArtistButton.setText(_translate("ConfigDlg", "Artist ", None))
        self.placeholderAlbumButton.setText(_translate("ConfigDlg", "Album", None))
        self.placeholderTitleButton.setText(_translate("ConfigDlg", "Title", None))
        self.placeholderTracknumberButton.setText(_translate("ConfigDlg", "Tracknumber", None))
        self.placeholderDurationButton.setText(_translate("ConfigDlg", "Duration", None))
        self.placeholderFilePathButton.setText(_translate("ConfigDlg", "Filepath", None))
        self.placeholderFileNameButton.setText(_translate("ConfigDlg", "Filename", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ConfigDlg", "Playlists", None))

