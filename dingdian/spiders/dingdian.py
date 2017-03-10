# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 20:53:50 2017

@author: ohlala
"""
#　命令行中使用scrapy startproject XXXXX创建项目

import re
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request #一个单独的request的模块，需要跟进URL的时候，需要用它
#from ..items import DcontentItem
#from dingdian.items import DingdianItem
#定义的需要保存的字段，（导入dingdian项目中items文件中的DingdianItem类）
from dingdian.items import *
from dingdian.mysqlpipelines.sql import *

class Myspider(scrapy.Spider):   #类继承自scrapy.Spider
    name = 'dingdian'   #爬虫的名字，这name就是我们在entrypoint.py文件中的第三个参数
    allowes_domains = ['http://www.23us.us/'] #使用爬取规则可以只跟进存在于allowed_domains中的URL
    url_s = 'http://www.23us.us/list/'
    url_e = ".html"
    
    def start_requests(self): #获取分类页面地址
        for i in range (1,2): #11
            url = self.url_s + str(i) + '_1' + self.url_e
            print(url)
            yield Request(url, self.parse) 
        #yield Request('http://www.23us.us/quanben/1', self.parse)        
        #使用Request包跟进URL,并将返回的response作为参数传递给回调函数self.parse
        #我的理解是这里将Request给了Scheduler，然后传至Downloader,response返回给callback函数
            
    def parse(self, response): #获取每个分类的所有页面地址
        max_num = BeautifulSoup(response.text, 'lxml').find('div', class_ = 'pagelink').find_all('a')[-1].get_text()
        url_s = str(response.url)[:-7]
        for i in range (1, 2): #int(max_num)+1):
            url = url_s + '_' + str(i) + self.url_e
            #print(url)
            yield Request(url, dont_filter=True, callback=self.get_name)
    
    def get_name(self, response): #获取一个页面中所有小说的主页
        tds = BeautifulSoup(response.text, 'lxml').find_all('tr', bgcolor="#FFFFFF")
#        for td in tds :
#            novelname = td.find('a').get_text()
#            novelurl = td.find('a')['href']
#            yield Request(novelurl, self.get_inf, meta={'name':novelname, 'url':novelurl})
        for i in range(1, 2) :
            novelname = tds[i].find('a').get_text()
            novelurl = tds[i].find('a')['href']
            yield Request(novelurl, self.get_inf, meta={'name':novelname, 'url':novelurl})
            #使用meta字典，在Scrapy中传递额外数据
    
    def get_inf(self, response):  #进入小说主页获取小说信息和章节列表
        item = DingdianItem()  #将导入的item文件进行实例化，用来存储数据
        item['name'] = str(response.meta['name'])  #item[key]  Key就是在items中定义的字段
        item['novelurl'] = str(response.meta['url'])
        item['category'] = BeautifulSoup(response.text, 'lxml').find('table').find('td').get_text().replace('\xa0','')           
        item['author'] = BeautifulSoup(response.text, 'lxml').find('table').find_all('td')[1].get_text().replace('\xa0','')
        item['serialstatus'] = BeautifulSoup(response.text, 'lxml').find('table').find_all('td')[2].get_text().replace('\xa0','')       
        item['serialnumbr'] = BeautifulSoup(response.text, 'lxml').find('table').find_all('td')[4].get_text().replace('\xa0','')        
        bash_url = BeautifulSoup(response.text, 'lxml').find('p', class_ = 'btnlinks').find('a', class_='read')['href']   
        name_id = str(bash_url)[-6:-1].replace('/','')
        item['name_id'] = name_id
        yield item      #返回字典，然后Pipelines可以对这些数据进行处理，不能用return否则程序结束
        yield Request(url=bash_url, callback=self.get_chapter, meta={'name_id':name_id})
    
    def get_chapter(self, response):  #获取章节地址
        urls = re.findall(r'<td class="L"><a href="(.*?)">(.*?)</a></td>', response.text)
        num = 0  #计数器，用于给章节排序
        for url in urls:
            num = num + 1
            chapterurl = response.url + url[0]
            chaptername = url[1]
            rets = Sql.sclect_chapter(chapterurl) #sql语句查重
            if rets[0] == 1:
                print('章节已经存在了')
                pass
            else:
                yield Request(chapterurl, callback=self.get_chaptercontent, meta={'num':num,
                                                                              'name_id':response.meta['name_id'],
                                                                              'chapterurl':chapterurl,
                                                                              'chaptername':chaptername
                                                                              })
    
    def get_chaptercontent(self, response): #获取章节内容
        item = DcontentItem()
        item['num'] = response.meta['num']
        item['id_name'] = response.meta['name_id']
        item['chapterurl'] = response.meta['chapterurl']
        item['chaptername'] = response.meta['chaptername']
        content = BeautifulSoup(response.text, 'lxml').find('dd', id='contents').get_text()
        item['chaptercontent'] = content.replace('\xa0', '')
        return item