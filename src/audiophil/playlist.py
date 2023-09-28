# -*- coding: utf-8 -*-

# Copyright (c) 2008, 2010 Lorenz Quack
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

import os.path
import random
from functools import partial
import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from track import Track
from tools import createAction, escapeSqlInput
        
def init():
    db = QSqlDatabase.database()
    db.transaction()
    query = QSqlQuery()
    # the "playlistTracks" table contains all tracks in any playlist
    query.exec_("""CREATE TABLE IF NOT EXISTS playlistTracks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   trackId REFERENCES mediaLibrary
                       ON DELETE CASCADE
                       ON UPDATE CASCADE,
                   playlistId REFERENCES playlists
                       ON DELETE CASCADE
                       ON UPDATE CASCADE,
                   position INTEGER)
                """)
    query.finish()
    db.commit()




class SearchLineEdit(QWidget):
    class MyLineEdit(QLineEdit):
        def keyPressEvent(self, event):
            if event.key() == Qt.Key_Escape:
                self.releaseKeyboard()
                self.emit(SIGNAL("editingFinished()"))
            elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                pass
            else:
                super(SearchLineEdit.MyLineEdit, self).keyPressEvent(event)
        def focusInEvent(self, event):
            self.grabKeyboard()
        def focusOutEvent(self, event):
            self.releaseKeyboard()
            
    def __init__(self, parent=None):
        super(SearchLineEdit, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.lineEdit = SearchLineEdit.MyLineEdit()
        self.closeButton = QPushButton(QIcon.fromTheme("window-close"), "abort")
        self.layout.addWidget(self.closeButton)
        self.setFocusProxy(self.lineEdit)
        self.connect(self.closeButton, SIGNAL("clicked(bool)"), self.abort)
        self.connect(self.lineEdit, SIGNAL("editingFinished()"), self.abort)
        self.connect(self.lineEdit, SIGNAL("textChanged(const QString&)"),
                     partial(self.emit, SIGNAL("textChanged(const QString&)")))
        self.layout.addWidget(self.lineEdit)
        self.setLayout(self.layout)
    def __getattr__(self, attr):
        return getattr(self.lineEdit, attr)

    def abort(self, *args):
        self.lineEdit.clear()
        self.emit(SIGNAL("editingFinished()"))
    
class Playlist(QWidget):
    formatTemplate = u"[%(artist)s] %(tracknumber)s %(tracktitle)s"
    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)
        self.model = None
        self.view = PlaylistView(self)
        self.searchLine = SearchLineEdit(self)
        self.searchLine.hide()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.searchLine)
        self.view.show()
        self.setLayout(self.layout)
        
    name = property(lambda self: self.model.name) 
    playlistId = property(lambda self: self.model.playlistId) 

    def init(self, playlistId):
        logging.debug("playlist init, id: %d" % playlistId)
        self.model = PlaylistModel(playlistId)
        self.setupConnections()
        self.view.setModel(self.model)

    def __len__(self):
        return self.model.getAccurateRowCount()
    
    def setupConnections(self):
        self.connect(self.view, SIGNAL("doubleClicked(QModelIndex)"), self.onActivation)
        self.connect(self.view, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     partial(self.emit, SIGNAL("customContextMenuRequested(const QPoint&)")))
        self.connect(self.view, SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                     self.onCurrentChanged)
        self.connect(self.searchLine, SIGNAL("textChanged(const QString&)"), self.model.setFilter)
        self.connect(self.searchLine, SIGNAL("editingFinished()"), lambda : self.searchLine.hide())

    def onCurrentChanged(self, newIndex, oldIndex):
        logging.debug("playlist current changed")
        track = self.model.getTrack(newIndex)
        self.emit(SIGNAL("currentChanged"), track)
        
    def onActivation(self, modelIndex):
        track = self.model.getTrack(modelIndex)
        self.emit(SIGNAL("playRequest"), track)

    def onSearch(self):
        self.searchLine.show()
        self.searchLine.setFocus(Qt.ShortcutFocusReason)

    def addTracks(self, trackIds):
        self.model.addTracks(trackIds)

    def getSelectedTrack(self):
        selectedModelIndex = self.view.currentIndex()
        if not selectedModelIndex.isValid():
            return None
        return self.model.getTrack(selectedModelIndex)

    def getSelectedTracks(self):
        selectedTracks = []
        selectedModelIndices = self.view.selectedIndexes()
        for selectedModelIndex in selectedModelIndices:
            selectedTracks.append(self.model.getTrack(selectedModelIndex))
        return selectedTracks

    def removeSelectedTracks(self):
        rows = list(track.row for track in self.getSelectedTracks())
        rows.sort()
        offset = 0
        while rows:
            row = rows.pop(0) - offset
            count = 1
            while rows and rows[0] == row + count - offset:
                count += 1
                rows.pop(0)
            self.model.removeRows(row, count)
            offset += count
        
    def getTrackByRow(self, row):
        trackModelIndex = self.model.index(row, PlaylistModel.TRACK_ID)
        if not trackModelIndex.isValid():
            return None
        return self.model.getTrack(trackModelIndex)

    def getRandomTrack(self):
        return self.getTrackByRow(random.randrange(len(self)))

    def setCurrentRow(self, row):
        modelIndex = self.model.index(row, PlaylistModel.TRACK_ID)
        self.view.setCurrentIndex(modelIndex)

    def __iter__(self):
        for i, trackModelIndex in enumerate(self.model):
            yield self.model.getTrack(trackModelIndex)            

            

class PlaylistDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # calculate the width of the first column. the + 20 is space for the playstatus Icon
        dummyString = " " + "8" * len(str(index.model().rowCount(index) + 1)) + ". "
        titleOffset = painter.fontMetrics().size(0, dummyString).width() + 20
        track = index.model().getTrack(index)
        playlistNumber = u"%d. " % (index.row() + 1)
        title = Playlist.formatTemplate % track
        duration = track.durationString

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())
        r = QRectF(option.rect)
        r.setWidth(titleOffset)
        painter.drawText(r, playlistNumber, QTextOption(Qt.AlignRight))
        r = QRectF(option.rect)
        r.setLeft(r.left() + titleOffset)
        painter.drawText(r, title, QTextOption(Qt.AlignLeft))
        painter.drawText(QRectF(option.rect), duration, QTextOption(Qt.AlignRight))


class PlaylistView(QListView):
    def __init__(self, parent=None):
        super(PlaylistView, self).__init__(parent)
        self.setupUI()

    def init(self, model):
        self.setModel(model)

    def setModel(self, model):
        super(PlaylistView, self).setModel(model)
        self.setModelColumn(PlaylistModel.TRACK_ID)

    def setupUI(self):
        self.setItemDelegate(PlaylistDelegate())
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def currentChanged(self, newModelIndex, oldModelIndex):
        super(PlaylistView, self).currentChanged(newModelIndex, oldModelIndex)
        self.emit(SIGNAL("currentChanged(QModelIndex, QModelIndex)"), newModelIndex, oldModelIndex)
        


