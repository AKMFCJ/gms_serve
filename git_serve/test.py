__author__ = 'changjie.fan'
import logging
import time

if __name__ == '__main__':
    logger = logging.getLogger('git-serve')
    log_file_name = time.strftime('%Y-%m-%d', time.localtime())+'_log.txt'
    datefmt = '%Y-%d-%b %H:%M:%S'
    formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s %(message)s")

    handler = logging.FileHandler('/home/roy/.git-server/logs/%s' % log_file_name)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel('INFO')

