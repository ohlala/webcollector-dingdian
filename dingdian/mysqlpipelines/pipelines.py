# -*- coding: utf-8 -*-

from .sql import Sql
from dingdian.items import *
#from dingdian.items import DingdianItem
#from dingdian.items import DcontentItem

#启用这个Pipeline应在settings中作如下设置
#ITEM_PIPELINES = {
##    'dingdian.pipelines.DingdianPipeline': 300,
#    'dingdian.mysqlpipelines.pipelines.DingdianPipeline': 1,
#}

#dingdian（项目目录）.mysqlpipelines（自己建立的MySQL目录）.pipelines（自己建立的pipelines
#文件）.DingdianPipeline（其中定义的类）后面的 1 是优先级程度（1-1000随意设置，数值越低，组件的优先级越高）

class DingdianPipeline(object):
    
    def process_item(self, item, spider): #item和spider这两个参数必不可少
        if isinstance(item, DingdianItem):
            name_id = item['name_id']
            ret = Sql.select_name(name_id)
            if ret[0] == 1:
                print('已经存在了')
                pass
            else:
                xs_name = item['name']
                xs_author = item['author']
                category = item['category']
                Sql.insert_dd_name(xs_name, xs_author, category, name_id)
                print('开始存小说标题')
                
        if isinstance(item, DcontentItem):
            url = item['chapterurl']
            name_id = item['id_name']
            num_id = item['num']
            xs_chaptername = item['chaptername']
            xs_content = item['chaptercontent']
            #到Spider中使用url进行查重判断,减少一次Request
            Sql.insert_dd_chaptername(xs_chaptername, xs_content, name_id, num_id, url)
            print('小说存储完毕')
            return item