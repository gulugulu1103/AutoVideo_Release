import logging
import os
import unittest

import ChatAIs
import utils
from Directors import Director, NewsDirector

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                    level = logging.DEBUG)


class TestNewsDirector(unittest.TestCase):

	def setUp(self):
		print("setUp")

	def test_init(self):
		director = NewsDirector()
		self.assertIsInstance(director, Director)

	def test_render_old_video(self):
		director = NewsDirector(date_path = "../daily/2023_11_05/")
		director.fetch_video_material()
		director.render_video(fps = 30)
		os.startfile(os.path.abspath("../daily/2023_11_05/output/output.mp4"))

	def test_font_list(self):
		from moviepy.video.VideoClip import TextClip
		font_list = TextClip.list('font')
		print(TextClip.search('', 'font'))  # 搜索字体名字中含Courier的字体

	# 构建在font_list中名字含s的列表

	def test_render_new_video(self):
		director = NewsDirector()
		director.fetch_video_material()
		director.render_video(fps = 1)
		os.startfile(os.path.abspath(utils.get_today_dir() + "output/output.mp4"))

	def test_generate_news_today(self):
		director = NewsDirector(chat_ai = ChatAIs.Qwen())
		print("We got this : ")
		print(director.generate_script_today())

	def tearDown(self):
		print("tearDown")
