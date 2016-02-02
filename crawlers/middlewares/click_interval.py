# -*- coding: utf-8 -*-

"""模拟用户点击浏览间隔时间，指数分布，每分钟点击3次
"""

import random
import time

class  ClickInterval(object):

    def process_request(self, request, spider):
        time.sleep(60*random.expovariate(3))
        return None
