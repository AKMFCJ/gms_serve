#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
ssh authorized_keys的初始化
.git-serve配置目录的初始化
所有仓库中.git/hooks/update的初始化
"""
import os
import logging
import util
import ConfigParser


logger = logging.getLogger('git-serve')


class Main(object):
    @staticmethod
    def run():
        os.umask(0022)
        repositories = os.path.expanduser('~/repositories')
        if not os.path.exists(repositories):
            util.mk_dir(repositories)

        ssh = os.path.expanduser('~/.ssh')
        if not os.path.exists(ssh):
            util.mk_dir(os.path.expanduser('~/.ssh'), 0700)
        else:
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

        git_serve_dir = os.path.expanduser('~/.git-serve')
        if not os.path.exists(git_serve_dir):
            util.mk_dir(git_serve_dir)
            util.mk_dir(os.path.join(git_serve_dir, 'logs'))
            Main.create_git_serve_conf(git_serve_dir)
        else:
            git_serve_conf = os.path.join(git_serve_dir, 'git-serve.conf')
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

    @staticmethod
    def create_git_serve_conf(git_serve_dir):
            rfp = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    'git_serve/git-serve.conf'), 'r')
            wfp = open(os.path.join(git_serve_dir, 'git-serve.conf'), 'w')
            for line in rfp.readlines():
                wfp.write(line)
            wfp.write('[localhost]\n')
            wfp.write('ip=%s\n' % util.get_localhost_ip("eth0"))
            wfp.close()
            rfp.close()