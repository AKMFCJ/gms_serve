#-*- coding:utf-8 -*-
from git_serve.utils import util

__author__ = 'changjie.fan'
"""
ssh authorized_keys的初始化
.git-serve配置目录的初始化
所有仓库中.git/hooks/update的初始化
"""
import os
import logging
import ConfigParser
import shutil

from git_serve.utils.util import create_hook_link


class Main(object):
    @staticmethod
    def run():
        #创建repository的根目录
        os.umask(0022)
        repositories = os.path.expanduser('~/repositories')
        if not os.path.exists(repositories):
            util.mk_dir(repositories)

        #初始化ssh认证
        ssh = os.path.expanduser('~/.ssh')
        if not os.path.exists(ssh):
            util.mk_dir(os.path.expanduser('~/.ssh'), 0700)
        else:
            logger.info('init')
            if os.path.exists(os.path.join(ssh, 'authorized_keys')):
                ssh_fp = open(os.path.join(ssh, 'authorized_keys'), 'r')
                if not ssh_fp.readline().startswith("###git-serve Don't Edit"):
                    ssh_fp.close()
                    os.rename(os.path.join(ssh, 'authorized_keys'), os.path.join(ssh, 'authorized_keys_old'))
                    ssh_fp = open(os.path.join(ssh, 'authorized_keys'), 'w')
                    ssh_fp.write("###git-serve Don't Edit\n")
                    ssh_fp.close()
            else:
                ssh_fp = open(os.path.join(ssh, 'authorized_keys'), 'w')
                ssh_fp.write("###git-serve Don't Edit\n")
                ssh_fp.close()

        #git-serve的配置文件和log目录
        git_serve_dir = os.path.expanduser('~/.git-serve')
        if not os.path.exists(git_serve_dir):
            util.mk_dir(git_serve_dir)
            util.mk_dir(os.path.join(git_serve_dir, 'logs'))
            Main.create_git_serve_conf(git_serve_dir)
        else:
            git_serve_conf = os.path.join(git_serve_dir, 'conf', 'git-serve.conf')
            if os.path.exists(git_serve_conf):
                cfg = ConfigParser.RawConfigParser()
                try:
                    conf_file = file(git_serve_conf)
                except (IOError, OSError), e:
                    pass
                try:
                    cfg.readfp(conf_file)
                finally:
                    conf_file.close()
                localhost_ip = util.get_localhost_ip('eth0')
                if cfg.get('localhost', 'ip') != localhost_ip:
                    cfg.set('localhost', 'ip', localhost_ip)
                    cfg.write(open(git_serve_conf, 'w'))
            else:
                Main.create_git_serve_conf(git_serve_dir)

        #拷贝hooks目录
        src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'git_serve/hooks')
        src_file_names = os.listdir(src_path)
        dst_path = os.path.expanduser('~/.git-serve/hooks')
        if os.path.exists(dst_path):
            for src_file_name in src_file_names:
                src_file = os.path.join(src_path, src_file_name)
                dst_file = os.path.join(dst_path, src_file_name)
                if os.path.exists(dst_file):
                    if not os.path.samefile(src_file, dst_file):
                        shutil.copy(src_file, dst_file)
                else:
                    shutil.copy(src_file, dst_file)
                os.chmod(dst_file, 0755)
        else:
            util.mk_dir(dst_path, 0755)
            for file_name in src_file_names:
                shutil.copy(os.path.join(src_path, file_name), dst_path)
                os.chmod(os.path.join(dst_path, file_name), 0755)
        create_hook_link(dst_path, src_file_names, repositories)

    @staticmethod
    def create_git_serve_conf(git_serve_dir):
            if not os.path.exists(os.path.join(git_serve_dir, 'conf')):
                os.mkdir(os.path.join(git_serve_dir, 'conf'))
            rfp = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    'git_serve/conf/git-serve.conf'), 'r')
            wfp = open(os.path.join(git_serve_dir, 'conf', 'git-serve.conf'), 'w')
            for line in rfp.readlines():
                wfp.write(line)
            wfp.write('[localhost]\n')
            wfp.write('ip=%s\n' % util.get_localhost_ip("eth0"))
            wfp.close()
            rfp.close()