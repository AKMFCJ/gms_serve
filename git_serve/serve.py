#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
git-serve的入口程序控制，仓库级的读写权限
"""
import logging
import os
import sys

from git_serve.app import App


logger = logging.getLogger('git-server')

COMMANDS_READONLY = ['git-upload-pack', 'git upload-pack', ]
COMMANDS_WRITE = ['git-receive-pack', 'git receive-pack', ]


class ServingError(Exception):
    """Serving error"""

    def __str__(self):
        return u'%s' % self.__doc__


class CommandMayNotContainNewlineError(ServingError):
    """Command may not contain newline"""


class UnknownCommandError(ServingError):
    """Unknown command denied"""


class UnsafeArgumentsError(ServingError):
    """Arguments to command look dangerous"""


class AccessDenied(ServingError):
    """Access denied to repository"""


class WriteAccessDenied(AccessDenied):
    """Repository write access denied"""


class ReadAccessDenied(AccessDenied):
    """Repository read access denied"""


def serve(user, command, ):
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

    logging.warning('user:%s' % user)
    logging.warning('verb:%s' % verb)
    logging.warning('args:%s' % args)

    full_path = os.path.join('repositories', args.strip("'"))
    logging.warning(full_path)
    new_cmd = "%(verb)s '%(path)s'" % dict(verb=verb, path=full_path,)
    logging.warning('new_cmd:%s' % new_cmd)

    return user, new_cmd, full_path


class Main(App):
    def create_parser(self):
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS] USER')
        parser.set_description('Allow restricted git operations under DIR')
        return parser

    def handle_args(self, options, args):
        try:
            (user,) = args
        except ValueError:
            logging.error('Missing argument USER.')

        ssh_cmd = os.environ.get('SSH_ORIGINAL_COMMAND', None)
        if ssh_cmd is None:
            logging.error('Need SSH_ORIGINAL_COMMAND in environment.')
            sys.exit(1)

        try:
            user, git_cmd, repo_path = serve(user=user, command=ssh_cmd,)
        except ServingError, e:
            logging.error('%s', e)
            sys.exit(1)

        logging.debug('Serving %s', git_cmd)
        os.putenv('git_user', user)
        os.putenv('repo_path', repo_path)
        os.execvp('git', ['git', 'shell', '-c', git_cmd])
        logging.error('Cannot execute git-shell.')
        sys.exit(1)
