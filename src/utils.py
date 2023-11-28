import json
import os
import time


def download(url: str, position: str):
	"""
	下载文件
	:param url:下载链接
	:param position:路径
	:return:
	"""
	import requests as re
	file = re.get(url)
	with open(position, 'wb') as f:
		f.write(file.content)


def ms_to_srt(ms) -> str:
	"""
	将毫秒转换为 srt 格式的时间字符串
	:param ms:
	:return:
	"""
	# 计算小时、分钟、秒和毫秒
	hours = ms // (1000 * 60 * 60)
	minutes = (ms % (1000 * 60 * 60)) // (1000 * 60)
	seconds = (ms % (1000 * 60)) // 1000
	milliseconds = ms % 1000
	# 返回格式化的时间字符串，补齐两位数和三位数
	return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def timestamps_to_srt(timestamps: list) -> str:
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
		text = item["sentence_texts"]
		start = int(item["begin_time"])
		end = int(item["end_time"])
		# 将开始时间和结束时间转换为 srt 格式的时间字符串
		start_srt = ms_to_srt(start)
		end_srt = ms_to_srt(end)
		# 将序号、时间范围、文本和空行拼接到 srt 文件内容中
		srt += f"{index}\n{start_srt} --> {end_srt}\n{text}\n\n"
	# 返回 srt 文件内容
	return srt


def date_str():
	"""
	返回时间字符串，用于演播稿使用。
	:return:
	"""
	wdaynum = time.localtime(time.time())
	weekday = ("周日", "周一", "周二", "周三", "周四", "周五", "周六")[wdaynum.tm_wday]
	return time.strftime("%Y年%m月%d日", time.localtime()) + " " + weekday


def get_today_dir():
	"""
	获取今天的文件夹路径
	:return:
	"""
	dir = "../daily/"
	if not os.path.exists(dir):
		os.mkdir(dir)
	date = time.strftime("%Y_%m_%d", time.localtime())
	today_folder = dir + date
	if not os.path.exists(today_folder):
		os.mkdir(today_folder)
	if not os.path.exists(today_folder + "/input"):
		os.mkdir(today_folder + "/input/")
	if not os.path.exists(today_folder + "/output"):
		os.mkdir(today_folder + "/output")
	return today_folder + "/"


def write_config(j):
	with open(os.path.abspath("../config/config.json"), "w+") as f:
		f.write(json.dumps(j, indent = 4))


def get_config() -> dict:
	with open(os.path.abspath("../config/config.json"), "r+") as f:
		j = f.read()
		return json.loads(j)


def get_cnt() -> int:
	cfg = get_config()
	return cfg["cnt"]


def add_cnt():
	cfg = get_config()
	cfg["cnt"] += 1
	write_config(cfg)


def save_tts_mp3(url):
	download(url, get_today_dir() + "/input/tts.mp3")


def save_background(url):
	download(url, get_today_dir() + "/input/background.png")


def save_srt(txt):
	with open(get_today_dir() + "/input/subtitle.srt", 'w', encoding = 'utf-8') as f:
		f.write(txt)


def save_script(txt):
	with open(get_today_dir() + "/input/script.txt", 'w', encoding = 'utf-8') as f:
		f.write(txt)


def read_script(script_path):
	with open(script_path, 'r', encoding = 'utf-8') as f:
		return f.read()


def save_description(txt):
	with open(get_today_dir() + "/input/description.json", 'w', encoding = 'utf-8') as f:
		f.write(txt)


def read_description(description_path):
	with open(description_path, 'r', encoding = 'utf-8') as f:
		return f.read()


def is_night():
	"""
	判断是否为晚上
	:return:
	"""
	hour = time.localtime().tm_hour
	return hour >= 18


if __name__ == "__main__":
	print(get_cnt())
