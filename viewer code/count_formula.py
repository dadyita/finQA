import json

if __name__ == '__main__':
    with open("../output/embedding/embedding_finQA_viewer4.3 (filter formula).json", "r", encoding="utf8") as f:
        doc_dic = json.load(f)
    formula_list = []
    formula_count_list = []
    for docid, doc in doc_dic.items():
        item_formula_list = doc['formula']
        for i in item_formula_list:
            formula = i['formula']
            temp_dic = {}
            if formula not in formula_list:
                formula_list.append(formula)
                temp_dic['formula'] = formula
                temp_dic['count'] = 1
                formula_count_list.append(temp_dic)
            else:
                index = formula_list.index(formula)
                formula_count_list[index]['count'] += 1
    with open('../count.json', 'w', encoding='utf8') as f:
        temp = json.dumps(formula_count_list, ensure_ascii=False)
        f.write(temp)
