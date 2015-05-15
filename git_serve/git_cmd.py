#-*- coding:utf-8 -*-
__author__ = 'changjie.fan'
"""
通过GitPython仓库操作仓库
"""
from git import *


class GitCmd():
    def __init__(self, repo_path=''):
        self.repo = Repo(repo_path)

    def diff_commit(self, old_commit, new_commit):
        """获取old和new commit之间的所有commit，包括old和new"""

        changes = list(self.repo.iter_commits('%s..%s' % (self.repo.commit(old_commit), self.repo.commit(new_commit))))
        return changes


if __name__ == '__main__':
    git_cmd = GitCmd('/home/roy/manifest_workspace/jst/jst-git1-admin')
    for commit in git_cmd.change_commits('2b329f2b1d7aaf', 'ce592d7497'):
        print commit