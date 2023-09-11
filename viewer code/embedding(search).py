import json
from openai.embeddings_utils import cosine_similarity

# compare cosine similarity of embedding array of formula and data
# and search the most similar_count relevant formula
similar_count = 10


def get_data():
    # load formula
    with open('../output/formula.json', 'r', encoding='utf8') as f:
        f_dict = json.load(f)
    formula_l = [k for k in f_dict]
    full_formula_l = [f"{v['url']},{v['before']},{k}, {v['after']}" for k, v in f_dict.items()]

    # load input
    with open('../dataset/dev.json', 'r', encoding='utf8') as f:
        input_list = json.load(f)
    with open('../dataset/test.json', 'r', encoding='utf8') as f:
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
    with open("../output/data_embedding.json", 'r', encoding='utf8') as f:
        data_embedding = json.load(f)
    with open("../output/formula_embedding.json", 'r', encoding='utf8') as f:
        formula_embedding = json.load(f)
    return [f_dict, formula_l, full_formula_l, dic, input_list, data_embedding, formula_embedding]


def similar():
    formula_dict, formula_list, full_formula_list, input_dic, ori_input_list, data_embedding, formula_embedding = get_data()
    for index in range(input_dic['len']):
        for category in input_dic:
            if category != 'len':
                text_embedding = data_embedding[category][index]
                similar_index = search_formula(formula_embedding, text_embedding)
                # get the most similar formula
                most_similar_formula = [formula_list[i] for i in similar_index]
                full_formula = []
                for formula in most_similar_formula:
                    t_dict = {'formula': formula}
                    t_dict.update(formula_dict[formula])
                    full_formula.append(t_dict)

                # add into ori_input
                ori_input_list[index]["formula_" + category] = full_formula

    with open('../output/embedding_finQA_data.json', 'w', encoding='utf8') as f:
        temp = json.dumps(ori_input_list, ensure_ascii=False)
        f.write(temp)


def search_formula(formula_embedding, text_embedding, n=similar_count):
    similarity = [cosine_similarity(x, text_embedding) for x in formula_embedding]
    # 对列表进行排序并获取前 similar_count 个元素的索引
    top_indices = sorted(range(len(similarity)), key=lambda i: similarity[i], reverse=True)[:n]
    return top_indices



