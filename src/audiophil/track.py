# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lorenz Quack
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

import logging
try:
    import copyreg
except ImportError:
    # Python 2 compability
    import copy_reg as copyreg

import mutagen

from tools import millisecondsToStr


class Track(object):
    def __init__(self, path=None):
        super(Track, self).__init__()
        self.__dict__["tags"] = {"artist" : "<unknown>",
                                 "album" : "<unknown>",
                                 "tracktitle" : "<unknown>",
                                 "tracknumber" : "",
                                 "duration" : 0,
                                 }
        self.path = path
        self.dbId = None
        self.playlistId = None
        self.row = None
        self.loaded = False

    id = property(lambda self: self.dbId)
    durationString = property(lambda self: millisecondsToStr(self.duration))
    
    def __eq__(self, other):
        if not isinstance(other, Track):
            return False
        if (self.playlistId != other.playlistId or
            self.row != other.row):
            return False
        if len(self.tags) != len(other.tags):
            return False
        for tag, val in self.tags.items():
            if val != other.tags[tag]:
                return False
        return True
    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "Track: row {self.row} from playlist {self.playlistId}".format(**locals())

    def __getattr__(self, attr):
#        print attr
        return self.tags[attr]

    def __setattr__(self, attr, val):
        if attr in self.tags:
            self.tags[attr] = val
        else:
            super(Track, self).__setattr__(attr, val)
            
    def __getitem__(self, key):
        if key == "durationString":
            return self.durationString
        return self.tags[key]

    def __setitem__(self, key, value):
        if key == "durationString":
            raise AttributeError("can't set attribute")
        self.tags[key] = value

    @classmethod
    def fromSqlRecord(cls, sqlRecord):
        track = cls(str(sqlRecord.value("path").toByteArray()))
        track.dbId, success = sqlRecord.value("id").toInt()
        if not success:
            print("error converting to int", sqlRecord.value("id").toString())
        track.duration = long(sqlRecord.value("duration").toDouble()[0])
        track.artist = unicode(sqlRecord.value("artist").toString().toUtf8(), "utf-8")
        track.album = unicode(sqlRecord.value("album").toString().toUtf8(), "utf-8")
        track.tracktitle = unicode(sqlRecord.value("tracktitle").toString().toUtf8(), "utf-8")
        track.tracknumber = unicode(sqlRecord.value("tracknumber").toString().toUtf8(), "utf-8")
        track.loaded = sqlRecord.value("loaded").toBool()
        return track

    @classmethod
    def fromFile(cls, filename):
        track = cls(filename)
        # try reading metadata
        track.loadMetadata()
        return track

    def loadMetadata(self):
        try:
            fileType = mutagen.File(self.path, easy=True)
        except IOError:
            return            
        if fileType is None:
            return
        def loadString(tag):
            try:
                return unicode(fileType[tag][0])
            except KeyError:
                return u""
        def loadTracknumber():
            try:
                tracknumberString = unicode(fileType[u"tracknumber"][0])
            except KeyError:
                return u""
            try:
                return u"%02d" % long(tracknumberString)
            except ValueError:
                if "/" in tracknumberString:
                    return u"%02d" % long(tracknumberString.split("/")[0])
                else:
                    return u""
        def loadDuration():
            try:
                return long(fileType.info.length * 1000)
            except AttributeError:
                return -1
            
        self.artist = loadString(u"artist")
        self.album = loadString(u"album")
        self.tracktitle = loadString(u"title")
        self.tracknumber = loadTracknumber()
        self.duration = loadDuration()
        self.loaded = True



def _pickleTrack(track):
    return _unpickleTrack, (track.__dict__,)

def _unpickleTrack(*args):
    track = Track()
    track.__dict__.update(args[0])
    return track
copyreg.pickle(Track, _pickleTrack, _unpickleTrack)

