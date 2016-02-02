# -*- coding: utf-8 -*-

"""whoosh索引，news和blog各自维护一个索引
"""

import os

from whoosh import index
from whoosh.fields import *
from jieba.analyse import ChineseAnalyzer
from jieba import load_userdict

from crawlers.settings import INDEX_DIR, DICT
from writer import Writer
from searcher import Searcher


# 加载自定义词典
load_userdict(DICT)
# 索引定义
analyzer = ChineseAnalyzer()  # 分词器
schema = Schema(id=NUMERIC(stored=True),  # 数据库主键
                title=TEXT(stored=True, analyzer=analyzer),  # 新闻标题
                source=ID(stored=True),  # 新闻源
                author=KEYWORD(stored=True, commas=True),  # 作者
                publish_time=DATETIME(stored=True, sortable=True),  # 发布时间
                digest=STORED,  # 摘要
                content=TEXT(stored=True, analyzer=analyzer)  # 正文
                )

# 索引路径
index_dir = {
    "news": INDEX_DIR+"/news",
    "blog": INDEX_DIR+"/blog",
}


class Indexer(object):
    """索引类,用于获取writer和searcher。
    writer只能打开一个，使用单例模式实现，不支持多进程同步；
    searcher每次打开一个新的，支持进程\线程同步。
    """

    __index__ = {}
    __writer__ = {}

    @staticmethod
    def __load__(region=None):
        """加载/建立索引
        :param region: 索引范围，None表示加载所有索引；news\blog表示加载对应索引
        :return: 是否加载成功
        """
        # 加载索引
        if region:
            if region in Indexer.__index__:
                return True
            else:
                if region not in index_dir:
                    return False
                if not os.path.exists(index_dir[region]):
                    os.makedirs(index_dir[region])
                    Indexer.__index__[region] = index.create_in(index_dir[region], schema, indexname=region)
                else:
                    Indexer.__index__[region] = index.open_dir(index_dir[region], indexname=region)
                return True
        else:  # 加载全部索引
            for reg in index_dir.keys():
                if reg in Indexer.__index__:
                    return True
                else:
                    if not os.path.exists(index_dir[reg]):
                        os.mkdir(index_dir[reg])
                        Indexer.__index__[reg] = index.create_in(index_dir[reg], schema, indexname=reg)
                    else:
                        Indexer.__index__[reg] = index.open_dir(index_dir[reg], indexname=reg)
                    return True

    @staticmethod
    def get_writer(index_name):
        """获取writer，单例模式。
        不允许同时打开两个writer，故不支持多进程操作
        :param: 索引名
        :return: region索引的Writer
        """
        if index_name not in Indexer.__writer__:
            Indexer.__load__(index_name)
            Indexer.__writer__[index_name] = Writer(Indexer.__index__[index_name])
        return Indexer.__writer__[index_name]

    @staticmethod
    def get_searcher(index_name):
        """
        :return: 新闻索引的Searcher
        """
        if index_name not in Indexer.__index__:
            Indexer.__load__(index_name)
        return Searcher(Indexer.__index__[index_name])


def add_word(word):
    """向自定义字典中增加词。
    增加的词将在下次启动索引模块时生效
    """
    dictionary = open(DICT, 'a')
    dictionary.write(word+" 5 nz\n")
    dictionary.close()
