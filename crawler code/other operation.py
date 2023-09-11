import json


def del_not_formula():
    f = open('new.json', 'r', encoding='utf8')
    content = f.read()
    dic = json.loads(content)
    f.close()
    for url, formula_dic in dic.items():
        new_dic = {}
        for formula in formula_dic:
            left = False
            right = False
            if '=' in formula:
                for char in formula[:formula.index("=")]:
                    # Check if the character is an alphabetic character
                    if char.isalpha():
                        left = True
                        break
                for char in formula[formula.index("="):]:
                    # Check if the character is an alphabetic character
                    if char.isalpha():
                        right = True
                        break
                bool5 = left and right
                if bool5:
                    new_dic[formula] = formula_dic[formula]
                    new_dic[formula]['url'] = url
            else:
                new_dic[formula] = formula_dic[formula]
                new_dic[formula]['url'] = url
        dic[url] = new_dic
    f = open('new1.json', 'w', encoding='utf8')
    temp = json.dumps(dic, ensure_ascii=False)
    f.write(temp)
    f.close()


def deduplicate():
    f0 = open('output/ver4.0_formula_list_10.json', 'r', encoding='utf8')
    content0 = f0.read()
    dic0 = json.loads(content0)

    f1 = open('output/add/format_accounting_formula_list.json', 'r', encoding='utf8')
    content1 = f1.read()
    dic1 = json.loads(content1)

    f2 = open('output/add/format_economics_formula_list.json', 'r', encoding='utf8')
    content2 = f2.read()
    dic2 = json.loads(content2)

    f3 = open('add.json', 'r', encoding='utf8')
    content3 = f3.read()
    dic3 = json.loads(content3)

    f0.close()
    f1.close()
    f2.close()
    f3.close()

    dic1.update(dic2)
    for i in dic0:
        for j in dic1:
            if j == i:
                dic1.pop(j)
                break

    seen = set()

    for key, value in dic3.items():
        if tuple(value) not in seen:
            print(1)
            seen.add(tuple(value))

    dic0 = {}

    for key, value in dic1.items():
        if tuple(value) not in seen:
            dic0[key] = value
            seen.add(tuple(value))
    temp = json.dumps(dic0, ensure_ascii=False)
    f2 = open('add_formula.json', 'w', encoding='utf-8')
    f2.write(temp)
    f2.close()


def del_url():
    f = open('new1.json', 'r', encoding='utf8')
    content = f.read()
    dic = json.loads(content)
    new_dic = {}
    for url, f_dic in dic.items():
        for f in f_dic:
            new_dic[f] = f_dic[f]

    f = open('new2.json', 'w', encoding='utf8')
    temp = json.dumps(new_dic, ensure_ascii=False)
    f.write(temp)
    f.close()


def merge_json():
    f = open('format_formula.json', 'r', encoding='utf8')
    content = f.read()
    dic1 = json.loads(content)
    f.close()
    f = open('add_format_formula.json', 'r', encoding='utf8')
    content = f.read()
    dic2 = json.loads(content)
    f.close()
    dic2.update(dic1)
    f = open('merge.json', 'w', encoding='utf8')
    temp = json.dumps(dic2, ensure_ascii=False)
    f.write(temp)
    f.close()


del_not_formula()
del_url()
