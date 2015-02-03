#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
创建裸库和连接hooks文件
"""
import os
import sys
import logging

logger = logging.getLogger('git-serve')


class Main(object):
    @staticmethod
    def run():
        logger.info(sys.argv)