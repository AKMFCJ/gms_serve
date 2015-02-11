#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
从数据库中读取当前用户操作的仓库是否有对应的权限
"""
import logging
import time
from git_serve.utils.util import DBConnect

logger = logging.getLogger('git-serve')


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
    db_connect.cursor.callproc('repository_read_access', (user, repo_path, cfg.get('localhost', 'ip'), '@my_user_id'))
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
    db_connect.cursor.callproc('repository_write_access', (user, repo_path, cfg.get('localhost', 'ip'), '@my_user_id'))
    data = db_connect.cursor.fetchall()
    logger.info(time.time()-start)
    db_connect.db_close()
    if data[0][0]:
        return True, ''
    else:
        return False, user + ":" + repo_path + "没有仓库的提交权限"


def have_reference_write_access(cfg, git_user, repo_path, reference_name):
    """判断是否有仓库具体引用的写权限"""

    db_connect = DBConnect(cfg.get('database', 'hostname').strip("'"),
                           cfg.get('database', 'db_name').strip("'"),
                           cfg.get('database', 'username').strip("'"),
                           cfg.get('database', 'password').strip("'"),
                           cfg.get('database', 'charset').strip("'"))

    start = time.time()
    #通过存储过程判断是否有权限
    db_connect.cursor.callproc('repository_write_reference_access', (git_user, reference_name, repo_path,
                                                                     cfg.get('localhost', 'ip'), '@my_user_id'))
    data = db_connect.cursor.fetchall()
    logger.info(time.time()-start)
    db_connect.db_close()
    if data[0][0]:
        return True, ''
    else:
        return False, git_user + ":" + repo_path + ":" + reference_name+"没有项目的提交权限"