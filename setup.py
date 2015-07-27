#!/usr/bin/python
#-*- coding:utf-8 -*-
import os
from setuptools import setup, find_packages


def subdir_contents(path_list):
    all_file = []
    for path in path_list:
        top_level_path = [os.path.join(path, tmp) for tmp in os.listdir(path)]
        for child_file in top_level_path:
            if os.path.isdir(child_file):
                child_folder = [os.path.join(child_file, tmp) for tmp in os.listdir(child_file)]
                for tmp in child_folder:
                    if os.path.isdir(tmp):
                        top_level_path.append(tmp)
                    else:
                        all_file.append(tmp[tmp.find('/')+1:])
            else:
                all_file.append(child_file[child_file.find('/')+1:])
    print all_file
    return all_file

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
            #ssh连接是运行的程序
            'git-serve = git_serve.serve:Main.run',
            #'git-serve-run-hook = git-serve.run_hook:Main.run',
            #服务器上git-serve初始化
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
        #'MySQLdb>=1.2.3',
    ],
)


if __name__ == '__main__':

    current_user_dir = os.path.expanduser('~')
    current_user_name = os.path.basename(current_user_dir)
    log_dir = os.path.join(current_user_dir, '.git_serve', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        import commands
        status, info = commands.getstatusoutput('sudo chown -R %s:%s %s ' % (current_user_name, current_user_name,
                                                                             os.path.dirname(log_dir)))
        print status, info

    setup()