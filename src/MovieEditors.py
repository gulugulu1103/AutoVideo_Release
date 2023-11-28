import logging
import re

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import TextClip, ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

import utils

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                    level = logging.DEBUG)


class MovieEditor:
	def create_subtitled_video(self, background_path, audio_path, output_path, subtitle_path, bgm_path,
	                           project_title: str = None, video_title: str = None,
	                           fps=30):
		"""
		将背景图片和语音合成为短视频，并在短视频中加入字幕，标题副标题，背景音乐。
		:param background_path: 背景路径
		:param audio_path: 语音路径
		:param output_path: 输出路径
		:param subtitle_path: 字幕路径
		:param bgm_path: 背景音乐路径
		:param project_title: 视频的标题，将放在短视频中间。
		:param video_title: 视频的副标题，将放在短视频下方。
		:param fps: 帧率, 默认为30
		:return:
		"""
		# 合成clip的列表
		composite_list = []

		# Load audio as a moviepy audio clip
		audio = AudioFileClip(audio_path, nbytes = 4, fps = 48000)
		duration = audio.duration  # Set the duration of the video (in seconds)

		# Load background music as a moviepy audio clip
		bgm = None
		if bgm_path is not None:
			from moviepy.audio.fx import audio_fadein, audio_normalize
			bgm = AudioFileClip(bgm_path, nbytes = 4, fps = 48000)
			bgm = audio_normalize.audio_normalize(bgm)
			# multiply the volume by 0.5 (half the original volume)
			bgm = bgm.fl(lambda get_frame, t: 0.1 * get_frame(t), keep_duration = True)
			bgm.duration = duration
			bgm.set_duration(duration)
			bgm = audio_fadein.audio_fadein(bgm, 1.686)
			bgm.set_fps(48000)

		# Create a black background video
		# black_clip = mp.ColorClip(size = (1920, 1080), color = (0, 0, 0), duration = duration)
		bg_clip = ImageClip(background_path)

		# Generate Title
		time_cnt = utils.get_cnt()
		if project_title is None:
			project_title = f"《AI信息差》"
		width, height = bg_clip.size
		# 视频的大标题，通常为系列名称，例如《今日信息差》
		title_clip = (
			TextClip(project_title, font = "UD-Digi-Kyokasho-N-B-&-UD-Digi-Kyokasho-NP-B-&-UD-Digi-Kyokasho-NK-B",
			         size = (width - 190, 280),
			         fontsize = 190, align = 'center', bg_color = "rgba(255,255,0,1)",
			         color = 'black', stroke_color = "black", stroke_width = 2)
			.set_position((80, height // 3 - 200))
			.set_duration(duration))
		import time
		# 视频的日期，通常为当天日期
		date_time_clip = (TextClip(str(time.strftime('%Y年%m月%d日', time.localtime())),
		                           font = "UD-Digi-Kyokasho-N-B-&-UD-Digi-Kyokasho-NP-B-&-UD-Digi-Kyokasho-NK-B",
		                           size = (width, 230),
		                           fontsize = 140, align = 'center', bg_color = "rgba(255,255,255,0.174)",
		                           color = 'white', stroke_color = "red", stroke_width = 4)
		                  .set_position((0, height // 3 - 500))
		                  .set_duration(duration))
		# 视频的副标题，通常为当天的主要新闻标题
		if video_title:
			sub_title_clip = (TextClip(video_title, font = "华文琥珀",
			                           size = (width - 50, 280),
			                           fontsize = 100, align = 'center',
			                           color = 'yellow', stroke_color = "black", stroke_width = 4)
			                  .set_position((25, height * 4 // 5))
			                  .set_duration(duration))

		final_audio_clip = CompositeAudioClip([bgm, audio]).set_fps(48000).set_duration(duration)

		composite_list.extend([bg_clip.set_audio(final_audio_clip), bg_clip, title_clip, date_time_clip])
		if video_title:
			composite_list.append(sub_title_clip)

		# Overlay subtitle on the background video
		final_clip = CompositeVideoClip(composite_list, )
		# attach bgm to the final video
		final_clip = self.AddSubtitles(final_clip, subtitle_path)

		# Write the final video to the specified output path
		final_clip.duration = duration
		final_clip.set_duration(duration)
		final_clip.write_videofile(output_path, codec = "libx264", fps = fps,
		                           audio_bitrate = "320k", audio_fps = 48000, audio_bufsize = 6000)

	# 读取字幕文件
	def read_srt(self, path):
		content = ""
		with open(path, 'r', encoding = 'UTF-8') as f:
			content = f.read()
			return content

	# 字幕拆分
	def get_sequences(self, content):
		sequences = content.split('\n\n')
		sequences = [sequence.split('\n') for sequence in sequences]
		# 去除每一句空值
		sequences = [list(filter(None, sequence)) for sequence in sequences]
		# 去除整体空值
		return list(filter(None, sequences))

	# 转换时间
	def strFloatTime(self, tempStr):
		xx = tempStr.split(':')
		hour = int(xx[0])
		minute = int(xx[1])
		second = int(xx[2].split(',')[0])
		minsecond = int(xx[2].split(',')[1])
		allTime = hour * 60 * 60 + minute * 60 + second + minsecond / 1000
		return allTime

	def AddSubtitles(self, videoClip, txtFile):
		src_video = videoClip
		sentences = txtFile

		video = src_video
		# 获取视频的宽度和高度
		w, h = video.w, video.h
		# 所有字幕剪辑
		txts = []
		# 读取字幕文件
		content = self.read_srt(sentences)
		sequences = self.get_sequences(content)

		# 删除< No Speech >
		sequences = list(filter(lambda x: x[2] != '< No Speech >', sequences))

		# exit()

		for line in sequences:
			if len(line) < 3:
				continue
			sentences = line[2]
			start = line[1].split(' --> ')[0]
			end = line[1].split(' --> ')[1]

			start = self.strFloatTime(start)
			end = self.strFloatTime(end)

			start, end = map(float, (start, end))
			span = end - start
			zmstr = []
			# 超过24个字符则换行
			if len(sentences) > 12:
				zmstr = re.findall(r'.{12}', sentences)
				zmstr.append(sentences[(len(zmstr) * 12):])
				print(zmstr)
				sentences = ""
				for s in zmstr:
					sentences += s + "\n"
			# #ddddff
			# https://moviepy-tburrows13.readthedocs.io/en/improve-docs/ref/VideoClip/TextClip.html

			# stroke_color描边颜色，stroke_width 描边宽度， bg_color="red"
			font = "Microsoft-YaHei-Bold-&-Microsoft-YaHei-UI-Bold"
			txt = (TextClip(sentences, fontsize = 110,
			                font = font, size = (w, len(zmstr) * 210),
			                align = 'center', color = '#FFF', stroke_color = "black", stroke_width = 2,
			                bg_color = "rgba(0,0,0,0.32)")
			       .set_position((0, h - 2000))
			       .set_duration(span)
			       .set_start(start))

			txts.append(txt)
		# 合成视频
		video = CompositeVideoClip([video, *txts])
		return video