class PlaylistModel(QSqlTableModel):
    ID, TRACK_ID, PLAYLIST_ID, POSITION = range(4)
    
    def __init__(self, playlistId, parent=None):
        super(PlaylistModel, self).__init__(parent)
        self.playlistId = playlistId
        self.setTable("playlistTracks")
        self.setFilter()
        self.setSort(PlaylistModel.POSITION, Qt.AscendingOrder)
        self.select()

    def _getName(self):
        query = QSqlQuery()
        query.prepare("""SELECT playlistName FROM playlists
                         WHERE id IS :playlistId""")
        query.bindValue(":playlistId", self.playlistId)
        query.exec_()
        if not query.next():
            raise RuntimeError("could not get playlistname: %s" % query.lastError().text())
        return unicode(query.value(0).toString().toUtf8(), "utf-8")
    name = property(_getName)
        
    def index(self, row, column, parent=QModelIndex()):
        while self.rowCount() <= row < self.getAccurateRowCount() and self.canFetchMore():
            self.fetchMore()
        return super(PlaylistModel, self).index(row, column, parent)

    def flags(self, index):
        if index.column() == PlaylistModel.TRACK_ID:
            return super(PlaylistModel, self).flags(index)
        return Qt.NoItemFlags

    def setFilter(self, pattern=QString()):
        pattern.trimmed()
        if pattern:
            pattern.replace("*", "%")
            pattern.replace("?", "_")
            pattern = escapeSqlInput("%" + pattern + "%")
            filterClause = """
            id IN
            (SELECT playlistTracks.id
             FROM mediaLibrary INNER JOIN playlistTracks
               ON mediaLibrary.id = playlistTracks.trackId
             WHERE (playlistTracks.playlistId IS {self.playlistId:d} AND
                    (mediaLibrary.path LIKE {pattern} OR
                     mediaLibrary.artist LIKE {pattern} OR
                     mediaLibrary.album LIKE {pattern} OR
                     mediaLibrary.tracktitle LIKE {pattern}
                     )))""".format(**locals())
        else:
            filterClause = "playlistId IS {self.playlistId:d}".format(**locals())
        return super(PlaylistModel, self).setFilter(filterClause)
        
    def getAccurateRowCount(self):
        query = QSqlQuery()
        query.prepare("""SELECT COUNT(*) FROM playlistTracks
                         WHERE playlistId IS :playlistId""")
        query.bindValue(":playlistId", self.playlistId)
        query.exec_()
        if not query.next():
            raise RuntimeError("could not get accurateRowCount: %s" % query.lastError().text())
        return query.value(0).toInt()[0]
        
    def getTrack(self, index):
        query = QSqlQuery()
        query.prepare("""SELECT id, path,
                                artist, album,
                                tracknumber,
                                tracktitle, duration,
                                mtime, loaded
                         FROM mediaLibrary
                         WHERE id IS :trackId
                      """)
        query.bindValue(":trackId", index.data())
        query.exec_()
        if not query.next():
            raise RuntimeError("could not get track: %s" % query.lastError().text())
        track = Track.fromSqlRecord(query.record())
        track.playlistId = self.playlistId
        track.row = index.row()
        return track

    def addTrackByPath(self, path):
        db = QSqlDatabase.database()
        db.transaction()
        query = QSqlQuery()
        query.prepare("""SELECT id FROM mediaLibrary
                         WHERE path LIKE :path""")
        query.bindValue(":path", path)
        query.exec_()
        if not query.next():
            return False
        trackId = query.value(0).toInt()[0]
        if query.next():
            # path not unique
            return False
        logging.debug("I would add the ID %d" % trackId)
        return True
        
    def addTracks(self, trackIds):
        logging.debug("adding tracks")
        rowCount = self.getAccurateRowCount()
        self.beginInsertRows(QModelIndex(), rowCount, rowCount + len(trackIds) - 1)
        db = QSqlDatabase.database()
        db.transaction()
        query = QSqlQuery()
        query.prepare("""INSERT INTO playlistTracks
                             (trackId, playlistId, position)
                         VALUES (:trackId, :playlistId, :position)
                      """)
        query.bindValue(":playlistId", self.playlistId)
        for i, trackId in enumerate(trackIds):
            query.bindValue(":trackId", trackId)
            query.bindValue(":position", rowCount + i)
            query.exec_()
        query.finish()
        db.commit()
        self.endInsertRows()
        self.select()

    def removeRows(self, row, count, parent=QModelIndex()):
        db = QSqlDatabase.database()
        db.transaction()
        super(PlaylistModel, self).removeRows(row, count, parent)
        query = QSqlQuery()
        query.prepare("""UPDATE playlistTracks
                         SET position = position - ?
                         WHERE (playlistId IS ? AND
                                position > ? + ? - 1)""")
        query.bindValue(0, count)
        query.bindValue(1, self.playlistId)
        query.bindValue(2, row)
        query.bindValue(3, count)
        query.exec_()
        query.finish()
        db.commit()
        self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                  self.index(row, PlaylistModel.POSITION),
                  self.index(self.getAccurateRowCount(), PlaylistModel.POSITION))

    def __iter__(self):
        i = 1
        for row in xrange(self.getAccurateRowCount()):
            i += 1
            idx = self.index(row, PlaylistModel.TRACK_ID)
            yield idx
