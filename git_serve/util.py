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


def get_localhost_ip():
    """获取本机的Ip地址"""

    ip = os.popen("/sbin/ifconfig | grep 'inet addr' | awk '{print $2}'").read()
    return ip[ip.find(':')+1:ip.find('\n')]
