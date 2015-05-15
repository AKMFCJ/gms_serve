#-*- coding:utf-8 -*-
from git_serve.utils import util

__author__ = 'changjie.fan'
"""

"""
import os
import sys
import logging
import shutil

logger = logging.getLogger('git-serve')


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
            if not os.path.exists(os.path.join(ssh, 'authorized_keys')):
                ssh_fp = open(os.path.join(ssh, 'authorized_keys'), 'w')
                ssh_fp.write("###git-serve Don't Edit\n")
                ssh_fp.close()

        #git-serve的配置文件和log目录
        git_serve_dir = os.path.expanduser('~/.git-serve')
        if not os.path.exists(git_serve_dir):
            util.mk_dir(git_serve_dir)
            util.mk_dir(os.path.join(git_serve_dir, 'logs'))
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

        #创建和更新指定仓库的hooks
        if len(sys.argv) > 1:
            src_path = os.path.expanduser('~/.git-serve/hooks')
            src_file_names = os.listdir(src_path)
            dst_path_list = []
            for git_path in sys.argv[1:]:
                if git_path.endswith('/'):
                    git_path = git_path[:-1]
                git_hook_path = os.path.join(git_path, 'hooks')
                if os.path.exists(git_path) and git_path.endswith('.git') and os.path.isdir(git_path) and \
                        os.path.exists(git_hook_path):
                    dst_path_list.append(git_hook_path)
                elif os.path.exists(git_path) and os.path.isdir(git_path):
                    git_dirs = [os.path.join(git_path, tmp) for tmp in os.listdir(git_path)
                                if os.path.isdir(os.path.join(git_path, tmp))]
                    for repo_path in git_dirs:
                        git_hook_path = os.path.join(repo_path, 'hooks')
                        if repo_path.endswith('.git') and os.path.exists(git_hook_path):
                            dst_path_list.append(git_hook_path)
                        else:
                            for tmp in os.listdir(repo_path):
                                tmp_path = os.path.join(repo_path, tmp)
                                if os.path.isdir(tmp_path):
                                    git_dirs.append(tmp_path)
                else:
                    print "%s is not git bare repository" % git_path
            if dst_path_list:
                Main.create_hook_link(src_file_names, src_path, dst_path_list)


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

    @staticmethod
    def create_hook_link(src_file_names=[], src_path='', dst_path_list=[]):
        for dst_path in dst_path_list:
            for src_file_name in src_file_names:
                src_file = os.path.join(src_path, src_file_name)
                dst_file = os.path.join(dst_path, src_file_name)
                if os.path.exists(dst_file):
                    if not os.path.samefile(src_file, dst_file):
                        os.remove(dst_file)
                        os.symlink(src_file, dst_file)
                else:
                    os.symlink(src_file, dst_file)
                os.chmod(dst_file, 0755)