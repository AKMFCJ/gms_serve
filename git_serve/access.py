#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
从数据库中读取当前用户操作的仓库是否有对应的权限
"""
from MySQLdb import connect


class DBConnect():
    def __init__(self, host, db, username, password, charset='utf8'):
        self.host = host
        self.db = db
        self.user = username
        self.passwd = password
        self.charset = charset
        self.conn = None
        self.cursor = None

    def db_conect(self):
        """连接权限配置的数据库"""
        self.conn = connect(host=self.host, db=self.db, user=self.user, passwd=self.passwd, charset=self.charset)
        self.cursor = self.conn.cursor()

    def db_close(self):
        """关闭数据库连接"""

        self.cursor.close()
        self.conn.close()

    def execute_query(self, sql=''):
        """执行查询语句"""

        return self.cursor.execute(sql)


def have_read_access(cfg, user, path):
    """判断是否有读权限"""

    db_connect = DBConnect(cfg.get('database', 'hostname'), cfg.get('database', 'db_name'),
                           cfg.get('database', 'username'), cfg.get('database', 'password'),
                           cfg.get('database', 'charset'))
    return False


def have_write_access(cfg, user, path):
    """判断是否有写权限"""

    db_connect = DBConnect(cfg.get('database', 'hostname'), cfg.get('database', 'db_name'),
                           cfg.get('database', 'username'), cfg.get('database', 'password'),
                           cfg.get('database', 'charset'))
    return False


