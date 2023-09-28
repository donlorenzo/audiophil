# -*- coding: utf-8 -*-

# Copyright (c) 2008, 2010, Lorenz Quack
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * The name of Lorenz Quack may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

u"""
"""

import os
import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ui_configDlg

class ConfigDlg(QDialog, ui_configDlg.Ui_ConfigDlg):
    def __init__(self, mediaLibrary, formatTemplate, parent=None):
        super(ConfigDlg, self).__init__(parent)
        self.mediaLibrary = mediaLibrary
        self.setupUi(self)
        self.setupSignals()
        self.formatTemplateLineEdit.setText(formatTemplate)

    def setupUi(self, instance):
        super(ConfigDlg, self).setupUi(instance)
        self.savePathLineEdit.setText(os.path.abspath(self.mediaLibrary.databaseName))
        for d in self.mediaLibrary.directories:
            self.addDirectory(d)

    def setupSignals(self):
        self.signalMapper = QSignalMapper()
        self.signalMapper.setMapping(self.placeholderArtistButton, "<artist>")
        self.signalMapper.setMapping(self.placeholderAlbumButton, "<album>")
        self.signalMapper.setMapping(self.placeholderTitleButton, "<title>")
        self.signalMapper.setMapping(self.placeholderTracknumberButton, "<tracknumber>")
        self.signalMapper.setMapping(self.placeholderDurationButton, "<duration>")
        self.signalMapper.setMapping(self.placeholderFilePathButton, "<filepath>")
        self.signalMapper.setMapping(self.placeholderFileNameButton, "<filename>")
        for button in (b for name, b in self.__dict__.items()
                       if (name.startswith("placeholder") and
                           name.endswith("Button") and
                           isinstance(b, QPushButton))):
            self.connect(button, SIGNAL("clicked(bool)"),
                         self.signalMapper, SLOT("map()"))
        self.connect(self.signalMapper, SIGNAL("mapped(const QString&)"),
                     self.formatTemplateLineEdit.insert)

    def updateButtonActivity(self, newSelection, oldSelection):
        if newSelection is not None:
            self.editDirectoryPushButton.setEnabled(True)
            self.removeDirectoryPushButton.setEnabled(True)
        else:
            self.editDirectoryPushButton.setEnabled(False)
            self.removeDirectoryPushButton.setEnabled(False)

    def editDirectory(self):
        newDirector = QFileDialog.getExistingDirectory(self, "Select directory to be added to the Media Library")
        if newDirector:
            row = self.directoriesListWidget.currentRow()
            self.directoriesListWidget.takeItem(row)
            self.directoriesListWidget.insertItem(row, newDirector)
            self.directoriesListWidget.setCurrentRow(row)

    def removeDirectory(self):
        self.directoriesListWidget.takeItem(self.directoriesListWidget.currentRow())

    def selectSavePath(self):
        filename = QFileDialog.getSaveFileName(self, "Selecte where the Media Library should be saved to",
                                               os.path.dirname(self.mediaLibrary.databaseName))
        if filename:
            self.savePathLineEdit.setValue(filename)

    def selectDirectory(self):
        self.addDirectory(QFileDialog.getExistingDirectory(self, "Select directory to be added to the Media Library"))

    def addDirectory(self, directoryPath):
        if directoryPath:
            logging.debug("dir type: %s" % str(type(directoryPath)))
            if isinstance(directoryPath, QString):
                self.directoriesListWidget.addItem(directoryPath)
            elif isinstance(directoryPath, str):
                self.directoriesListWidget.addItem(QString.fromUtf8(directoryPath))
            elif isinstance(directoryPath, unicode):
                self.directoriesListWidget.addItem(QString(directoryPath))
            else:
                logging.warning("configDlg.addDirectory: unknown type: %s" % type(directoryPath))

        
