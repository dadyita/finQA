import openai
import json
import tiktoken

# get embedding array of formula and data

# yilun's key: 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
# my key: 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
openai.api_key = "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"


def check_token(text_list):
    max_tokens = 8000
    embedding_encoding = "cl100k_base"
    encoding = tiktoken.get_encoding(embedding_encoding)
    for i in text_list:
        if not len(encoding.encode(i)) <= max_tokens:
            print("Check Token ERROR:" + i)


# use embedding API
# return One-dimensional array of size 1536
# take it as the similarity with 1536 dialogues in API database
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


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
    return [f_dict, formula_l, full_formula_l, dic, input_list]


def embedding_save():
    formula_dict, formula_list, full_formula_list, input_dic, ori_input_list = get_data()
    data_embedding = {'table': [], 'text': [], "table_text": []}
    formula_embedding = []

    # formula embedding
    try:
        for x in full_formula_list:
            formula_embedding.append(get_embedding(x))
        with open('../formula_embedding.json', 'w', encoding='utf8') as f0:
            temp = json.dumps(formula_embedding, ensure_ascii=False)
            f0.write(temp)
    except Exception as e:
        print(e)
        with open('../formula_embedding.json', 'w', encoding='utf8') as f0:
            temp = json.dumps(formula_embedding, ensure_ascii=False)
            f0.write(temp)
        print("1")

    # data embedding
    try:

        for index in range(input_dic['len']):
            # cate: text, table,table_text
            for category in input_dic:
                if category != 'len':
                    text = input_dic[category][index]
                    embedding = get_embedding(text)
                    data_embedding[category].append(embedding)
        with open('../data_embedding.json', 'w', encoding='utf8') as f0:
            temp = json.dumps(data_embedding, ensure_ascii=False)
            f0.write(temp)
    except Exception as e:
        print(e)
        with open('../data_embedding.json', 'w', encoding='utf8') as f0:
            temp = json.dumps(data_embedding, ensure_ascii=False)
            f0.write(temp)
        print("1")



