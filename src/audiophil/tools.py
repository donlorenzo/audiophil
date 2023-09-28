# -*- coding: utf-8 -*-

# Copyright (c) 2008, Lorenz Quack
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
import errno
import logging

from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtCore import SIGNAL, QVariant
from PyQt4.QtCore import *
from PyQt4.QtSql import QSqlDatabase, QSqlField

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

def safeUtfDecode(s):
    try:
        return unicode(s, "utf8")
    except UnicodeDecodeError:
        logging.warning('Unicode decode error. cannot decode: "{0}"'.format(s))
        return u""

def millisecondsToStr(milliseconds):
    seconds = abs(milliseconds) // 1000
    sign = "" if milliseconds == abs(milliseconds) else "-"
    return "%s%d:%02d" % (sign, seconds // 60, seconds % 60)


def createAction(parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered(bool)"):
    action = QAction(text, parent)
    if icon is not None:
        action.setIcon(QIcon(icon))
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if slot is not None:
        action.connect(action, SIGNAL(signal), slot)
    action.setCheckable(checkable)
    parent.addAction(action)
    return action

def escapeSqlInput(string):
    # use the SQL driver's formatValue to escape malicious input
    tmp = QSqlField("dummy", QVariant.String)
    tmp.setValue(string)
    escapedString = QSqlDatabase.database().driver().formatValue(tmp)
    return escapedString


class CallbackList(list):
    def __new__(cls, *args, **kwargs):
        callback = kwargs["callback"]
        def makeWrappedMethod(func):
            def wrapper(self, *args, **kwargs):
                ret = func(self, *args, **kwargs)
                callback()
                return ret
            wrapper.func_name = func.__name__
            wrapper.func_doc = func.__doc__
            return wrapper
        # create a list of revision controlled methods
        methodList = ("__add__", "__delitem__", "__delslice__", "__iadd__", "__imul__", "__mul__", "__rmul__",
                      "__setitem__", "__setslice__", "append", "extend", "insert", "pop", "remove", "reverse", "sort")
        # wrap all listed methods
        for methodName in methodList:
            setattr(cls, methodName, makeWrappedMethod(getattr(list, methodName)))
        return list.__new__(cls, *args, **kwargs)

    def __init__(self, seq=[], **kwargs):
        super(CallbackList, self).__init__(seq)

