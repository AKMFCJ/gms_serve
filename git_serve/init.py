#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'

import os
import logging

import util

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
                ssh_fp = open(os.path.exists(os.path.join(ssh, 'authorized_keys')), 'r')
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
            rfp = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    'git_serve/git-serve.conf'))
            wfp = open(os.path.join(git_serve_dir, 'git-serve.conf'), 'w')
            for line in rfp.readline():
                wfp.write(line+'\n')
            wfp.close()
            rfp.close()