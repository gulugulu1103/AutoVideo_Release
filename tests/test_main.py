import os
import unittest

import utils
from Directors import NewsDirector
from Uploaders import DouyinNewsUploader


class TestMain(unittest.TestCase):
	def test_main(self):
		# 生成脚本
		director = NewsDirector()
		director.fetch_video_material()
		director.render_video(fps = 30)
		os.startfile(os.path.abspath(utils.get_today_dir() + "output/output.mp4"))
		# 上传
		uploader = DouyinNewsUploader()
		file_path = utils.get_today_dir() + "output/output.mp4"
		with open(utils.get_today_dir() + "input/description.json", "r", encoding = 'utf-8') as f:
			description = f.read()
			uploader.upload(file_path = file_path, video_description = description)
