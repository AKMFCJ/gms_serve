#-*- encoding:utf-8-*_
__author__ = 'changjie.fan'
"""程序入口的基类，加载通用设置和处理log设置"""
import logging
import os
import sys
import optparse
import errno
import ConfigParser
import datetime


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

    def setup_basic_logging(self):
        logging.basicConfig()

    def setup_logging(self, cfg):
        """初始化日志配置"""

        log_dir = os.path.expanduser('~/.git-serve/logs/')
        log_file = datetime.datetime.now().strftime('%Y-%m-%d')+'.log'
        info_level = cfg.get('log', 'log_level') or logging.INFO
        logging.basicConfig(
            level=info_level,
            format='',
            datefmt='%Y-%m-%d/%H:%M:%S',
            filename=os.path.join(log_dir,log_file),
            filemode='a'
            )

        file_handler = logging.FileHandler(os.path.join(log_dir,log_file),'w')
        formatter = logging.Formatter('%(asctime)s %(name)s[line:%(lineno)d]:%(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)

        console = logging.StreamHandler()
        console.setLevel(info_level)
        logging.root.addHandler(console)

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
        parser.set_defaults(config=os.path.expanduser('~/.git-serve/conf/git-serve.conf'), )
        parser.add_option('--config', metavar='FILE', help='read config from FILE', )
        return parser

    def handle_args(self, parser, cfg, options, args):
        if args:
            App.logger.error('not expecting arguments')
