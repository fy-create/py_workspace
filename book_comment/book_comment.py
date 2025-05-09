import csv
import os
import time
from sanic import Sanic, response
from sanic.response import json
import json as ger_json
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import zipfile
import glob

JSON_DATA_FILE = "./output/books.json"

app = Sanic("mySanic")

app.static("/", "./public")


# 定义路由GET/heLlo, 简单测试用
@app.get("/hello")
async def hello_world(request):
    # 返回文本
    return response.text("Hello,world\n")


# 上传接口
@app.route("/v1/book/crawled/upload", methods=["POST"])
async def upload(request):
    allow_type = [".json"]
    file = request.files.get("file")
    type = os.path.splitext(file.name)
    print(type)

    # 如果文件没有后缀len(type)就是1,如果哟后缀需要判断是否在允许的类型中
    if len(type) == 1 or type[1] not in allow_type:
        return json({"code": 8, "message": "file's format is error!"})

    path = "./upload"
    # 格式化为年月日时分秒Y-yeah,以此类推
    now_time = time.strftime("%Y%m%d%_H_%M_%S", time.localtime())
    file_name = "upload_" + type[0] + ".json"  # now_time

    dest_json_file = path + "/" + file_name
    with open(dest_json_file, "wb") as f:
        # 写入文件
        f.write(file.body)
        f.close()

        convert_book(dest_json_file)
        convert_book_comments(dest_json_file)

    return json({"code": 1, "msg": "upload successfully", "data": None})


def convert_book(file_name):
    # 打印开始转换文件的信息，显示当前要处理的文件名
    print(f"开始转换文件 {file_name}")

    try:
        # 以只读模式打开指定的 JSON 文件，并使用 UTF-8 编码
        with open(file_name, "r", encoding="utf-8") as file:
            body = ger_json.load(file)
    except Exception:
        return -1

    keys = []  # 初始化一个空列表，用于存储最终要写入 CSV 文件的列名
    first_element = body[0]  # 获取 JSON 数据中第一个元素，用于分析列名和数据类型

    # 获取第一个元素的所有键，并将其转换为列表
    element_keys = list(first_element.keys())
    key_types = {}  # 初始化一个空字典，用于存储每个键对应的值的类型

    # 遍历第一个元素的所有键
    for key in element_keys:
        # 获取当前键对应的值
        value = first_element[key]

        # 获取值的类型名称，并存储到 key_types 字典中
        key_types[key] = type(value).__name__

        # 打印当前键和其对应值的类型
        print(f"键: {key}, 类型: {key_types[key]}")

        # 如果当前键对应的值的类型不是列表
        if key_types[key] != "list":
            keys.append(key)

    print(f"csv title keys is: {keys}")

    # 生成要写入的 CSV 文件的文件名，将原文件名中的 .json 替换为 .csv，upload 替换为 csv
    csv_file = file_name.replace(".json", ".csv").replace("upload", "csv")

    # 打印开始写入 CSV 文件的信息，显示要写入的 CSV 文件名
    print(f"开始写入csv_file: {csv_file}")

    try:
        # 以写入模式打开生成的 CSV 文件，并使用 UTF-8 编码
        with open(csv_file, "w", encoding="utf-8", newline="") as file:
            # 创建一个 DictWriter 对象，指定文件和列名
            writer = csv.DictWriter(file, fieldnames=keys)

            # 写入 CSV 文件的表头
            writer.writeheader()

            # 遍历 JSON 数据中的每个元素
            for item in body:
                # 删除每个元素中的 "comment_list" 键值对，即删除评论信息
                item.pop("comment_list", None)

                writer.writerow(item)
    except Exception as e:
        # 若写入 CSV 文件时出现异常，打印错误信息并返回 -1 表示转换失败
        print(f"错误：写入 CSV 文件时出现问题 - {e}")
        return -1

    # 返回 0 表示转换成功
    return 0


