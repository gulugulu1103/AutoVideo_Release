import json
import logging
import time
from abc import ABCMeta, abstractmethod
from http import HTTPStatus

import dashscope
import requests
from dashscope import ImageSynthesis

import config

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                    level = logging.DEBUG)


class DrawAI(metaclass = ABCMeta):
	"""
	画图AI抽象类，定义了画图AI的接口
	"""

	@abstractmethod
	def create_art_once(self, prompt: str) -> str:
		"""
		创建画作，返回下载地址
		:param prompt: text
		:return: 下载地址
		"""
		pass

	@abstractmethod
	def create_art_multi(self, prompt: str, times: int) -> str:
		"""
		创建画作，返回下载地址
		:param prompt: text
		:return: 下载地址
		"""
		pass


class BaiduDrawBot(DrawAI):
	"""
	百度画图AI，继承自DrawAI
	"""

	API_KEY = config.DRAW_BAIDU_API_KEY
	SECRET_KEY = config.DRAW_BAIDU_SECRET_KEY

	def __init__(self):
		logging.debug("[BaiduDrawBot] __init__")

	def create_art_once(self, prompt: str) -> str:
		"""
		创建画作，返回下载地址
		:param prompt: text
		:return: 下载地址
		"""
		logging.debug("[BaiduDrawBot] Got prompt, ready to create task: prompt = " + prompt)
		task_id = self.create_task(prompt)
		download_url = self.query_task(task_id)
		return download_url

	def create_art_multi(self, prompt: str, times: int) -> list:
		"""
		创建多个画作，返回下载地址列表
		:param prompt: text
		:param times: 下载次数
		:return: 下载地址列表
		"""
		logging.debug("[BaiduDrawBot] create_art_multi: prompt = " + prompt + " times = " + str(times))
		download_urls = []
		for i in range(times):
			download_urls.append(self.create_art_once(prompt))
			time.sleep(3)
		return download_urls

	def get_access_token(self):
		"""
		使用 AK，SK 生成鉴权签名（Access Token）
		:return: access_token，或是None(如果错误)
		"""
		url = "https://aip.baidubce.com/oauth/2.0/token"
		params = { "grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY }
		return str(requests.post(url, params = params).json().get("access_token"))

	def create_task(self, prompt, width=1440, height=2560) -> str:
		"""
		创建新闻背景，返回创建成功的task_id
		:return: task_id
		"""
		logging.debug(
				"[BaiduDrawBot] create_task: text = " + prompt + " width = " + str(width) + " height = " + str(
						height))
		url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2?access_token=" + self.get_access_token()

		payload = json.dumps({
			"prompt" : prompt,
			"version": "v2",
			"width"  : width,
			"height" : height
		})
		headers = {
			'Content-Type': 'application/json',
			'Accept'      : 'application/json'
		}

		response = requests.request("POST", url, headers = headers, data = payload)
		logging.debug("[BaiduDrawBot] create_task: response = " + response.text)
		task_id = str(response.json()["data"]["primary_task_id"])
		logging.debug("[BaiduDrawBot] create_task: task_id = " + task_id)
		return task_id

	def query_task(self, task_id: str) -> str:
		"""
		查询task_id的工作进度，返回下载链接
		:param task_id: 从create_task返回的task_id
		:return: 解析出的下载链接
		"""
		logging.debug("[BaiduDrawBot] query_task: task_id = " + task_id)
		url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2?access_token=" + self.get_access_token()

		payload = json.dumps({
			"task_id": str(task_id)
		})
		headers = {
			'Content-Type': 'application/json',
			'Accept'      : 'application/json'
		}

		response = requests.request("POST", url, headers = headers, data = payload).json()
		logging.debug("[BaiduDrawBot] Got response from the server = " + str(response))
		# 请求出错
		if "error_code" in response:
			logging.error("[BaiduDrawBot] Opps, There's an error " + str(response))
			raise Exception("Opps, There's an error " + str(response))

		# task_id正在运行中
		while response["data"]["task_status"] == "RUNNING":
			logging.info(f"[BaiduDrawBot] It seems like the task {task_id} is still running, retrying......")
			time.sleep(3)
			response = requests.request("POST", url, headers = headers, data = payload).json()
			logging.debug("[BaiduDrawBot] Got response from the server = " + str(response))

		download_url = response["data"]["sub_task_result_list"][0]["final_image_list"][0]["img_url"]
		logging.debug(f"[BaiduDrawBot] Oh, now we got this task {task_id} finished, link here:" + download_url)
		return download_url


class PexelsDrawAI(DrawAI):
	"""
	Pexels素材库，API文档：https://www.pexels.com/zh-cn/api/documentation/
	"""
	API_KEY = config.DRAW_PEXELS_API_KEY

	def create_art_once(self, prompt: str) -> str:
		pass

	def create_art_multi(self, prompt: str, times: int) -> str:
		pass


class WanXiangDrawAI(DrawAI):
	"""
	万象画作，API文档：https://www.xfyun.cn/doc/words/word2picture/API.html
	"""
	dashscope.api_key = config.DRAW_WANXIANG_API_KEY

	def create_art_once(self, prompt: str) -> str:
		"""
		创建画作，返回下载地址
		:param prompt:
		:return:
		"""
		response = ImageSynthesis.call(model = ImageSynthesis.Models.wanx_v1,
		                               prompt = prompt,
		                               n = 1,
		                               size = "720*1280")
		if response.status_code == HTTPStatus.OK:
			logging.debug(response.output)
			logging.debug(response.usage)
			# save file to current directory
			if response.output.task_status == "SUCCEEDED":
				return response.output.results[0].url
			else:
				logging.error('Failed, task_id: %s, task_status: %s, results: %s'
				              % (response.output.task_id, response.output.task_status, response.output.results))
				raise Exception('Failed, ' + str(response))
		else:
			logging.error('Failed, status_code: %s, code: %s, message: %s' %
			              (response.status_code, response.code, response.message))
			raise Exception('Failed, status_code: %s, code: %s, message: %s' %
			                (response.status_code, response.code, response.message))

	def create_art_multi(self, prompt: str, times: int) -> str:
		pass
