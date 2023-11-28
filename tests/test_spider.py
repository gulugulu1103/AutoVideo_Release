import random
import time
import unittest

import Spiders


class TestZhihuSpider(unittest.TestCase):
	def test_get_news_list(self):
		news = Spiders.ZhihuHotSpider().get_news_list()
		for each in news:
			print(each)

	def test_fetch_and_write_news(self):
		Spiders.ZhihuHotSpider().fetch_and_write_news()

	def test_continuous_fetch_and_write_news(self):
		# 每间隔一段时间爬取一次
		while True:
			Spiders.ZhihuHotSpider().fetch_and_write_news()
			time.sleep(60 * 60 * random.randint(3, 6))
