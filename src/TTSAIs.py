import base64
import hashlib
import hmac
import http
import json
import logging
import time
import urllib
import uuid
from abc import ABCMeta, abstractmethod
from urllib import parse

import azure.cognitiveservices.speech as speechsdk
import dashscope
import requests
from dashscope import SpeechSynthesizer

import config
import utils


class TextToSpeechAI(metaclass = ABCMeta):
	"""
	语音合成AI抽象类，定义了语音合成AI的接口
	"""

	@abstractmethod
	def create_audio_once(self, text: str, download_mp3_path: str, download_subtitle_path: str) -> None:
		"""
		创建语音，将语音和字幕文件下载到download_path
		:param text: text
		:param download_mp3_path: 音频的下载路径
		:param download_subtitle_path: 字幕的下载路径
		:return: 无
		"""

	@abstractmethod
	def create_audio_multi(self, text: str, times: int) -> str:
		"""
		创建语音，返回下载地址
		:param text: text
		:return: 下载地址
		"""


class BaiduTextToSpeechAI(TextToSpeechAI):
	"""
	百度语音合成AI
	"""

	API_KEY = config.TTS_BAIDU_API_KEY
	SECRET_KEY = config.TTS_BAIDU_SECRET_KEY

	def create_audio_once(self, text: str, download_mp3_path: str, download_subtitle_path: str) -> None:
		"""
		创建语音，将语音和字幕文件下载到download_path
		:param text: text
		:param download_mp3_path: 音频的下载路径
		:param download_subtitle_path: 字幕的下载路径
		:return: None
		"""
		logging.debug("[BaiduTextToSpeechAI] Got text, text = " + text.replace("\n", " ").strip())
		task_id = self.create_task(text)
		logging.debug("[BaiduTextToSpeechAI] Created text to speech task,  task_id = " + task_id)
		while self.parser_response(self.query_task(task_id)) is None:
			time.sleep(3)
		# 处理response，获得mp3和time_stamp
		mp3_link, time_stamps = self.parser_response(self.query_task(task_id))
		# 下载mp3
		utils.download(mp3_link, download_mp3_path)
		# 得到srt字符串
		srt = utils.timestamps_to_srt(time_stamps)
		# 写入字幕文件
		with open(download_subtitle_path, "w", encoding = 'utf-8') as f:
			f.write(srt)

	def create_audio_multi(self, text_list: list) -> list:
		"""
		批量创建语音，返回下载地址列表
		:param text_list: text列表
		:return: 下载地址列表
		"""
		download_urls = []
		for text in text_list:
			download_urls.append(self.create_audio_once(text, ))
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

	def create_task(self, text, fmt="mp3-48k", voice=106, lang="zh", speed=7, pitch=5, volume=7, enable_subtitle=1,
	                brk=660) -> str | None:
		"""
		创建语音，返回创建成功的task_id
		:param fmt: 输出音频格式
		:param text: 文本
		:param voice: 发音人选择
		:param lang: 语言
		:param speed: 语速
		:param pitch: 音高
		:param volume: 音量
		:param enable_subtitle: 是否开启字幕
		:param brk: 停顿时间，单位ms
		:return: task_id
		"""
		url = "https://aip.baidubce.com/rpc/2.0/tts/v1/create?access_token=" + self.get_access_token()

		payload = json.dumps({
			"text"           : text,
			"format"         : fmt,
			"voice"          : voice,
			"lang"           : lang,
			"speed"          : speed,
			"pitch"          : pitch,
			"volume"         : volume,
			"enable_subtitle": enable_subtitle,
			"break"          : brk,

		})
		headers = {
			'Content-Type': 'application/json',
			'Accept'      : 'application/json'
		}

		response = requests.request("POST", url, headers = headers, data = payload)
		logging.debug("[BaiduTextToSpeechAI] Posted request, response = " + response.text)

		j = response.json()
		if j["task_status"] == "Created":
			return j["task_id"]
		else:
			return None

	def query_task(self, task_id) -> dict | None:
		"""
		查询任务状态
		:param task_id: 任务ID
		:return: json
		"""
		url = "https://aip.baidubce.com/rpc/2.0/tts/v1/query?access_token=" + self.get_access_token()

		payload = json.dumps({
			"task_ids": [
				task_id
			]
		})
		headers = {
			'Content-Type': 'application/json',
			'Accept'      : 'application/json'
		}

		response = requests.request("POST", url, headers = headers, data = payload)
		return response.json()

	def parser_response(self, response):
		"""
	 	处理query_task获得的response，获得mp3和time_stamp
		:param response: json
		:return: MP3文件地址和time_stamp或者None
		"""
		response = response["tasks_info"][0]
		if response["task_status"] == "Success":
			response = response["task_result"]
			mp3 = response["speech_url"]
			time_stamp = response["speech_timestamp"]["sentences"]
			return mp3, time_stamp
		else:
			return None


