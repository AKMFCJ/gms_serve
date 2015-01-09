#!/usr/bin/python
from setuptools import setup, find_packages
import os


def _subdir_contents(path):
    for top_level in os.listdir(path):
        top_level_path = os.path.join(path, top_level)
        if not os.path.isdir(top_level_path):
            continue
        for dir_path, dir_names, file_names in os.walk(top_level_path):
            for file_name in file_names:
                full_path = os.path.join(dir_path, file_name)
                if not full_path.startswith(path+'/'):
                    raise RuntimeError()
                yield full_path[len(path)+1:]


def subdir_contents(path):
    return list(_subdir_contents(path))

setup(
    name="git-serve",
    version="0.1",
    packages=find_packages(),

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
            'git-server = git_serve.serve:Main.run',
            #'git-serve-run-hook = git-serve.run_hook:Main.run',
            #'git-serve-init = git-serve.init:Main.run',
        ],
    },

    package_data={
    },

    # templates need to be a real directory, for git init
    zip_safe=False,

    install_requires=[
        # setuptools 0.6a9 will have a non-executeable post-update
        # hook, this will make gitosis-admin settings not update
        # (fixed in 0.6c5, maybe earlier)
        'setuptools>=0.6c5',
    ],
)

