#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'changjie.fan'

"""
当前用户对当前仓库的当前引用是否有提交权限
"""
import sys
import os
from simplejson import loads as json_loads

reload(sys)
sys.setdefaultencoding('utf-8')


def check_write_permission():
    """检查提交权限"""

    current_user_name = os.getenv('git_user')
    permission_config = json_loads(os.getenv('permission_config'))

    # 当前push的分支或Tag名称
    reference_name = ''
    for line in sys.stdin:
        reference_name = line.strip()
    if reference_name:
        reference_name = reference_name.split()[2]
    else:
        print u'pre-receive execute Failure'
        sys.exit(1)

    print current_user_name, permission_config, reference_name


if __name__ == '__main__':
    check_write_permission()