class AzureTTS(TextToSpeechAI):
	"""
	微软的语音合成AI，调试url：https://speech.microsoft.com/portal/8790fff05c5b4fc3b74dec9bbcb18fa2/voicegallery
	For more samples please visit https://github.com/Azure-Samples/cognitive-services-speech-sdk
	"""
	# TODO: 比较拉，没有自己生成字幕的功能，只能生成mp3

	# 创建一个带有指定订阅密钥和服务区域的语音配置实例。
	SPEECH_KEY = config.TTS_AZURE_SPEECH_KEY
	service_region = "eastasia"

	speech_config = speechsdk.SpeechConfig(subscription = SPEECH_KEY, region = service_region)
	# 注意：语音设置不会覆盖输入 SSML 中的语音元素。
	# TODO: 设置语音合成的语速，现在的语速有点慢
	# 设置语音合成的讲话人。
	speech_config.speech_synthesis_voice_name = "zh-CN-YunyangNeural"
	# 设置语音输出格式。
	speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3)
	speech_config.request_word_level_timestamps()
	speech_config.output_format = speechsdk.OutputFormat(1)

	def __init__(self):
		logging.debug("[AzureTTS] Inited successfully!")

	def create_audio_once(self, text: str, download_mp3_path: str, download_subtitle_path: str) -> None:
		# 设置语音输出位置。
		audio_config = speechsdk.audio.AudioOutputConfig(filename = download_mp3_path)
		# 开始生成语音
		speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config = self.speech_config,
		                                                 audio_config = audio_config)
		# 得到结果
		result = speech_synthesizer.speak_text_async(text).get()

		# 解析结果
		# 解析成功
		if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
			logging.info("[AzureTTS] Speech synthesized for text [{}]".format(text))
		# 解析失败
		elif result.reason == speechsdk.ResultReason.Canceled:
			cancellation_details = result.cancellation_details
			logging.info("[AzureTTS] Speech synthesis canceled: {}".format(cancellation_details.reason))
			if cancellation_details.reason == speechsdk.CancellationReason.Error:
				if cancellation_details.error_details:
					logging.error("[AzureTTS] Error details: {}".format(cancellation_details.error_details))
					logging.error("[AzureTTS] Did you set the speech resource key and region values?")

		# 开始生成srt字幕
		print(str(result))

	def create_audio_multi(self, text: str, times: int) -> str:
		pass


class DashScopeTTS(TextToSpeechAI):

	def __init__(self):
		dashscope.api_key = config.TTS_DASHSCOPE_API_KEY

	def create_audio_once(self, text: str, download_mp3_path: str, download_subtitle_path: str) -> None:
		ssml_text = self.pre_SSML(text)
		logging.debug("[DashScopeTTS] Got SSML text : " + ssml_text.replace("\n", " ").strip())
		result = SpeechSynthesizer.call(model = 'sambert-zhide-v1',
		                                text = ssml_text,
		                                sample_rate = 48000,
		                                format = 'mp3',
		                                rate = 1.1,
		                                volume = 85,
		                                word_timestamp_enabled = True,
		                                )
		# 保存文件到当前目录
		if result.get_audio_data() is not None:
			with open(download_mp3_path, 'wb') as f:
				f.write(result.get_audio_data())

			word_timestamps = result.get_timestamps()
			# 拿到字级时间戳，使用算法来进行句级时间戳的生成
			time_stamps = []
			for sentence in word_timestamps:
				d = { "begin_time"    : sentence["begin_time"], "end_time": sentence["end_time"],
				      "sentence_texts": "".join([word["text"] for word in sentence["words"]]) }
				time_stamps.append(d)
			srt = utils.timestamps_to_srt(time_stamps)
			# 写入字幕文件
			with open(download_subtitle_path, "w", encoding = 'utf-8') as f:
				f.write(srt)

	def pre_SSML(self, text: str) -> str:
		"""
		将一些文本进行SSML预处理，使得语音合成更加自然，首要保证字音读准。
		:param text: 需要处理的源文本
		:return: 处理后的SSML
		"""
		replace_dict = {
			"信息差": "<phoneme alphabet=\"py\" ph=\"xin4 xi1 cha1\">信息差</phoneme>",
		}

		for key in replace_dict.keys():
			text = text.replace(key, replace_dict[key])
		return f"<speak>{text}</speak>"

	def create_audio_multi(self, text: str, times: int) -> str:
		pass


