import os
import csv
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


def create_emotion_info():
    os.makedirs("csv", exist_ok=True)
    emotion_file_name = "csv/comments_emotion.csv"
    comments = []
    semantic_cls = pipeline(
        Tasks.text_classification,
        "iic/nlp_structbert_sentiment-classification_chinese-tiny",
    )
    print("开始分析csv_books_comments.csv")
    with open("csv/csv_books_comments.csv", "r", encoding="utf-8") as file:
        mycsv = list(csv.reader(file))
        print(f"mycsv len={len(mycsv)}")
        for i in range(1, len(mycsv)):
            comments.append(mycsv[i][7])  #  第7列是评论内容,从0开始计数

    print("正在分析,请稍后 ...")
    result = semantic_cls(input=comments)
    print(f"分析完成,正在写入 {emotion_file_name}")
    fld_name = ["book_name", "is_positive", "positive_probs", "negative_probs"]
    name_index = 1
    with open(emotion_file_name, "w+", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fld_name)
        writer.writeheader()
        for info in result:
            sorted_labels_scores = sorted(
                zip(info["labels"], info["scores"]),
                key=lambda x: x[0] == "正面",
                reverse=True,
            )
            positive_label, positive_probs = sorted_labels_scores[0]
            negative_label, negative_probs = sorted_labels_scores[1]
            is_positive = 1 if positive_probs > negative_probs else 0
            value = {
                "book_name": mycsv[name_index][1],
                "is_positive": is_positive,
                "positive_probs": positive_probs,
                "negative_probs": negative_probs,
            }
            print(f"{mycsv[name_index][1]} 评论分析结果: {value}")
            writer.writerow(value)
            name_index += 1


if __name__ == "__main__":
    create_emotion_info()
