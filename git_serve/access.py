#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
从数据库中读取当前用户操作的仓库是否有对应的权限
"""
import logging
import os
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

    platform = util.dir_name(repo_path, 1)
    query_sql = \
        "select id from repository_wild where repository_wild='%s' and id in ( SELECT repository_wild_id from " \
        "repository_permission where repository_permission.id in (SELECT repositorypermission_id from " \
        "repository_permission_group where gitusergroup_id in(select id from repository_user_group where name='All')))"
    logger.info(query_sql)
    if db_connect.execute_query(query_sql):
        return True
    else:
        query_sql = \
            "select username from auth_user where auth_user.username='%s' and auth_user.id " \
            "in(select git_user.user_id from repository_user git_user where git_user.id in" \
            "(select member.gituser_id from repository_permission_member member where member.repositorypermission_id " \
            "in(select repository_permission.id from repository_permission where repository_permission.permission in " \
            "('R', 'RW', 'RW+') and repository_permission.repository_wild_id in(select wild.id from repository_wild wild " \
            "JOIN repository_server serve on wild.repository_server_id=serve.id where serve.ip='%s'and " \
            "wild.repository_wild LIKE '%s%%'))))" % (user, cfg.get('localhost', 'ip'), platform)
        logger.info(query_sql)

        if db_connect.execute_query(query_sql):
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