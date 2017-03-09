# -*- coding: utf-8 -*-

import mysql.connector
#from dingdian import settings

MYSQL_HOSTS ='127.0.0.1' 
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'aywk'
MYSQL_PORT = '3389'
MYSQL_DB = 'xiaoshuo'

cnx = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOSTS, database=MYSQL_DB)
cur = cnx.cursor(buffered=True)
class Sql:
    
    @classmethod
    def insert_dd_name(cls, xs_name, xs_author, category, name_id):
        sql = 'INSERT INTO dd_name (`xs_name`, `xs_author`, `category`, `name_id`) VALUES (%(xs_name)s,%(xs_author)s,%(category)s,%(name_id)s)'
        value = {
            'xs_name':xs_name,
            'xs_author':xs_author,
            'category':category,
            'name_id':name_id
        }
        cur.execute(sql, value)
        cnx.commit()
    
    @classmethod 
    def select_name(cls, name_id):
        sql = "SELECT EXISTS(SELECT 1 FROM dd_name WHERE name_id=%(name_id)s)"
        value = {
            'name_id':name_id
        }
        cur.execute(sql, value)
        return cur.fetchall()[0]  
  #Cursor对象执行select语句时，通过featchall()可以拿到结果集。结果集是一个list
    @classmethod
    def insert_dd_chaptername(cls, xs_chaptername, xs_content, id_name, num_id, url):
        sql = 'INSERT INTO dd_chaptername (`xs_chaptername`, `xs_content`, `id_name`, `num_id`, `url`)\
                VALUE (%(xs_chaptername)s, %(xs_content)s, %(id_name)s, %(num_id)s, %(url)s)'
        value = {
            'xs_chaptername': xs_chaptername,
            'xs_content': xs_content,
            'id_name' : id_name, 
            'num_id': num_id, 
            'url': url
        }
        cur.execute(sql, value)
        cnx.commit()
    
    @classmethod
    def sclect_chapter(cls, url):
        sql = "SELECT EXISTS(SELECT 1 FROM dd_chaptername WHERE url=%(url)s)"
        value = {
            'url':url
        }
        cur.execute(sql, value)
        return cur.fetchall()[0]  
    