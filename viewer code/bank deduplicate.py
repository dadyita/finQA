import json
import numpy as np
import textdistance
from sklearn.feature_extraction.text import TfidfVectorizer


def remove_similar_formulas(dic, threshold):
    formula_url = {}
    for formula in dic:
        formula_url[formula] = dic[formula]["url"]
    processed_formulas = {
        formula: formula.replace("\\text", "").replace("\\frac", "").replace("\\", "").replace("displaystyle", "").replace("{", "").replace("}", "") for formula in
        formula_url}
    tfidf = TfidfVectorizer().fit_transform(list(processed_formulas.values()))
    rows, cols = np.where((tfidf * tfidf.T).A > threshold)
    similar_indices = set()
    formulas = list(processed_formulas.keys())
    for row, col in zip(rows, cols):
        if row != col and formula_url[formulas[row]] != formula_url[formulas[col]]:
            if textdistance.jaccard(processed_formulas[formulas[row]], processed_formulas[formulas[col]]) > threshold:
                if len(formulas[row]) > len(formulas[col]):
                    similar_indices.add(col)
                else:
                    similar_indices.add(row)
    return {key: value for i, (key, value) in enumerate(dic.items()) if i not in similar_indices}


def how_many_formula():
    with open('../output/embedding_finQA_viewer.json', 'r', encoding='utf8') as f:
        dic = json.load(f)
    formula_dic = {}
    for doc_id in dic:
        for index in dic[doc_id]:
            if index in ["formula_table", "formula_table", "formula_text"]:
                sub_dic = dic[doc_id][index]
                for i in sub_dic:
                    formula = i["formula"]
                    formula_dic[formula] = ""
    print(formula_dic)


def bank_deduplicate():
    with open('output/merge.json', 'r', encoding='utf8') as f:
        dic = json.load(f)
    new_dic = remove_similar_formulas(dic, 0.55)
    dic = {key: value for key, value in dic.items() if key in new_dic}
    with open('new_output/merge.json', 'w', encoding='utf8') as f:
        temp = json.dumps(dic, ensure_ascii=False)
        f.write(temp)


