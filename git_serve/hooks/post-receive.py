#!/usr/bin/env python
#-*- encoding:utf-8 -*-

"""
Created on 2013-5-7
@author: changjie.fan
GIT_DIR/hooks/post-receive-email钩子的实现
设定项目更新后的通知邮件
"""

import sys
import os
import smtplib
#多个MIME对象的集合
from email.mime.multipart import MIMEMultipart
#MIME文本对象
from email.mime.text import MIMEText
from email.header import Header
import time
import commands
import MySQLdb
import ConfigParser


def send_mail(config_parser, to_list=[], sub='', content='', appendix_file=''):
    """"send_mail("aaa@163.com","sub","content")
    :param to_list:发给谁
    :param sub:主题
    :param content:内容
    :param appendix_file: 附件
    """

    #设置服务器、用户名、口令及邮箱的后缀
    mail_host = config_parser.get("email", "host")
    mail_user = config_parser.get("email", "username")
    mail_pass = config_parser.get("email", "password")
    sender = config_parser.get("email", "sender")

    msg_root = MIMEMultipart()
     #解决中文乱码
    att_text = MIMEText(content, 'html', 'UTF-8')
    #添加邮件正文
    msg_root.attach(att_text)

     #发件人
    msg_root['from'] = sender
    #邮件标题
    msg_root['Subject'] = Header(sub, 'utf-8')
    #设置时间
    msg_root['Date'] = time.ctime(time.time())
    msg_root['To'] = ';'.join(to_list)

    #构造附件(附件路径出现中文，会提示编码错误)
    if appendix_file != '':
        rar_file_path = appendix_file
        att = MIMEText(open(rar_file_path, 'rb').read(), 'gbk', 'UTF-8')
        att['Content-Type'] = 'application/octet-stream;name=%s' % Header(rar_file_path, 'UTF-8')
        att['Content-Disposition'] = 'attachment;filename=%s' % Header(rar_file_path, 'UTF-8')
        msg_root.attach(att)

    #群发邮件
    smtp = smtplib.SMTP(mail_host, 25)
    smtp.login(mail_user, mail_pass)

    smtp.sendmail(sender, to_list, msg_root.as_string())
    #休眠5秒
    time.sleep(5)
    #断开与服务器的连接
    smtp.quit()


def get_commit_info(git_path='', new_rev='', tag_name=''):
    """
        获取提交的详细信息
    :param git_path: 仓库路径
    :param new_rev: 新的Commit Id
    :param tag_name: 提交的tag或branch名称
    """

    os.chdir(git_path)
    result = []
    commit_info = commands.getoutput('git show '+new_rev)
    commit_info = commit_info.replace('<', '&lt;')
    lines = commit_info.split('\n')
    short_info = False
    if len(lines) < 1000:
        for tmp_line in lines:
            if tmp_line.startswith('-'):
                tmp_line = '<font color="red">'+tmp_line+'</font>'
            elif tmp_line.startswith('+'):
                tmp_line = '<font color="green">'+tmp_line+'</font>'
            result.append(tmp_line)
    else:
        commit_info = commands.getoutput('git log -1 '+tag_name)
        commit_info = commit_info.replace('<', '&lt;')
        result = commit_info.split('\n')
        short_info = True

    return short_info, '<br/>'.join(result)


def get_commit_notice_email_list(repo_server_ip='', git_path='', tag_name='', host_ip='',
                                 db_name='', user_name='', password=''):
    """
        获取项目的设置信息
    """
    email_address_list = ''
    try:
        conn = MySQLdb.connect(host=host_ip, db=db_name, user=user_name, passwd=password)
        cursor = conn.cursor()
        #具体仓库的配置
        repository_query_sql = 'SELECT email_address FROM repository_commit_notice WHERE reference_name="%s" ' \
                               'AND repository_server_ip="%s" AND repository_path="%s"' % (tag_name, repo_server_ip,
                                                                                           git_path)
        cursor.execute(repository_query_sql)
        email_address_list = cursor.fetchone()
        if email_address_list:
            email_address_list = email_address_list[0]
        else:
            #查找平台的配置
            platform_name = git_path.split('/home/git/repositories/')[1]
            platform_name = platform_name[:platform_name.find('/')]
            platform_query_sql = 'SELECT email_address FROM repository_commit_notice WHERE reference_name="%s" ' \
                                 'AND repository_server_ip="%s" AND platform_name="%s"' % (tag_name, repo_server_ip,
                                                                                           platform_name)
            cursor.execute(platform_query_sql)
            email_address_list = cursor.fetchone()
            if email_address_list:
                email_address_list = email_address_list[0]
            else:
                #原来直接用引用配置的实现
                old_query_sql = 'SELECT email_address FROM repository_commit_notice WHERE ' \
                                'reference_name="%s"' % tag_name
                cursor.execute(old_query_sql)
                email_address_list = cursor.fetchone()
                if email_address_list:
                    email_address_list = email_address_list[0]

        cursor.close()
        conn.close()
    except MySQLdb.Error, e:
        send_mail(["changjie.fan@tinno.com"], "提交的邮件通知发送失败", '连接Tup数据库失败')

    return email_address_list


