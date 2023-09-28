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

import os.path
import copy_reg
from functools import partial
import random
import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from tools import createAction, CallbackList
import playlist


class Playlists(QWidget):
    def __init__(self, parent=None):
        super(Playlists, self).__init__(parent)
        self.model = None
        self.view = PlaylistsView(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.view)

    currentPlaylist = property(lambda self: self.view.currentWidget())
    
    def init(self):
        self.model = PlaylistsModel(self)
        self.setupActions()
        self.setupUI()
        self.setupConnections()
        self.model.init()
        self.view.setModel(self.model)

    def __len__(self):
        return self.model.rowCount()

    def setupUI(self):
        self.tabBarContextMenu = QMenu()
        # FIXME: ugly hack
        for action in self.window().menuPlaylist.actions():
            if action.objectName() in ["newPlaylistAction", "renamePlaylistAction", "removePlaylistAction", "savePlaylistAction"]:
                self.tabBarContextMenu.addAction(action)
        self.playlistContextMenu = QMenu()
        self.playlistContextMenu.addAction(self.playlistRemoveItemsAction)
        self.playlistContextMenu.addSeparator()
        self.playlistCopyToMenu = QMenu("copy To Playlist...", self.playlistContextMenu)
        self.playlistContextMenu.addMenu(self.playlistCopyToMenu)

    def setupActions(self):
        #def createAction(parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered(bool)")
        self.playlistRemoveItemsAction = createAction(self, "remove", self.playlistRemoveSelectedItems, "Delete", None, "remove selected Track(s) from Playlist")
        self.playlistCopyItemsToNewAction = createAction(self, "new playlist", self.playlistCopySelectedItemsToNewPlaylist, None, None, "copies selected Track(s) to a new Playlist")
        
    def setupConnections(self):
        self.connect(self.view, SIGNAL("mouseLeftDoubleClickEvent(QMouseEvent)"), self.addEmptyPlaylist)
        self.connect(self.view, SIGNAL("playlistCloseRequest(int)"), self.onRemovePlaylist)
        self.connect(self.view, SIGNAL("playlistRenameRequest(int,QString)"), self.model.renamePlaylist)
        self.connect(self.view, SIGNAL("playlistMoveRequest(int,int)"), self.model.movePlaylist)
        self.connect(self.view, SIGNAL("tabInserted"), self.connectPlaylist)
        self.connect(self.view, SIGNAL("customContextMenuRequested(const QPoint&)"), self.onTabBarContextMenu)
        self.connect(self.view, SIGNAL("currentChanged(int)"), partial(self.emit, SIGNAL("currentChanged(int)")))
        self.connect(self.playlistCopyToMenu, SIGNAL("aboutToShow()"), self.createCopyToMenu)
        
        
    def createCopyToMenu(self):
        self.playlistCopyToMenu.clear()
        self.playlistCopyToMenu.addAction(self.playlistCopyItemsToNewAction)
        self.playlistCopyToMenu.addSeparator()
        playlistNames = []
        for playlistId, playlistName in zip(self.model.getPlaylistIds(),
                                            self.model.getPlaylistNames()):
            self.playlistCopyToMenu.addAction(createAction(self, playlistName,
                                                           partial(self.playlistCopySelectedItemsToPlaylist, playlistId),
                                                           None, None, "copies selected Track(s) to %s" % playlistName))    

    def onSearchPlaylist(self):
        self.currentPlaylist.onSearch()

    def onRenamePlaylist(self):
        self.view.tabBar().renameTab(self.view.currentIndex())

    def onRemovePlaylist(self):
        self.model.removePlaylist(self.currentPlaylist.playlistId)
        if self.model.rowCount() == 0:
            self.addEmptyPlaylist()

    def onTabBarContextMenu(self, pos):
        self.tabBarContextMenu.exec_(self.mapToGlobal(pos))

    def onPlaylistContextMenu(self, pos):
        self.playlistContextMenu.exec_(self.view.widget(0).mapToGlobal(pos))
            
    def renamePlaylist(self, playlistId, newPlaylistName):
        self.model.renamePlaylist(playlistId, newPlaylistName)
        
    def playlistRemoveSelectedItems(self):
        logging.debug("remove selected tracks")
        self.currentPlaylist.removeSelectedTracks()
        
    def playlistCopySelectedItemsToNewPlaylist(self):
        logging.debug("copy selected to new playlist")
        tracks = self.currentPlaylist.getSelectedTracks()
        trackIds = list(track.dbId for track in tracks)
        self.addTracksToNewPlaylist(trackIds)
        
    def playlistCopySelectedItemsToPlaylist(self, playlistId):
        logging.debug("copy selected to %s" % self.model.getPlaylistName(playlistId))
        tracks = self.currentPlaylist.getSelectedTracks()
        trackIds = list(track.dbId for track in tracks)
        self.addTracksToPlaylist(trackIds, playlistId)
        
    def connectPlaylist(self, playistPosition, playlistWidget):
        logging.debug("connecting playlist")
        self.connect(playlistWidget, SIGNAL("playRequest"),
                     partial(self.emit, SIGNAL("playRequest")))
        self.connect(playlistWidget, SIGNAL("customContextMenuRequested(const QPoint&)"), self.onPlaylistContextMenu)

    def addEmptyPlaylist(self, *args):
        logging.debug("add empty")
        playlistNames = self.model.getPlaylistNames()
        newPlaylistName = "<unnamed Playlist>"
        if newPlaylistName in playlistNames:
            counter = 2
            newPlaylistName = "<unnamed Playlist %d>" % counter
            while newPlaylistName in playlistNames:
                counter += 1
                newPlaylistName = "<unnamed Playlist %d>" % counter
        return self.addPlaylist(newPlaylistName)

    def addPlaylist(self, playlistName):
        playlistId = self.model.addPlaylist(playlistName)
        return playlistId
        
    def addTracksToNewPlaylist(self, trackIds):
        newPlaylistId = self.addEmptyPlaylist()
        self.addTracksToPlaylist(trackIds, newPlaylistId)
        return newPlaylistId

    def addTracksToPlaylist(self, trackIds, playlistId=None):
        if playlistId is None:
            playlistId = self.currentPlaylist.playlistId
        playlistPosition = self.model.getPlaylistPosition(playlistId)
        playlist = self.view.widget(playlistPosition)
        playlist.addTracks(trackIds)

    def getPlaylistById(self, playlistId):
        return self.view.widget(self.model.getPlaylistPosition(playlistId))

    def getRandomPlaylist(self):
        return self.view.widget(random.randrange(len(self)))

    def setCurrentPlaylist(self, playlistId):
        playlistPosition = self.model.getPlaylistPosition(playlistId)
        self.view.setCurrentIndex(playlistPosition)



