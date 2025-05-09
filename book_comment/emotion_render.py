import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import numpy as np
from matplotlib import font_manager

# 注册字体
font_path = "./font/NotoSansCJKsc-Regular.otf"
font_manager.fontManager.addfont(font_path)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 1. 从CSV文件读取数据
try:
    df = pd.read_csv("csv/comments_emotion.csv")
except FileNotFoundError:
    print("错误：未找到 comments_emotion.csv 文件")
    exit()

# 2. 统计每本书的情感分布
book_stats = defaultdict(lambda: {"total": 0, "positive": 0, "negative": 0})
for _, row in df.iterrows():
    book_name = row["book_name"]
    book_stats[book_name]["total"] += 1
    if row["is_positive"] == 1:
        book_stats[book_name]["positive"] += 1
    else:
        book_stats[book_name]["negative"] += 1

# 3. 准备绘图数据
books = list(book_stats.keys())
total = [stats["total"] for stats in book_stats.values()]
positive = [stats["positive"] for stats in book_stats.values()]
negative = [stats["negative"] for stats in book_stats.values()]

# 4. 设置图形
plt.figure(figsize=(12, 6))
bar_width = 0.25
index = np.arange(len(books))

# 5. 绘制柱状图
bars1 = plt.bar(index, total, bar_width, label="总评论数", color="#1f77b4")
bars2 = plt.bar(
    index + bar_width, positive, bar_width, label="正向评论", color="#2ca02c"
)
bars3 = plt.bar(
    index + 2 * bar_width, negative, bar_width, label="负向评论", color="#d62728"
)

# 6. 添加标签和标题
plt.xlabel("书籍名称", fontsize=12)
plt.ylabel("评论数量", fontsize=12)
plt.title("书籍评论情感分析统计", fontsize=14, pad=20)
plt.xticks(index + bar_width, books, rotation=30, ha="right")
plt.legend()


# 7. 添加数值标签
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            "%d" % int(height),
            ha="center",
            va="bottom",
        )


add_labels(bars1)
add_labels(bars2)
add_labels(bars3)

# 8. 调整布局
plt.tight_layout()
plt.grid(axis="y", alpha=0.3)

# 9. 保存和显示图形
plt.savefig("./public/books_sentiment_analysis.png", dpi=300, bbox_inches="tight")
plt.show()
