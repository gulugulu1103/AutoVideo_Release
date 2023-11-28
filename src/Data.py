import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import LONGBLOB

import config

# 创建基类, 用于创建表
Base = sqlalchemy.orm.declarative_base()
# 创建连接引擎
engine = create_engine(config.sql)
# 创建连接
conn = engine.connect()
# 创建session
Session = sqlalchemy.orm.sessionmaker(bind = engine)
session = Session()


class News(Base):
	"""
	新闻类，用于创建新闻表
	"""
	# 表名
	__tablename__ = 'news'
	# 定义表结构
	__table_args__ = {
		"mysql_charset": "utf8"
	}
	# 表结构
	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True, autoincrement = True)
	# 新闻标题
	title = sqlalchemy.Column(sqlalchemy.String(255), nullable = False)
	# 新闻内容，可能会很长，可以统一使用短网址服务，或者直接使用数据库的text类型
	content = sqlalchemy.Column(sqlalchemy.Text, nullable = False)
	# 新闻类型
	category = sqlalchemy.Column(sqlalchemy.String(20), nullable = True)
	# 来源网站名称
	source_site_name = sqlalchemy.Column(sqlalchemy.String(255))
	# 来源网站可能会很长，可以统一使用短网址服务，或者直接使用数据库的text类型
	source = sqlalchemy.Column(sqlalchemy.String(1000), nullable = True, unique = True)
	# 新闻发布时间
	posted_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable = True)
	# 新闻抓取时间
	fetched_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable = False)
	# 封面链接
	cover_url = sqlalchemy.Column(sqlalchemy.TEXT, nullable = True)
	# 新闻封面，二进制文件
	cover_data = sqlalchemy.Column(LONGBLOB, nullable = True)
	# 新闻是否已经被创建成为视频任务
	is_created = sqlalchemy.Column(sqlalchemy.Boolean, default = False, nullable = False)


class DownloadedImage(Base):
	"""
	下载图片类，用于创建下载图片表
	"""
	# 表名
	__tablename__ = 'downloaded_image'
	# 定义表结构
	__table_args__ = {
		"mysql_charset": "utf8"
	}
	# id
	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True, autoincrement = True)
	# 图片标题
	title = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 图片文件名
	file_name = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 来源网站链接
	source = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 图片二进制文件
	data = sqlalchemy.Column(LONGBLOB)


class GeneratedImage(Base):
	"""
	生成图片类，用于创建生成图片表
	"""
	# 表名
	__tablename__ = 'generated_image'
	# 定义表结构
	__table_args__ = {
		"mysql_charset": "utf8"
	}
	# id
	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True, autoincrement = True)
	# 图片的prompt
	prompt = sqlalchemy.Column(sqlalchemy.Text, nullable = True)
	# 图片文件名
	file_name = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 生成时间
	generated_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable = True)
	# 图片二进制文件
	data = sqlalchemy.Column(LONGBLOB, nullable = True)


class Speech(Base):
	"""
	语音类，用于创建语音表
	"""
	# 表名
	__tablename__ = 'speech'
	# 定义表结构
	__table_args__ = {
		"mysql_charset": "utf8"
	}
	# id
	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True, autoincrement = True)
	# 语音标题
	title = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 语音文件名
	file_name = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 语音格式，枚举：mp3、wav
	format = sqlalchemy.Column(sqlalchemy.Enum('mp3', 'wav'), nullable = True)
	# 字幕文本
	subtitle = sqlalchemy.Column(sqlalchemy.Text, nullable = True)
	# 字幕文件格式，枚举：srt、ass
	subtitle_format = sqlalchemy.Column(sqlalchemy.Enum('srt', 'ass'), nullable = True)
	# 语音二进制文件
	data = sqlalchemy.Column(LONGBLOB)


