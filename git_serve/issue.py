#-*- coding:utf-8 -*-
__author__ = 'changjie.fan'
"""
检查提交说明中的key是否真实存在
检查说明中是否包含JIRA_TITLE(默认不检查)
"""
import os

from MySQLdb import OperationalError
from git_serve.utils.DBConnect import DBConnect
from git_serve.utils.send_mail import send_mail


def check_issue_key(cfg, commit_msg_list, check_title=False):
    """检查JIRA_KEY是否正式有效"""

    try:
        db_connect = DBConnect(cfg.get('ISSUE', 'hostname').strip("'"),
                               cfg.get('ISSUE', 'db_name').strip("'"),
                               cfg.get('ISSUE', 'username').strip("'"),
                               cfg.get('ISSUE', 'password').strip("'"),
                               cfg.get('ISSUE', 'charset').strip("'"))
    except OperationalError, e:
        # 通过邮件标记为避免重复发生相同的错误邮件
        if cfg.get('admin', 'send_error_mail') == 'true':
            send_mail(u'JIRA数据库连接失败', e, [cfg.get('admin', 'admin_mail')])
        else:
            cfg.set('admin', 'send_error_mail', 'false')
            cfg.write(open(os.path.expanduser('~/.git-serve/conf/git-serve.conf'), 'w'))
        return True, ''

    if cfg.get('admin', 'send_error_mail') == 'false':
        cfg.set('admin', 'send_error_mail', 'true')
        cfg.write(open(os.path.expanduser('~/.git-serve/conf/git-serve.conf'), 'w'))

    issue_num_list = []
    project_key = ''
    change_commits = []
    for commit, issue_key, issue_title in commit_msg_list:
        project_key, issue_num = issue_key.split('-')
        issue_num_list.append(issue_num)
        change_commits.append((issue_num, issue_key, issue_title, commit))

    if not issue_num_list and not change_commits:
        return True, ''

    # 检查提交说明中的JIRA_TITLE
    if check_title:
        # 判断issue key在数据库中是否存在
        query_sql = "SELECT issue.issuenum, issue.SUMMARY FROM jiraissue issue JOIN project pro WHERE issue.issuenum " \
                    "IN (%s) AND issue.project=pro.id AND pro.pkey='%s'" % (','.join(issue_num_list), project_key)
        records = [(str(tmp[0]), tmp[1].strip()) for tmp in db_connect.execute_query(query_sql)]
        db_connect.db_close()

        has_error = False
        message = []
        for issue_num, issue_key, issue_title, commit in change_commits:
            error = True
            for record in records:
                if issue_num == record[0] and issue_title.find(record[1]) >= 0:
                    error = False
                    break

            if error:
                has_error = True
                message.append('\n'.join([commit.hex_sha[:8], commit.message]))
    # 不检查提交说明中的JIRA_TITLE
    else:
        query_sql = "SELECT issue.issuenum FROM jiraissue issue JOIN project pro WHERE issue.issuenum " \
                    "IN (%s) AND issue.project=pro.id AND pro.pkey='%s'" % (','.join(issue_num_list), project_key)
        records = [str(tmp[0]) for tmp in db_connect.execute_query(query_sql)]
        db_connect.db_close()

        has_error = False
        message = []
        for issue_num, issue_key, issue_title, commit in change_commits:
            if issue_num not in records:
                message.append('\n'.join([commit.hex_sha[:8], commit.message]))

    if has_error:
        return False, '\n'.join(message)
    else:
        return True, ''





