import time

import utils
from Directors import NewsDirector

if __name__ == '__main__':
	while True:
		config = utils.get_config()
		# 检测是否到达新的一天
		while time.strftime("%Y_%m_%d", time.localtime()) <= config["last_date"]:
			print("还没到新的一天，等待中")
			time.sleep(60 * 30)
			config = utils.get_config()
		# 检测是否到达晚上
		# while not utils.is_night():
		# 	print("还没到晚上，等待中")
		# 	time.sleep(60 * 30)
		print("开始运行")

		director = NewsDirector()
		director.fetch_video_material()
		director.render_video(fps = 30)
		director.upload_video()

		# 记录最后成功生成的日期
		config["last_date"] = time.strftime("%Y_%m_%d", time.localtime())
		utils.write_config(config)
