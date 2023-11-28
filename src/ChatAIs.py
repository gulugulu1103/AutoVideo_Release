import json
import logging
import time
from abc import abstractmethod, ABCMeta
from http import HTTPStatus

import dashscope
import requests
from dashscope.api_entities.dashscope_response import Role

import config

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                    level = logging.DEBUG)


class ChatAI(metaclass = ABCMeta):
	"""
	对话大模型AI抽象类，定义了对话大模型AI的接口
	"""
	prompt = ""

	@abstractmethod
	def ask_once(self, question) -> str:
		"""
		对话大模型AI的问答，返回一个回答，不改变self.messages
		:param question: 问题
		:return: 回答
		"""

	@abstractmethod
	def conversation(self, question: str) -> str:
		"""
		开始对话，更新self.messages，并返回最新的回答
		:return: 回答
		"""

	@abstractmethod
	def end_conversation(self) -> None:
		"""
		结束对话，清空self.messages
		:return: None
		"""


class ErnieBot(ChatAI):
	"""
	百度文心一言API，Ernie Bot的对话大模型AI
	"""

	API_KEY = config.LLM_Ernie_API_KEY
	SECRET_KEY = config.LLM_Ernie_SECRET_KEY
	# 用于对话的消息列表
	messages: list = []
	prompt: str = ""

	def __init__(self, prompt=""):
		"""
		初始化ErnieBot，设置prompt
		:param prompt: prompt
		"""
		self.prompt = prompt
		logging.debug("ErnieBot inited successfully! prompt = {0}".format(self.prompt))

	def get_once_response(self, question, messages=None) -> json:
		if messages is None:
			messages = [
				{
					"role"   : "user",
					"content": question
				},
			]

		url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + self.get_access_token()

		payload = json.dumps({
			"messages": messages,
			"system"  : self.prompt
		})

		headers = {
			'Content-Type': 'application/json'
		}

		response = requests.request("POST", url, headers = headers, data = payload)
		while "error_code" in response.json():
			logging.warning("[ErnieBot] Error at parsing response: " + str(response.json()) + ", retrying...")
			time.sleep(3)
			response = requests.request("POST", url, headers = headers, data = payload)
		return response.json()

	def parse_response(self, response) -> str:
		answer = response["result"]
		return answer

	def ask_once(self, question) -> str:
		logging.debug("[ErnieBot] Asked once: " + question)
		_ = self.get_once_response(question)
		answer = self.parse_response(_)
		logging.debug("[ErnieBot] Answered : answer = " + answer)
		return answer

	def conversation(self, question) -> str:
		logging.debug("[ErnieBot] Asked in conversation: " + question)
		self.messages.append({
			"role"   : "user",
			"content": question
		})
		response = self.get_once_response(question, self.messages)
		answer = self.parse_response(response)
		logging.debug("[ErnieBot] Answered : answer = " + answer)
		self.messages.append({
			"role"   : "assistant",
			"content": answer
		})
		return answer

	def end_conversation(self) -> None:
		self.messages = []
		logging.debug("[ErnieBot] All messages cleared.")

	def get_access_token(self):
		"""
		使用 AK，SK 生成鉴权签名（Access Token）
		:return: access_token，或是None(如果错误)
		"""
		url = "https://aip.baidubce.com/oauth/2.0/token"
		params = { "grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY }
		return str(requests.post(url, params = params).json().get("access_token"))


class Qwen(ChatAI):
	"""
	对话大模型AI，Qwen的对话大模型AI。
	"""

	def __init__(self, prompt="你好，你需要回答我的问题。"):
		dashscope.api_key = config.LLM_DASHSCOPE_API_KEY
		self.prompt = prompt
		self.messages = []

	def ask_once(self, question) -> str:
		response = dashscope.Generation.call(
				model = 'qwen-max',
				prompt = self.prompt + question,
				enable_search = True,
				top_p = 0.5,
				temperature = 1,
				result_format = 'message',
				seed = 9879,
				max_length = 1500
		)
		if response.status_code == HTTPStatus.OK:
			print(response.output.choices[0].message.content)
			return response.output.choices[0].message.content
		else:
			logging.error('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
				response.request_id, response.status_code,
				response.code, response.message
			))
			raise Exception('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
				response.request_id, response.status_code,
				response.code, response.message
			))

	def conversation(self, question: str) -> str:
		if not self.messages:
			# 如果self.messages为空，说明是第一次对话，需要加入self.prompt
			self.messages = ([{ "role"   : Role.SYSTEM,
			                    "content": self.prompt,
			                    },
			                  { "role"   : Role.USER,
			                    "content": question,
			                    }])
		else:
			# 如果self.messages不为空，说明不是第一次对话，不需要加入self.prompt，并且需要加入上一次的回答
			self.messages.append({ 'role'   : Role.USER,
			                       'content': question })
		response = dashscope.Generation.call(
				model = dashscope.Generation.Models.qwen_plus,
				messages = str(self.messages),
				enable_search = True,
				top_p = 0.5,
				temperature = 1,
				result_format = 'message',
				seed = 1234,
				max_length = 1500
		)
		if response.status_code == HTTPStatus.OK:
			answer = response.output.choices[0].message.content
			logging.debug("[Qwen] Answered in conversation: " + answer)
			# 将回答加入self.messages
			self.messages.append({ 'role'   : response.output.choices[0]['message']['role'],
			                       'content': answer })
			return answer
		else:
			logging.error('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
				response.request_id, response.status_code,
				response.code, response.message
			))
			raise Exception('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
				response.request_id, response.status_code,
				response.code, response.message
			))

	def end_conversation(self) -> None:
		self.messages = []
		logging.debug("[Qwen] All messages cleared.")
