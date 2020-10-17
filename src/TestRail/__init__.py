# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from TRLogging import log
from typing import List
from collections import namedtuple
import logging
import sys
import os
from .api import *


Vector = List[str]

def objectBuilder(*args: Vector, **kwargs) -> namedtuple:
    wsdata = namedtuple("WSData", args)
    return wsdata(**kwargs)

TRACE = 5


class CustomLogging(logging.Logger):
    """A custom logger that incorporates trace


    Extends:
        log.Logger

    Variables:
        TRACE {number} -- [description]

    """
    def trace(self, msg, *args, **kwargs):
        #self.log(TRACE, msg, *args, **kwargs)
        fn, lno, func = self.__findCaller()
        exc_info = sys.exc_info()
        record = self.makeRecord(self.name, TRACE, fn, lno, msg, args, exc_info, func)
        self.handle(record)

    def __findCaller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        _srcfile = __file__
        if hasattr(sys, 'frozen'): #support for py2exe
            _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
        elif __file__[-4:].lower() in ['.pyc', '.pyo']:
            _srcfile = __file__[:-4] + '.py'
        else:
            _srcfile = __file__
        _srcfile = os.path.normcase(_srcfile)

        def currentframe():
            """Return the frame object for the caller's stack frame."""
            try:
                raise Exception
            except:
                return sys.exc_info()[2].tb_frame.f_back.f_back
        f = currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv


def loggingSetup(logfilepath, loglevel=TRACE):
    from logging.handlers import RotatingFileHandler
    logformat = "%(asctime)-15s %(levelname)-8s: %(threadName)-8s: %(module)-12s: %(funcName)-15s: %(lineno)-4s %(message)s"
    lg = logging.getLogger()
    handler = RotatingFileHandler(logfilepath, 'a', 10000000, 100)
    formatter = logging.Formatter(logformat)
    handler.setFormatter(formatter)
    lg.addHandler(handler)
    lg.setLevel(loglevel)
    logging.setLoggerClass(CustomLogging)
    logging.addLevelName(TRACE, "TRACE")
    logging.captureWarnings(True)
    return logging.getLogger("TestRailLib")


log = loggingSetup("TestRailLib.log")
