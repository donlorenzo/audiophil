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
import mimetypes
import hashlib
import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.phonon import *

from track import Track
from tools import createAction, millisecondsToStr, escapeSqlInput

class MediaLibraryGenericDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MediaLibraryGenericDelegate, self).__init__(parent)
        
    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
            painter.drawText(QRectF(option.rect), Qt.AlignVCenter, index.data().toString())
        else:
            painter.setPen(option.palette.text().color())
            painter.drawText(QRectF(option.rect), Qt.AlignVCenter, index.data().toString())
    
class MediaLibraryDurationDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MediaLibraryDurationDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        assert index.column() == MediaLibraryView.DURATION
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())
        painter.drawText(QRectF(option.rect), Qt.AlignVCenter|Qt.AlignRight, millisecondsToStr(index.data().toInt()[0]) + " ")


class MediaLibraryPathDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MediaLibraryPathDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        assert index.column() == MediaLibraryView.PATH
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())
        text = QString.fromUtf8(index.data().toByteArray())
        text = option.fontMetrics.elidedText(text, Qt.ElideLeft, option.rect.width())
        painter.drawText(QRectF(option.rect), Qt.AlignVCenter, text)

class MediaLibraryView(QTableView):
    ID, PATH, ARTIST, ALBUM, TITLE, TRACKNUMBER, DURATION, MTIME, LOADED = range(9)
    def __init__(self, parent=None):
        super(MediaLibraryView, self).__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(18)
        self.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.genericDelegate = MediaLibraryGenericDelegate()
        self.setItemDelegate(self.genericDelegate)
        self.durationDelegate = MediaLibraryDurationDelegate()
        self.setItemDelegateForColumn(MediaLibraryView.DURATION, self.durationDelegate)
        self.pathDelegate = MediaLibraryPathDelegate()
        self.setItemDelegateForColumn(MediaLibraryView.PATH, self.pathDelegate)
        self.setupActions()
        self.setupContextMenu()

    def init(self, model):
        self.setModel(model)

    def setModel(self, model):
        QTableView.setModel(self, model)
        self.setColumnHidden(MediaLibraryView.ID, True)
        self.setColumnHidden(MediaLibraryView.LOADED, True)
        self.setColumnHidden(MediaLibraryView.MTIME, True)
        self.sortByColumn(MediaLibraryView.PATH, Qt.AscendingOrder)
        self.resizeColumnsToContents()

    def setupActions(self):
        self.enqueueAction = createAction(self, "Enqueue to current playlist", self.enqueue)
        self.addToNewAction = createAction(self, "Add to new playlist", self.addToNew)

    def setupContextMenu(self):
        self.contextMenu = QMenu()
        self.contextMenu.addAction(self.enqueueAction)
        self.contextMenu.addAction(self.addToNewAction)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def popupMenu(self, pos):
        self.contextMenu.popup(self.mapToGlobal(pos))

    def getSelectedTrackIds(self):
        selectedIds = []
        model = self.model()
        for modelIndex in self.selectionModel().selectedRows():
            selectedIds.append(model.data(model.index(modelIndex.row(), MediaLibraryView.ID)).toInt()[0])
        logging.debug("selected Ids: %s" % str(selectedIds))
        return selectedIds

    def enqueue(self):
        self.emit(SIGNAL("enqueue"), self.getSelectedTrackIds())

    def addToNew(self):
        self.emit(SIGNAL("addToNewPlaylist"), self.getSelectedTrackIds())



