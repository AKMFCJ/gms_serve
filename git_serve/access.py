#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
从数据库中读取当前用户操作的仓库是否有对应的权限
"""
import logging
import time
import os
from simplejson import loads as json_loads

from git_serve.utils.util import DBConnect

logger = logging.getLogger('git-serve')


def have_read_access(cfg, user, repo_path):
    """
    判断是否有读权限
    1. 获取用户所属的Git用户组
    2. 获取要克隆仓库的权限设置
    3. 判断用户组是否在仓库的读权限中
    """

    db_connect = DBConnect(cfg.get('database', 'hostname').strip("'"),
                           cfg.get('database', 'db_name').strip("'"),
                           cfg.get('database', 'username').strip("'"),
                           cfg.get('database', 'password').strip("'"),
                           cfg.get('database', 'charset').strip("'"))
    start = time.time()
    logger.info(repo_path)
    logger.info(cfg.get('localhost', 'ip').strip())
    logger.info(user)
    group_sql = "SELECT group_server.gitusergroup_id,repo_server.id, repo_server.backup_dir_path FROM " \
                "repository_user_group_repository_server AS group_server JOIN repository_server AS repo_server " \
                "ON group_server.repositoryserver_id=repo_server.id AND repo_server.ip='%s' AND " \
                "group_server.gitusergroup_id IN(SELECT gitusergroup_id FROM repository_user_git_group WHERE " \
                "gituser_id IN(SELECT id FROM repository_user WHERE user_id " \
                "IN (SELECT id FROM auth_user WHERE username='%s')))" % (cfg.get('localhost', 'ip').strip(), user)
    logger.info(group_sql)

    cursor = db_connect.cursor
    cursor.execute(group_sql)
    group_query_data = [(tmp[0], tmp[1], tmp[2]) for tmp in cursor.fetchall()]
    if not group_query_data or len(group_query_data) == 0:
        return False

    backup_dir_path = group_query_data[0][2]
    repository_server_id = group_query_data[0][1]
    repo_path = os.path.join(backup_dir_path, repo_path+".git")

    permission_sql = "SELECT permission FROM repository_permission WHERE id IN(SELECT permission_id FROM " \
                     "repository_repository WHERE path='%s' AND " \
                     "repository_server_id=%s);" % (repo_path, repository_server_id)
    logger.info(backup_dir_path)
    logger.info(repo_path)
    logger.info(permission_sql)
    cursor.execute(permission_sql)
    permission_data = cursor.fetchone()
    
    if not permission_data or len(permission_data) == 0:
        return False

    permission = json_loads(permission_data[0])
    for group in group_query_data:
        logger.info(permission["read"])
        logger.info(group[0])
        if str(group[0]) in permission["read"]:
            logger.info(time.time()-start)
            return True

    logger.info(time.time()-start)
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
        return False, user + ":" + repo_path + "no repository PUSH permission"


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
        return False, git_user + ":" + repo_path + ":" + reference_name+"no TAG/BRANCH PUSH permission"