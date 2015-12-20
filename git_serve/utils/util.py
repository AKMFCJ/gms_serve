#-*- coding:utf-8 -*-
__author__ = 'changjie.fan'
"""
工具类
"""
import errno
import os
import socket
import fcntl
import struct
import time


def get_current_time(format_str='%Y-%m-%d %H:%M:%S'):
    """获取当前时间"""
    return time.strftime(format_str, time.localtime())


def mk_dir(*a, **kw):
    try:
        os.mkdir(*a, **kw)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise


def get_localhost_ip(ifname):
    """获取本机的Ip地址"""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def dir_name(path, hierarchy):
    """返回指定层级的目录路径"""

    dirs = path.split('/')
    result_path = ''
    if len(dirs) <= hierarchy:
        return path
    else:
        for i in range(hierarchy):
            if i == 0:
                result_path = dirs[0]
            else:
                result_path = os.path.join(result_path, dirs[i])

    return result_path


def create_hook_link(hook_path, hook_name, repository_root):
    """所有的仓库创建钩子文件的链接"""

    for root_path, dirs, files in os.walk(repository_root):
        for folder_name in dirs:
            if folder_name.endswith('.git') and dir_name != '.git':
                child_hook_path = os.path.join(root_path, folder_name, 'hooks')

                old_hooks = os.listdir(child_hook_path)
                for old_hook_name in old_hooks:
                    old_hook_path = os.path.join(child_hook_path, old_hook_name)
                    if os.path.islink(old_hook_path):
                        try:
                            os.remove(old_hook_path)
                        except IOError:
                            pass
                for hook in hook_name:
                    hook_link_path = os.path.join(child_hook_path, hook)
                    if not os.path.exists(hook_link_path):
                        os.symlink(os.path.join(hook_path, hook), hook_link_path)


def create_repository_hook_link(repo_path=''):
    """"创建单个仓库的hook连接文件"""

    hook_path = os.path.expanduser('~/.git-serve/hooks')
    for hook_name in os.listdir(hook_path):
        os.symlink(os.path.join(hook_path, hook_name), os.path.join(repo_path, 'hooks', hook_name))