def add_push_history(repo_path='', reference='', old_rev='', new_rev='', local_ip='', host_ip='', db_name='',
                     user_name='', password=''):
    """推送日志记入数据库中便于tsds解析
    """

    date_format = '%Y-%m-%d-%H-%M'
    now = time.strftime(date_format, time.localtime())
    try:
        conn = MySQLdb.connect(host=host_ip, db=db_name, user=user_name, passwd=password)
        cursor = conn.cursor()
        sql = "insert into git_push_log set server_ip='%s',repository_path='%s',reference='%s',pstatus=0," \
              "create_time='%s',old_revision='%s',new_revision='%s'" \
              % (local_ip, repo_path, reference, now, old_rev, new_rev)

        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
    except MySQLdb.Error, e:
        send_mail(["changjie.fan@tinno.com"], "数据库记录Push history失败",
                  'Git服务器Ip:%s<br>git仓库路径:%s<br>git分支:%s<br>更新时间:%s' %
                  (local_ip, repo_path, reference, now))


def repository_push_log(repo_path='', reference='', old_rev='', new_rev='', local_ip='', host_ip='', db_name='',
                     user_name='', password=''):
    """推送日志记入数据库中便于tsds解析
    """

    date_format = '%Y-%m-%d %H:%M:%S'
    now = time.strftime(date_format, time.localtime())
    try:
        conn = MySQLdb.connect(host=host_ip, db=db_name, user=user_name, passwd=password)
        cursor = conn.cursor()
        sql = "insert into repository_push_log set server_ip='%s',repository_path='%s',reference='%s',status=0," \
              "create_time='%s',old_revision='%s',new_revision='%s'" \
              % (local_ip, repo_path, reference, now, old_rev, new_rev)

        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
    except MySQLdb.Error, e:
        send_mail(["changjie.fan@tinno.com"], "Tup数据库记录Push history失败",
                  'Git服务器Ip:%s<br>git仓库路径:%s<br>git分支:%s<br>更新时间:%s' %
                  (local_ip, repo_path, reference, now))


if __name__ == "__main__":
    """
        第一个参数是post-receive 钩子pwd命令获取的仓库目录
        第二个参数是新的commit id
        第三个参数是更新的tag名称
        第四个参数是sqlite3 db文件的具体路径
    """
    git_path = os.getcwd()
    #print git_path
    argv = []
    for line in sys.stdin:
        line = line.strip()
        argv = line.split(' ')
    
    old_rev = argv[0].strip()
    new_rev = argv[1].strip()
    tag_name = argv[2].strip('\n')

    config_parser = ConfigParser()
    try:
        config_parser.read(os.path.expanduser('~/.git-serve/conf/git-serve.conf'))
        hostname = config_parser.get('database', 'hostname').strip("'")
        db_name = config_parser.get('database', 'db_name').strip("'")
        username = config_parser.get('database', 'username').strip("'")
        password = config_parser.get('database', 'password').strip("'")
        localhost = config_parser.get('localhost', 'ip').strip("")
    except IOError:
        config_parser = None
        localhost = 'localhost'
        hostname = '172.16.20.162'
        db_name = 'tup'
        username = 'root'
        password = 'root'
        pass

    repository_push_log(git_path, tag_name, old_rev, new_rev, localhost, hostname, db_name, username, password)
    notice_email_list = get_commit_notice_email_list(localhost, git_path, tag_name,
                                                     hostname, db_name, username, password)

    if notice_email_list:
        (short_info, commit_info) = get_commit_info(git_path, new_rev, tag_name)
        git_path = git_path.split('/home/git/repositories')[1]
        commit_info = '\n'.join([git_path, commit_info])
        title = tag_name+"___项目更新通知邮件"
        if short_info:
            title = tag_name+" ___项目更新通知邮件(简略信息)"

        send_mail(config_parser, str(notice_email_list).split(';'), title, commit_info)

