#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
git-serve的入口程序控制，仓库级的读写权限
"""
import logging
import os
import sys

from git_serve.app import App
from git_serve.access import have_read_access, have_write_access

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
    """没有仓库的写权限"""


class ReadAccessDenied(AccessDenied):
    """没有仓库的读权限"""


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
        temp_repo_path = repo_path[:-4]
    else:
        temp_repo_path = repo_path
    is_write = False
    if verb in COMMANDS_READONLY:
        if not have_read_access(cfg, user, temp_repo_path):
            raise ReadAccessDenied()
    elif verb in COMMANDS_WRITE:
        is_write = True
        if not have_write_access(cfg, user, temp_repo_path):
            raise WriteAccessDenied()

    logger.warning('user:%s' % user)
    logger.warning('verb:%s' % verb)
    logger.warning('args:%s' % args)

    #仓库绝对路径的拼装
    full_path = os.path.join('repositories', repo_path)
    new_cmd = "%(verb)s '%(path)s'" % dict(verb=verb, path=full_path,)
    logger.warning('new_cmd:%s' % new_cmd)

    return user, new_cmd, full_path, is_write


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
            user, git_cmd, repo_path, is_write = serve(cfg=cfg, user=user, command=ssh_cmd,)
        except ServingError, e:
            logger.error(u'\033[43;31;1m %s:%s\033[0m' % (user, e))
            sys.exit(1)

        #提交操作时,设置环境变量供hook/update 判断项目级权限使用
        if is_write:
            #提交的用户名称, 配置在~/.ssh/authorized_keys中
            os.putenv('git_user', user)
            #提交仓库的相对路径, 从repositories/开始
            os.putenv('repo_path', repo_path)
            #存在权限设置的数据库访问信息
            os.putenv('db_host', cfg.get('database', 'hostname').strip("'"))
            os.putenv('db_name', cfg.get('database', 'db_name').strip("'"))
            os.putenv('db_username', cfg.get('database', 'username').strip("'"))
            os.putenv('db_password', cfg.get('database', 'password').strip("'"))
            os.putenv('db_charset', cfg.get('database', 'charset').strip("'"))

        os.execvp('git', ['git', 'shell', '-c', git_cmd])
        logging.error('Cannot execute git-shell.')
        sys.exit(1)
