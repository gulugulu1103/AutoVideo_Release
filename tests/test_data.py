import unittest

import Data
import Spiders


class TestNews(unittest.TestCase):
	def test_create_tables(self):
		Data.create_tables()

	def test_alter_tables(self):
		Data.alter_tables()

	def test_write_news(self):
		news_list = Spiders.ZhihuHotSpider().fetch_and_write_news()
