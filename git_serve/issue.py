#-*- encoding:utf-8 -*-
__author__ = 'changjie.fan'
"""
检查提交说明中的key是否真实存在
"""

from util import DBConnect


def check_issue_key(cfg, git_user, reference_name, repo_path, localhost_ip):
    """检查JIRA_KEY是否正式有效"""


    issue_key = ''
    issue_num, project_key = issue_key.split('-')
    query_sql = "select id from jiraissue issue join project pro where issue.issuenum=%s and issue.project=pro.id " \
                "and  pro.pkey='%s'" % (issue_num, project_key)
    DBConnect()