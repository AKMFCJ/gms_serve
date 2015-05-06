#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
git-serve的入口程序控制，仓库级的读写权限
"""
import logging
import os
import sys

from git_serve.app import App
from git_serve.access import have_read_access

logger = logging.getLogger('git-serve')

COMMANDS_READONLY = ['git-upload-pack', 'git upload-pack', ]
COMMANDS_WRITE = ['git-receive-pack', 'git receive-pack', ]


class ServingError(Exception):
    """Serving error"""

    def __str__(self):
        return u"%s" % unicode(self.__doc__, 'utf-8')


class CommandMayNotContainNewlineError(ServingError):
    """Command may not contain newline"""


class UnknownCommandError(ServingError):
    """Unknown command denied"""


class UnsafeArgumentsError(ServingError):
    """Arguments to command look dangerous"""


class AccessDenied(ServingError):
    """Access denied to repository"""


class WriteAccessDenied(AccessDenied):
    """no repository PUSH permission"""


class ReadAccessDenied(AccessDenied):
    """no repository CLONE permission"""


def serve(cfg, user, command, ):
    """仓库级权限控制"""

    if '\n' in command:
        raise CommandMayNotContainNewlineError()

    try:
        verb, args = command.split(None, 1)
    except ValueError:
        # all known "git-foo" commands take one argument; improve
        # if/when needed
        raise UnknownCommandError()

    if verb == 'git':
        try:
            sub_verb, args = args.split(None, 1)
        except ValueError:
            raise UnknownCommandError()
        verb = '%s %s' % (verb, sub_verb)

    if verb not in COMMANDS_WRITE and verb not in COMMANDS_READONLY:
        raise UnknownCommandError()

    repo_path = args.strip("'")

    #仓库级读写权限判断
    if repo_path.endswith('.git'):
        access_repo_path = repo_path[:-4]
    else:
        access_repo_path = repo_path
    is_write = False
    if verb in COMMANDS_READONLY:
        if not have_read_access(cfg, user, access_repo_path):
            raise ReadAccessDenied()
    elif verb in COMMANDS_WRITE:
        is_write = True
        if not have_read_access(cfg, user, access_repo_path):
            raise WriteAccessDenied()

    #仓库绝对路径的拼装
    full_path = os.path.join('repositories', repo_path)
    new_cmd = "%(verb)s '%(path)s'" % dict(verb=verb, path=full_path, )

    return user, new_cmd, full_path, access_repo_path, is_write


class Main(App):
    def create_parser(self):
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS] USER')
        parser.set_description('Allow restricted git operations under DIR')
        return parser

    def handle_args(self, parser, cfg, options, args):
        try:
            (user,) = args
        except ValueError:
            logging.error('Missing argument USER.')

        ssh_cmd = os.environ.get('SSH_ORIGINAL_COMMAND', None)
        if ssh_cmd is None:
            logging.error('Need SSH_ORIGINAL_COMMAND in environment.')
            sys.exit(1)

        try:
            user, git_cmd, repo_path, access_repo_path, is_write = serve(cfg=cfg, user=user, command=ssh_cmd, )
        except ServingError, e:
            logger.error(u'\033[43;31;1m %s:%s\033[0m' % (user, e))
            sys.exit(1)

        #提交操作时,设置环境变量供hook/update 判断项目级权限使用
        if is_write:
            #提交的用户名称, 配置在~/.ssh/authorized_keys中
            os.putenv('git_user', user)
            #提交仓库的相对路径, 从repositories/开始
            os.putenv('repo_path', repo_path)
            os.putenv('access_repo_path', access_repo_path)

        os.execvp('git', ['git', 'shell', '-c', git_cmd])
        logging.error('Cannot execute git-shell.')
        sys.exit(1)
