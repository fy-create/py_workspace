import logging

# 创建全局日志对象
logger = logging.getLogger('book')
logger.setLevel(logging.DEBUG)

# 修改格式字符串以包含文件名和行号
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)4d - %(message)s'
)

# 文件处理器
file_handler = logging.FileHandler('book.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 控制台处理器
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)