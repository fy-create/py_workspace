import html
import json
import os
import requests
import time
import random
from logger_config import logger
from utils import save_to_json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

CRAWL_STATE_FILE = "./output/crawl_state.json"
JSON_DATA_FILE = "./output/books.json"

page_books_data = []

headers = {
    "authority": "book.douban.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://accounts.douban.com/",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}

cookies = {
    "bid": "cGWLwOt7Oh4",
    "douban-fav-remind": "1",
    "ll": '"108299"',
    "_vwo_uuid_v2": "D0938AEC52C4CBDF5AAEF505BB41A8CE6|5b0d1f6152aeefb3422a35c5276a9a53",
    "push_noty_num": "0",
    "push_doumail_num": "0",
    "__utmv": "30149280.15129",
    "_pk_id.100001.3ac3": "19b4ee41d1a4f737.1742783292.",
    "__yadk_uid": "yRZsOIA1amCcq7UYHwAFucJnLVX6UyOH",
    "dbcl2": '"151299840:3JceDWyZ9w8"',
    "ck": "KPKr",
    "_pk_ref.100001.3ac3": "%5B%22%22%2C%22%22%2C1745456089%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D",
    "_pk_ses.100001.3ac3": "1",
    "__utma": "30149280.1320575057.1741329696.1744809433.1745456089.26",
    "__utmb": "30149280.0.10.1745456089",
    "__utmc": "30149280",
    "__utmz": "30149280.1745456089.26.5.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/",
}


# 目标URL
base_url = "https://book.douban.com/tag/编程"


def get_book_comments(book_url, max_pages=10):
    """获取单本书的所有有效评论（分页处理）"""
    comments_url = urljoin(book_url, "comments")
    logger.info(f"书籍的分页评论URL: {comments_url}")
    all_comments = []

    for page in range(1, max_pages + 1):
        try:
            # 构建分页URL
            page_url = f"{comments_url}?start={(page-1)*20}"
            logger.info(f"正在爬取评论页: {page_url}")
            response = requests.get(page_url, headers=headers, cookies=cookies)
            response.raise_for_status()
            response.encoding = "utf-8"

            soup = BeautifulSoup(response.text, "html.parser")
            comments_items = soup.find_all("li", class_="comment-item")

            # 如果当前页没有评论，终止分页
            if not comments_items:
                break

            for comment_item in comments_items:
                # 评论 ID
                comment_id = comment_item.get("data-cid")
                if comment_id is None:
                    logger.info("没有获取到评论ID,跳过")
                    break

                # 评论内容
                comment_content = comment_item.find("span", class_="short").text.strip()
                # 评论时间戳
                comment_timestamp = comment_item.find(
                    "a", class_="comment-time"
                ).text.strip()
                # 评论星级
                star_span = comment_item.find("span", class_="user-stars")
                comment_rating = star_span.get("title") if star_span else None
                # 评论用户名称
                comment_username = (
                    comment_item.find("span", class_="comment-info")
                    .find("a")
                    .text.strip()
                )
                # 评论有用点赞数
                vote_isuseful = comment_item.find(
                    "span", class_="vote-count"
                ).text.strip()
                # 评论位置
                comment_location = comment_item.find(
                    "span", class_="comment-location"
                ).text.strip()

                all_comments.append(
                    {
                        "comment_id": comment_id,
                        "comment_content": comment_content,
                        "comment_timestamp": comment_timestamp,
                        "comment_rating": comment_rating,
                        "comment_username": comment_username,
                        "vote_isuseful": vote_isuseful,
                        "comment_location": comment_location,
                    }
                )

                # 打印评论信息
                logger.info(f"   评论者: {comment_username}")
                logger.info(f"      内容: {comment_content[:30]}")

            time.sleep(random.uniform(1, 1.5))  # 随机延迟

        except Exception as e:
            logger.error(f"获取评论页失败: {page_url}, 错误: {e}")
            break

    return all_comments


