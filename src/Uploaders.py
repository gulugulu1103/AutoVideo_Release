import logging
import time
from abc import ABCMeta, abstractmethod

from playwright.sync_api import sync_playwright

import ChatAIs

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                    level = logging.DEBUG)


class Uploader(metaclass = ABCMeta):
	"""
	上传器基类
	"""

	@abstractmethod
	def generate_description(self, chat_ai: ChatAIs.ChatAI, video_script: str) -> str:
		"""
		根据视频脚本生成视频描述
		:param chat_ai: 对话大模型AI
		:param video_script: 视频脚本
		:return: 视频描述
		"""
		pass

	@abstractmethod
	def upload(self, file_path: str, video_description: str) -> None:
		"""
		上传视频
		:param file_path: 文件路径
		:param video_description_path: 视频描述路径
		:return: None
		"""
		pass


class DouyinNewsUploader(Uploader):

	def upload(self, file_path: str, video_description: str) -> None:
		with sync_playwright() as playwright:
			browser = playwright.chromium.launch_persistent_context(
					headless = False,
					user_data_dir = f"../bin/playwright_usr_cache"
			)

			page = browser.new_page()
			page.goto("https://creator.douyin.com/creator-micro/content/upload")
			# page.locator("label").click()
			page.locator("input").set_input_files(file_path)
			page.locator(".zone-container").click()
			page.locator(".zone-container").fill(video_description)

			# 选择视频分类
			# page.locator("div").filter(has_text = re.compile(r"^视频分类请选择视频内容分类$")).locator("svg").nth(
			# 	1).click()
			# page.locator("li").filter(has_text = "社会时政").click()
			# page.get_by_text("新闻资讯", exact = True).click()
			#
			# 选择视频标签
			# page.get_by_placeholder("输入后按 Enter 键可添加自定义标签").fill("国内新闻")
			# page.get_by_placeholder("输入后按 Enter 键可添加自定义标签").press("Enter")
			# page.get_by_role("textbox").fill("新闻评论")
			# page.get_by_role("textbox").press("Enter")
			# page.get_by_role("textbox").fill("国际新闻")
			# page.get_by_role("textbox").press("Enter")

			# 点击发布
			time.sleep(60)
			page.get_by_role("button", name = "发布", exact = True).click()
			# page.locator("body").set_input_files(r"C:\Users\gulugulu1103\OneDrive\Python\AutoVideo\daily\2023_10_25\output\output.mp4")
			# page.locator(".mask--1_QzR").click()
			# page.locator(".zone-container").click()
			# page.locator(".zone-container").fill("# 你好，这是作品描述​")
			# page.get_by_role("button", name = "发布", exact = True).click()
			# page.get_by_role("button", name = "确定").click()

			# ---------------------

			# ---------------------
			browser.close()

	def generate_description(self, chat_ai: ChatAIs.ChatAI, video_script: str) -> str:
		"""
		根据视频脚本生成视频描述
		:param chat_ai: 对话大模型AI
		:param video_script: 视频脚本
		:return: 视频描述
		"""
		douyin_description = chat_ai.ask_once(
				f"{video_script}\n\n对于以上文稿，写一个适合抖音的视频描述，可以使用#标上话题， 回答以“以下为视频描述：”开头：")

		# 如果没有以下字样，则继续对话
		while not "：\n" in douyin_description:
			douyin_description = chat_ai.ask_once(
					f"{video_script}\n\n对于以上演播稿，写一个适合抖音的视频描述，可以使用#标上话题， 回答以“以下为视频描述：”开头：")
			time.sleep(5)

		i = douyin_description.find("以下为视频描述：\n\n")  # 找到\n的位置
		douyin_description = douyin_description[i + 10:]  # 从该位置之后截取字符串
		return douyin_description
