# -*- coding: utf-8 -*-

"""微信公众号
"""

import re
import json
from datetime import datetime
from crawlers.index_spider import IndexSpider
from crawlers.items import WeChat
from crawlers.utils.html_formatter import HtmlFormatter
from crawlers.logs.crawler_logger import spider_logger
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Wechat(IndexSpider):
    """
    @summary: 搜狗微信公众号爬虫
    """
    name = "wechat"
    # 搜索页面链接
    _search_url = "http://weixin.sogou.com/weixin?&type=1&query={0}&ie=utf8"

    def _get_result(self, response):
        """
        @summary: 从文章目录页（json格式）中提取具体资讯页面的URL列表
        @param response: 目录页面
        @return: crawlers.items.Base或其子类对象(必须抽取url和publish_time)的列表
        """
        rel = []
        idx1 = response.body.index("{")
        idx2 = response.body.index("}")
        # 解码目录页json数据
        decoded_json = json.loads(response.body[idx1: idx2+1].strip())
        new_data = decoded_json['items']
        # 提取搜索结果
        for result in new_data:
            result = result.encode("utf-8")
            item = WeChat()
            url = re.split("url><!.CDATA.|..></url", result)[1]
            if "http://" not in url:
                item['url'] = "http://weixin.sogou.com" + \
                    re.split("url><!.CDATA.|..></url", result)[1]
            else:
                item['url'] = url
            item['title'] = re.split(
                "title><!.CDATA.|..></title", result)[1].encode('utf8')
            try:
                # 部分文章内容全部由图构成，没有文本摘要，在json数据中没有<content168>标签（即摘要信息），此时爬取的摘要默认为空
                item['digest'] = re.split("content168><!.CDATA.|..></content168", result)[1]
            except Exception, e:
                spider_logger.info("Digest data lack in %s ! Set default value null." % response.url)
                item['digest'] = ""
            publish_time = re.split("date><!.CDATA.|..></date", result)[1]
            item['publish_time'] = datetime.strptime(
                publish_time+" 00:00:00", "%Y-%m-%d %H:%M:%S")
            item['target_topic'] = [
                re.split("sourcename><!.CDATA.|..></sourcename", result)[1]]
            item['source'] = re.split(
                "sourcename><!.CDATA.|..></sourcename", result)[1]
            item['icon'] = re.split(
                "imglink><!.CDATA.|..></imglink", result)[1]
            rel.append(item)
        return rel

    def _next_result_page(self, response):
        """
        @summary: 获取当前目录页的下一页URL
        @param response: 当前的目录页
        @return: 下一页目录的URL或空值
        """
        idx1 = response.body.index("{")
        idx2 = response.body.index("}")
        decoded_json = json.loads(response.body[idx1: idx2+1].strip())
        # 总共可爬取的目录页数
        totalPages = int(decoded_json['totalPages'])
        # 当前所爬页码
        page = int(decoded_json['page'])
        # 比较当前页码与指定爬取的目录页数的大小（先比较了指定爬取的目录页数与总共可爬取的目录页数，避免越界）
        if page < (self.index_pages if self.index_pages<=totalPages else totalPages):
            attr = re.split("=|&", response.url)
            term = attr[1]
            passwd = attr[3]
            nextpage = page+1
            return r"http://weixin.sogou.com/gzhjs?openid={}&ext={}&cb=sogou.weixin_gzhcb&page={}&gzhArtKeyWord=".format(term, passwd, nextpage)
        else:
            # 当前页码已达到本次设置爬取的最后一页，返回空
            spider_logger.info("No pages after {0}!".format(response.url))
            return

    def _finish_item(self, item, response):
        """
        @summary: 处理单个资讯页面，抽取属性并填充item对象
        @mark: 网页的属性可以从self._get_result()或本函数中提取
        @param item: self._get_result()中提取的item对象
        @param response: 当前处理网页
        @return: 处理完毕的item对象或新构造的Request对象
        """
        item['article_addr'] = response.url
        item['crawl_time'] = datetime.now()
        item['website'] = u"微信"
        # 获取正文
        content = response.xpath("//div[@id='js_content']").extract()
        item['content'] = HtmlFormatter.format_content(content[0])
        item['image_urls'] = []
        for image_url in response.xpath("//div[@id='js_content']//img/@data-src").extract():
            if re.match("http.*", image_url):
                item['image_urls'].append(image_url)
        return item