def convert_book_comments(file_name):
    # 打印开始转换文件的信息，显示当前要处理的文件名
    print(f"conver_book_comments: {file_name}")
    try:
        # 以只读模式打开指定的 JSON 文件，并使用 UTF-8 编码
        with open(file_name, "r", encoding="utf-8") as file:
            body = ger_json.load(file)
    except Exception:
        return -1

    # 准备CSV文件头
    headers = [
        "book_id",  # 冗余字段
        "book_name",  # 冗余字段
        "comment_id",
        "comment_username",
        "comment_timestamp",
        "comment_location",
        "comment_rating",
        "comment_content",
        "comment_isuseful",
    ]

    # 写入CSV文件
    file_name = file_name.replace(".json", "_comments.csv").replace("upload", "csv")
    with open(file_name, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for item in body:
            # 获取书籍信息
            book_id = item.get("book_id")
            book_name = item.get("book_name")
            comment_list = item.get("comment_list", [])

            # 遍历评论列表
            for comment in comment_list:
                # 创建一个新的字典，将书籍信息和评论信息合并
                row = {
                    "book_id": book_id,  # 为每条评论添加冗余的book信息
                    "book_name": book_name,  # 为每条评论添加冗余的book信息
                    "comment_id": comment.get("comment_id"),
                    "comment_username": comment.get("comment_username"),
                    "comment_timestamp": comment.get("comment_timestamp"),
                    "comment_location": comment.get("comment_location"),
                    "comment_rating": comment.get("comment_rating"),
                    "comment_content": comment.get("comment_content"),
                    "comment_isuseful": comment.get("comment_isuseful"),
                }
                writer.writerow(row)


@app.route("/")
async def index(request):
    # 渲染 HTML 表单页面
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>书籍信息查询</title>
    </head>
    <body>
        <h1>书籍信息查询</h1>
        <form action="/v1/book/info" method="get">
            <label for="book_name">输入书名进行模糊查询：</label>
            <input type="text" id="book_name" name="book_name">
            <input type="submit" value="查询">
        </form>
    </body>
    </html>
    """
    return response.html(html)


@app.route("/v1/book/info")
async def get_books_info(request):
    # 获取用户输入的书名
    query_name = request.args.get("book_name", "")
    # 进行模糊查询
    print(f"book_name is: {query_name}")

    if os.path.exists(JSON_DATA_FILE):
        with open(JSON_DATA_FILE, "r", encoding="utf-8") as file:
            global page_books_data
            page_books_data = ger_json.load(file)

    html = "<table border='0'>"
    for book in page_books_data:
        if not query_name or query_name.lower() in book.get("book_name", "").lower():
            book_id = book.get("book_id", "")
            book_name = book.get("book_name", "")
            wordCloudLink = (
                f'<a href="/v1/comment/wordCloud?book_id={book_id}">{book_id}</a>'
            )
            commentLink = (
                f'<a href="/v1/comment/info?book_name={book_name}">{book_name}</a>'
            )
            html += "<tr>"
            html += f"<td>{wordCloudLink}</td>"
            html += f"<td>{commentLink}</td>"
            html += f"<td>{book.get('book_author', '')}</td>"
            html += f"<td>{book.get('book_rating', '')}</td>"
            html += "</tr>"

    html += "</table>"
    # results.append(book.get("book_name", ""))

    return response.html("查询结果：<br>" + html)


@app.route("/v1/comment/info")
async def get_comments_info(request):
    # 获取用户输入的书名
    book_name = request.args.get("book_name", "")
    # 进行模糊查询
    print(f"book_name is: {book_name}")

    html = "<table border='0'>"
    for book in page_books_data:
        if book_name.lower() == book.get("book_name", "").lower():
            comment_list = book.get("comment_list", [])
            for comment in comment_list:
                # 处理每个评论
                html += f"<tr><td>{comment.get('comment_username', '')}</td>"
                html += f"<td>{comment.get('comment_content', '')}</td>"
                html += f"<td>{comment.get('comment_location', '')}</td></tr>"

    html += "</table>"

    return response.html("评论查询结果：<br>" + html)


@app.route("/v1/comment/emotion")
async def get_emotion_info(request):
    return response.html(
        """
            <img src='/books_sentiment_analysis.png' alt='情感分析结果' 
                style='max-width: 100%; height: auto; display: block; margin: 0 auto;'>
        """
    )


@app.route("/v1/comment/wordCloud")
async def get_wordCloud_info(request):
    book_id = request.args.get("book_id", "")
    # 进行模糊查询
    print(f"book_name is: {book_id}")

    return response.html(
        f"""
            <img src='/{book_id}_wordcloud.png' alt='词云结果' 
                style='max-width: 100%; height: auto; display: block; margin: 0 auto;'>
        """
    )


def file2zip(zip_file_name, file_names: list):
    with zipfile.ZipFile(zip_file_name, "w") as zipf:
        for fn in file_names:
            parent_path,name = os.path.split(fn)
            zipf.write(fn, arcname=name)

@app.route("/v1/book/comment/sentiment_analysis/package/download")
async def get_data_show(request):
    public_files = glob.glob('./public/*')
    file2zip("pic_archive.zip",public_files)
    
    return await response.file(
        "./public/books_sentiment_analysis.png",
        filename="books_sentiment_analysis.png",  # 可选：自定义下载文件名
        headers={
            "Content-Disposition": "attachment; filename=books_sentiment_analysis.png"  # 强制下载
        },
    )


if __name__ == "__main__":
    # 运行服务器
    app.run(host="0.0.0.0", port=8000)
