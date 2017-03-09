# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 20:53:50 2017

@author: ohlala
"""

import re
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request #一个单独的request的模块，需要跟进URL的时候，需要用它
#from ..items import DcontentItem
#from ..items import DingdianItem
#import dingdian.items
from dingdian.items import *
from dingdian.mysqlpipelines.sql import *

#定义的需要保存的字段，（导入dingdian项目中items文件中的DingdianItem类）


class Myspider(scrapy.Spider):
    name = 'dingdian'
    allowes_domains = ['http://www.23us.us/']
    url_s = 'http://www.23us.us/list/'
    url_e = ".html"
    
    def start_requests(self):
        for i in range (1,2): #11
            url = self.url_s + str(i) + '_1' + self.url_e
            print(url)
            yield Request(url, self.parse)
        #yield Request('http://www.23us.us/quanben/1', self.parse)        
        
#使用Request包跟进URL,并将返回的response作为参数传递给回调函数self.parse

    def parse(self, response):
        max_num = BeautifulSoup(response.text, 'lxml').find('div', class_ = 'pagelink').find_all('a')[-1].get_text()
        url_s = str(response.url)[:-7]
        for i in range (1, 2): #int(max_num)+1):
            url = url_s + '_' + str(i) + self.url_e
            print(url)
            yield Request(url, dont_filter=True, callback=self.get_name)
    
    def get_name(self, response):
        tds = BeautifulSoup(response.text, 'lxml').find_all('tr', bgcolor="#FFFFFF")
#        for td in tds :
#            novelname = td.find('a').get_text()
#            novelurl = td.find('a')['href']
#            print(novelurl)
#            print(novelname,'  Q')
#            yield Request(novelurl, self.get_inf, meta={'name':novelname, 'url':novelurl})
        for i in range(1, 2) :
            novelname = tds[i].find('a').get_text()
            novelurl = tds[i].find('a')['href']
            print(novelurl)
            print(novelname,'  Q')
            yield Request(novelurl, self.get_inf, meta={'name':novelname, 'url':novelurl})
    
    def get_inf(self, response):
        item = DingdianItem()
        item['name'] = str(response.meta['name'])
        item['novelurl'] = str(response.meta['url'])
        item['author'] = BeautifulSoup(response.text, 'lxml').find('table').find_all('td')[1].get_text().replace('\xa0','')
        item['serialstatus'] = BeautifulSoup(response.text, 'lxml').find('table').find_all('td')[2].get_text().replace('\xa0','')       
        item['serialnumbr'] = BeautifulSoup(response.text, 'lxml').find('table').find_all('td')[4].get_text().replace('\xa0','')      
        item['category'] = BeautifulSoup(response.text, 'lxml').find('table').find('td').get_text().replace('\xa0','')   
        bash_url = BeautifulSoup(response.text, 'lxml').find('p', class_ = 'btnlinks').find('a', class_='read')['href']   
        name_id = str(bash_url)[-6:-1].replace('/','')
        item['name_id'] = name_id
        yield item
        yield Request(url=bash_url, callback=self.get_chapter, meta={'name_id':name_id})
    
    def get_chapter(self, response):
        urls = re.findall(r'<td class="L"><a href="(.*?)">(.*?)</a></td>', response.text)
        num = 0
        print (urls)
        for url in urls:
            num = num + 1
            chapterurl = response.url + url[0]
            chaptername = url[1]
            rets = Sql.sclect_chapter(chapterurl)
            if rets[0] == 1:
                print('章节已经存在了')
                pass
            else:
                yield Request(chapterurl, callback=self.get_chaptercontent, meta={'num':num,
                                                                              'name_id':response.meta['name_id'],
                                                                              'chapterurl':chapterurl,
                                                                              'chaptername':chaptername
                                                                              })
    
    def get_chaptercontent(self, response):
        item = DcontentItem()
        item['num'] = response.meta['num']
        item['id_name'] = response.meta['name_id']
        item['chapterurl'] = response.meta['chapterurl']
        item['chaptername'] = response.meta['chaptername']
        content = BeautifulSoup(response.text, 'lxml').find('dd', id='contents').get_text()
        item['chaptercontent'] = str(content).replace('\xa0', '')
        return item