#-*- coding:utf-8 -*-
__author__ = 'changjie.fan'
"""
从数据库中读取当前用户操作的仓库是否有对应的权限
"""
import time
import os
from simplejson import loads as json_loads


def read_permission_config(db_connect, cfg, user, repo_path):
    """
    读取用户的对仓库的读写权限

    1. 获取用户所属的Git用户组
    2. 获取要克隆仓库的权限设置
    3. 判断用户组是否在仓库的读权限中
    """

    start = time.time()

    permission_config = []
    return True, permission_config

