"""
视频任务管理类
"""

import Data
from Data import VideoTask, News


# 查询视频任务
def create_task(id: int, force: bool = False) -> VideoTask | None:
	"""
	从数据库中，拿到第id个新闻数据，首先交给AI判断，将其进行栏目分类，如果这个新闻不适合生成视频，则跳过，返回一个None否则，将它创建为视频任务，写进数据库中，并且返回None。
	:param id: 新闻id
	:param force: 是否强制创建视频任务，不管AI判断如何
	:return:
	"""
	# 从数据库中拿到第id个新闻对象
	news: News = Data.get_news(id)
