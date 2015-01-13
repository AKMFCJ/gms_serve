#-*- encoding:utf-8-*_
__author__ = 'changjie.fan'
"""程序入口的基类，加载通用设置和处理log设置"""
import logging
import os
import sys
import optparse
import errno
import ConfigParser
import time

import util


logger = logging.getLogger('git-serve')


class CannotReadConfigError(Exception):
    """Unable to read config file"""

    def __str__(self):
        return u'%s: %s' % (self.__doc__, ': '.join(self.args))


class ConfigFileDoesNotExistError(CannotReadConfigError):
    """Configuration does not exist"""


class App(object):
    name = None

    def run(class_):
        app = class_()
        return app.main()
    run = classmethod(run)

    def main(self):
        self.setup_basic_logging()
        parser = self.create_parser()
        (options, args) = parser.parse_args()
        cfg = self.create_config(options)
        try:
            self.read_config(options, cfg)
        except CannotReadConfigError, e:
            logger.error(str(e))
            sys.exit(1)
        self.setup_logging(cfg)
        self.handle_args(parser, cfg, options, args)

    def init(self):
        os.umask(0022)
        repositories = os.path.expanduser('~/repositories')
        if not os.path.exists(repositories):
            util.mk_dir(repositories)

        ssh = os.path.expanduser('~/.ssh')
        if not os.path.exists(ssh):
            util.mk_dir(os.path.expanduser('~/.ssh'), 0700)
        else:
            if os.path.exists(os.path.join(ssh, 'authorized_keys')):
                os.rename(os.path.join(ssh, 'authorized_keys'), os.path.join(ssh, 'authorized_keys_old'))

        git_serve_dir = os.path.expanduser('~/.git-serve')
        if not os.path.exists(git_serve_dir):
            util.mk_dir(git_serve_dir)
            util.mk_dir(os.path.join(git_serve_dir, 'logs'))
            rfp = open('../git-serve.conf')
            wfp = open(os.path.join(git_serve_dir, 'git-serve.conf'), 'w')
            for line in rfp.readline():
                wfp.write(line+'\n')
            wfp.close()
            rfp.close()

    def setup_basic_logging(self):
        logging.basicConfig()

    def setup_logging(self, cfg):
        """初始化日志配置"""

        log_file_name = time.strftime('%Y-%m-%d', time.localtime())+'_log.txt'
        formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s %(message)s")
        log_file = os.path.expanduser('~/.git-serve/logs/%s' % log_file_name)
        if not os.path.exists(log_file):
            open(log_file, 'w').close()
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

        log_level = cfg.get('log', 'log_level')
        logging.root.setLevel(log_level)

    def create_config(self, options):
        cfg = ConfigParser.RawConfigParser()
        return cfg

    def read_config(self, options, cfg):
        try:
            conf_file = file(options.config)
        except (IOError, OSError), e:
            if e.errno == errno.ENOENT:
                raise ConfigFileDoesNotExistError(str(e))
            else:
                raise CannotReadConfigError(str(e))
        try:
            cfg.readfp(conf_file)
        finally:
            conf_file.close()

    def create_parser(self):
        parser = optparse.OptionParser()
        parser.set_defaults(config=os.path.expanduser('~/.git-serve/git-serve.conf'), )
        parser.add_option('--config', metavar='FILE', help='read config from FILE', )
        return parser

    def handle_args(self, parser, cfg, options, args):
        if args:
            logger.error('not expecting arguments')