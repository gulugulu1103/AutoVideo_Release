import os.path
import unittest

import utils


class TestUtils(unittest.TestCase):
	def test_get_today_dir(self):
		print(utils.get_today_dir())

	def test_download(self):
		utils.download(os.path.abspath("../daily/2023_11_03/input/background.png"), "baidu.png")
