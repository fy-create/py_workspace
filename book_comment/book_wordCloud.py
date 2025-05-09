import jieba
from wordcloud import WordCloud
import csv

def plot_book_comment_wordcloud(id):
    """
    生成书籍评论的词云图
    :param book_comments: 书籍评论列表
    """

    stopwords = {
        '我', '你', '他', '她', '它', '我们', '你们', '他们', 
        '这个', '那个', '这些', '那些',
        '和', '与', '或', '而且', '但是', '因为', '所以',
        '的', '地', '得', '了', '着', '过',
        '个', '些', '种', '项', '本', '章',
        '很', '非常', '十分', '特别', '最', '太',
        '在', '从', '到', '关于', '对于', '根据',
        '可以', '可能', '应该', '一般', '就是', '这样','有','都','是','要','会',
    }
    comment = ""

    with open("csv/csv_books_comments.csv", "r", encoding="utf-8") as file:
        mycsv = list(csv.reader(file))
        print(f"mycsv len={len(mycsv)}")
        for i in range(1, len(mycsv)):
            if mycsv[i][0] == id:
                # print(f"book_name={mycsv[i][1]}  book_id={mycsv[i][0]}")
                # 读取评论内容
                comment += mycsv[i][7]

    # 将所有评论连接成一个字符串

    # 使用jieba进行中文分词
    word_list = jieba.cut(comment)
    words = " ".join(word_list)

    # 生成词云图
    wordcloud = WordCloud(
        stopwords=stopwords,
        font_path='./font/NotoSansCJKsc-Regular.otf',  # 使用您的字体文件
        background_color="white",
        width=800,
        height=400,
        max_words=200,
        min_font_size=10,
        max_font_size=100,
        colormap="viridis",
    ).generate(words)

    # 显示词云图
    wordcloud.to_file(f"./public/{id}_wordcloud.png")


if __name__ == "__main__":
    with open("csv/csv_books.csv", "r", encoding="utf-8") as file:
        mycsv = list(csv.reader(file))
        print(f"mycsv len={len(mycsv)}")
        for i in range(1, len(mycsv)):
            plot_book_comment_wordcloud(mycsv[i][0])
