#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'

import os
import logging

from git_serve import app
import util

logger = logging.getLogger('git-serve')


class Main(app.App):
    def create_parser(self):
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS]')
        parser.set_description(
            'Initialize a user account for use with gitosis')
        return parser

    def read_config(self, *a, **kw):
        # ignore errors that result from non-existent config file
        try:
            super(Main, self).read_config(*a, **kw)
        except app.ConfigFileDoesNotExistError:
            pass

    def handle_args(self, parser, cfg, options, args):
        super(Main, self).handle_args(parser, cfg, options, args)

        os.umask(0022)
        repositories = os.path.expanduser('~/repositories')
        if not os.path.exists(repositories):
            util.mkdir(repositories)

        ssh = os.path.expanduser('~/.ssh')
        if not os.path.exists(ssh):
            util.mkdir(os.path.expanduser('~/.ssh'), 0700)
        else:
            if os.path.exists(os.path.join(ssh, 'authorized_keys')):
                os.rename(os.path.join(ssh, 'authorized_keys'), os.path.join(ssh, 'authorized_keys_old'))

        git_serve_dir = os.path.expanduser('~/.git-serve')
        if not os.path.exists(git_serve_dir):
            util.mkdir(git_serve_dir)
            util.mkdir(os.path.join(git_serve_dir, 'logs'))
            rfp = open('../git-serve.conf')
            wfp = open(os.path.join(git_serve_dir, 'git-serve.conf'), 'w')
            for line in rfp.readline():
                wfp.write(line+'\n')
            wfp.close()
            rfp.close()