class VideoTask(Base):
	"""
	视频任务类，用于记录视频生成的参数
	"""
	# 表名
	__tablename__ = 'video_task'
	# 定义表结构
	__table_args__ = {
		"mysql_charset": "utf8"
	}
	# id
	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True, autoincrement = True)
	# 新闻 id
	news_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news.id'))
	# 视频标题，不同于新闻标题，可以是新闻标题的一部分，也可以是新闻标题的变体
	title = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 视频脚本，给视频配音的脚本
	script = sqlalchemy.Column(sqlalchemy.Text, nullable = True)
	# 视频栏目分类，枚举：社会民生、国际风云、科技前沿、生活百态、体育风暴
	category = sqlalchemy.Column(sqlalchemy.Enum('社会民生', '国际风云', '科技前沿', '生活百态', '体育风暴'),
	                             nullable = True)
	# AI文稿生成的prompt，根据栏目分类而变化
	prompt = sqlalchemy.Column(sqlalchemy.Text, nullable = True)
	# 视频配音id
	speech_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('speech.id'), nullable = True)
	# 视频插图id列表，JSON，例如：[1,2,3,4,5]
	downloaded_image_ids = sqlalchemy.Column(sqlalchemy.JSON, nullable = True)
	generated_image_ids = sqlalchemy.Column(sqlalchemy.JSON, nullable = True)
	# 视频时长
	duration = sqlalchemy.Column(sqlalchemy.Integer, nullable = True)
	# 视频的简介
	description = sqlalchemy.Column(sqlalchemy.Text, nullable = True)
	# 是否渲染完成
	is_rendered = sqlalchemy.Column(sqlalchemy.Boolean, default = False)
	# 渲染完成时间
	rendered_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable = True)
	# 渲染视频输出id
	video_output_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('video_output.id'), nullable = True)
	# 发布平台，字符串列表，例如：[bilibili, youtube, weibo, douyin]
	platforms = sqlalchemy.Column(sqlalchemy.JSON, nullable = True)
	# 是否发布完成
	is_published = sqlalchemy.Column(sqlalchemy.Boolean, default = False)
	# 视频发布时间
	posted_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable = True)


class VideoOutput(Base):
	"""
	视频输出类，用于记录视频输出的参数
	"""
	# 表名
	__tablename__ = 'video_output'
	# 定义表结构
	__table_args__ = {
		"mysql_charset": "utf8"
	}
	# id
	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True, autoincrement = True)
	# 视频任务 id
	video_task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('video_task.id'))
	# 视频标题
	title = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 视频文件名
	file_name = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 视频格式，枚举：mp4、mov、avi、flv、mkv、wmv、rmvb、3gp
	format = sqlalchemy.Column(sqlalchemy.Enum('mp4', 'mov', 'avi', 'flv', 'mkv', 'wmv', 'rmvb', '3gp'),
	                           nullable = True)
	# 视频二进制文件
	data = sqlalchemy.Column(LONGBLOB)


class Music(Base):
	"""
	音乐类，用于创建音乐表
	"""
	# 表名
	__tablename__ = 'music'
	# 定义表结构
	__table_args__ = {
		"mysql_charset": "utf8"
	}
	# id
	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True, autoincrement = True)
	# 音乐标题
	title = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 作曲家
	composer = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 适合的栏目分类，枚举：社会民生、国际风云、科技前沿、生活百态、体育风暴
	category = sqlalchemy.Column(sqlalchemy.Enum('社会民生', '国际风云', '科技前沿', '生活百态', '体育风暴'),
	                             nullable = True)
	# 音乐文件名
	file_name = sqlalchemy.Column(sqlalchemy.String(255), nullable = True)
	# 音乐二进制文件
	data = sqlalchemy.Column(LONGBLOB, nullable = True)
	# 音乐时长
	duration = sqlalchemy.Column(sqlalchemy.Integer, nullable = True)
	# 音乐的简介
	description = sqlalchemy.Column(sqlalchemy.Text, nullable = True)
	# 音乐标签列表，用逗号分隔，例如：流行,摇滚,民谣
	tags = sqlalchemy.Column(sqlalchemy.JSON, nullable = True)


def create_tables() -> None:
	"""
	创建表
	:return:
	"""
	# 执行sql语句
	Base.metadata.create_all(engine)


def write_news(news_list: list[News]) -> None:
	"""
	将新闻写入数据库
	:return:
	"""
	# 使用News.source判断是否已经存在（source = 网页）
	for each in news_list:
		# 如果已经存在，则跳过
		if session.query(News).filter(News.source == each.source).first() is not None:
			continue
		# 如果不存在，则添加
		else:
			session.add(each)
	# 提交
	session.commit()
