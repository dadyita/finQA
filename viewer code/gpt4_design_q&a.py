import json
import openai
import threading
import time
import os

# yilun's key: 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
# my key: sk-jOM3RhzjthMGY7tSLteST3BlbkFJXHnGjZ1fKA2uVRQ2yP0w
openai.api_key = "sk-jOM3RhzjthMGY7tSLteST3BlbkFJXHnGjZ1fKA2uVRQ2yP0w"

finish_list = []


class DesignQA(object):
    @staticmethod
    def design_qa(text):
        system = """A financial report and formulas related to the financial reprot represented by a python dictionary, and the structure of the dictctionary is as follows.
{
"pre_text":[sentece1,sentence2...],
"table":[[word1,word2...],[word1,word2...]...],
"post_text":[[sentece1,sentence2...],
"formula_list":[
{"formula":formula,"explanation":explanation},
{"formula":formula,"explanation":explanation}
]
}
Where 

- "pre_text" is a list representing the text before table  in the financial report and each item is a sentence.
- "table" is a nested list representing a table in the financial report, each item of the outer list is an inner list representing a row of the table and the first inner list represents the first row, the second inner list represents the second row, and so on. Each item of inner list is the value of a cell of the table.
- "post_text" is a list representing the text after table  in the financial report and each item is a sentence.
- "formula_list" is a list representing formulas related to the financial reprot. Each item is a dict with two key-value. The first key-value is formula and the second key-value is the explanation of formula.

The task is to try to devise a question and answer with each formula (20 formulas). Check all formulas in the formula list. The designed question answering needs to meet the following requirements.

1. The question and answer must involve one of the formulas in the list of financial statements and formulas.
2. The variables that must be asked in design questions cannot be obtained directly in "pre_text", "table" or "post_text", but can be calculated through the formulas and data in "pre_text", "table" or "post_text".
3. If some variables are missing when calculating the answer with the formula, but some variables can be obtained from "pre_text", "table" or "post_text", ignore the missing variables and treat them as 0. Note that you can only assume missing variables when some variables are available from "pre_text", "table" or "post_text", and missing variables can only be assumed to be 0.
4. Output "It is impossible to design Q&A meet the above requirements." when you can't design Q&A meet requirements


Output in the following format. Note that Fomula1,3,20 is output format if you can design Q&A use this formula. Fomula2 is output format if you can't design Q&A use this formula. If there are formulas can be used to design Q&A meet requirement, output "We can design Q&A meet requirement" at the end.Otherwise, output "We can't design any Q&A meet requirement.":

Formula1:formula
Question1:
Answer1:
Variables come from "pre_text", "table" or "post_text":

Formula2:fomula
***It is impossible to design Q&A meet the above requirements.

Formula3:formula
Question3:
Answer3:
Variables come from "pre_text", "table" or "post_text":

....
Formula20:formula
Question20:
Answer20:
Variables come from "pre_text", "table" or "post_text":

We can design Q&A meet requirement./We can't design any Q&A meet requirement."""
        user1 = """{
"pre_text":[sentece1,sentence2...],
"post_text":[[sentece1,sentence2...],
"table":[[word1,word2...],[word1,word2...]...],
"formula_list":[
{"formula":formula,"explanation":explanation},
{"formula":formula,"explanation":explanation}
]
}"""
        assistant1 = """Formula1:formula
Question1:
Answer1:
Variables come from financial report:

Formula2:formula
 It is impossible to design Q&A meet the above requirements.

Formula3:formula
Question3:
Answer3:
Variables come from financial report:
....
Formula20:formula
Question20:
Answer20:
Variables come from financial report:

END!!!"""
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": system},
                # {"role": "user", "content": user1},
                # {"role": "assistant", "content": assistant1},
                {"role": "user", "content": text}
            ],
            temperature=0,
        )
        # response_text = response['choices'][0]['text']
        response_text = response['choices'][0]['message']['content']
        return response_text

    @staticmethod
    def run(t_count):
        for i in range(679):
            str_doc_id = str(i)
            if os.path.exists("../output/embedding/ver4.1/" + str_doc_id + ".json"):
                finish_list.append(i)
        with open("../output/embedding/embedding_finQA_viewer4.2 (key word embedding).json", 'r',
                  encoding='utf8') as f:
            text_dic = json.load(f)
        t_list = []
        print(finish_list)
        for i in range(t_count):
            t = threading.Thread(target=DesignQA.process,
                                 args=(i, t_count, text_dic))
            t_list.append(t)
            t.start()

        for t in t_list:
            t.join()

    @staticmethod
    def process(thread_id, thread_count, text_dic):
        # 每个线程执行的doc_id分配
        total = len(text_dic)
        step = total / thread_count
        start = int(thread_id * step)
        end = int(thread_id * step + step)
        count = 0
        for str_doc_id in text_dic:
            doc_id = int(str_doc_id)
            # 如果是自己线程执行的id
            if start <= doc_id < end and doc_id not in finish_list and count <= 4:
                # 生成随机数
                # temp = random.choice([i for i in range(0, 678) if i not in finish_list])
                # str_doc_id = str(temp)

                # 获取给api的输入
                input_dic = text_dic[str_doc_id]
                input_dic_str = json.dumps(input_dic, indent=4, ensure_ascii=False)
                try:
                    start_time = time.time()  # record the start time
                    print("Thread-" + str(thread_id) + ":Start Process docID-" + str_doc_id)
                    # 调用API
                    response = DesignQA.design_qa(input_dic_str)
                    with open("../output/embedding/ver4.1/" + str_doc_id + ".json", "w",
                              encoding='utf8') as f:
                        f.write(response)

                    # if response.endswith("We can design Q&A meet requirement."):
                    #     with open("../output/embedding/ver4.1/" + str_doc_id + ".json", "w",
                    #               encoding='utf8') as f:
                    #         f.write(response)
                    # else:
                    #     with open("../output/embedding/ver4.1/can't/" + str_doc_id + ".json", "w",
                    #               encoding='utf8') as f:
                    #         f.write(response)

                    end_time = time.time()  # record the end time
                    elapsed_time = end_time - start_time  # calculate the elapsed time
                    print(f"Elapsed time: {elapsed_time:.2f} seconds")  # display the elapsed time
                    print("Thread-" + str(thread_id) + ":Finish Process docID-" + str_doc_id)
                    finish_list.append(doc_id)
                    # finish_list.append(temp)
                    # count = count + 1
                except Exception as e:
                    print(e)
                    print("Error in docID-" + str_doc_id + "!!!\n\n\n")
                # if count == 4:
                #     break


