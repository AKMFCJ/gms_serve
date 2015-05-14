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
import time

from MySQLdb import connect


def get_current_time(format_str='%Y-%m-%d %H:%M:%S'):
    """获取当前时间"""
    return time.strftime(format_str, time.localtime())


class DBConnect():
    def __init__(self, host, db, user, password, charset='utf8'):
        self.conn = connect(host=host, db=db, user=user, passwd=password, charset=charset)
        self.cursor = self.conn.cursor()

    def db_close(self):
        """关闭数据库连接"""

        self.cursor.close()
        self.conn.close()

    def execute_query(self, sql=''):
        """执行查询语句"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def execute_many(self, insert_sql, values=[]):
        """执行批量插入语句"""
        self.cursor.executemany(insert_sql, values)
        self.conn.commit()


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

    repository_list = [os.path.join(repository_root, tmp)
                       for tmp in os.listdir(repository_root) if os.path.isdir(os.path.join(repository_root, tmp))]
    for folder_path in repository_list:
        folder_child = os.listdir(folder_path)
        for child in folder_child:
            child_path = os.path.join(folder_path, child)
            if child_path.endswith('.git'):
                child_hook_path = os.path.join(child_path, 'hooks')
                old_hooks = os.listdir(child_hook_path)
                for old_hook_name in old_hooks:
                    old_hook_path = os.path.join(child_hook_path, old_hook_name)
                    if os.path.islink(old_hook_path):
                        try:
                            os.remove(old_hook_path)
                        except IOError:
                            pass
                for hook in hook_name:
                    hook_link_path = os.path.join(child_path, 'hooks', hook)
                    if not os.path.exists(hook_link_path):
                        os.symlink(os.path.join(hook_path, hook), hook_link_path)
            elif os.path.isdir(child_path):
                repository_list.append(child_path)


def create_repository_hook_link(repo_path=''):
    """"创建单个仓库的hook连接文件"""

    hook_path = os.path.expanduser('~/.git-serve/hooks')
    for hook_name in os.listdir(hook_path):
        os.symlink(os.path.join(hook_path, hook_name), os.path.join(repo_path, 'hooks', hook_name))


if __name__ == '__main__':
    db_connect = DBConnect('192.168.33.106', 'tup', 'root', 'root')
    insert_sql = "insert into notice_repo_error_issue_key (repo_path, reference_name, committer, push_date, message) " \
                 "values(%s, %s, %s, %s, %s)"
    db_connect.execute_many(insert_sql, [('/home/git/repositories/qc8909/platform/build.git', 'refs/heads/master', 'changjie.fan', '2015-02-09 17:26:00', u'/home/git/repositories/qc8909/platform/build.git\nrefs/heads/master\n\\changjie.fan\\2015-02-09 17:26:00\n851b4a12389661c50ed96c912ddb8be4c89473ee\t<REQ><SCM-1><test access>\n\tSCM-1\n9c25e65d67e090a86829e1e0a13c6d7406457b31\t<REQ><SCM-1><test access>\n\tSCM-1\n1bf4febdecae05eda90afdcab48792f351a61bbd\t<REQ><SCM-1><test access>\n\tSCM-1')])
    db_connect.db_close()