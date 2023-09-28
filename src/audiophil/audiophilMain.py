#!/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2008, 2010, 2015 Lorenz Quack
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
from __future__ import division

__version__ = "0.4.2"

import sys
import os.path
import pickle
import bz2
import re
import random
import logging
import platform
from datetime import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom
import urllib
random.seed()

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from PyQt5.phonon import *

import ui_audiophil
import mediaLibrary
import configDlg
from track import Track 
from tools import millisecondsToStr, createAction, safeUtfDecode, mkdir_p
import playlists
import playlist
        


class AudioPhil(ui_audiophil.Ui_AudioPhil, QMainWindow):
    MAGIC_NUMBER = 0xBABB5ACC
    FILE_VERSION = 5
    TIME_LABEL_ELAPSED = 0
    TIME_LABEL_REMAINING = 1
    TIME_LABEL_TOTAL = 2
    configPath = os.path.join(os.path.expanduser("~"), ".audiophil")

    def __init__(self, parent=None):
        super(AudioPhil, self).__init__(parent)
        mkdir_p(self.configPath)
        logging.basicConfig(filename=os.path.join(self.configPath, "audiophil.log"), level=logging.DEBUG)
        logging.info("={0:=^50}=".format(datetime.now().strftime("%c")))
        self._qt_workaround_old_volume = None
        self.setupEnvironment()
        self.setupMedia()
        self.setupUi(self)
        self.setupSignals()
        if os.path.exists(self.configFile):
            try:
                self.loadState()
            except Exception as e:
                logging.error("An error occured during loading of the config file '{filename}'.\n"
                              "The config file will be ignored. The error message follows:\n"
                              "{t.__name__}: {exc!s}".format(filename=self.configFile,
                                                             t=type(e), exc=e))
        self.show()

    def setupEnvironment(self):
        if not os.path.exists(AudioPhil.configPath) or not os.path.isdir(AudioPhil.configPath):
            os.mkdir(AudioPhil.configPath, 0o755)
        self.configFile = os.path.join(AudioPhil.configPath, "audiophil.cfg")
        self.databasePath = os.path.join(AudioPhil.configPath, "audiophil.sql")
        self.openDatabase(self.databasePath)

    def setupMedia(self):
        self.mediaObject = Phonon.MediaObject(self)
        self.mediaObject.setTickInterval(250)
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        path = Phonon.createPath(self.mediaObject, self.audioOutput)
        self.__activeTrack = None

    def setupUi(self, *args):
        super(AudioPhil, self).setupUi(*args)
        self.mediaLibrary.init()
        self.playlists.init()
        self.setupToolBar()
        self.setupTrayIcon()
        self.addAction(self.playlistSearchAction)
        self.playlistSearchAction.setIconVisibleInMenu(False)
        self.playlistSearchAction.setShortcuts(("J", "Ctrl+F"))
        self.showMediaLibraryAction = self.mediaLibrary.toggleViewAction()
        self.showMediaLibraryAction.setObjectName("showMediaLibraryAction")
        self.showMediaLibraryAction.setText("Show Media Library")
        self.menuView.addAction(self.showMediaLibraryAction)
        self.showSidebarAction = self.sidebar.toggleViewAction()
        self.showSidebarAction.setObjectName("showSidebarAction")
        self.showSidebarAction.setText("Show Sidebar")
        self.menuView.addAction(self.showSidebarAction)
        self.showCurrentlyPlayingAction = self.currentlyPlaying.toggleViewAction()
        self.showCurrentlyPlayingAction.setObjectName("showCurrentlyPlayingAction")
        self.showCurrentlyPlayingAction.setText('Show "Currently Playing" Info')
        self.menuView.addAction(self.showCurrentlyPlayingAction)
        self.menuView.addSeparator()
        self.showControlsAction = createAction(self, "Show Playback Controls", self.controlsToolBar.setVisible, checkable=True)
        self.showControlsAction.setObjectName("showControlsAction")
        self.menuView.addAction(self.showControlsAction)
        self.showVolumeControlsAction = createAction(self, "Show Volume Controls", self.volumeToolBar.setVisible, checkable=True)
        self.showVolumeControlsAction.setObjectName("showVolumeControlsAction")
        self.menuView.addAction(self.showVolumeControlsAction)
        self.showSeekControlsAction = createAction(self, "Show Seek Controls", self.seekToolBar.setVisible, checkable=True)
        self.showSeekControlsAction.setObjectName("showSeekControlsAction")
        self.menuView.addAction(self.showSeekControlsAction)
        

    def openDatabase(self, filename):
        db = QSqlDatabase.addDatabase("QSQLITE")
        if not db.isValid():
            raise RuntimeError("Error creating database. Is Sqlite support enabled?")
        if not os.path.exists(filename):
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename), 0o755)
        elif not os.access(filename, os.W_OK):
            raise IOError("No write permission on '{filename}'".format(**locals()))
        db.setDatabaseName(filename)
        ## try:
        ##     self.databaseLock = os.open("/var/run/audiophil.pid", os.O_EXLOCK)
        ## except IOError:
        ##     print "unable to aquire lock"
        ##     sys.exit(1)
        if not db.open():
            raise DatabaseError(db.lastError().text())
        db.exec_("PRAGMA foreign_keys = true")

    def setupToolBar(self):
        self.toolBarVolumeSlider = Phonon.VolumeSlider(self.audioOutput, self)
        self.toolBarVolumeSlider.setMuteVisible(True)
        self.toolBarVolumeSlider.setIconSize(QSize(24,24))
        self.toolBarVolumeSlider.findChild(QToolButton).setDefaultAction(self.muteAction)
        self.volumeToolBar.addWidget(self.toolBarVolumeSlider)
        self.timeLabel = QPushButton("0:00")
        self.timeLabel.setFlat(True)
        self.timeLabelMode = AudioPhil.TIME_LABEL_ELAPSED
        self.seekToolBar.addWidget(self.timeLabel)
        self.toolBarSeekSlider = Phonon.SeekSlider(self.mediaObject, self)
        self.seekToolBar.addWidget(self.toolBarSeekSlider)

    def setupTrayIcon(self):
        self.trayIcon = QSystemTrayIcon(QIcon(":/icons/audiophil.svg"), self)
        self.trayIcon.setContextMenu(self.menuPlayer)
        self.trayIcon.setToolTip("Not playing")
        self.connect(self.trayIcon, SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.trayIconActivated)
        self.trayIcon.show()

    def trayIconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def setupSignals(self):
        self.connect(self.mediaLibrary.mediaLibraryView, SIGNAL("enqueue"), self.playlists.addTracksToPlaylist)
        self.connect(self.mediaLibrary.mediaLibraryView, SIGNAL("addToNewPlaylist"), self.playlists.addTracksToNewPlaylist)
        self.connect(self.volumeToolBar, SIGNAL("orientationChanged(Qt::Orientation)"),
                     self.toolBarVolumeSlider, SLOT("setOrientation(Qt::Orientation)"))
        self.connect(self.mediaObject, SIGNAL("tick(qint64)"), self.updateTimeLabel)
        self.connect(self.timeLabel, SIGNAL("clicked()"), self.changeTimeLabelMode)
        self.connect(self.seekToolBar, SIGNAL("orientationChanged(Qt::Orientation)"),
                     self.toolBarSeekSlider, SLOT("setOrientation(Qt::Orientation)"))
