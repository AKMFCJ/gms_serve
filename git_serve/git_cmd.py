#-*- coding:utf-8 -*-
__author__ = 'changjie.fan'
"""
通过GitPython仓库操作仓库
"""
from git import *
import commands


class CommitObj:
    def __init__(self, message='', hex_sha=''):
        self.message = message
        self.hex_sha = hex_sha


class GitCmd:
    def __init__(self, repo_path=''):
        self.repo_path = repo_path
        self.repo = Repo(repo_path)

    def diff_commit(self, old_commit, new_commit):
        """获取old和new commit之间的所有commit，包括old和new"""

        changes = []
        status, info = commands.getstatusoutput('git --git-dir=%s log --pretty="%s" %s..%s' %
                                                (self.repo_path, "%H<-br->%s%b", old_commit, new_commit))
        if status:
            try:
                changes = list(self.repo.iter_commits('%s..%s' % (self.repo.commit(old_commit),
                                                                  self.repo.commit(new_commit))))
            except GitCommandError:
                changes = []
        else:
            info = [tmp for tmp in info.split('\n') if tmp]
            for message in info:
                message = message.split('<-br->')
                if len(message) == 2:
                    if message[1].find('Change-Id:') > 0:
                        changes.append(CommitObj(hex_sha=message[0], message=message[1].split('Change-Id:')[0]))
                    else:
                        changes.append(CommitObj(hex_sha=message[0], message=message[1]))

        return changes


if __name__ == '__main__':
    git_cmd = GitCmd('/home/roy/manifest_workspace/jst/jst-git1-admin')
    for commit in git_cmd.change_commits('2b329f2b1d7aaf', 'ce592d7497'):
        print commit
