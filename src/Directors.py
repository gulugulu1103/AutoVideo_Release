import logging
import os
import random
import time
from abc import abstractmethod, ABCMeta

import ChatAIs
import DrawAIs
import MovieEditors
import Spiders
import TTSAIs
import Uploaders
import artUtils
import utils
from MovieEditors import MovieEditor

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                    level = logging.DEBUG)


class Director(metaclass = ABCMeta):
	"""
	导演类
	"""

	@abstractmethod
	def fetch_video_material(self) -> None:
		"""
		获取视频素材，其中包括图片、视频、TTS配音、字幕、期号，没有则现场生成，有则直接使用。
		:return: None
		"""
		pass

	@abstractmethod
	def check_video_material(self) -> bool:
		"""
		审核视频素材是否合法合规，如果不合法合规则返回False，否则返回True。
		:return: bool
		"""
		pass

	@abstractmethod
	def render_video(self) -> None:
		"""
		渲染视频，将素材渲染为视频。
		:return: None
		"""
		pass

	@abstractmethod
	def upload_video(self) -> None:
		"""
		上传视频。
		:return: None
		"""
		pass


class NewsDirector(Director):
	"""
	新闻播报导演类，用于生成新闻播报视频。
	"""

	def __init__(self, date_path: str = None,
	             chat_ai: ChatAIs.ChatAI = ChatAIs.Qwen(),
	             tts_ai: TTSAIs.TextToSpeechAI = TTSAIs.DashScopeTTS(),
	             draw_ai: DrawAIs.DrawAI = DrawAIs.WanXiangDrawAI(),
	             editor: MovieEditor = MovieEditors.MovieEditor(),
	             uploader: Uploaders.Uploader = Uploaders.DouyinNewsUploader(),
	             bgm_path: str = None
	             ):
		"""
		初始化新闻播报导演类，用于生成新闻播报视频。
		:param date_path: 日期路径
		:param chat_ai: 对话AI，用于生成脚本和视频描述
		:param tts_ai: 文字转语音AI，用于生成TTS配音
		:param draw_ai: 绘画AI，用于生成背景图片
		:param editor: 视频编辑器，目前只有movieEditor.MovieEditor，使用的moviepy库
		:param uploader: 上传器，使用爬虫上传
		"""

		logging.debug("[NewsDirector] __init__")
		# 注入
		self.chat_ai = chat_ai
		self.chat_ai.prompt = "以下是近期热点，你在运营一档名为《Ai信息差》的抖音节目的主持人小艾，请生成你的播音稿。对于该条热点，将其进行详细报道并且进行扩写和点评。请控制文本数量在3000字以内。生成不包含标题的演播稿，请以\"这是我生成的稿子：\"为开头。"
		self.tts_ai = tts_ai
		self.draw_ai = draw_ai
		self.editor = editor
		self.uploader = uploader
		self.script = None
		self.description = None
		self.news_str = None
		self.title = None
		# 日期路径
		if date_path is None:
			self.date_path = utils.get_today_dir()
		else:
			self.date_path = date_path
		if bgm_path is None:
			self.bgm_path = "../bin/bgm.flac"
		else:
			self.bgm_path = bgm_path
		# 原始背景图片路径
		self.raw_bg_path = self.date_path + "/input/background.png"
		# 模糊背景图片路径
		self.blured_bg_path = self.date_path + "/input/background_blured.png"
		# 脚本路径
		self.script_path = self.date_path + "/input/script.txt"
		# TTS配音路径
		self.tts_path = self.date_path + "/input/tts.mp3"
		# 字幕路径
		self.subtitle_path = self.date_path + "/input/subtitle.srt"
		# 输出路径
		self.output_path = self.date_path + "/output/output.mp4"
		# 视频描述路径
		self.description_path = self.date_path + "/input/description.json"
		logging.debug("[NewsDirector] __init__" + str(self.__dict__))

	def fetch_video_material(self) -> None:
		"""
		获取视频素材，其中包括图片、视频、TTS配音、字幕、期号，没有则现场生成，有则直接使用。
		:return: None
		"""
		logging.debug("[NewsDirector] fetch_video_material")

		# 生成脚本，如果没有的话
		if not os.path.exists(self.script_path):
			logging.debug("[NewsDirector] fetch_video_material: script not found, generating...")
			self.script = self.generate_script_today()
		else:
			logging.debug("[NewsDirector] fetch_video_material: script found, reading...")
			self.script = utils.read_script(self.script_path)

		# 生成TTS配音
		if not os.path.exists(self.tts_path):
			logging.debug("[NewsDirector] fetch_video_material: tts not found, generating...")
			self.generate_tts_mp3(self.script)
		else:
			logging.debug("[NewsDirector] fetch_video_material: tts found, reading...")

		# 生成背景图片
		if not os.path.exists(self.raw_bg_path):
			logging.debug("[NewsDirector] fetch_video_material: background not found, generating...")
			self.generate_background_today()
		else:
			logging.debug("[NewsDirector] fetch_video_material: background found, reading...")

		# 生成模糊背景图片
		if not os.path.exists(self.blured_bg_path):
			logging.debug("[NewsDirector] fetch_video_material: blured background not found, generating...")
			artUtils.blur_resize(self.raw_bg_path, self.blured_bg_path)
		else:
			logging.debug("[NewsDirector] fetch_video_material: blured background found, reading...")

		# 生成视频描述
		if not os.path.exists(self.description_path):
			self.generate_description()
			logging.debug("[NewsDirector] fetch_video_material: description not found, generating...")
		else:
			self.description = utils.read_description(self.description_path)
			logging.debug("[NewsDirector] fetch_video_material: description found, reading...")

	def generate_script_today(self) -> str:
		"""
		爬取今天的热点，通过和大模型API交互生成《AI评论》的文稿并返回
		:return: 生成的新闻播音稿
		"""
		news = Spiders.WeiBo(
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
				"_zap=2dcd386f-35ef-49b5-9a63-240b320b7295; d_c0=ACAYje8nKBaPTm7hDMFV1rUKWk99Qnz4yik=|1673431945; YD00517437729195%3AWM_TID=4XvSXI3sz8RBVEFUVBbFaZFeQMrN45Ch; __snaker__id=2YUVyUjuyjKNhphF; YD00517437729195%3AWM_NI=kOuUDgVtNcEnT9Dc808Rj11gWKBsOWecfQyYI1NHCec2%2FKRbUxbNE8KxKezYmikZJydCOKcsI%2B4MWFClB5sOpFlDx3a16PMC6g6W9%2FVKj6QVAnE%2BHTrhLDj8D87a9a1nSG8%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6ee8fae49a2ebe185e47a9abc8ea7d14f828e9e86c548a2a79faaea73b5899e8fc42af0fea7c3b92aa991bbb6c76d96ac8284c86698e78c84bb3cfc8ea6d2b46d95958e94ce5da7bdaab2fc538bef82a9c26fa1eee1acd16a97a8aeafc83489a88586f953afb7a5bbc973a89d81ace2798bf5fcaed64e81b48ed6f245b49aa4a5fb39a3effab1d049f6b9fab8bc259695a6d7d45e83b28bcccb60b2b884a5e93488e8f982bc6bf3b29da8bb37e2a3; q_c1=46ae590826624150bc0c04f866ca348a|1678936637000|1678936637000; z_c0=2|1:0|10:1699939230|4:z_c0|80:MS4xUmE2RkNBQUFBQUFtQUFBQVlBSlZUUUtzTldiUXd1ZzN3VTJxMGgwVWdFUmpVeVdwS2pLN09RPT0=|6667fdde5e996d9294a22c1ab0fc13ab54ce6f26fa898705d038d79c1dab18f6; tst=h; _xsrf=296cef34-d81d-494b-acbf-17e9f048a554; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1699688361,1699836450,1699938459,1700052688; SESSIONID=cV7o1YemROdq41wgEq8pDgKoGGdAdz3RjbTCcyGRHdX; JOID=VF8WBU-bIILX6tUpUJtzELEEAEpD-XKwutmNSDjLbuKj3OZfM0-f0bLp0ChXtsAVXly1a11xoPfHDx52pX2yu88=; osd=Ul0cBU-dIojX6tMrWptzFrMOAEpF-3iwut-PQjjLaOCp3OZZMUWf0bTr2ihXsMIfXlyzaVdxoPHFBR52o3-4u88=; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1700052726; KLBRSID=76ae5fb4fba0f519d97e594f1cef9fab|1700052728|1700052685",
				"https://www.zhihu.com/hot").Crawl()
		logging.debug("[NewsDirector] generate_script_today: found news here:" + str(news).replace('\n\n', ' '))
		prompt = "你是"
		# 截短新闻列表长度
		# while len(str(news)) > 4600:
		# 	news.pop()
		# logging.debug("[NewsDirector] generate_script_today: trimmed news here:" + str(news).replace('\n\n', ' '))

		error_cnt = 0
		while True:
			# 随机选择一个新闻
			chosen_news = news[random.randint(0, len(news) - 1)]
			# self.news_str = "标题：" + chosen_news["title"] + "正文：" + chosen_news["content"]
			self.news_str = chosen_news["title"] + chosen_news["content"]
			self.title = chosen_news["title"]

			# 构造容易阅读的新闻串字符串
			# self.news_str = ""
			# for i, each in zip(range(0, len(news)), news):
			# 	_ = f"新闻{i + 1}标题:" + each['title'] + f"\n新闻{i + 1}正文：" + each['content'] + "\n"
			# 	self.news_str += _
			logging.debug(
					"[NewsDirector] generate_script_today: news_str for reading:" + str(self.news_str).replace('\n\n',
					                                                                                           ' '))
			try:
				self.script = self.chat_ai.ask_once(self.news_str)
			except:
				# TODO: 补完报错信息
				logging.error("[NewsDirector] ")
				error_cnt += 1
				continue

			logging.debug(
					"[NewsDirector] generate_script_today: generated script:" + str(self.script).replace('\n\n', ' '))
			if "：\n" not in self.script:
				logging.warn("重试中")
				time.sleep(3)
				error_cnt += 1
				continue
			elif error_cnt > 5:
				# TODO: 补完报错信息
				raise Exception("e")
			else:
				break

		# 截取"生成的稿子：\n\n后面的内容"
		i = self.script.index("：\n")
		self.script = self.script[i + 2:]  # 从该位置之后截取字符串
		logging.debug("[NewsDirector] generate_script_today: trimmed script:" + str(self.script).replace('\n\n', ' '))
		utils.save_script(self.script)
		return self.script

	def check_video_material(self) -> bool:
		"""
		审核视频素材是否合法合规，如果不合法合规则返回False，否则返回True。
		:return: bool
		"""
		return True

	def render_video(self, fps=60) -> None:
		"""
		渲染视频，使用MovieEditor编辑视频。
		:param fps:
		:return:
		"""
		self.editor.create_subtitled_video(background_path = self.blured_bg_path, audio_path = self.tts_path,
		                                   output_path = self.output_path, subtitle_path = self.subtitle_path,
		                                   bgm_path = self.bgm_path, video_title = None,
		                                   fps = fps)

	def upload_video(self) -> None:
		self.uploader.upload(file_path = self.output_path, video_description = self.description)

	def generate_tts_mp3(self, script):
		"""
		生成tts配音
		:param script: 脚本
		:return: None
		"""
		self.tts_ai.create_audio_once(script, self.tts_path, self.subtitle_path)

	def generate_background_today(self):
		"""
		生成背景图片
		:return: None
		"""
		# ai = ChatAIs.ErnieBot()
		# ai.ask_once()
		png_link = self.draw_ai.create_art_once("新闻播报 AI 信息 背景 麦克风")
		utils.save_background(png_link)

	def generate_description(self):
		"""
		生成视频描述
		:return: None
		"""
		# 要交给uploader进行视频简介生成，因为每个平台对应的简介不一样。
		self.description = self.uploader.generate_description(chat_ai = self.chat_ai, video_script = self.script)
		logging.info("[NewsDirector] Got generated description :" + str(self.description))
		utils.save_description(self.description)


class ChatDirector(Director):
	def fetch_video_material(self) -> None:
		pass

	def check_video_material(self) -> bool:
		pass

	def render_video(self) -> None:
		pass

	def upload_video(self) -> None:
		pass
