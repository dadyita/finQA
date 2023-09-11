import openai
import time
import json
from openai.embeddings_utils import cosine_similarity
import os

# compare cosine similarity of embedding array of formula and data
# and search the most similar_count relevant formula
similar_count = 20

# yilun's key: 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
# my key: sk-jOM3RhzjthMGY7tSLteST3BlbkFJXHnGjZ1fKA2uVRQ2yP0w
openai.api_key = "sk-jOM3RhzjthMGY7tSLteST3BlbkFJXHnGjZ1fKA2uVRQ2yP0w"


# use embedding API
# return One-dimensional array of size 1536
# take it as the similarity with 1536 dialogues in API database
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


def embedding_formula():
    with open("../output/formula in list (gpt4 explanation).json", "r", encoding="utf8") as f:
        formula_list = json.load(f)
    for index in range(len(formula_list)):
        if os.path.exists(
                "../output/useless/embedding/similarity/formula(explanation+formula)/" + str(index) + ".json"):
            continue
        temp = formula_list[index]
        temp.pop("before")
        temp.pop("after")
        temp.pop("url")
        input_str = json.dumps(temp, indent=4, ensure_ascii=False)
        try:
            similarity = get_embedding(input_str)
            print(index)
        except Exception as e:
            print(e)
            time.sleep(10)
            similarity = get_embedding(input_str)
        with open("../output/useless/embedding/similarity/formula(explanation+formula)/" + str(index) + ".json", "w",
                  encoding="utf8") as f:
            temp = json.dumps(similarity, ensure_ascii=False)
            f.write(temp)


def embedding_report():
    for docID in range(679):
        with open("../output/embedding/report key word/" + str(docID) + ".json", "r", encoding="utf8") as f:
            input_str = f.read()
        if input_str.lower().startswith("financial concepts:", 0, len("Financial concepts:")):
            input_str = input_str[len("Financial concepts:"):]
        try:
            similarity = get_embedding(input_str)
        except Exception as e:
            print(e)
            time.sleep(10)
            similarity = get_embedding(input_str)
        with open("../output/embedding/similarity/report/" + str(docID) + ".json", "w", encoding="utf8") as f:
            temp = json.dumps(similarity, ensure_ascii=False)
            f.write(temp)


def similar():
    report_embedding_list = []
    formula_embedding_list = []
    for reportID in range(679):
        with open("../output/useless/embedding/similarity/report/" + str(reportID) + ".json", "r",
                  encoding="utf8") as f:
            temp = json.load(f)
            report_embedding_list.append(temp)
    for formulaID in range(1141):
        with open("../output/useless/embedding/similarity/formula(explanation+formula)/" + str(formulaID) + ".json",
                  "r", encoding="utf8") as f:
            temp = json.load(f)
            formula_embedding_list.append(temp)
    with open("../output/formula in list (gpt4 explanation).json", "r", encoding="utf8") as f:
        formula_list = json.load(f)
    with open("../output/embedding/embedding_finQA_viewer3.0 (select 5 formula and add explanation).json", "r",
              encoding="utf8") as f:
        report_dic = json.load(f)
    for reportID in range(679):
        report_embedding = report_embedding_list[reportID]
        similar_index = search_formula(formula_embedding_list, report_embedding)
        temp_list = []
        for index in similar_index:
            item = formula_list[index]
            temp_list.append(item)
        report_dic[str(reportID)]["formula"] = temp_list
        print(reportID)
        # get the most similar formula
    with open("../output/embedding/embedding_finQA_viewer4.2 (key word embedding).json", "w",
              encoding="utf8") as f:
        temp = json.dumps(report_dic, indent=4, ensure_ascii=False)
        f.write(temp)


def search_formula(formula_embedding, text_embedding, n=similar_count):
    similarity = [cosine_similarity(x, text_embedding) for x in formula_embedding]
    # 对列表进行排序并获取前 similar_count 个元素的索引
    top_indices = sorted(range(len(similarity)), key=lambda i: similarity[i], reverse=True)[:n]
    return top_indices


def merge():
    with open('../output/embedding/used formula.json', 'r', encoding='utf8') as f:
        url_formula = json.load(f)
    with open('../output/embedding/used formula (only explanation).json', 'r', encoding='utf8') as f:
        explanation = json.load(f)
    formula_dic = {}
    for url in url_formula:
        temp_dic = url_formula[url]
        for item in temp_dic:
            formula = item["formula"]
            formula_dic[formula] = item
            formula_dic[formula]["explanation"] = explanation[formula]
    with open('../output/embedding/used formula (full).json', 'w', encoding='utf8') as f:
        temp = json.dumps(formula_dic, ensure_ascii=False)
        f.write(temp)
