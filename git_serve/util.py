#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
工具类
"""
import errno
import os


def mk_dir(*a, **kw):
    try:
        os.mkdir(*a, **kw)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

