#-*- coding:utf-8 -*-
from git_serve.utils import util

__author__ = 'changjie.fan'
"""
ssh authorized_keys的初始化
初始化
[repository]
root_path下的所有仓库的hooks文件
"""
import os
import ConfigParser
import shutil
import sys


from git_serve.utils.util import create_hook_link, get_current_time
from git_serve.utils.Mylogging import logger


class Main(object):
    @staticmethod
    def run():

        # 读取git-serve配置文件
        conf_file = os.path.expanduser('~/.git-serve/conf/git-serve.conf')
        cfg = ConfigParser.RawConfigParser()
        try:
            cfg.read(conf_file)
        except IOError, e:
            print "Can't read %s" % conf_file
            sys.exit(1)

        repositories_path = cfg.get('repository', 'root_path')
        if not os.path.exists(repositories_path):
            os.makedirs(repositories_path)

        # 初始化ssh认证
        ssh = os.path.expanduser('~/.ssh')
        if not os.path.exists(ssh):
            util.mk_dir(os.path.expanduser('~/.ssh'), 0700)
        else:
            logger.info('init')
            if os.path.exists(os.path.join(ssh, 'authorized_keys')):
                ssh_fp = open(os.path.join(ssh, 'authorized_keys'), 'r')
                if not ssh_fp.readline().startswith("###git-serve Don't Edit"):
                    ssh_fp.close()
                    os.rename(os.path.join(ssh, 'authorized_keys'),
                              os.path.join(ssh, 'authorized_keys_old_%s' % get_current_time("%Y-%m-%d")))
                    ssh_fp = open(os.path.join(ssh, 'authorized_keys'), 'w')
                    ssh_fp.write("###git-serve Don't Edit\n")
                    ssh_fp.close()
            else:
                ssh_fp = open(os.path.join(ssh, 'authorized_keys'), 'w')
                ssh_fp.write("###git-serve Don't Edit\n")
                ssh_fp.close()

        # 所有的钩子
        hooks_src_path = os.path.expanduser('~/.git-serve/hooks')
        src_file_names = os.listdir(hooks_src_path)

        # 为所有的仓库的构建创建连接文件
        create_hook_link(hooks_src_path, src_file_names, repositories_path)
