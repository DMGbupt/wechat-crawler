爬虫使用说明：
1、数据库配置：
	crawlers/setting.py中须要修改数据库连接信息DB_CONFIG
	crawlers/utils/create_db： 自动建表脚本，需手动执行，可不使用
	数据库说明详见doc文件夹下的说明文档
2、启动爬虫
	I.在项目目录下输入： scrapy crawl crawler_name ，其中crawler_name为crawlers/spiders中各爬虫文件的文件名
	II.运行启动脚本crawlers/initiator.py
3、关于正文部分(content)的说明:
	正文部分放在一个<div></div>标签内，其中
	使用<p></p>和<br>标签分段，保留<table>及相关标签用于记录表格的格式信息，保留<img>标签用于记录图片信息，删除了其他标签
	清除了所有标签的属性以及css样式等内容
	<img>标签仅保留了src属性，属性值为本地下载的图片相对于存储图片的目录的位置，一般为"full/文件名"
4、索引模块：
	使用crawlers/index/indexer.py中Indexer的get方法获取索引的writer和searcher。
	新闻和博客的索引是分开的
	索引不支持多进程/线程写，可多进程/线程读

其他：
1、文件结构：
	crawlers/database：dao类
	crawlers/index: 索引读写模块
    crawlers/pipelines: 各种pipeline
    crawlers/spiders: 各网站的爬虫
    crawlers/topics: 结巴分词扩展词典，以及爬虫使用的查询词
    crawlers/utils: 附加工具脚本
    crawlers/index_spider.py: 爬虫的基类，定义了从一个目录页面（例如搜索结果页面）为入口爬取网页的流程
    crawlers/items.py: 爬取的各种item,如新闻、博客、研报等等
    crawlers/setting.py 爬虫设置
    doc: 爬虫的数据库设计文档和测试文档
    initiator.py:爬虫启动脚本
    test.py:索引测试脚本
2、index_spider为所有爬虫的抽象基类，实现了以目录页面（例如搜索结果页面）为入口爬取网页的流程
    _init()_的参数中：
		queries： 传递搜索词，即股票名称，较特殊的，新浪新闻需要股票编码；
		          不提供此参数时从crawlers/stocks_name或crawlers/stocks_code中读取股票名称和编码。
		from_time: 仅爬取发布时间在from_time之后的网页，目录中的网页列表按时间排序。利用这一参数，可实现爬虫快速收敛；
				   不提供此参数时，默认爬取最近100天内发布的文章。
3、过滤和去重
	crawlers.pipelines/filter是过滤模块，已实现的具体去重规则请参看注释
	crawlers/pipelines/duplicate_removal是去重模块，已实现的具体去重规则请参看注释
4、正文处理
	crawlers/utils/html_formatter.py是正文处理方法