#-*- encoding:utf-8-*_
__author__ = 'changjie.fan'
"""程序入口的基类，加载通用设置和处理log设置"""
import logging
import os
import sys
import optparse
import errno
import ConfigParser

logger = logging.getLogger('git-server')


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
        self.setup_logging()
        parser = self.create_parser()
        (options, args) = parser.parse_args()
        cfg = self.create_config(options)
        try:
            self.read_config(options, cfg)
        except CannotReadConfigError, e:
            logger.error(str(e))
            sys.exit(1)
        self.handle_args(parser, cfg, options, args)

    def setup_logging(self, log_level='WARNING'):
        logging.root.setLevel(log_level)

    def create_config(self, options):
        cfg = ConfigParser.RawConfigParser()
        return cfg

    def read_config(self, options, cfg):
        try:
            conffile = file(options.config)
        except (IOError, OSError), e:
            if e.errno == errno.ENOENT:
                raise ConfigFileDoesNotExistError(str(e))
            else:
                raise CannotReadConfigError(str(e))
        try:
            cfg.readfp(conffile)
        finally:
            conffile.close()

    def create_parser(self):
        parser = optparse.OptionParser()
        parser.set_defaults(config=os.path.expanduser('~/.git-serve.conf'), )
        parser.add_option('--config', metavar='FILE', help='read config from FILE', )
        return parser

    def handle_args(self, parser, cfg, options, args):
        if args:
            logger.error('not expecting arguments')