class NLSTTS(TextToSpeechAI):
	"""
	阿里云API，该服务名叫“智能语音交互”，短时间的语音生成只能
	Console：https://nls-portal.console.aliyun.com/overview
	DOC: https://help.aliyun.com/document_detail/130555.html
	"""

	def __init__(self):
		self.appkey = config.TTS_NLS_APPKEY
		self.AccessKeyID = config.TTS_NLS_ACCESSKEYID
		self.AccessKeySecret = config.TTS_NLS_ACCESSKEYSECRET

	def create_audio_once(self, text: str, download_mp3_path: str, download_subtitle_path: str) -> None:
		"""
		创建语音，将语音和字幕文件下载到download_path
		:param text: text
		:param download_mp3_path: 音频的下载路径
		:param download_subtitle_path: 字幕的下载路径
		:return: None
		"""
		logging.debug("[NLS] Got text, text = " + text.replace("\n", " ").strip())
		task_id = self.create_task(text)
		logging.debug("[NLS] Created text to speech task,  task_id = " + task_id)
		error_count = 0
		while self.parser_response(self.query_task(task_id)) is None:
			time.sleep(5)
			error_count += 1
			logging.debug(f"[NLS] It seems like the task {task_id} is still running, retrying......")
			if error_count > 10:
				logging.error("[NLS] Opps, There's an error " + str(self.query_task(task_id)))
				raise Exception("Opps, There's an error " + str(self.query_task(task_id)))

		# 处理response，获得mp3和time_stamp
		mp3_link, time_stamps = self.parser_response(self.query_task(task_id))
		# 下载mp3
		utils.download(mp3_link, download_mp3_path)
		# 得到srt字符串
		srt = self.timestamps_to_srt(time_stamps)
		# 写入字幕文件
		with open(download_subtitle_path, "w", encoding = 'utf-8') as f:
			f.write(srt)

	def create_audio_multi(self, text_list: list) -> list:
		"""
		批量创建语音，返回下载地址列表
		:param text_list: text列表
		:return: 下载地址列表
		"""
		download_urls = []
		for text in text_list:
			download_urls.append(self.create_audio_once(text, ))
			time.sleep(3)
		return download_urls

	def get_access_token(self):
		"""
		使用 AK，SK 生成鉴权签名（Access Token）
		:return: access_token, expire_time，或是None(如果错误)
		"""

		def _encode_text(text):
			encoded_text = parse.quote_plus(text)
			return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')

		def _encode_dict(dic):
			keys = dic.keys()
			dic_sorted = [(key, dic[key]) for key in sorted(keys)]
			encoded_text = parse.urlencode(dic_sorted)
			return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')

		parameters = { 'AccessKeyId'     : self.AccessKeyID,
		               'Action'          : 'CreateToken',
		               'Format'          : 'JSON',
		               'RegionId'        : 'cn-shanghai',
		               'SignatureMethod' : 'HMAC-SHA1',
		               'SignatureNonce'  : str(uuid.uuid1()),
		               'SignatureVersion': '1.0',
		               'Timestamp'       : time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
		               'Version'         : '2019-02-28' }
		# 构造规范化的请求字符串
		query_string = _encode_dict(parameters)
		print('规范化的请求字符串: %s' % query_string)
		# 构造待签名字符串
		string_to_sign = 'GET' + '&' + _encode_text('/') + '&' + _encode_text(query_string)
		print('待签名的字符串: %s' % string_to_sign)
		# 计算签名
		secreted_string = hmac.new(bytes(self.AccessKeySecret + '&', encoding = 'utf-8'),
		                           bytes(string_to_sign, encoding = 'utf-8'),
		                           hashlib.sha1).digest()
		signature = base64.b64encode(secreted_string)
		print('签名: %s' % signature)
		# 进行URL编码
		signature = _encode_text(signature)
		print('URL编码后的签名: %s' % signature)
		# 调用服务
		full_url = 'http://nls-meta.cn-shanghai.aliyuncs.com/?Signature=%s&%s' % (signature, query_string)
		print('url: %s' % full_url)
		# 提交HTTP GET请求
		response = requests.get(full_url)
		if response.ok:
			root_obj = response.json()
			key = 'Token'
			if key in root_obj:
				token = root_obj[key]['Id']
				expire_time = root_obj[key]['ExpireTime']
				return token, expire_time
		print(response.text)
		return None, None

	def create_task(self, text,
	                voice="xiaoyun", sample_rate=16000,
	                format: str = "mp3", enable_subtitle=True) -> str | None:
		"""
		创建语音，返回创建成功的task_id

		:return: task_id
		"""
		url = "	https://nls-gateway.cn-shanghai.aliyuncs.com/rest/v1/tts/async"

		payload = json.dumps({
			"payload"      : {
				"tts_request": {
					"voice"          : voice,
					"sample_rate"    : sample_rate,
					"format"         : format,
					"text"           : text,
					"enable_subtitle": enable_subtitle,
				}
			},
			"enable_notify": False,
			"header"       : {
				"appkey": self.appkey,
				"token" : self.get_access_token()[0],
			}
		})
		headers = {
			'Content-Type': 'application/json',
			"appkey"      : self.appkey,
			"token"       : self.get_access_token()[0],

		}
		context = {
			"device_id": "my_device_id",
		}

		response = requests.request("POST", url, headers = headers, data = payload)
		logging.debug("[BaiduTextToSpeechAI] Posted request, response = " + response.text)

		j = response.json()
		print(j)
		if j["status"] == http.HTTPStatus.OK:
			return j["data"]["task_id"]
		else:
			logging.error("[BaiduTextToSpeechAI] Error at creating task: " + str(j))
			return None

	def query_task(self, task_id) -> dict | None:
		"""
		查询任务状态，返回response.json()
		:param task_id: 任务ID
		:return: json
		"""
		url = \
			rf"https://nls-gateway.cn-shanghai.aliyuncs.com/rest/v1/tts/async?appkey={self.appkey}&task_id={task_id}&token={self.get_access_token()[0]}"

		host = { "Host"      : "nls-gateway.cn-shanghai.aliyuncs.com", "Accept": "*/*",
		         "Connection": "keep-alive", 'Content-Type': 'application/json' }

		response = urllib.request.urlopen(url).read()
		j = json.loads(response)
		logging.debug("[NLS] Got response, response = " + str(j))
		return j

	def parser_response(self, response):
		"""
	 	处理query_task获得的response，获得mp3和time_stamp
		:param response: json
		:return: MP3文件地址和time_stamp或者None
		"""
		if response["status"] != http.HTTPStatus.OK:
			logging.error("[NLS] Error at querying task: " + str(response))
			raise Exception("[NLS] Error at querying task: " + str(response))

		if response["error_message"] == "SUCCESS":
			response = response["data"]
			mp3 = response["audio_address"]
			time_stamp = response["sentences"]
			return mp3, time_stamp
		elif response["error_message"] == "RUNNING":
			logging.debug("[NLS] The task is still running")
			return None
		else:
			raise Exception("[NLS] Error at querying task: " + str(response))

	def timestamps_to_srt(self, timestamps: list) -> str:
		"""
		将时间戳数据转换为 srt 文件内容
		:param timestamps: 时间戳数据列表
		:return:
		"""
		# 解析时间戳数据为 Python 列表
		data = timestamps
		# 创建一个空字符串，用于存储 srt 文件内容
		srt = ""
		# 遍历时间戳数据中的每个字典
		for item, i in zip(data, range(0, len(data))):
			# 获取字典中的段落序号、文本、开始时间和结束时间
			index = i
			text = item["text"]
			start = int(item["begin_time"])
			end = int(item["end_time"])
			# 将开始时间和结束时间转换为 srt 格式的时间字符串
			start_srt = utils.ms_to_srt(start)
			end_srt = utils.ms_to_srt(end)
			# 将序号、时间范围、文本和空行拼接到 srt 文件内容中
			srt += f"{index}\n{start_srt} --> {end_srt}\n{text}\n\n"
		# 返回 srt 文件内容
		return srt
