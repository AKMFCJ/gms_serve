#-*- encoding:utf-8-*_
__author__ = 'changjie.fan'
"""程序入口的基类，加载通用设置和处理log设置"""
import logging
import sys
import optparse

logger = logging.getLogger('git-server')


class App():

    def __init__(self, name):
        self.name = name

    @staticmethod
    def run(class_):
        app = class_()
        return app.main()

    def main(self):
        self.setup_logging()
        parser = self.create_parser()
        (options, args) = parser.parse_args()
        self.handle_args(options, args)

    def setup_logging(self, log_level='warning'):
        logging.root.setLevel(log_level)

    def create_parser(self):
        parser = optparse.OptionParser()
        return parser

    def handle_args(self, options, args):
        if args:
            logger.error('not expecting arguments')