# -*- coding: utf-8 -*-

"""写whoosh索引
"""

class Writer(object):
    """写索引
    """

    def __init__(self, index):
        self.index = index

    def write(self, item):
        """写索引。
        非线程安全方法，调用时需在外部同步。
        :param item: 写入索引的对象
        """
        src = item['url']  # 来源
        if item['source']:
            src = item['source']
        writer = self.index.writer()
        writer.add_document(id=item['id'], title=item['title'], source=src, author=item['author'],
                            publish_time=item['publish_time'], digest=item['digest'], content=item['content'])
        writer.commit()
