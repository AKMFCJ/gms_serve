#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import shutil
import commands
from setuptools import setup, find_packages


def subdir_contents(path_list):
    all_file = []
    for path in path_list:
        for root_path, dirs , files in os.walk(path):
            for file_name in files:
                all_file.append(os.path.join(root_path, file_name))
    print all_file
    return all_file


def _setup():
    setup(
        name="git-serve",
        version="0.1",
        packages=find_packages(),
        package_data={
            '': ['*.conf'],
            '': ['*.sh'],
            'git_serve': subdir_contents(['git_serve/hooks', 'git_serve/conf']),
        },
        author="changjie.fan",
        author_email="changjie.fan@tinno.com",
        description="software for hosting git repositories permission",
        long_description="""
            Manage git repositories, provide access to them over SSH, with tight
            access control by database and not needing shell accounts.
            git-serve aims to make hosting git repos easier and safer. It manages
            multiple repositories under one user account, using SSH keys to
            identify users. End users do not need shell accounts on the server,
            they will talk to one shared account that will not let them run
            arbitrary commands.""".strip(),

        license="GPL",
        keywords="git scm version-control ssh",
        url="http://github/git-serve/",

        entry_points={
            'console_scripts': [
                # ssh连接是运行的程序
                'git-serve = git_serve.serve:Main.run',
                # 'git-serve-run-hook = git-serve.run_hook:Main.run',
                # 服务器上git-serve初始化
                'git-serve-init = git_serve.init:Main.run',
                'git-serve-update = git_serve.update:Main.run',
                'git-serve-repo = git_serve.repository:Main.run',
            ],
        },
        scripts=['git_serve/git-serve-ssh'],
        zip_safe=False,

        install_requires=[
            # setuptools 0.6a9 will have a non-executeable post-update
            # hook, this will make gitosis-admin settings not update
            # (fixed in 0.6c5, maybe earlier)
            'setuptools>=0.6c5',
            # 'MySQLdb>=1.2.3',
        ],
    )


def main():
    """
    安装软件
    设置配置目录和文件
    """
    # 安装
    _setup()

    # 配置日志目录
    current_user_dir = os.path.expanduser('~')
    current_user_name = os.path.basename(current_user_dir)
    log_dir = os.path.join(current_user_dir, '.git-serve', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        status, info = commands.getstatusoutput('sudo chown -R %s:%s %s ' % (current_user_name, current_user_name,
                                                                             os.path.dirname(log_dir)))
        print status, info

    # 初始化配置文件
    config_dir = os.path.join(current_user_dir, '.git-serve', 'conf')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    config_file_path = os.path.join(config_dir, 'git-serve.conf')
    if not os.path.exists(config_file_path):
        shutil.copy2('git_serve/conf/git-serve.conf', config_dir)

if __name__ == '__main__':
    main()

