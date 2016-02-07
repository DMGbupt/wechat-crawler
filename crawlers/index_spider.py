# -*- coding: utf-8 -*-

import urllib2
import cookielib
import time
import random
from datetime import datetime
from datetime import timedelta
from abc import ABCMeta, abstractmethod
from scrapy import Spider
from scrapy import Request
from scrapy.exceptions import CloseSpider
from logs.crawler_logger import spider_logger

class IndexSpider(Spider):
    """
    @summary: 以搜狗微信公众号搜索页面"weixin.sogou.com"为入口的爬虫的抽象基类
    @mark: 子类只须实现抽象方法并提供self._search_url属性
    """
    __metaclass__ = ABCMeta  # 实现抽象基类
    # 搜索页面的搜索公众号链接，用{0}代替搜索词
    _search_url = ""
    # 字符集，默认为utf8
    _char_set = "utf8"

    def __init__(self,
                 query=None,
                 start_time=None,
                 end_time=None,
                 crawl_mode=None):
        """
        @summary: 用于向爬虫传递参数, 请注意默认参数仅供测试使用
        @param query: 搜索词,单个公众号名称
        @param start_time: 仅爬取发布时间在start_time之后的网页，须保证目录页面中的网页以时间排序。
        @param end_time: 仅爬取发布时间在end_time之前的网页
        @param crawl_mode: 爬取模式
        """
        # 搜索词，为了减小反爬概率，每次只搜索一条公众号并爬取
        if query:
            self.query = query # self.query为单条要搜索的公众号名字
        else:
            # 必须提供要搜索的公众号名字，否则报错并停止爬虫
            spider_logger.error("Spider need single search word each time!Check input!")
            raise CloseSpider('invaild search word')
        # 起始时间，默认值爬虫启动时间的100日前
        if start_time:
            self.from_time = start_time
        else:
            self.from_time = datetime.now()-timedelta(days=100)  # 默认值：100日前
        # 终止时间，默认值为当前时刻
        if end_time:
            self.end_time = end_time
        else:
            self.end_time = datetime.now()  # 默认值：当前时刻
        # 爬取模式，1为全量抓取，2为增量抓取
        if crawl_mode:
            self.crawl_mode = int(crawl_mode)
        else:
            self.crawl_mode = 2 # 默认值：增量抓取

    def start_requests(self):
        """
        @summary:启动爬虫时会首先调用这个方法，子类不需要重构
        """
        try:
            cookies = self.get_cookie(self.query) # 获取cookie,爬取公众号必须有cookie
            yield Request(self._search_url.format(self.query),callback=self.parse_search,cookies=cookies,meta ={'cookies':cookies,'query':self.query})
        except Exception, e:
                spider_logger.error("Query {0} can't be encoded in {1}, because of {2}!".format(self.query, self.name, e))
        '''
        """以下为废弃版本，self.query为一个数组，此时for循环会增加搜索并发量，很容易被反爬，故不要再尝试了
        """
        squery = None
        for squery in self.query:
            try:
                cookies = self.get_cookie(squery)
                yield Request(self._search_url.format(squery),callback=self.parse_search,cookies=cookies,meta ={'cookies':cookies,'query':squery})
            except Exception, e:
                spider_logger.error("Query {0} can't be encoded in {1}, because of {2}!".format(squery, self.name, e))
        '''

    def parse_search(self, response):
        """
        @summary: 处理搜索结果页面，最后发起request请求文章目录页
        @param response:start_requests()方法发送的请求所返回的响应
        """
        # 搜狗的反爬措施是返回一条验证码链接，链接中含有"antispider"字样
        # 故遇到含"antispider"的链接说明已被搜狗锁定，需停止爬虫，等待解封后再次爬取
        if "antispider" in response.url:
            spider_logger.error("Closing spider for verification code received in %s ! Spider will restart automatically after 12 hours!" % response.url)
            time.sleep(43200) # 等待下次爬取的时间，单位为秒
            raise CloseSpider('antispider')
        # ext变量是获取公众号文章目录页数据（json格式）的url中的关键字段，每次搜索都不一样
        ext = response.xpath(
            '//div[@class="wx-rb bg-blue wx-rb_v1 _item"][1]/@href').extract() # 获取公众号搜索结果页面中的第一个公众号（即要爬的公众号）的ext变量
        if not ext:
            spider_logger.error("Faild searching {0} !".format(response.meta['query']))
            return
        # 拼接获取目录页json数据的url：一个公众号通常有10页文章目录，这里拼接的是第1页(page=1参量决定)的url
        json_url = "".join(ext).replace('/gzh?','http://weixin.sogou.com/gzhjs?')+'&cb=sogou.weixin_gzhcb&page=1&gzhArtKeyWord='
        cookies = response.meta['cookies']
        yield Request(json_url, callback= self.parse_index, cookies=cookies, meta ={'cookies':cookies})

    def parse_index(self, response):
        """
        @summary: 处理目录页面，返回指向待爬取网页的Request列表
        @param response: parse_search()方法发送的请求所返回的响应
        @return: list，里边是目录页每篇文章的url和时间，按时间倒序排列
        """
        if "antispider" in response.url:
            spider_logger.error("Closing spider for verification code received in %s ! Spider will restart automatically after 12 hours!" % response.url)
            time.sleep(43200)
            raise CloseSpider('antispider')
        requests = []
        page_list = self._get_result(response)
        # 如果目录中没有内容，返回空列表
        if not page_list:
            return requests
        next_page = True  # 目录是否需要翻页
        # 逐条测试从目录中提取的网页列表
        for item in page_list:
            if isinstance(item, Request):  # 返回了新的Request
                requests.append(item)
                next_page = False
                break
            if item['publish_time'] <= self.from_time:  # 网页发布时间早于self.from_time
                next_page = False
                break
            elif item['publish_time'] > self.end_time:  # 网页发布时间晚于self.end_time
                continue
            else:
                req = Request(item['url'], self.parse_page)
                # 传递已抽取信息
                req.meta["item"] = item
                requests.append(req)
        # 如需要翻页,添加下一页的Request;否则关闭生成器
        if next_page and self._next_result_page(response):
            cookies = response.meta['cookies']
            requests.append(Request(self._next_result_page(response),callback=self.parse_index,cookies=cookies, meta ={'cookies':cookies}))
        return requests

    def parse_page(self, response):
        """
        @summary: 处理一个网页
        @param response: parse_index()方法发送的请求所返回的响应
        @return: 一个列表，_finish_item()所处理的结果
        """
        if "antispider" in response.url:
            spider_logger.error("Closing spider for verification code received in %s ! Spider will restart automatically after 12 hours!" % response.url)
            time.sleep(43200)
            raise CloseSpider('antispider')
        item = response.meta["item"]
        return self._finish_item(item, response)

    def get_cookie(self,query):
        """
        @summary: 获取cookie
        @param query: 待搜索的公众号名字
        @return: 有效cookie或空
        """
        cookies={}
        i=0
        while True:
            cookie = cookielib.CookieJar()
            handler=urllib2.HTTPCookieProcessor(cookie)
            opener = urllib2.build_opener(handler)
            response = opener.open(self._search_url.format(query)) # 向搜狗发送搜索请求，获取返回的cookie
            for item in cookie:
                # 搜狗会检查请求中携带的cookie中是否有SNUID字段，如果没有则认为是爬虫
                # 故含有SNUID字段的cookie才是有效cookie，可以在发送请求时携带
                if("SNUID" in item.name):
                    cookies[item.name]=item.value
                    return cookies
            if(i>3):
                # 重复发送3次搜索请求都未获得有效cookie，说明该IP已被搜狗封了，此时返回空cookie，后续操作会停止爬虫
                spider_logger.error("Can't get cookies when searching {0} !".format(query))
                return cookies
            i=i+1
            time.sleep(10*random.expovariate(1)) # 随机休息一段时间等待下次发送搜索请求，时间间隔符合指数分布

    @abstractmethod
    def _get_result(self, response):
        """
        @summary: 从目录页面中获取网页列表
        @param response: 目录页面
        @return: crawlers.items.Base或其子类对象(必须抽取url和publish_time)的列表
        """
        pass

    @abstractmethod
    def _next_result_page(self, response):
        """
        @summary: 抽取下一页目录的URL
        @param response: 当前处理的目录页面
        @return: 下一页目录的URL
        """
        pass

    @abstractmethod
    def _finish_item(self, item, response):
        """
        @summary: 处理单个网页，抽取属性并填充item对象
        @mark: 网页的属性可以从self._get_result()或本函数中提取
        @param item: self._get_result()中提取的item对象
        @param response: 当前处理网页
        @return: 处理完毕的item对象或新构造的Request对象
        """
        pass
