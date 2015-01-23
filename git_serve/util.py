#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
工具类
"""
import errno
import os
import socket
import fcntl
import struct


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


def create_hook_link(hook_path='', hook_name=[], repository_root=''):
    """所有的仓库创建钩子文件的链接"""

    repository_list = [os.path.isdir(os.path.join(repository_root, tmp))
                       for tmp in os.listdir(repository_root) if os.path.isdir(os.path.join(repository_root, tmp))]
    for folder_path in repository_list:
        folder_child = os.listdir(folder_path)
        for child in folder_child:
            child_path = os.path.join(folder_path, child)
            if child_path.endswith('.git'):
                for hook in hook_name:
                    hook_link_path = os.path.join(child_path, 'hooks', hook)
                    if not os.path.exists(hook_link_path):
                        os.symlink(os.path.join(hook_path, hook), hook_link_path)
            elif os.path.isdir(child_path):
                repository_list.append(child_path)


if __name__ == '__main__':
    print dir_name('mt6572/platform/build.git', 1)