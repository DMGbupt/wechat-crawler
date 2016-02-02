# -*- coding: utf-8 -*-

"""从文本文件提取查询词
"""

import pickle
import random

from crawlers.topics.stocks_name import STOCKS_NAME
from crawlers.topics.stocks_code_sina import STOCK_CODE


stocks_name = STOCKS_NAME  # 股票名称
stocks_code = STOCK_CODE  # 股票编号


def random_stock(num, stocks):
    rel = []
    for i in range(num):
        rel.append(stocks[random.randrange(len(stocks))])
    return rel


def add_to_dict(file_name):
    code = []
    f_in = open(file_name, "r")
    for line in f_in.readlines():
        if len(line.split(" ")) > 3:
            print line
        code.append(line.split(" ")[2].split("/")[-2])  # 存储unicode
    f_in.close()

    f_code = open("../topics/tmp.txt", "w")
    for c in code:
        f_code.write("  u\"{0}\",\n".format(c))
    f_code.close()

    print("SUCCEED!")


add_to_dict("../../doc/stocks.txt")
# for stock in random_stock(10, stocks_name):
#     print stock
