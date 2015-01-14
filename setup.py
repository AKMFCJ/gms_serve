#!/usr/bin/python
#-*- encoding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="git-serve",
    version="0.1",
    packages=find_packages(),
    package_data={
        '': ['*.conf'],
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
        ],
    },

    zip_safe=False,

    install_requires=[
        # setuptools 0.6a9 will have a non-executeable post-update
        # hook, this will make gitosis-admin settings not update
        # (fixed in 0.6c5, maybe earlier)
        'setuptools>=0.6c5',
        #'MySQLdb>=1.2.3',
    ],
)

