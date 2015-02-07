#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
创建裸库和连接hooks文件
"""
import os
import sys
import logging
import commands
from optparse import OptionParser

from git_serve.util import  create_repository_hook_link


class Main(object):
    @staticmethod
    def run():
        parser = OptionParser(usage="%prog [options] arg1 arg2", version="%prog 1.0")
        parser.add_option("-c", action="store_true", dest="create")
        parser.add_option("-p", "--path", dest="path", help="repository absolute path")
        parser.add_option("-t", "--tag", dest="tag", help="init tags")
        parser.add_option("-b", "--branch", dest="branch", help="init branches")

        (options, args) = parser.parse_args()

        if options.create and options.path:
            Main.create_repo(options.path)
        if options.tag:
            Main.create_tag(options.path, [tag for tag in options.tag.split(';') if tag])
        if options.branch:
            Main.create_branch(options.path, [branch for branch in options.branch.split(';') if branch])

    @staticmethod
    def create_repo(path=''):
        """创建裸库"""
        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)
        (result, info) = commands.getstatusoutput('git init --bare')
        if result:
            sys.exit(1)

        #创建hooks
        create_repository_hook_link(path)

        #创建初始化tag和分支
        (result, info) = commands.getstatusoutput('GIT_WORK_TREE=%s git --git-dir="%s"  commit --allow-empty -m "init"'
                                                  % (path, path))
        if result:
            sys.exit(1)

    @staticmethod
    def create_tag(path='', tags=[]):
        """创建初始tag"""

        for tag_name in tags:
            (result, info) = commands.getstatusoutput('GIT_WORK_TREE=%s git --git-dir="%s" tag %s ' %
                                                      (path, path, tag_name))
            if result:
                sys.exit(1)

    @staticmethod
    def create_branch(path='', branches=[]):
        """创建初始tag"""

        for branch_name in branches:
            (result, info) = commands.getstatusoutput('GIT_WORK_TREE=%s git --git-dir="%s" branch %s master' %
                                                      (path, path, branch_name))
            if result:
                sys.exit(1)