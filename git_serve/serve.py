#-*- coding:utf-8 -*-
__author__ = 'changjie.fan'
"""
git-serve的入口程序控制，仓库级的读写权限
"""
import logging
import os
import sys
from simplejson import dumps as json_dumps

from git_serve.app import App
from git_serve.access import read_permission_config
from git_serve.utils.Mylogging import logger
from git_serve.utils.DBConnect import DBConnect

reload(sys)
sys.setdefaultencoding('utf-8')


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


class Main(App):

    def create_parser(self):
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS] USER')
        parser.set_description('Allow restricted git operations under DIR')
        return parser

    def serve(self, cfg, user, command, ):
        """仓库级权限控制"""

        if not command or command == 'info':
            logger.info('SSH Key validate is OK')
            sys.exit(0)

        if '\n' in command:
            raise CommandMayNotContainNewlineError()

        try:
            verb, args = command.split(None, 1)
        except ValueError:
            raise UnknownCommandError()

        if verb == 'git':
            try:
                sub_verb, args = args.split(None, 1)
            except ValueError:
                raise UnknownCommandError()
            verb = '%s %s' % (verb, sub_verb)

        if verb not in COMMANDS_WRITE and verb not in COMMANDS_READONLY:
            raise UnknownCommandError()

        db_connect = DBConnect(cfg.get('database', 'hostname').strip("'"),
                               cfg.get('database', 'db_name').strip("'"),
                               cfg.get('database', 'username').strip("'"),
                               cfg.get('database', 'password').strip("'"),
                               cfg.get('database', 'charset').strip("'"))

        repo_path = args.strip("'")
        logger.info("repo_path:%s" % repo_path)
        # Git仓库的绝对路径
        access_repo_path = os.path.join(cfg.get('repository', 'root_path'), repo_path)

        # 仓库级读写权限判断
        result, permission_config = read_permission_config(db_connect, cfg, user, access_repo_path)

        is_write = False
        if verb in COMMANDS_READONLY:
            logger.info('{0} read {1}'.format(user, access_repo_path))
            if not result:
                print u"\033[43;31;1m %s 没有仓库的读权限 %s\033[0m\n" % (user, repo_path)
                raise ReadAccessDenied()

        elif verb in COMMANDS_WRITE:
            logger.info('{0} write {1}'.format(user, access_repo_path))
            is_write = True
            if not result:
                print u"\033[43;31;1m %s 没有仓库的写权限 %s\033[0m\n" % (user, repo_path)

        # 仓库绝对路径的拼装
        new_cmd = "%(verb)s '%(path)s'" % dict(verb=verb, path=access_repo_path, )

        return new_cmd, access_repo_path, is_write, permission_config

    def handle_args(self, parser, cfg, options, args):
        try:
            (user,) = args
        except ValueError:
            logger.error('Missing argument USER.')

        ssh_cmd = os.environ.get('SSH_ORIGINAL_COMMAND', None)
        if ssh_cmd is None:
            logging.error('Need SSH_ORIGINAL_COMMAND in environment.')
            sys.exit(1)
        try:
            git_cmd, access_repo_path, is_write, permission_config = self.serve(cfg=cfg, user=user, command=ssh_cmd, )
        except ServingError, e:
            logger.error(u'\033[43;31;1m %s:%s\033[0m' % (user, e))
            sys.exit(1)

        # 提交操作时,设置环境变量供hook/update 判断项目级权限使用
        if is_write:
            # 提交的用户名称, 配置在~/.ssh/authorized_keys中
            os.putenv('git_user', user)
            # 仓库的权限配置
            os.putenv('permission_config', json_dumps(permission_config))
            # 仓库完整的绝对路径
            os.putenv('access_repo_path', access_repo_path)

        os.execvp('git', ['git', 'shell', '-c', git_cmd])
        logger.error('Cannot execute git-shell.')
        sys.exit(1)
