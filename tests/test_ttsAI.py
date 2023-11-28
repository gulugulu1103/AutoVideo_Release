import logging
import unittest

from TTSAIs import AzureTTS, DashScopeTTS, NLSTTS

example_text = """
		各位观众，大家好！欢迎收看今天的《今日信息差》。今天我们要讨论的话题是近期的一些热点新闻。首先，让我们来看看缅北冲突。这场冲突已经导致三个政府控制区失守，数百人越过边境逃入中国。这无疑会对中缅边境的安全稳定带来一定的影响。中国外交部发言人已经表示，中方高度关注缅北冲突态势，敦促各方立即停火止战，采取切实有效措施，确保中缅边境安全稳定。这场冲突提醒我们，和平与稳定才是国际关系的基石，希望各方能够加强对话，寻求和平解决方案。再来看看《英雄联盟》S13全球总决赛。LNG能否击败T1，与其他三个LPL的战队成功会师四强，这无疑是电竞迷们关注的焦点。各个队伍的实力和优劣需要具体分析，但无论如何，我们都期待看到一场精彩的比赛。
		"""

logging.basicConfig(level = logging.DEBUG)


class TestAzureTTS(unittest.TestCase):
	def test_init(self):
		azure_tts = AzureTTS()
		self.assertIsInstance(azure_tts, AzureTTS)

	def test_create_audio_once(self):
		azure_tts = AzureTTS()
		azure_tts.create_audio_once(example_text, "output.mp3", "subtitle.srt")


class TestDashScopeTTS(unittest.TestCase):
	def test_init(self):
		azure_tts = DashScopeTTS()
		self.assertIsInstance(azure_tts, AzureTTS)

	def test_create_audio_once(self):
		azure_tts = DashScopeTTS()
		example_text = """
				<speak>
				各位观众，大家好！欢迎收看今天的《今日<phoneme alphabet="py" ph="xin4 xi1 cha1">信息差</phoneme>》。今天我们要讨论的话题是近期的一些热点新闻。首先，让我们来看看缅北冲突。这场冲突已经导致三个政府控制区失守，数百人越过边境逃入中国。这无疑会对中缅边境的安全稳定带来一定的影响。中国外交部发言人已经表示，中方高度关注缅北冲突态势，敦促各方立即停火止战，采取切实有效措施，确保中缅边境安全稳定。这场冲突提醒我们，和平与稳定才是国际关系的基石，希望各方能够加强对话，寻求和平解决方案。再来看看《英雄联盟》S13全球总决赛。LNG能否击败T1，与其他三个LPL的战队成功会师四强，这无疑是电竞迷们关注的焦点。各个队伍的实力和优劣需要具体分析，但无论如何，我们都期待看到一场精彩的比赛。
				</speak>
				"""
		time_stamp = azure_tts.create_audio_once(example_text, "output.mp3", "subtitle.srt")
		print(time_stamp)


class TestNLSTTS(unittest.TestCase):
	example_task_id = "091bfc7e430c4084b8ce2da2cbb2c1dd"

	def test_create_task(self):
		tts = NLSTTS()
		print(tts.create_task(example_text))

	def test_query_task(self):
		tts = NLSTTS()
		print(tts.query_task(self.example_task_id))

	def test_parser_response(self):
		tts = NLSTTS()
		response = tts.query_task(self.example_task_id)
		mp3, stamp = tts.parser_response(response)
		print("mp3 = " + mp3)
		print("srt = " + str(stamp))

	def test_create_audio_once(self):
		tts = NLSTTS()
		tts.create_audio_once(example_text, "output.mp3", "subtitle.srt")


if __name__ == '__main__':
	unittest.main()
