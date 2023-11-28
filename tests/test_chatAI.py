import logging
import unittest

import ChatAIs
from ChatAIs import ErnieBot

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                    level = logging.DEBUG)


class TestErnieBot(unittest.TestCase):
	def setUp(self):
		print("setUp")

	def test_init(self):
		ai = ErnieBot()
		self.assertIsInstance(ai, ErnieBot)

	def test_ask_once(self):
		ai = ErnieBot()
		response = ai.ask_once("你好")
		self.assertIsInstance(response, str)

	def test_conversation(self):
		ai = ErnieBot()
		ai.conversation("a = 20")
		response = ai.conversation("上文中a的值是多少？")
		print(response)
		self.assertEquals("20" in response, True)

	def test_end_conversation(self):
		ai = ErnieBot()
		ai.conversation("a = 20")
		ai.end_conversation()
		response = ai.conversation("上文中a的值是多少？")
		self.assertEquals("20" in response, False)

	def test_generate_video_description(self):
		video_script = """
		大家好，我是AI评论的主持人小艾。今天，我们一起来探讨几条热门新闻。
首先，我们看到美元大跳水，10年期美债收益率大跌，离岸人民币大涨400点，美股五连阳。这一系列的金融市场动态，让人不禁想问，美联储加息周期是否已经到头？最新的就业数据显示，美国的劳动力市场似乎正在降温，这给了美联储更多的理由将利率保持在当前高位，不再进一步加息。然而，最终的决策还需依赖于更多的通胀报告。金融市场的变化牵动着全球经济的脉搏，我们将继续关注这一进展。
接下来，我们看到一则有关电影和游戏的新闻。《完蛋！我被美女包围了！》的人气角色扮演者钟晨瑶参演的电影《热搜》定档，其背后出品方百纳千成的股价也因此大涨。这显示了电影和游戏产业的紧密联系，以及公众对热门IP的热烈追捧。
然后，有新闻称美方已在以色列部署特种部队，这将给中东地区带来怎样的影响？美国国防部表示，这些特种部队的主要任务是协助确定被哈马斯扣押人员的位置和确认人质身份等。这一行动引发了地区局势的紧张，各方都应保持克制，通过对话解决问题。
此外，我们还看到有关直播带货、网购物流以及核能充电宝等话题的讨论。无论是带货还是销售核能充电宝，都应该遵循诚信原则，保障消费者的权益。而网购物流的问题也提醒我们，网络服务质量的提升仍然有待加强。
以上就是今天的热点新闻，感谢大家的收听。我们期待与您在下一次播音中再会！
		"""
		ai = ErnieBot()
		ai.conversation("a = 20")
		ai.end_conversation()
		response = ai.conversation()
		self.assertIsInstance(response, str)

	def tearDown(self):
		print("tearDown")


class TestQwen(unittest.TestCase):
	def test_ask_once(self):
		ai = ChatAIs.Qwen()
		response = ai.ask_once("你好？")
		self.assertIsInstance(response, str)

	def test_conversation(self):
		ai = ChatAIs.Qwen()
		ai.conversation("a = 20")
		response = ai.conversation("上文中a的值是多少？")
		print(response)
		self.assertEquals("20" in response, True)

	def test_end_conversation(self):
		ai = ChatAIs.Qwen()
		ai.conversation("a = 20")
		ai.end_conversation()
		response = ai.conversation("上文中a的值是多少？")
		print(response)
		self.assertEquals("20" in response, False)