def load_last_data():
    """加载最后爬取的页面和数据"""
    if os.path.exists(JSON_DATA_FILE):
        logger.info(f"{JSON_DATA_FILE}文件存在,先读取他")
        with open(JSON_DATA_FILE, "r", encoding="utf-8") as file:
            global page_books_data
            page_books_data = json.load(file)
            print("成功读取 JSON 文件内容到数组:")

    if os.path.exists(CRAWL_STATE_FILE):
        with open(CRAWL_STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
            return state.get("last_page", -1)

    return -1


def save_last_page(page):
    """保存最后爬取的页面"""
    os.makedirs(os.path.dirname(CRAWL_STATE_FILE), exist_ok=True)
    with open(CRAWL_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_page": page}, f, ensure_ascii=False, indent=2)


def get_book_info(book_url):
    logger.info("-" * 80)
    logger.info(f"book_url : {book_url}")
    response = requests.get(book_url, headers=headers, cookies=cookies)
    response.raise_for_status()
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    book_id = book_url.split("/")[-2]

    # 查找 id 为 wrapper 的元素
    wrapper_element = soup.find(id="wrapper")
    if wrapper_element:
        span_element = wrapper_element.find("span", property="v:itemreviewed")
        if span_element:
            book_name = span_element.get_text()

        # 使用 CSS 选择器一次性定位到 info 元素
        info_element = wrapper_element.select_one("#content #info")
        if info_element:
            data = {}

            for element in info_element.descendants:
                if hasattr(element, "get") and "pl" in element.get("class", []):
                    label = element.get_text().strip().replace(":", "")  # 去掉冒号

                    # logger.info(f"找到 class 为 'pl' 的节点: {label}")
                    def get_value(label, element):
                        if label in [
                            "作者",
                            "译者",
                        ]:  # 作者节点特殊,需要拿到下下一个兄弟节点
                            next_next_sibling = element.next_sibling.next_sibling
                            if next_next_sibling:
                                return next_next_sibling.get_text().strip()
                        elif label in [
                            "出版社",
                            "出品方",
                            "丛书",
                        ]:  # 这些节点后面可能有一个空格,需要继续往下找
                            next_sibling = element.next_sibling
                            while next_sibling and isinstance(next_sibling, str):
                                next_sibling = next_sibling.next_sibling
                            if next_sibling:
                                return next_sibling.get_text().strip()
                        elif label in [
                            "副标题",
                            "原作名",
                            "出版年",
                            "页数",
                            "定价",
                            "装帧",
                            "ISBN",
                        ]:
                            next_sibling = element.next_sibling
                            if isinstance(next_sibling, str):
                                return next_sibling.strip()
                        return None

                    value = get_value(label, element)
                    if value:
                        data[label] = value

            # logger.info(f"提取到的信息: {data}")

            # 提取我们所需信息
            book_author = data.get("作者")
            book_publisher = data.get("出版社")
            book_price = data.get("定价")
            book_date = data.get("出版年")

        target_element = soup.select_one("#content .ll.rating_num")
        if target_element:
            rating = target_element.get_text().strip()

    # 开始获取评论信息
    comment_list = get_book_comments(book_url, 999)  # TODO 只获取第一页的评论用于测试用,不然时间太长

    book_info = {
        "book_id": book_id,
        "book_name": book_name,
        "book_rating": rating,  # rating,
        "book_author": book_author,
        "book_publisher": book_publisher,
        "book_price": book_price,
        "book_date": book_date,
        "comment_list": comment_list,
    }

    # logger.info(f"book_info : {book_info}")
    return book_info


def crawl_single_page(page):
    url = f"{base_url}?start={ page * 20 }&type=T"
    logger.info(f"正在爬取第 {page} 页: {url}")

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("li", class_="subject-item")

        # 准备批量保存的数据
        for book in books:
            h2_tag = book.find("h2")
            # title = h2_tag.get_text(strip=True)
            link = urljoin(url, h2_tag.a["href"]) if h2_tag.a else None

            if not link:  # 如果没有链接，跳过本书
                continue

            book_info = get_book_info(link)

            # 将书籍信息添加到批量保存列表
            global page_books_data
            page_books_data.append(book_info)
            time.sleep(random.uniform(1, 2))

        # 批量保存当前页的所有书籍数据
        if page_books_data:
            save_to_json(page_books_data, JSON_DATA_FILE)
            save_last_page(page)  # 成功爬取后更新最后页面
            logger.info(f"第 {page} 页数据保存完成")
        else:
            logger.info(f"第 {page} 页没有获取到有效数据")

    except requests.exceptions.RequestException as e:
        logger.error(f"请求第 {page} 页失败: {e}")
    except Exception as e:
        logger.error(f"处理第 {page} 页数据时发生错误: {e}")


def crawl_multiple_pages(start_page=0, end_page=999):
    for page in range(start_page, end_page):
        crawl_single_page(page)

        # 随机延迟，避免请求过于频繁
        time.sleep(random.uniform(1, 3))


if __name__ == "__main__":
    # 禁用压缩,不然爬回来的数据是压缩格式显示为乱码
    # 用Accept-Encoding = identity, 让服务器直接返回常规数据.
    headers["Accept-Encoding"] = "identity"

    start_page = 0
    last_page = load_last_data()

    # 确定起始页面（取start_page和last_page+1中的较大值）
    current_page = max(start_page, last_page + 1)

    logger.info(f"开始爬取，从第 {current_page} 页开始")
    crawl_multiple_pages(current_page, 1)
