#!/usr/bin/env python
#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
引用级(项目级)的权限控制及提交规范的检查
"""

import sys
import os
from git_serve.access import have_reference_write_access

#从环境变量中读取中在git-serve/serve中设置的环境变量
#存储权限设置的数据库访问信息
db_host = os.getenv('db_host')
db_name = os.getenv('db_name')
db_username = os.getenv('db_username')
db_password = os.getenv('db_password')
db_charset = os.getenv('db_charset')

#当前进行的提交的用户名称
git_user = os.getenv('git_user')
#当前提交仓库的相对路径
repo_path = os.getenv('repo_path')

#git向update钩子传递的参数
#第一个参数是钩子的相对路径
#第二个参数是引用的名称
#第三个参数是旧的commit_id，新增的tag和branch此值为40个0
#第四个参数是当前最新的commit_id
reference_name = sys.argv[1]
old_rev = sys.argv[2]
new_rev = sys.argv[3]

print git_user
print repo_path
print sys.argv

if have_reference_write_access(db_host, db_name, db_username, db_password, db_charset, git_user, refname, repo_path):
    sys.exit(1)
else:
    print u"%s: 没有提交权限" % git_user
    sys.exit(1)