#!/usr/bin/env python
#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
引用级(项目级)的权限控制及提交规范的检查
"""

import sys
import os
from git_serve.access import have_write_access

cfg = os.getenv('cfg')
git_user = os.getenv('git_user')
repo_path = os.getenv('repo_path')
refname = sys.argv[0]
oldrev = sys.argv[1]
newrev = sys.argv[2]

print git_user
print repo_path
print sys.argv

if have_write_access(cfg, git_user, refname, repo_path):
    sys.exit(1)
else:
    print u"%s: 没有提交权限" % git_user
    sys.exit(1)