import os
from datetime import datetime

import Data
import ffmpeg
import requests
from bs4 import BeautifulSoup

import config
import utils
from Data import News


class WeiBo:
	"""
	微博热搜爬虫
	"""

	def __init__(self, UserAgent, Cookie, Url):
		self.Headers = { "User-Agent": UserAgent, "Cookie": Cookie }
		self.Url = Url

	##爬取成功 返回列表  爬取失败返回None
	def Crawl(self):
		response = requests.get(headers = self.Headers, url = self.Url)
		if response.ok:
			soup = BeautifulSoup(response.text, "html.parser")
			all = soup.findAll("div", attrs = { "class": "HotItem-content" })
			list = []
			for item in all:
				if item.find("p") != None:
					list.append({ "title": item.find("h2").text, "content": item.find("p").text })
			return list
		else:
			print("爬取失败，请检查输入的UserAgent和Cookie是否有效。")
			return None


class ZhihuHotSpider:
	"""
	知乎热榜爬虫
	"""

	def __init__(self):
		self.Headers = config.SPYDER_ZHIHU_HEADER
		self.Url = "https://www.zhihu.com/hot"

	def get_news_list(self) -> list[dict]:
		response = requests.get(headers = self.Headers, url = self.Url)
		if response.ok:
			soup = BeautifulSoup(response.text, "html.parser")
			all = soup.findAll("section", attrs = { "class": "HotItem" })
			list = []
			for item in all:
				if item.find("p") is not None and item.find("img") is not None:
					list.append({ "title"           : item.find("h2").text,
					              "content"         : item.find("p").text,
					              "source"          : item.find("a").get("href"),
					              "source_site_name": "zhihu",
					              "fetched_at"      : datetime.now(),
					              # 如果出现，则截取?source=前的内容
					              "cover_url"       : item.find("img").get("src").split("?source=")[0],
					              })
			return list
		else:
			raise Exception("爬取失败，请检查输入的UserAgent和Cookie是否有效。")

	def fetch_and_write_news(self) -> list[News]:
		"""
		获取知乎热榜，将封面转码为jpg格式，写入数据库中。最后，返回这个列表。
		"""

		news_list: list[dict] = self.get_news_list()
		News_list: list[News] = []

		for news in news_list:
			News_list.append(
					News(
							title = news["title"],
							content = news["content"],
							source = news["source"],
							source_site_name = news["source_site_name"],
							fetched_at = news["fetched_at"],
							cover_url = news["cover_url"],
					)
			)
		# 下载cover_url中的图片，并把不是.jpg的图片使用ffmpeg-python转换为.jpg
		for news in News_list:
			# 下载图片
			response = requests.get(news.cover_url)
			# 如果图片是.jpg格式，则直接保存
			if response.headers["Content-Type"] == "image/jpeg":
				news.cover_data = response.content
			# 如果图片不是.jpg格式，则使用ffmpeg-python转换为.jpg
			else:
				# 保存图片到临时文件夹
				# 首先删除临时文件夹中的temp.jpg
				if os.path.exists("../temp/temp.jpg"):
					os.remove("../temp/temp.jpg")
				# 取得后缀名
				suffix = response.headers["Content-Type"].split("/")[-1]
				input_file_name = f"../temp/temp.{suffix}"
				output_file_name = "../temp/temp.jpg"
				utils.download(news.cover_url, input_file_name)
				# 使用ffmpeg-python转换为.jpg
				input_file = ffmpeg.input(input_file_name)
				output_file = (ffmpeg
				               .output(input_file, output_file_name))
				ffmpeg.run(output_file)
				with open("../temp/temp.jpg", "rb") as f:
					news.cover_data = f.read()
		Data.write_news(news_list = News_list)
		return News_list
