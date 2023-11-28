import unittest

import DrawAIs
from DrawAIs import BaiduDrawBot, DrawAI


class TestBaiduDrawBot(unittest.TestCase):
	def setUp(self):
		print("setUp")

	def test_init(self):
		ai = BaiduDrawBot()
		self.assertIsInstance(ai, BaiduDrawBot)
		self.assertIsInstance(ai, DrawAI)


class TestWanXiangDrawAI(unittest.TestCase):
	def setUp(self):
		print("setUp")

	def test_init(self):
		ai = DrawAIs.WanXiangDrawAI()
		self.assertIsInstance(ai, DrawAIs.WanXiangDrawAI)
		self.assertIsInstance(ai, DrawAI)

	def test_create_art_once(self):
		ai = DrawAIs.WanXiangDrawAI()
		response = ai.create_art_once("新闻播报 AI 信息查 背景 麦克风")
		print(str(response))
		self.assertIsInstance(response, str)
