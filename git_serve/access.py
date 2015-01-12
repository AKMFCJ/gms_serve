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


def have_read_access(cfg, user, repo_path):
    """
    判断是否有读权限
    1. 判断仓库是否设置了R=@All的权限，所有可读
    2. 获取当前用户的所有可读权限的仓库
    """

    db_connect = DBConnect(cfg.get('database', 'hostname'), cfg.get('database', 'db_name'),
                           cfg.get('database', 'username'), cfg.get('database', 'password'),
                           cfg.get('database', 'charset'))
    query_sql = "select wild.repository_wild from repository_wild as wild join repository_permission as repo " \
                "on wild.id=repo.repository_wild_id JOIN repository_permission_member as member " \
                "on member.repositorypermission_id = repo.id JOIN repository_user as git_user " \
                "on member.gituser_id=git_user.id where git_user.name='%s'" % user
    repository_wild = db_connect.execute_query(query_sql).fetchall()
    for tmp in repository_wild:
        if repo_path.startswith(tmp) or repo_path == tmp:
            return True
    return False


def have_write_access(cfg, user, path, reference_name):
    """判断是否有写权限"""

    db_connect = DBConnect(cfg.get('database', 'hostname'), cfg.get('database', 'db_name'),
                           cfg.get('database', 'username'), cfg.get('database', 'password'),
                           cfg.get('database', 'charset'))
    return False


