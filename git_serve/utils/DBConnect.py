# -*- coding:utf-8 -*-
__author__ = 'changjie.fan'

""""""
from MySQLdb import connect, OperationalError


class DBConnect:
    def __init__(self, host, db, user, password, charset='utf8'):
        self.conn = connect(host=host, db=db, user=user, passwd=password, charset=charset)
        self.cursor = self.conn.cursor()

    def db_close(self):
        """关闭数据库连接"""

        self.cursor.close()
        self.conn.close()

    def execute_query(self, sql=''):
        """执行查询语句"""

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def insert_many(self, insert_sql, values=[]):
        """执行批量插入语句"""

        self.cursor.executemany(insert_sql, values)
        self.conn.commit()

    def insert_one(self, insert_sql):
        """执行插入一条记录语句"""

        self.cursor.execute(insert_sql)
        self.conn.commit()

if __name__ == '__main__':
    try:
        db = DBConnect('192.168.33.6', 'tms', 'root', 'root')
    except OperationalError, e:
        print e