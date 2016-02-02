# -*- coding: utf-8 -*-

"""读whoosh索引
"""

from whoosh.query import *
from scrapy import log

class Searcher(object):
    """读索引
    """

    def __init__(self, index):
        self.index = index
        self.searcher = None

    def search(self, query, page_num=1, page_len=100):
        """搜索词.
        每个对象仅维持一个查询，新的查询会使上一次查询自动失效
        :param query: 搜索词
        :param page_num: 读取结果中的第几页，从1开始；默认值：1
        :param page_len: 每页中的结果数
        :return: 搜索结果
        """
        term = Or([Term("title", query), Term("content", query)])
        if self.searcher:
            self.searcher.close()
        self.searcher = self.index.searcher()
        return self.searcher.search_page(term, page_num, page_len, sortedby="publish_time", reverse=True)

    def search_author(self, author, page_num=1, page_len=100):
        """搜索作者.
        每个对象仅维持一个查询，新的查询会使上一次查询自动失效
        :param query: 要搜索作者
        :param page_num: 读取结果中的第几页，从1开始；默认值：1
        :param page_len: 每页中的结果数
        :return: 搜索结果
        """
        term = Term("author", author)
        if self.searcher:
            self.searcher.close()
        self.searcher = self.index.searcher()
        return self.searcher.search_page(term, page_num, page_len, sortedby="publish_time", reverse=True)