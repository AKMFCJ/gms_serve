#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
从数据库中读取当前用户操作的仓库是否有对应的权限
"""
import logging
import time
from MySQLdb import connect

import util

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
    1. 判断仓库权限是否有All组
    2. 判断仓库权限R/RW/RW+权限组的成员中是否有当前用户
    都是通过仓库根路径的权限控制的
    """

    db_connect = DBConnect(cfg.get('database', 'hostname').strip("'"),
                           cfg.get('database', 'db_name').strip("'"),
                           cfg.get('database', 'username').strip("'"),
                           cfg.get('database', 'password').strip("'"),
                           cfg.get('database', 'charset').strip("'"))
    start = time.time()
    #通过存储过程判断是否有权限
    db_connect.cursor.callproc('repository_read_access', (user, repo_path, cfg.get('localhost', 'ip')))
    data = db_connect.cursor.fetchall()
    logger.info(time.time()-start)
    db_connect.db_close()
    if data[0][0]:
        return True
    else:
        return False


def have_write_access(cfg, user, repo_path):
    """判断是否有仓库的写权限"""

    db_connect = DBConnect(cfg.get('database', 'hostname').strip("'"),
                           cfg.get('database', 'db_name').strip("'"),
                           cfg.get('database', 'username').strip("'"),
                           cfg.get('database', 'password').strip("'"),
                           cfg.get('database', 'charset').strip("'"))

    start = time.time()
    #通过存储过程判断是否有权限
    db_connect.cursor.callproc('repository_write_access', (user, repo_path, cfg.get('localhost', 'ip')))
    data = db_connect.cursor.fetchall()
    logger.info(time.time()-start)
    db_connect.db_close()
    if data[0][0]:
        return True
    else:
        return False


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