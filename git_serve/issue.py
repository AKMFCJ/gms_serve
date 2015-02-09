#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
检查提交说明中的key是否真实存在
"""

from git_serve.utils.util import DBConnect, get_current_time
from git_serve.utils.send_mail import send_mail


def check_issue_key(cfg, git_user, reference_name, repo_path, commits):
    """检查JIRA_KEY是否正式有效"""

    db_connect = DBConnect(cfg.get('ISSUE', 'hostname').strip("'"),
                           cfg.get('ISSUE', 'db_name').strip("'"),
                           cfg.get('ISSUE', 'username').strip("'"),
                           cfg.get('ISSUE', 'password').strip("'"),
                           cfg.get('ISSUE', 'charset').strip("'"))

    issue_num_list = []
    project_key = ''
    change_commits = []
    for commit, issue_key in commits:
        project_key, issue_num = issue_key.split('-')
        issue_num_list.append(issue_num)
        change_commits.append((issue_num, issue_key, commit))

    #判断issue key在数据库中是否存在
    query_sql = "select issue.issuenum from jiraissue issue join project pro where issue.issuenum in (%s) and " \
                "issue.project=pro.id and  pro.pkey='%s'" % (''.join(issue_num_list), project_key)
    records = [tmp[0] for tmp in db_connect.execute_query(query_sql)]
    db_connect.db_close()

    push_date = get_current_time()
    message = "%s\n%s\n\%s\%s" % (repo_path, reference_name, git_user, push_date)
    has_error = False
    for issue_num, issue_key, commit in commits:
        if issue_num not in records:
            has_error = True
            message = '\n'.join([message, commit.hexsha+'\t'+commit.message+'\t'+issue_key])

    if has_error:
        insert_sql = "insert into notice_repo_error_issue_key values(%s, %s, %s, %s, %s)"

        db_connect = DBConnect(cfg.get('database', 'hostname').strip("'"),
                               cfg.get('database', 'db_name').strip("'"),
                               cfg.get('database', 'username').strip("'"),
                               cfg.get('database', 'password').strip("'"),
                               cfg.get('database', 'charset').strip("'"))
        db_connect.execute_many(insert_sql, [repo_path, reference_name, git_user, push_date, message])

        #发送提醒邮件
        query_sql = "select email from notice_reference_commit_email where reference_name='%s'" % reference_name
        mail_list = [tmp[0] for tmp in db_connect.execute_query(query_sql)][0]
        db_connect.db_close()
        if mail_list:
            send_mail(cfg, "%s: JIRA_KEY_ERROR" % reference_name, message, mail_list.split(';'))
        else:
            send_mail(cfg, "%s: JIRA_KEY_ERROR" % reference_name, message, cfg.get('admin', 'admin_mail'))
        return False, message
    else:
        return True