#        self.connect(self.mediaObject, SIGNAL("aboutToFinish()"), self.enqueueNext)
        self.connect(self.mediaObject, SIGNAL("finished()"), self.playNext)
        self.connect(self.mediaObject, SIGNAL("stateChanged(Phonon::State,Phonon::State)"), self.stateChanged)
        self.connect(self.playlists, SIGNAL("currentChanged(int)"), self.updateInfoToolBoxConnections)
        self.connect(self, SIGNAL("activeTrackChanged"), self.onActiveTrackChanged)
        self.connect(self.playlists, SIGNAL("playRequest"), self.onPlayRequest)
        self.updateInfoToolBoxConnections()
        
    def onPlayRequest(self, track):
        logging.debug("received play request %s" % str(track.__dict__))
        self.playTrack(track)

    def onActiveTrackChanged(self, track):
        infoLabel = self.findChild(QLabel, "activeSongInfoLabel")
        infoText = ""
        if track:
            path = safeUtfDecode(os.path.split(track.path)[1])
            if track.tracktitle:
                title = track.tracktitle
            else:
                title = "(unknown title)"
            if track.artist:
                artist = track.artist
            else:
                artist = "(unknown artist)"
            infoText = '<font size="+1"><b>' + title + '</b></font><br/>by ' + artist
        else:
            infoText = '<font size="+1"><b>(Not Playing)</b></font><br/>&nbsp;'
            path = ""
        self.trayIcon.setToolTip(path)
        self.updateWindowTitle(path)
        infoLabel.setText(infoText)

    def _getActiveTrack(self):
        return self.__activeTrack
    def _setActiveTrack(self, newTrack):
        if newTrack != self.__activeTrack:
            self.__activeTrack = newTrack
            self.emit(SIGNAL("activeTrackChanged"), newTrack)
    activeTrack = property(_getActiveTrack, _setActiveTrack)
            
    currentPlaylist = property(lambda self : self.playlists.view.currentWidget())

    def updateInfoToolBoxConnections(self):
        logging.debug("update Toolbox connection")
        # disconnect the currentPlaylist in case it was already connected
        if self.currentPlaylist is not None:
            self.disconnect(self.currentPlaylist, SIGNAL("currentChanged"), self.updateInfoToolBox)
            self.connect(self.currentPlaylist, SIGNAL("currentChanged"), self.updateInfoToolBox)

    def helpAbout(self):
        QMessageBox.about(self, "About AudioPhil",
                          """<h1>AudioPhil</h1>
                          Version {version}
                          <p>Copyright &copy; 2010, 2015 Lorenz Quack. All rights reserved</p>
                          <p>&lt;<a href="mailto:don@amberfisharts.com">don@amberfisharts.com</a>&gt;</p>
                          <p>Debug Info: <pre>  Python: {pythonVersion}
  Qt:     {qtVersion}
  PyQt:   {pyqtVersion}
</pre></p>
                            """.format(version=__version__,
                                       pythonVersion=platform.python_version(),
                                       qtVersion=QT_VERSION_STR,
                                       pyqtVersion=PYQT_VERSION_STR))
        
    def updateInfoToolBox(self, track):
        logging.debug("updateToolbox")
        self.sidebar.findChild(QLineEdit, "albumLineEdit").setText(track.album)
        self.sidebar.findChild(QLineEdit, "artistLineEdit").setText(track.artist)
        self.sidebar.findChild(QLineEdit, "trackLineEdit").setText(track.tracktitle)
        if track.tracknumber:
            self.sidebar.findChild(QSpinBox, "tracknumberSpinBox").setValue(int(track.tracknumber))
        else:
            self.sidebar.findChild(QSpinBox, "tracknumberSpinBox").clear()
        self.sidebar.findChild(QLineEdit, "fileNameLineEdit").setText(safeUtfDecode(os.path.split(track.path)[1]))
        self.sidebar.findChild(QLineEdit, "filePathLineEdit").setText(safeUtfDecode(track.path))
        size = os.stat(track.path).st_size
        unitNames = ["Byte", "KB" , "MB", "GB"]
        unit = 0
        while size > 1024:
            size /= 1024.
            unit += 1
        self.sidebar.findChild(QLineEdit, "fileSizeLineEdit").setText("{size:.2f} {unitName}".format(size=size, unitName=unitNames[unit]))
        
    def updateWindowTitle(self, path):
        self.setWindowTitle(u"AudioPhil - {0}".format(path))
            
    def play(self):
        selectedTrack = self.currentPlaylist.getSelectedTrack()
        if selectedTrack is None:
            selectedTrack = self.currentPlaylist.getTrackByRow(0)
        self.playTrack(selectedTrack)

    def playTrack(self, track):
        self.activeTrack = track
        if track:
            try:
                source = Phonon.MediaSource(unicode(track.path, "utf8"))
            except UnicodeDecodeError:
                logging.warning('Unicode decode error: cannot decode "{0}"'.format(track.path))
                self.playNext()
            else:
                self.mediaObject.setCurrentSource(source)
                self.mediaObject.play()

    def enqueueTrack(self, track):
        self.activeTrack = track
        if track:
            try:
                source = Phonon.MediaSource(unicode(track.path, "utf8"))
            except UnicodeDecodeError:
                logging.warning('Unicode decode error: cannot decode "{0}"'.format(track.path))
                self.enqueueNext()
            else:
                self.mediaObject.enqueue(source)

    def pause(self):
        if self.mediaObject:
            if self.mediaObject.state() == Phonon.PlayingState:
                self.mediaObject.pause()
            elif self.mediaObject.state() == Phonon.PausedState:
                currentTime = self.mediaObject.currentTime()
                self.mediaObject.play()
                self.mediaObject.seek(currentTime)

    def stop(self):
        self.updateTimeLabel(0)
        if self.activeTrack:
            self.activeTrack = None
        if self.mediaObject:
            self.mediaObject.stop()

    def getNextTrack(self):
        if self.stopAfterCurrentAction.isChecked():
            return None
        followCursor = True if self.playbackFollowCursorAction.isChecked() else False
        repeatTrack = True if self.playbackModeRepeatTrackAction.isChecked() else False
        repeatPlaylist = True if self.playbackModeRepeatPlaylistAction.isChecked() else False
        randomTrack = True if self.playbackModeRandomAction.isChecked() else False
        randomPlaylist = True if self.playbackModeRandomPlaylistAction.isChecked() else False

        activeTrack = self.activeTrack
        activePlaylist = self.playlists.getPlaylistById(activeTrack.playlistId)
        selectedTrack = self.currentPlaylist.getSelectedTrack()
        if selectedTrack is None:
            selectedTrack = activePlaylist.getTrackByRow(0)

        if followCursor and activeTrack != selectedTrack:
            nextTrack = selectedTrack
        elif repeatTrack:
            nextTrack = activeTrack
        elif not randomTrack:
            nextTrack = activePlaylist.getTrackByRow(activeTrack.row + 1)
            if nextTrack is None and repeatPlaylist:
                nextTrack = activePlaylist.getTrackByRow(0)
        else:
            if randomPlaylist:
                nextPlaylist = self.playlists.getRandomPlaylist()
            else:
                nextPlaylist = activePlaylist
            nextTrack = nextPlaylist.getRandomTrack()
        return nextTrack

    def playNext(self):
        logging.debug("play next")
        self.updateTimeLabel(0)
        nextTrack = self.getNextTrack()
        self.playTrack(nextTrack)
        if nextTrack:
            self.playlists.setCurrentPlaylist(nextTrack.playlistId)
            if self.cursorFollowPlaybackAction.isChecked():
                self.currentPlaylist.setCurrentRow(nextTrack.row)
        else:
            self.stop()

    def enqueueNext(self):
        nextTrack = self.getNextTrack()
        self.enqueueTrack(nextTrack)
        if nextTrack:
            self.playlists.setCurrentPlaylist(nextTrack.playlistId)
            if self.cursorFollowPlaybackAction.isChecked():
                self.currentPlaylist.setCurrentRow(nextTrack.row)
        else:
            self.stop()

    def previous(self):
        self.currentPlaylist.previous()
        self.play()

    def setMute(self, checked):
        # FIXME: a bug in Qt doesn't restore the volume if set in this way. so we do it by hand as a workaournd
        ## self.audioOutput.setMuted(checked)
        logging.debug("setmute: %s" % str(checked))
        if checked:
            if self._qt_workaround_old_volume:
                self._qt_workaround_old_volume = self.audioOutput.volume()
            else:
                self._qt_workaround_old_volume = 1.
            self.audioOutput.setVolume(0)
            icon = QIcon(":/icons/volume-mute.svg")
        else:
            if self._qt_workaround_old_volume is None:
                self._qt_workaround_old_volume = 1.
            self.audioOutput.setVolume(self._qt_workaround_old_volume)
            icon = QIcon(":/icons/volume-med.svg")
        self.muteAction.setIcon(icon)
        self.toolBarVolumeSlider.findChild(QToolButton).setIcon(icon)
        self.toolBarVolumeSlider.findChild(QSlider).setEnabled(not checked)

    def updateTimeLabel(self, time):
        totalTime = self.mediaObject.totalTime()
        remainingTime = time - totalTime
        if self.timeLabelMode == AudioPhil.TIME_LABEL_ELAPSED:
            self.timeLabel.setText(millisecondsToStr(time))
        elif self.timeLabelMode == AudioPhil.TIME_LABEL_REMAINING:
            self.timeLabel.setText(millisecondsToStr(remainingTime))
        elif self.timeLabelMode == AudioPhil.TIME_LABEL_TOTAL:
            self.timeLabel.setText("{0}/{1}".format(millisecondsToStr(time), millisecondsToStr(totalTime)))
        else:
            logging.error("timeLabel in unknown mode: %d" % self.timeLabelMode)

    def changeTimeLabelMode(self):
        self.timeLabelMode = (self.timeLabelMode + 1) % 3
        self.updateTimeLabel(self.mediaObject.currentTime())

    def stateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            self.playNext()

    def addPlaylistItems(self):
        files = QFileDialog.getOpenFileNames(self, "Add files to playlist", ".")
        for f in files:
            self.currentPlaylist.addEntry(Track(f))

    def removePlaylistItems(self):
        self.currentPlaylist.removeSelectedItems()

    def config(self):
        formatTemplate = re.sub(r'%\(([^)]+)\)s', r'<\1>',
                                playlist.Playlist.formatTemplate)
        dlg = configDlg.ConfigDlg(self.mediaLibrary, formatTemplate)
        if dlg.exec_():
            # TODO: set mediaLibrary save location!
            for d in (str(dlg.directoriesListWidget.item(row).text().toUtf8())
                      for row in xrange(dlg.directoriesListWidget.count())):
                self.mediaLibrary.mediaLibraryModel.addDirectory(d)
            template = unicode(dlg.formatTemplateLineEdit.text().toUtf8(), "utf8")
            formatTemplate = re.sub(r'<([^>]+)>', r'%(\1)s', template)
            playlist.Playlist.formatTemplate = formatTemplate
            self.mediaLibrary.mediaLibraryModel.refresh()
            
    def closeEvent(self, event=None):
        self.saveState_()
        QMainWindow.close(self)
    close = closeEvent

    def onSavePlaylist(self):
        filename = str(QFileDialog.getSaveFileName(self, "Save Playlist to...", "", "All Files (*);;All known Playlists (*.xspf *.m3u *.pls);;XSPF (*.xspf);;M3U (*.m3u);;PLS (*.pls)", "XSPF (*.xspf)"))
        if filename:
            if filename.endswith(".xspf"):
                self.savePlaylistAsXSPF(self.currentPlaylist, filename)
            else:
                logging.error("unsupported file format selected: %s", filename)

    def savePlaylistAsXSPF(self, playlist, filename, prettyPrint=True):
        baseDir = os.path.dirname(filename)
        root = ET.Element("playlist")
        root.set("xmlns", "http://xspf.org/ns/0/")
        root.set("version", "1")
        playlistTitle = ET.SubElement(root, "title")
        playlistTitle.text = playlist.name
        playlistDate = ET.SubElement(root, "date")
        now = datetime.utcnow()
        playlistDate.text = now.strftime("%Y-%m-%dT%H:%M:%S")
        tracklist = ET.SubElement(root, "trackList")
        for track in playlist:
            trackElement = ET.SubElement(tracklist, "track")
            trackPath = ET.SubElement(trackElement, "location")
            if baseDir is None:
                path = track.path.strip()
            else:
                path = os.path.relpath(track.path.strip(), baseDir)
            trackPath.text = urllib.pathname2url(path)
            if track.tracktitle.strip():
                trackTitle = ET.SubElement(trackElement, "title")
                trackTitle.text = track.tracktitle.strip()
            if track.artist.strip():
                trackArtist = ET.SubElement(trackElement, "creator")
                trackArtist.text = track.artist.strip()
            if track.album.strip():
                trackAlbum = ET.SubElement(trackElement, "album")
                trackAlbum.text = track.album.strip()
            if track.tracknumber.strip():
                trackNumber = ET.SubElement(trackElement, "trackNum")
                trackNumber.text = track.tracknumber.strip()
            if track.duration:
                trackDuration = ET.SubElement(trackElement, "duration")
                trackDuration.text = str(track.duration)
        xspf = ET.tostring(root)
        if prettyPrint:
            xspf = xml.dom.minidom.parseString(xspf).toprettyxml("\t", "\n", "UTF-8")
        f = open(filename, "w")
        f.write(xspf)
        f.close()
        return xspf

    def onOpenPlaylists(self):
        filenames = QFileDialog.getOpenFileNames(self, "Open Playlist(s)...", "",
                                                 "All Files (*);;All known Playlists (*.xspf *.m3u *.pls);;.xspf (*.xspf);;.m3u (*.m3u);;.pls (*.pls)",
                                                 "All known Playlists (*.xspf *.m3u *.pls)")
        filenames = list(str(filename) for filename in filenames)
        for filename in filenames:
            if filename.endswith(".xspf"):
                self.loadPlaylistFromXSPF(filename)
            else:
                logging.error("playlist format not supported: %s", filename)
        
    def loadPlaylistFromXSPF(self, filename):
        f = open(filename, "r")
        xspf = f.read()
        f.close()
        baseDir = os.path.dirname(filename)
        logging.debug("loading xspf playlist: %s" % filename)
        xspfNS = "http://xspf.org/ns/0/"
        root = ET.fromstring(xspf)
        assert root.tag == "{{{namespace}}}playlist".format(namespace=xspfNS)
        assert root.get("version") == "1"
        playlistNameElement = root.find("{{{namespace}}}title".format(namespace=xspfNS))
        playlistName = playlistNameElement.text.strip()
        trackList = root.find("{{{namespace}}}trackList".format(namespace=xspfNS))
        trackIds = []
        for track in trackList.getiterator("{{{namespace}}}track".format(namespace=xspfNS)):
            location = track.find("{{{namespace}}}location".format(namespace=xspfNS))
            if location is None:
                logging.warning("Discarding track from playlist because it doesn't contain a location tag. fuzzy playlists aren't supported yet")
                continue
            location = urllib.url2pathname(location.text.strip())
            if baseDir:
                location = os.path.normpath(os.path.join(baseDir, location))
            matchingTrackIds = self.mediaLibrary.getTrackIdsByPath(location, False)
            if len(matchingTrackIds) < 1:
                log.warning('location "{location}" not found in mediaLibrary. external data not supported yet'.format(**locals()))
            elif len(matchingTrackIds) > 1:
                log.warning('location "{location}" not unique. following hits: {matchingTrackIds}'.format(**locals()))
            else:
                logging.debug("loading trackID: %s" % str(matchingTrackIds[0]))
                trackIds.append(matchingTrackIds[0])
        playlistId = self.playlists.addTracksToNewPlaylist(trackIds)
        self.playlists.renamePlaylist(playlistId, playlistName)

        
    def loadState(self):
        logging.debug("loading state file")
        f = bz2.BZ2File(self.configFile, "r")
        unpickler = pickle.Unpickler(f)
        settings = unpickler.load()
        f.close()
        if settings["magic_number"] != AudioPhil.MAGIC_NUMBER:
            logging.warning("Magic Number mismatch!")
            return
        if settings["file_version"] != AudioPhil.FILE_VERSION:
            logging.warning("File Version mismatch!")
            return
        self.restoreState(settings["state"])
        self.restoreGeometry(settings["geometry"])
        for widgetName, checked in settings["checkboxes"]:
            getattr(self, widgetName).setChecked(checked)
        self.setMute(self.muteAction.isChecked())
        self.timeLabelMode = settings["timeLabelMode"]
        self.updateTimeLabel(0)
        playlist.Playlist.formatTemplate = settings["formatTemplate"]
        self.databasePath = settings["databasePath"]
        if settings["currentPlaylistId"]:
            self.playlists.setCurrentPlaylist(settings["currentPlaylistId"])
        self.activeTrack = settings["activeTrack"]
        if self.activeTrack:
            self.currentPlaylist.setCurrentRow(self.activeTrack.row)

    def saveState_(self):
        checkboxes = []
        for checkbox in (widget for widget in self.__dict__.values() if isinstance(widget, QAction) and widget.isCheckable()):
            checkboxes.append((unicode(checkbox.objectName()), checkbox.isChecked()))
        settings = {"magic_number" : AudioPhil.MAGIC_NUMBER,
                    "file_version" : AudioPhil.FILE_VERSION,
                    "state" : self.saveState(),
                    "geometry" : self.saveGeometry(),
                    "checkboxes" : checkboxes,
                    "timeLabelMode" : self.timeLabelMode,
                    "formatTemplate" : playlist.Playlist.formatTemplate,
                    "databasePath" : self.databasePath,
                    "activeTrack" : self.activeTrack,
                    }
        if self.currentPlaylist:
            settings["currentPlaylistId"] = self.currentPlaylist.playlistId
        else:
            settings["currentPlaylistId"] = None
        # use pickle protocol 1 because protocol 2 somehow breaks the CallbackList
        f = bz2.BZ2File(self.configFile, "w")
        pickler = pickle.Pickler(f, 1)
        pickler.dump(settings)
        f.close()


def main(argv):
    app = QApplication(sys.argv)
    app.setApplicationName("AudioPhil")
    mainWindow = AudioPhil()
    mainWindow.show()
    app.exec_()
    
if __name__ == '__main__':
    main(sys.argv)