def add():
    with open("../output/embedding/embedding_finQA_viewer4.2 (key word embedding).json", "r",
              encoding="utf8") as f:
        dic = json.load(f)
    for i in range(679):
        str_doc_id = str(i)
        if os.path.exists("../output/embedding/ver4.1/" + str_doc_id + ".json"):
            with open("../output/embedding/ver4.1/" + str_doc_id + ".json", "r", encoding="utf-8") as f:
                temp = f.read()
                dic[str_doc_id]["exampleQA"] = temp.replace("$", "￥").replace("\n", "<br>")
        else:
            dic[str_doc_id]["exampleQA"] = "END!!!"
    with open("../output/embedding/embedding_finQA_viewer4.2 (key word embedding).json", "w", encoding="utf8") as f:
        temp = json.dumps(dic, ensure_ascii=False)
        f.write(temp)


def cannot_formula_filter():
    doc = {}
    for i in range(679):
        str_doc_id = str(i)
        if os.path.exists("../output/embedding/ver4.1/" + str_doc_id + ".json"):
            with open("../output/embedding/ver4.1/" + str_doc_id + ".json", "r", encoding="utf-8") as f:
                temp = f.read()
                doc[str_doc_id] = temp

    # 按照formula分item
    doc = {key: value.split('\n\n') for key, value in doc.items()}
    for doc_id in doc:
        value = doc[doc_id]
        # 去除不可能
        # value = [x for x in value if not x.endswith('***It is impossible to design Q&A meet the above requirements.')]
        # 去除结尾判断
        value = [x for x in value if not x.startswith('We ')]

        # 把impossible设为空
        for index in range(len(value)):
            x = value[index]
            if x.endswith('***It is impossible to design Q&A meet the above requirements.'):
                value[index] = ''

        doc[doc_id] = value

    # 去除不为20个formula的doc
    doc = {key: value for key, value in doc.items() if len(value) == 20}

    # for doc_id in doc:
    #     lis = doc[doc_id]
    #     new_lis = {}
    #     for item in lis:
    #         # 取出formula
    #         formula = item[item.index(':') + 1:item.index('\n')]
    #         # 取出 Q&A
    #         new_lis[formula] = item[item.index('\n') + 1:]
    #     doc[doc_id] = new_lis

    # 去除全空的
    new_doc = {}
    for doc_id in doc:
        item = doc[doc_id]
        flag = True
        for x in item:
            if x != '':
                flag = False
        if not flag:
            new_doc[doc_id] = item
    for doc_id in new_doc:
        with open("../output/embedding/ver4.1/filter/" + doc_id + ".json", "w",
                  encoding='utf8') as f:
            temp = json.dumps(doc[doc_id], ensure_ascii=False)
            f.write(temp)


def add_v2():
    cannot_formula_filter()
    with open("../output/embedding/embedding_finQA_viewer4.2 (key word embedding).json", "r",
              encoding="utf8") as f:
        dic = json.load(f)
    for i in range(679):
        str_doc_id = str(i)
        if os.path.exists("../output/embedding/ver4.1/filter/" + str_doc_id + ".json"):
            with open("../output/embedding/ver4.1/filter/" + str_doc_id + ".json", "r", encoding="utf-8") as f:
                # example_qa取出设计的问题
                example_qa = json.load(f)
                # formula_index_list可以设计问题的formula在ori_formula_list中的index
                formula_index_list = [index for index in range(len(example_qa)) if example_qa[index] != '']
                ori_formula_list = dic[str_doc_id]['formula']
                # 剔除没用的formula
                new_formula_list = [ori_formula_list[index] for index in formula_index_list]
                # example_qa去掉空的
                example_qa = [x for x in example_qa if x != '']
                str_example_qa = ''
                for x in example_qa:
                    str_example_qa = str_example_qa + x + '\n\n'
                dic[str_doc_id]['formula'] = new_formula_list
                dic[str_doc_id]["exampleQA"] = str_example_qa.replace("$", "￥").replace("\n", "<br>")
        else:
            dic[str_doc_id]["exampleQA"] = ""

    # 替代 $ 至 ￥
    for i in range(679):
        str_doc_id = str(i)
        item = dic[str_doc_id]
        item['pre_text'] = [x.replace("$", "￥") for x in item['pre_text']]
        item['post_text'] = [x.replace("$", "￥") for x in item['post_text']]
        item['table'] = [[y.replace("$", "￥") for y in x] for x in item['table']]
        dic[str_doc_id] = item
        # item['formula']=[]

    with open("../output/embedding/embedding_finQA_viewer4.3 (filter formula).json", "w", encoding="utf8") as f:
        temp = json.dumps(dic, ensure_ascii=False)
        f.write(temp)

# try:
#     os.makedirs("../output/embedding/ver4.1")
# except Exception as e:
#     print(e)
# DesignQA.run(5)
