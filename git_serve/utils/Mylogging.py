#-*- coding:utf-8 -*-
__author__ = 'changjie.fan' '15-7-3'
"""
日志类
日志输出到文件同时在控制台显示
"""

#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging
import datetime
import os

#DIR_NAME = os.path.dirname(os.path.abspath(__file__))
DIR_NAME = '/var/log/scm_auto/'
LOG_DIR = os.path.join(DIR_NAME, 'log')
LOG_FILE = os.path.join(LOG_DIR, 'git-server-'+datetime.datetime.now().strftime('%Y-%m-%d')+'.log')
logging.basicConfig(
    level=logging.INFO,
    format='',
    datefmt='%Y-%m-%d/%H:%M:%S',
    filename=LOG_FILE,
    filemode='a'
)

fileLog = logging.FileHandler(LOG_FILE, 'w')
formatter = logging.Formatter('%(asctime)s %(name)s[line:%(lineno)d]:%(levelname)s %(message)s')
fileLog.setFormatter(formatter)

logger = logging.getLogger('git-server')

#输出到控制台
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)
