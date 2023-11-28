import unittest

import utils
from Uploaders import DouyinNewsUploader


class TestUploader(unittest.TestCase):

	def test_douyin_upload(self):
		uploader = DouyinNewsUploader()
		file_path = "../daily/2023_11_13/output/output.mp4"
		with open("../daily/2023_11_13/input/description.json", "r", encoding = 'utf-8') as f:
			description = f.read()
			uploader.upload(file_path = file_path, video_description = description)

	def test_douyin_upload_today(self):
		today_dir = utils.get_today_dir()
		file_path = today_dir + "output/output.mp4"
		uploader = DouyinNewsUploader()
		with open(today_dir + "input/description.json", "r", encoding = 'utf-8') as f:
			description = f.read()
			uploader.upload(file_path = file_path, video_description = description)
