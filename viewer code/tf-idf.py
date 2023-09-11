import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy


similar_count = 10


def get_data():
    # load formula
    with open('new_output/merge.json', 'r', encoding='utf8') as f:
        f_dict = json.load(f)
    formula_l = [k for k in f_dict]
    full_formula_l = [f"{v['url']},{v['before']},{k}, {v['after']}" for k, v in f_dict.items()]

    # load input
    with open('dataset/dev.json', 'r', encoding='utf8') as f:
        input_list = json.load(f)
    with open('dataset/test.json', 'r', encoding='utf8') as f:
        add_input_list = json.load(f)
    input_list = input_list + add_input_list
    # input to string
    dic = {'table': [], 'text': [], 'table_text': []}
    for d in input_list:
        table = [f"{', '.join(i)}" for i in d['table']]
        table_text = f"{', '.join(table)}"
        dic['table'].append(f"{table_text}")
        dic['text'].append(f"{', '.join(d['pre_text'])},{', '.join(d['post_text'])}")
        dic['table_text'].append(f"{', '.join(d['pre_text'])},{', '.join(d['post_text'])},{table_text}")

    # reduplicate
    temp_1 = {}
    for i in range(len(dic['table_text'])):
        temp_1[dic['table_text'][i]] = i
    index = list(temp_1.values())
    input_list = [input_list[i] for i in index]
    dic = {k: [dic[k][i] for i in index] for k, v in dic.items()}
    dic['len'] = len(index)
    return [f_dict, formula_l, full_formula_l, dic, input_list]


def similar():
    formula_dict, formula_list, full_formula_list, input_dic, ori_input_list = get_data()
    # create TfidfVectorizer object
    vectorizer = TfidfVectorizer()
    # fit_transform the formula bank
    tfidf = vectorizer.fit_transform(full_formula_list)
    for index in range(input_dic['len']):
        for category in input_dic:
            if category != 'len':
                text = input_dic[category][index]
                # transform the input text
                input_tfidf = vectorizer.transform([text])
                # compute the cosine similarity between input_tfidf and tfidf
                cosine_similarities = cosine_similarity(input_tfidf, tfidf).flatten()
                # get the index of the most a similar formula
                most_similar_formula_index = numpy.argsort(cosine_similarities)[-similar_count:].tolist()
                most_similar_formula_index.reverse()
                # get the most similar formula
                most_similar_formula = [formula_list[i] for i in most_similar_formula_index]
                full_formula = []
                for formula in most_similar_formula:
                    t_dict = {'formula': formula}
                    t_dict.update(formula_dict[formula])
                    full_formula.append(t_dict)

                # add into ori_input
                ori_input_list[index]["formula_" + category] = full_formula

    with open('new_output/finQA_data.json', 'w', encoding='utf8') as f:
        temp = json.dumps(ori_input_list, ensure_ascii=False)
        f.write(temp)


similar()
