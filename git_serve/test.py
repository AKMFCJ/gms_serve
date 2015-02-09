__author__ = 'changjie.fan'
import logging
import time
import ConfigParser

if __name__ == '__main__':
    '''logger = logging.getLogger('git-serve')
    log_file_name = time.strftime('%Y-%m-%d', time.localtime())+'_log.txt'
    datefmt = '%Y-%d-%b %H:%M:%S'
    formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s %(message)s")

    handler = logging.FileHandler('/home/roy/.git-server/logs/%s' % log_file_name)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel('INFO')'''

    cfg = ConfigParser.RawConfigParser()
    try:
        conf_file = open('/home/roy/workspace/git-serve/git_serve/conf/git-serve.conf', 'r')
    except (IOError, OSError), e:
        print "IOError"
    try:
        cfg.readfp(conf_file)
    finally:
        conf_file.close()

    print cfg.get('email', 'host').strip("'")
    print cfg.get('email', 'username').strip("'")
    print cfg.get('email', 'password').strip("'")
    print cfg.get('email', 'subject_prefix').strip("'")
    print cfg.get('email', 'user_tls').strip("'")