class MediaLibraryModel(QSqlTableModel):
    def init(self):
        mimetypes.init()
        db = QSqlDatabase.database()
        db.transaction()
        query = QSqlQuery()
        # the "mediaLibrary" table contains all known tracks
        query.exec_("""CREATE TABLE IF NOT EXISTS mediaLibrary (
                       id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                       path TEXT UNIQUE NOT NULL,
                       artist TEXT,
                       album TEXT,
                       tracknumber INTEGER,
                       tracktitle TEXT,
                       duration INTEGER,
                       mtime INTEGER,
                       loaded INTEGER)
                    """)
        # the "directories" table keeps track of the directories
        # that are watched by the mediaLibrary
        query.exec_("""CREATE TABLE IF NOT EXISTS directories (
                       id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                       absolutePath TEXT UNIQUE NOT NULL,
                       contentHash TEXT NOT NULL,
                       firstClassCitizen INTEGER)
                    """)
        query.finish()
        db.commit()
        self.setTable("mediaLibrary")
        self.refresh()

    ## def getAccurateRowCount(self):
    ##     query = QSqlQuery()
    ##     query.exec_("SELECT count(*) FROM mediaLibrary")
    ##     if not query.next():
    ##         raise RuntimeError("could not get accurate row count")
    ##     return query.value(0).toInt()[0]

    ## def index(self, row, column, parent=QModelIndex()):
    ##     while (self.rowCount() < row < self.getAccurateRowCount() and
    ##            self.canFetchMore()):
    ##         self.fetchMore()
    ##     return super(MediaLibraryModel, self).index(row, column, parent)
        
    def addFiles(self, fileList, transaction=True):
        cnt = len(fileList)
        if transaction:
            db = QSqlDatabase.database()
            db.transaction()
        query = QSqlQuery()
        query.prepare("""
            INSERT OR REPLACE INTO mediaLibrary
            (path, artist, album, tracknumber, tracktitle, duration, mtime, loaded)
            VALUES
            (:path, :artist, :album, :tracknumber, :tracktitle, :duration, :mtime, :loaded)
            """)
        for i, f in enumerate(fileList):
            track = Track.fromFile(f)
            query.bindValue(":path", QVariant(track.path))
            query.bindValue(":artist", QVariant(track.artist))
            query.bindValue(":album", QVariant(track.album))
            query.bindValue(":tracknumber", QVariant(track.tracknumber))
            query.bindValue(":tracktitle", QVariant(track.tracktitle))
            query.bindValue(":duration", QVariant(track.duration))
            query.bindValue(":mtime", QVariant(os.stat(f).st_mtime))
            query.bindValue(":loaded", QVariant(track.loaded))
            query.exec_()
        query.finish()
        if transaction:
            db.commit()

    def addDirectory(self, dirPath, recursive=True):
        logging.debug("addDir %s" % dirPath)
        # expand path, make absolute and check for validity
        dirPath = os.path.abspath(os.path.expanduser(os.path.expandvars(dirPath)))
        if not os.path.exists(dirPath):
            raise IOError("path '{dirPath}' doen't exist".format(**locals()))
        if not os.path.isdir(dirPath):
            raise IOError("path '{dirPath}' is not a directory".format(**locals()))
        db = QSqlDatabase.database()
        try:
            db.transaction()
            query = QSqlQuery()
            # check if dir is already being directly or indirectly watched
            query.prepare("""SELECT firstClassCitizen FROM directories WHERE absolutePath IS :dirPath""")
            query.bindValue(":dirPath", dirPath)
            query.exec_()
            if query.next():
                # directory is already being watched. just make sure it is a first class citizen and return
                query.prepare("""UPDATE directories SET firstClassCitizen = 1 WHERE absolutePath IS :dirPath""")
                query.bindValue(":dirPath", dirPath)
                query.exec_()
                query.finish()
                db.commit()
                return
            # walk directories
            unsupportedFileExtensions = {}
            for root, dirs, files in os.walk(dirPath):
                if not recursive and root != dirPath:
                    break
                logging.debug("processing directory: %s" % root)
                dirs.sort()
                files.sort()
                if not os.access(dirPath, os.R_OK | os.X_OK):
                    logging.warning("Wrong permissions on '{dirPath}'. read and execute are needed".format(**locals()))
                    continue
                # TODO: add a watcher for this directory. use pyinotify or something similar
                contentHash = hashlib.sha1()
                contentHash.update("".join(dirs))
                contentHash.update("".join(files))
                query.prepare("""INSERT INTO directories
                                 (absolutePath, contentHash, firstClassCitizen)
                                 VALUES
                                 (:dirPath, :contentHash, :firstClassCitizen)""")
                query.bindValue(":dirPath", root)
                query.bindValue(":contentHash", contentHash.hexdigest())
                query.bindValue(":firstClassCitizen", 1 if root == dirPath else 0)
                query.exec_()
                # add files
                fileList = []
                for filePath in map(lambda f : os.path.join(root, f), files):
                    mimeType = mimetypes.guess_type(filePath)[0]
                    # only accept audio/* mimetypes and work around ogg mime type
                    if ((mimeType and mimeType.startswith("audio") and Phonon.BackendCapabilities.isMimeTypeAvailable(mimeType)) or
                        filePath.endswith(".ogg")):
                        fileList.append(filePath)
                    else:
                        tmp = (os.path.splitext(filePath)[1], mimeType)
                        if tmp not in unsupportedFileExtensions:
                            unsupportedFileExtensions[tmp] = 1
                        else:
                            unsupportedFileExtensions[tmp] += 1
                self.addFiles(fileList, False)
            query.finish()
            db.commit()
            # report unsupported types for debugging
            if unsupportedFileExtensions:
                logging.info("Omitted the following file extensions with the guessed mime-type:")
                for (ext, mimetype), cnt in unsupportedFileExtensions.items():
                    logging.info("    %s %s %d" % (ext, mimetype, cnt))
        except:
            logging.error("rolling back")
            db.rollback()
            
    ## def rescanLibrary(self):
        
    ##     for root, dirs, files in 
        
    def getDirectories(self):
        directories = []
        query = QSqlQuery()
        query.exec_("""SELECT absolutePath FROM directories WHERE firstClassCitizen IS 1""")
        while query.next():
            directories.append(str(query.value(0).toString()))
        query.finish()
        return directories

    def updateTrack(self, track):
        QSqlDatabase.database().transaction()
        query = QSqlQuery()
        query.prepare("""UPDATE media SET artist = :artist, album = :album, title = :title,
                                          tracknumber = :tracknumber, duration = :duration,
                                          loaded = :loaded
                         WHERE path == :path""")
        query.bindValue(":artist", track.artist)
        query.bindValue(":album", track.album)
        query.bindValue(":title", track.title)
        query.bindValue(":tracknumber", track.tracknumber)
        query.bindValue(":duration", track.duration)
        query.bindValue(":loaded", track.loaded)
        query.exec_()
        query.finish()
        QSqlDatabase.database().commit()
        self.model.select()
        if track in self.pendingTracks:
            self.pendingTracks.remove(track)

    def setFilter(self, filterString):
        # We use SQL's LIKE comparison but GLOB syntax because GLOB itself is case sensitive
        if filterString.trimmed():
            filterString.replace("*", "%")
            escapedFilterString = escapeSqlInput(filterString)
            filterClause = """path LIKE {pattern} OR artist LIKE {pattern} OR 
                              album LIKE {pattern} OR tracktitle LIKE {pattern}
                              """.format(pattern=escapedFilterString)
        else:
            filterClause = ""
        super(MediaLibraryModel, self).setFilter(filterClause)

    def __getitem__(self, index):
        return Track.fromSqlRecord(self.model.record(index))

    def refresh(self):
        if not self.select():
            logging.error("selecting database: %s" % self.lastError().text())


import ui_mediaLibrary
class MediaLibrary(ui_mediaLibrary.Ui_MediaLibrary, QDockWidget):
    def init(self):
        # do setupUi here because the AudioPhil.setupUi overwrites the central Widget
        self.setupUi(self)
        self.mediaLibraryModel = MediaLibraryModel()
        self.mediaLibraryModel.init()
        self.mediaLibraryView.init(self.mediaLibraryModel)
        
    def setFilter(self, filterString):
        self.mediaLibraryModel.setFilter(filterString)

    def _getDatabaseName(self):
        return str(QSqlDatabase.database().databaseName())
    databaseName = property(_getDatabaseName)

    def _getDirectories(self):
        return self.mediaLibraryModel.getDirectories()
    directories = property(_getDirectories)
    
    def getTrackIdsByPath(self, path, fuzzy=False):
        query = QSqlQuery()
        query.prepare("""SELECT id FROM mediaLibrary WHERE path LIKE :path""")
        if fuzzy:
            query.bindValue(":path", "%" + path + "%")
        else:
            query.bindValue(":path", path)
        query.exec_()
        trackIds = []
        while query.next():
            trackIds.append(query.value(0).toInt()[0])
        return trackIds
