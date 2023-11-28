import ffmpeg


def create_subtitled_video(background_path, audio_path, output_path, subtitle_path, bgm_path,
                           project_title=None, video_title=None, fps=30):
	"""
    使用 ffmpeg-python 创建带字幕的视频。

    :param background_path: 背景图片的路径。这张图片将被用作视频的背景。
    :param audio_path: 音频文件的路径。这个音频将被用作视频的主音轨。
    :param output_path: 视频输出的路径。
    :param subtitle_path: 字幕文件的路径。字幕将被添加到视频中。
    :param bgm_path: 背景音乐文件的路径。背景音乐将被添加到视频中。
    :param project_title: 视频的主标题，如果提供，将出现在视频中。
    :param video_title: 视频的副标题，如果提供，将出现在视频中。
    :param fps: 背景视频的帧率，默认为30。

    :return: None
    """

	# 步骤1: 创建一个基于背景图片的视频流
	background_input = ffmpeg.input(background_path, loop = 1, framerate = fps)
	audio_duration = float(ffmpeg.probe(audio_path)['format']['duration'])
	background_video = ffmpeg.filter(background_input, 'trim', duration = audio_duration)

	# 步骤2: 读取音频文件
	audio_input = ffmpeg.input(audio_path)

	# 步骤3: 添加字幕
	video_with_subtitles = ffmpeg.filter([background_video], 'subtitles', subtitle_path)

	# 步骤4: 添加标题（如果提供）
	if project_title:
		video_with_subtitles = ffmpeg.drawtext(video_with_subtitles,
		                                       text = project_title,
		                                       x = '(w-text_w)/2', y = '(h-text_h)/2')
	if video_title:
		video_with_subtitles = ffmpeg.drawtext(video_with_subtitles, text = video_title,
		                                       x = '(w-text_w)/2', y = 'h-50')

	# 步骤5: 处理背景音乐
	bgm_input = ffmpeg.input(bgm_path)
	bgm_trimmed = ffmpeg.filter(bgm_input, 'atrim', duration = audio_duration)
	mixed_audio = ffmpeg.filter([audio_input, bgm_trimmed], 'amix', duration = 'first')

	# 步骤6: 结合音频和视频
	final_video = ffmpeg.output(video_with_subtitles, mixed_audio, output_path, vcodec = 'libx264', acodec = 'aac')

	# 执行ffmpeg命令并生成视频
	ffmpeg.run(final_video)


# 这个函数可以用来创建带字幕的视频，适用于生成各种配有背景音乐、字幕和标题的视频内容。

if __name__ == '__main__':
	create_subtitled_video(background_path = "../daily/2023_11_03/input/background_blured.png",
	                       audio_path = "../daily/2023_11_03/input/tts.mp3",
	                       output_path = "../daily/2023_11_03/output/output.mp4",
	                       subtitle_path = "../daily/2023_11_03/input/subtitle.srt",
	                       bgm_path = "../bin/bgm.flac",
	                       fps = 30)
