import csv
import os
import json
from logger_config import logger


def save_to_json(page_books_data, filename, mode="a"):
    try:
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # 打开文件以写入模式
        with open(filename, "w", encoding="utf-8") as file:
            # 将数组写入 JSON 文件，使用 indent=4 使文件内容更易读
            json.dump(page_books_data, file, ensure_ascii=False, indent=4)
        logger.info(f"数据已成功写入 {filename}")
    except Exception as e:
        print(f"写入文件时出现错误: {e}")

