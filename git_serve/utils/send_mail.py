#-*- coding:utf-8 -*-
__author__ = 'changjie.fan'

"""
邮件发送类
"""

import smtplib
#多个MIME对象的集合
from email.mime.multipart import MIMEMultipart
#MIME文本对象
from email.mime.text import MIMEText
from email.header import Header
import time


def send_mail(cfg, subject='', message='', recipient_list=[], appendix_file=''):
    """"
    to_list:发给谁
    sub:主题
    content:内容
    send_mail(cfg,"sub","content", "aaa@163.com")
    """

    # 设置服务器、用户名、口令及邮箱的后缀
    mail_host = cfg.get('email', 'host').strip("'")
    mail_user = cfg.get('email', 'username').strip("'")
    mail_pass = cfg.get('email', 'password').strip("'")
    mail_postfix = cfg.get('email', 'subject_prefix').strip("'")
    sender = "TSDS[%s]" % mail_user

    msg_root = MIMEMultipart()
    # 解决中文乱码
    att_text = MIMEText(message, 'html', 'UTF-8')
    # 添加邮件正文
    msg_root.attach(att_text)

    # 发件人
    msg_root['from'] = sender
    # 邮件标题
    msg_root['Subject'] = Header(subject, 'utf-8')
    # 设置时间
    msg_root['Date'] = time.ctime(time.time())
    msg_root['To'] = ';'.join(recipient_list)

    # 构造附件(附件路径出现中文，会提示编码错误)
    if appendix_file != '':
        rar_file_path = appendix_file
        att = MIMEText(open(rar_file_path, 'rb').read(), 'gbk', 'UTF-8')
        att['Content-Type'] = 'application/octet-stream;name=%s' % Header(rar_file_path, 'UTF-8')
        att['Content-Disposition'] = 'attachment;filename=%s' % Header(rar_file_path, 'UTF-8')
        msg_root.attach(att)

    # 群发邮件
    smtp = smtplib.SMTP(mail_host, 25)
    smtp.login(mail_user, mail_pass)

    smtp.sendmail(sender, recipient_list, msg_root.as_string())
    # 休眠5秒
    time.sleep(2)
    # 断开与服务器的连接
    smtp.quit()