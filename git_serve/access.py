#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
从数据库中读取当前用户操作的仓库是否有对应的权限
"""
import logging
from MySQLdb import connect

logger = logging.getLogger('git-serve')


class DBConnect():
    def __init__(self, host, db, user, password, charset):
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


def have_read_access(cfg, user, repo_path):
    """
    判断是否有读权限
    1. 判断仓库是否设置了R=@All的权限，所有可读
    2. 获取当前用户的所有可读权限的仓库
    """

    db_connect = DBConnect(cfg.get('database', 'hostname').strip("'"),
                           cfg.get('database', 'db_name').strip("'"),
                           cfg.get('database', 'username').strip("'"),
                           cfg.get('database', 'password').strip("'"),
                           cfg.get('database', 'charset').strip("'"))

    query_sql = \
        "select username from auth_user where auth_user.username='%s' and auth_user.id " \
        "in(select git_user.user_id from repository_user git_user where git_user.id in" \
        "(select member.gituser_id from repository_permission_member member where member.repositorypermission_id " \
        "in(select repository_permission.id from repository_permission where repository_permission.permission='R' " \
        "and repository_permission.repository_wild_id " \
        "in(select wild.id from repository_wild wild JOIN repository_server serve on wild.repository_server_id=serve.id" \
        "where serve.ip='%s' and wild.repository_wild LIKE '%s%%'))))" % (user, cfg.get('localhost', 'ip'), repo_path)
    logger.info(query_sql)
    repository_wild = [tmp[0]for tmp in db_connect.execute_query(query_sql)]
    logger.warning(repository_wild)
    logging.warning(repo_path)
    for tmp in repository_wild:
        if repo_path.startswith(tmp) or repo_path == tmp:
            return True
    return False


def have_write_access(cfg, user, repo_path):
    """判断是否有仓库的写权限"""

    db_connect = DBConnect(cfg.get('database', 'hostname').strip("'"),
                           cfg.get('database', 'db_name').strip("'"),
                           cfg.get('database', 'username').strip("'"),
                           cfg.get('database', 'password').strip("'"),
                           cfg.get('database', 'charset').strip("'"))

    query_sql = "select wild.repository_wild from repository_wild as wild join repository_permission as repo " \
                "on wild.id=repo.repository_wild_id JOIN repository_permission_member as member " \
                "on member.repositorypermission_id = repo.id JOIN repository_user as git_user " \
                "on member.gituser_id=git_user.id where git_user.name='%s' and repo.permission='RW'" % user

    repository_wild = [tmp[0]for tmp in db_connect.execute_query(query_sql)]
    logger.warning(repository_wild)
    logging.warning(repo_path)
    for tmp in repository_wild:
        if repo_path.startswith(tmp) or repo_path == tmp:
            return True
    #return False
    return True


def have_reference_write_access(db_host, db_name, db_username, db_password, db_charset,
                                user, reference_name, repo_path):
    """判断是否有仓库具体引用的写权限"""

    db_connect = DBConnect(db_host, db_name, db_username, db_password, db_charset)

    query_sql = "select wild.repository_wild from repository_wild as wild join repository_permission as repo " \
                "on wild.id=repo.repository_wild_id JOIN repository_permission_member as member " \
                "on member.repositorypermission_id = repo.id JOIN repository_user as git_user " \
                "on member.gituser_id=git_user.id where git_user.name='%s' and repo.permission='RW'" % user

    repository_wild = [tmp[0]for tmp in db_connect.execute_query(query_sql)]
    logger.warning(repository_wild)
    logging.warning(repo_path)
    for tmp in repository_wild:
        if repo_path.startswith(tmp) or repo_path == tmp:
            return True
    return False