# Qt 4.5 comes with support for moveable tabbars
# furthermore in-place renaming can be achieve via setting the tabWidget
class PlaylistsTabBar(QTabBar):
    tabRenameRequested = pyqtSignal(int,QString)
    
    def __init__(self, parent=None):
        super(PlaylistsTabBar, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setMovable(True)
        self.tabTitleEdit = QLineEdit()
        self.currentEditIndex = None
        self.connect(self.tabTitleEdit, SIGNAL("editingFinished()"), self.renameDone)
        self.tabRemoveCandidate = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MidButton:
            self.tabRemoveCandidate = self.tabAt(event.pos())
        super(PlaylistsTabBar, self).mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        if self.tabRemoveCandidate is not None:
            if self.tabRemoveCandidate == self.tabAt(event.pos()):
                self.emit(SIGNAL("tabCloseRequested(int)"), self.tabRemoveCandidate)
            self.tabRemoveCandidate = None
        super(PlaylistsTabBar, self).mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        tabIndex = self.tabAt(event.pos())
        self.renameTab(tabIndex)
        
    def renameTab(self, tabIndex):
        self.setTabButton(tabIndex, QTabBar.LeftSide, self.tabTitleEdit)
        self.setFocusProxy(self.tabTitleEdit)
        self.tabTitleEdit.setText(self.tabText(tabIndex))
        self.tabTitleEdit.grabKeyboard()
        self.tabTitleEdit.setFocus()
        self.tabTitleEdit.selectAll()
        self.setTabText(tabIndex, "")
        self.currentEditIndex = tabIndex

    def renameDone(self):
        if self.currentEditIndex is None:
            logging.warning("dropping rename because no tabIndex is assosiated")
            return
        self.tabTitleEdit.releaseKeyboard()
        self.setTabButton(self.currentEditIndex, QTabBar.LeftSide, None)
        newTabTitle = unicode(self.tabTitleEdit.text().toUtf8(), "utf8")
        self.tabIndexEdit = None
        self.setFocusProxy(None)
#        self.setTabText(self.currentEditIndex, self.tabTitleEdit.text())
#        self.tabRenameRequested.emit(self.currentEditIndex, newTabTitle)
        self.emit(SIGNAL("tabRenameRequested(int,QString)"),
                  self.currentEditIndex, newTabTitle)


class PlaylistsView(QTabWidget):
    mouseLeftDoubleClickEvent = pyqtSignal(QMouseEvent)
    
    def __init__(self, parent=None):
        super(PlaylistsView, self).__init__(parent)
        self.setTabBar(PlaylistsTabBar(self))
        self.setTabsClosable(True)
        self.setupConnections()
        self._model = None

    def setupConnections(self):
        self.connect(self.tabBar(), SIGNAL("customContextMenuRequested(const QPoint&)"),
                     partial(self.emit, SIGNAL("customContextMenuRequested(const QPoint&)")))
        self.connect(self.tabBar(), SIGNAL("tabCloseRequested(int)"), self.requestPlaylistClose)
        self.connect(self.tabBar(), SIGNAL("tabRenameRequested(int,QString)"), self.requestPlaylistRename)
        self.connect(self.tabBar(), SIGNAL("tabMoved(int, int)"), self.requestPlaylistMove)
        
    def tabInserted(self, index):
        logging.debug("tabInserted")
        self.emit(SIGNAL("tabInserted"), index, self.widget(index))

    def requestPlaylistClose(self, position):
        self.emit(SIGNAL("playlistCloseRequest(int)"), self.widget(position).playlistId)

    def requestPlaylistRename(self, position, newPlaylistName):
        self.emit(SIGNAL("playlistRenameRequest(int,QString)"), self.widget(position).playlistId, newPlaylistName)

    def requestPlaylistMove(self, fromRow, toRow):
        self.emit(SIGNAL("playlistMoveRequest(int, int)"), fromRow, toRow)

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.emit(SIGNAL("mouseLeftDoubleClickEvent(QMouseEvent)"), event)

    def model(self):
        return self._model
    def setModel(self, model):
        self._model = model
        self.connect(model, SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.updatePlaylist)
        self.connect(model, SIGNAL("modelReset()"), self.refreshAll)
        self.connect(model, SIGNAL("rowsInserted(QModelIndex, int, int)"),
                     lambda parent, start, end: self.addPlaylist(start))
        self.connect(model, SIGNAL("rowsRemoved(QModelIndex, int, int)"),
                     lambda parent, start, end: self.removeTab(start))
        self.refreshAll()

    def updatePlaylist(self, topLeftIndex, bottomRightIndex):
        logging.debug("updatePlaylist")
        assert topLeftIndex == bottomRightIndex, "more than one database entry changed"
        if topLeftIndex.column() == PlaylistsModel.PLAYLIST_NAME:
            tabIndex = topLeftIndex.sibling(topLeftIndex.row(), PlaylistsModel.POSITION).data().toInt()[0]
            tabTitle = unicode(topLeftIndex.data().toString().toUtf8(), "utf8")
            self.setTabText(tabIndex, tabTitle)

    def refreshAll(self):
        # remove all Plylists
        self.clear()
        for i in xrange(self.model().rowCount()):
            self.addPlaylist(i)

    def addPlaylist(self, tabIndex):
        newPlaylist = playlist.Playlist()
        playlistId = self.model().getPlaylistIdFromPosition(tabIndex)
        logging.debug("add playlist id: %d" % playlistId)
        newPlaylist.init(playlistId)
        self.addTab(newPlaylist, self.model().getPlaylistName(playlistId))

    def onCloseTab(self, position):
        self.model().removePlaylist(self.widget(position).playlistId)

    def getPlaylistWidgetFromId(self, playlistId):
        tabIndex = self.model().getPlaylistPosition(playlistId)
        return self.widget(tabIndex)



class PlaylistsModel(QSqlTableModel):
    ID, PLAYLIST_NAME, POSITION = range(3)

    def init(self):
        db = QSqlDatabase.database()
        db.transaction()
        query = QSqlQuery()
        # the "playlists" table contains all open playlists 
        query.exec_("""CREATE TABLE IF NOT EXISTS playlists (
                       id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                       playlistName TEXT,
                       position INTEGER)
                    """)
        query.finish()
        db.commit()
        #FIXME: this is fucked up! when setting the table rowCount the starts to behave strangely
#        self.setTable("playlists")
#        self.setSort(PlaylistsModel.POSITION, Qt.AscendingOrder)
        playlist.init()
#        self.select()

    def index(self, row, column, parent=QModelIndex()):
        query = QSqlQuery()
        query.prepare("SELECT id FROM playlists WHERE position IS :row")
        query.bindValue(":row", row)
        query.exec_()
        if not query.next():
            raise RuntimeError("could not create index: %s" % query.lastError().text())
        return self.createIndex(row, column, query.value(0).toInt()[0])

    def rowCount(self, parent=QModelIndex()):
        query = QSqlQuery()
        query.exec_("SELECT count(*) FROM playlists")
        if not query.next():
            raise RuntimeError("could not get rowCount: %s" % query.lastError().text())
        rowCount = query.value(0).toInt()[0]
        query.finish()
        return rowCount

    def columnCount(self, parent=QModelIndex()):
        return 3
    
    def data(self, index, role=Qt.DisplayRole):
        if index.column() == self.PLAYLIST_NAME:
            return self.getPlaylistName(index.internalId())
        elif index.column() == self.POSITION:
            return self.getPlaylistPosition(index.internalId())
        elif index.column() == self.ID:
            return index.internalId()
        
    def setData(self, index, value, role=Qt.EditRole):
        if index.column() == self.ID:
            return False
        elif index.column() == self.PLAYLIST_NAME:
            newPlaylistName = unicode(value.toString().toUtf8(), "utf8")
            self.setPlaylistName(index.internalId(), newPlaylistName)
        elif index.column() == self.POSITION:
            newPlaylistPosition = value.toInt()[0]
            self.setPlaylistPosition(index.internalId(), newPlaylistPosition)
        else:
            return False
        self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
        return True

    def flags(self, index):
        if index.column == self.ID:
            return Qt.NoItemFlags
        else:
            return super(PlaylistsModel, self).flags(index) | Qt.ItemIsEditable
        
    def getPlaylistPosition(self, playlistId):
        logging.debug("get Playlist pos for id %d" % playlistId)
        query = QSqlQuery()
        query.prepare("SELECT position FROM playlists WHERE id IS :playlistId")
        query.bindValue(":playlistId", playlistId)
        query.exec_()
        if not query.next():
            raise RuntimeError("could not get playlist position: %s" % query.lastError().text())
        playlistPosition = query.value(0).toInt()[0]
        query.finish()
        return playlistPosition

    def setPlaylistPosition(self, playlistId, newPlaylistPosition):
        query = QSqlQuery()
        query.prepare("""UPDATE playlists
                             SET position = :newPlaylistPosition
                             WHERE id IS :playlistId""")
        query.bindValue(":newPlaylistPosition", newPlaylistPosition)
        query.bindValue(":playlistId", playlistId)
        if not query.next():
            raise RuntimeError("could not set playistPosition: %s" % query.lastError().text())
        query.finish()
        
    def getPlaylistName(self, playlistId):
        logging.debug("get playlistName for id %d" % playlistId)
        query = QSqlQuery()
        query.prepare("SELECT playlistName FROM playlists WHERE id IS :playlistId")
        query.bindValue(":playlistId", playlistId)
        query.exec_()
        if not query.next():
            raise RuntimeError("could not get playistName: %s" % query.lastError().text())
        playlistName = unicode(query.value(0).toString().toUtf8(), "utf8")
        query.finish()
        return playlistName

    def setPlaylistName(self, playlistId, newPlaylistName):
        logging.debug("setPlaylistName")
        query = QSqlQuery()
        query.prepare("""UPDATE playlists
                             SET playlistName =:newPlaylistName
                             WHERE id IS :playlistId""")
        query.bindValue(":newPlaylistName", newPlaylistName)
        query.bindValue(":playlistId", playlistId)
        query.exec_()
        logging.error("SQL error: %s" % query.lastError().text())
        query.finish()
        
    def getPlaylistNames(self):
        playlistNames = []
        query = QSqlQuery()
        query.exec_("SELECT playlistName FROM playlists ORDER BY position ASC")
        while query.next():
            playlistNames.append(unicode(query.value(0).toString().toUtf8(), "utf8"))
        query.finish()
        return playlistNames

    def getPlaylistIds(self):
        playlistIds = []
        query = QSqlQuery()
        query.exec_("SELECT id FROM playlists ORDER BY position ASC")
        while query.next():
            playlistIds.append(query.value(0).toInt()[0])
        query.finish()
        return playlistIds
        
    def addPlaylist(self, playlistName):
        logging.debug("adding Playlist %s" % playlistName)
        rowCount = self.rowCount()
        self.beginInsertRows(QModelIndex(), rowCount, rowCount)
        db = QSqlDatabase.database()
        db.transaction()
        query = QSqlQuery()
        # TODO: I guess this can be done more elegantly
        query.exec_("SELECT count(*) FROM playlists")
        query.next()
        query.prepare("""INSERT INTO playlists (playlistName, position)
                             SELECT :playlistName, COALESCE(MAX(position)+1,0)
                                 FROM playlists
                          """)
        query.bindValue(":playlistName", playlistName)
        query.exec_()
        query.exec_("SELECT MAX(id) FROM playlists")
        if not query.next():
            raise RuntimeError("Error in add Playlist: could not get playlistId")
        playlistId = query.value(0).toInt()[0]
        logging.debug("newplaylistID: %d" % playlistId)
        query.finish()
        db.commit()
        self.endInsertRows()
        return playlistId

    def removePlaylist(self, playlistId):
        logging.debug("removing PlaylistId %d" % playlistId)
        position = self.getPlaylistPosition(playlistId)
        self.beginRemoveRows(QModelIndex(), position, position)
        db = QSqlDatabase.database()
        db.transaction()
        query = QSqlQuery()
        query.prepare("""UPDATE playlists
                         SET position = position - 1
                         WHERE position > (SELECT position FROM playlists
                                           WHERE id IS :playlistId)""")
        query.bindValue(":playlistId", playlistId)
        query.exec_()
        query.prepare("""DELETE FROM playlists
                         WHERE id IS :playlistId""")
        query.bindValue(":playlistId", playlistId)
        query.exec_()
        query.finish()
        db.commit()
        self.endRemoveRows()

    def movePlaylist(self, fromPosition, toPosition):
        logging.debug("moving from %d to %d" % (fromPosition, toPosition))
        db = QSqlDatabase.database()
        db.transaction()
        query = QSqlQuery()
        # Note: we could use named placeholder, but PyQt4-4.7.3 seems to not bind them correctly if they occure more than once
        if fromPosition > toPosition:
            query.prepare("""UPDATE playlists
                             SET position = CASE
                                 WHEN position == ? THEN ?
                                 ELSE position + 1 END
                             WHERE position BETWEEN ? AND ?""")
            query.bindValue(0, fromPosition)
            query.bindValue(1, toPosition)
            query.bindValue(2, toPosition)
            query.bindValue(3, fromPosition)
        else:
            query.prepare("""UPDATE playlists
                             SET position = CASE
                                 WHEN position == ? THEN ?
                                 ELSE position - 1 END
                             WHERE position BETWEEN ? AND ?""")
            query.bindValue(0, fromPosition)
            query.bindValue(1, toPosition)
            query.bindValue(2, fromPosition)
            query.bindValue(3, toPosition)
        query.exec_()
        query.finish()
        db.commit()
        # TODO: we should emit dataChanged even if it is ignored
#       self.dataChanged(index, index)

    def renamePlaylist(self, playlistId, newPlaylistName):
        logging.debug("renameing playlist to %s" % newPlaylistName)
        row = self.getPlaylistPosition(playlistId)
        index = self.createIndex(row, self.PLAYLIST_NAME, playlistId)
        self.setData(index, QVariant(newPlaylistName))
    
    def getPlaylistIdFromPosition(self, position):
        logging.debug("getting id from pos %d" % position)
        query = QSqlQuery()
        query.prepare("""SELECT id FROM playlists WHERE position IS :position""")
        query.bindValue(":position", position)
        query.exec_()
        if not query.next():
            raise RuntimeError("could not retrieve playlistId from position: %s" % query.lastError().text())
        playlistId = query.value(0).toInt()[0]
        query.finish()
        return playlistId
        
