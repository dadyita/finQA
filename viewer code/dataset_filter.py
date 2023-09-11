import os
import json
import re
import tiktoken
import openai
import threading

# yilun's key: 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
# my key: sk-jOM3RhzjthMGY7tSLteST3BlbkFJXHnGjZ1fKA2uVRQ2yP0w
openai.api_key = "sk-jOM3RhzjthMGY7tSLteST3BlbkFJXHnGjZ1fKA2uVRQ2yP0w"

doc_list = []


class TextProcess(object):
    @staticmethod
    def del_dollar(formula_list):
        for index in range(len(formula_list)):
            for category in formula_list[index]:
                if category == "before" or category == "after":
                    if '$' in formula_list[index][category]:
                        formula_list[index][category] = formula_list[index][category].replace("$", "￥")
        return formula_list

    @staticmethod
    def text_process(text_list):
        regex = re.compile('[a-zA-Z]')
        text_list = [i for i in text_list if regex.search(i)]
        for i in range(len(text_list)):
            text_list[i] = text_list[i].replace("$", "￥")
            '''
            if text_list[i].count(".") > 1:
                dot_index = text_list[i].find(".")
                left_substring = text_list[i][dot_index - 1:dot_index]
                right_substring = text_list[i][dot_index + 1:dot_index + 2]
                flag = left_substring.isdigit() or right_substring == " " or right_substring.isdigit()
                flag = flag or text_list[i][dot_index - 1:dot_index + 2] == "u.s"
                if not flag:
                    print(text_list[i])'''
            # text_list[i] = text_list[i].capitalize()

        return text_list

    @staticmethod
    def check_token(doc_id, category, text):
        max_tokens = 1500
        embedding_encoding = "cl100k_base"
        encoding = tiktoken.get_encoding(embedding_encoding)
        l1 = len(encoding.encode(text))
        if not l1 <= max_tokens:
            print("Check Token ERROR:" + doc_id + "-" + category + "-" + str(len(encoding.encode(text))) + "-")
        return l1

    @staticmethod
    def process(index, data):
        temp_dic = {}
        count = 0
        try:
            for doc_id in data:
                if int(doc_id) % 15 == index and doc_id not in doc_list:
                    # pattern = re.compile(r'^\d+\.')
                    pre_text = ''.join(data[doc_id]["pre_text"])
                    if pre_text:
                        # data[doc_id]["pre_text"] = [string for string in split_sentences(pre_text) if pattern.match(string)]
                        data[doc_id]["pre_text"] = [s for s in TextProcess.split_sentences(pre_text) if s != '']
                    print("doc-id:" + doc_id + "-pre_text")
                    print(data[doc_id]["pre_text"])
                    post_text = ''.join(data[doc_id]["post_text"])
                    if post_text:
                        data[doc_id]["post_text"] = [s for s in TextProcess.split_sentences(post_text) if s != '']
                    print("doc-id:" + doc_id + "-post_text")
                    print(data[doc_id]["post_text"])

                    # load
                    temp_list = [data[doc_id]["pre_text"], data[doc_id]["post_text"]]
                    temp_dic[doc_id] = temp_list
                    count = count + 1
                    if count % 5 == 0:
                        filename = "pre post text-" + str(index) + ".json"
                        with open('../output/A tempText/' + filename, 'w', encoding='utf8') as f:
                            temp = json.dumps(temp_dic, ensure_ascii=False)
                            f.write(temp)
            filename = "pre post text-" + str(index) + ".json"
            with open('../output/A tempText/' + filename, 'w', encoding='utf8') as f:
                temp = json.dumps(temp_dic, ensure_ascii=False)
                f.write(temp)
        except Exception as e:
            print("Error!!!")
            print(e)

    @staticmethod
    def main():
        with open('../output/embedding/new_embedding_finQA_viewer.json', 'r', encoding='utf8') as f:
            data = json.load(f)
        # 存储pre_text_list和post_text_list
        # item数量为docID的两倍
        t_list = []
        for i in range(15):
            t = threading.Thread(target=TextProcess.process, args=(i, data))
            t_list.append(t)
            t.start()

        for t in t_list:
            t.join()

    @staticmethod
    def split_sentences(text):
        system = "把下面的文本分割成句子，首字母大写。最后标上序号，序号要求为“数字+.”的形式（英文作答）"
        '''请注意，最后一句话有可能是介绍一个表格的句子，他错误的包含了一部分的表格数据/标题，请判断后删除最后一句话中的表格内容。'''
        '''
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="把下面的文本分割成句子，并标上序号（英文作答）\n\n\n" + text,
            max_tokens=2048,
            temperature=0,
        )'''
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            temperature=0,
        )
        # response_text = response['choices'][0]['text']
        response_text = response['choices'][0]['message']['content']
        response_list = response_text.split("\n")
        return response_list

    @staticmethod
    def merge():
        doc_dic = {}
        for index in range(15):
            try:
                with open('../output/A tempText/pre post text-' + str(index) + '.json', 'r', encoding='utf8') as f:
                    temp = json.load(f)
                    for i in temp:
                        doc_dic[i] = temp[i]
                        doc_list.append(i)
            except Exception as e:
                print(e)
        with open('../output/A tempText/pre post text.json', 'r', encoding='utf8') as f:
            temp = json.load(f)
            for i in temp:
                doc_dic[i] = temp[i]
                doc_list.append(i)
        with open('../output/A tempText/pre post text.json', 'w', encoding='utf8') as f:
            temp = json.dumps(doc_dic)
            f.write(temp)

    @staticmethod
    def get_doc_list():
        with open('../output/A tempText/pre post text.json', 'r', encoding='utf8') as f:
            temp = json.load(f)
            for i in temp:
                doc_list.append(i)


class FormulaProcess(object):

    @staticmethod
    def change_format(text):
        system = "the origin json list format is as follows:\n[{\"formula\":fomula,\"before\":formula-before-text,\"after\":formula-after-text,\"url\":url},{\"formula\":fomula,\"before\":formula-before-text,\"after\":formula-after-text,\"url\":url}...]\nEach \"before\" and \"after\" in the items of the list is related to the text of the formula and explains the variables in the formula.\nYou need to complete three steps: (1)understand and modify the formula based on \"before\" and \"after\" and gpt's knowledge, replace the variables in the formula with nouns that someone without  any financial background knowledge can understand  (2) Convert the formula in LaTeX format into formula in mathematical format.Ensure that the formula does not contain any LaTeX formatting.\nThe final output should be in the following JSON format. :\n[{\"ori\": ori-fomula,\"change\":changed formula,\"before\":formula-before-text,\"after\":formula-after-text,\"url\":url},{\"ori\": ori-fomula,\"change\":changed formula,\"before\":formula-before-text,\"after\":formula-after-text,\"url\":url}...]"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            temperature=0,
        )
        # response_text = response['choices'][0]['text']
        response_text = response['choices'][0]['message']['content']
        return response_text

    @staticmethod
    def run():
        with open("../output/embedding/embedding_formula.json", 'r', encoding='utf8') as f:
            url_dic = json.load(f)
        t_list = []
        t_count = 20
        for i in range(t_count):
            t = threading.Thread(target=FormulaProcess.process, args=(i, t_count, url_dic))
            t_list.append(t)
            t.start()

        for t in t_list:
            t.join()

    @staticmethod
    def process(thread_id, thread_count, url_dic):
        embedding_encoding = "cl100k_base"
        encoding = tiktoken.get_encoding(embedding_encoding)
        url_list = [url for url in url_dic]
        for index in range(len(url_list)):
            if index % thread_count == thread_id and not os.path.exists(
                    "../output/embedding/process formula/urlID" + str(index) + ".json"):
                url = url_list[index]
                text_formula_list = json.dumps(url_dic[url], indent=4, ensure_ascii=False)
                length = len(encoding.encode(text_formula_list))
                if length < 1300:
                    change_item_formula_list = []
                    try:
                        print("Thread-" + str(thread_id) + ":Start Process url-" + str(index))
                        change_item_formula_list = json.loads(FormulaProcess.change_format(text_formula_list))
                        with open("../output/embedding/process formula/urlID" + str(index) + ".json", 'w',
                                  encoding='utf8') as f:
                            temp = json.dumps(change_item_formula_list, indent=4, ensure_ascii=False)
                            f.write(temp)
                        print("Thread-" + str(thread_id) + ":Finish Process url-" + str(index))
                    except Exception as e:
                        print("ERROR!!!\n\n\n")
                        print(change_item_formula_list)
                        print(e)


class FormulaProcessV2(object):

    @staticmethod
    def change_format(text):
        system = """the origin json list format is as follows:[{"formula":fomula,"before":formula-before-text,"after":formula-after-text,"url":url},{"formula":fomula,"before":formula-before-text,"after":formula-after-text,"url":url}...]
Each "before" and "after" in the items of the list is related to the text of the formula and explains the variables in the formula. 
You need to complete four steps:
(1)Convert the formula in LaTeX format into formula in mathematical format.Ensure that the formula does not contain any LaTeX formatting.
(2)understand every variable in the formula and replace the every variables in the formula with Financial nouns or everyday expressions
(3) make sure every variable in the formula can be understand without help of "before" and "after"
(4)give the explanation of changed formula
The final output should be in the following JSON format. :
[{"ori": ori-fomula,"change":changed formula and explanation},{"ori": ori-fomula,"change":explanation}...]"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            temperature=0,
        )
        # response_text = response['choices'][0]['text']
        response_text = response['choices'][0]['message']['content']
        return response_text

    @staticmethod
    def run(t_count):
        finish = []
        for i in range(1200):
            if os.path.exists("../output/embedding/all formula explanation/" + str(i) + ".json"):
                finish.append(i)
        with open("../output/formula in list.json", 'r', encoding='utf8') as f:
            formula_list = json.load(f)
        t_list = []
        for i in range(t_count):
            t = threading.Thread(target=FormulaProcessV2.process, args=(i, t_count, formula_list, finish))
            t_list.append(t)
            t.start()

        for t in t_list:
            t.join()

    @staticmethod
    def process(thread_id, thread_count, formula_list, finish):
        # 每个线程执行的doc_id分配
        total = len(formula_list)
        step = total / thread_count
        start = int(thread_id * step)
        end = int(thread_id * step + step)

        for index in range(start, end, 5):
            if index in finish:
                continue
            index_end = min(end, index + 5)
            input_list = [formula_list[x] for x in range(index, index_end)]
            str_input = json.dumps(input_list, indent=4, ensure_ascii=False)
            try:
                print("Thread-" + str(thread_id) + ":Start Process FormulaIndex-" + str(index))
                response = FormulaProcessV2.change_format(str_input)
                change_item_formula_list = json.loads(response)
                with open("../output/embedding/all formula explanation/" + str(index) + ".json", 'w',
                          encoding='utf8') as f:
                    temp = json.dumps(change_item_formula_list, indent=4, ensure_ascii=False)
                    f.write(temp)
                print("Thread-" + str(thread_id) + ":Finish Process url-" + str(index))
            except Exception as e:
                print("ERROR!!! " + str(index) + "\n\n\n")
                print(e)


class DeleteFormulaProcess(object):
    decoder_error_id = []
    error_response = {}

    @staticmethod
    def check_formula():
        # embedding_encoding = "cl100k_base"
        # encoding = tiktoken.get_encoding(embedding_encoding)
        with open("../output/embedding/merge_embedding_finQA_viewer.json", 'r', encoding='utf8') as f:
            text_dic = json.load(f)
        with open("../output/embedding/formula and explanation.json", 'r', encoding='utf8') as f:
            formula_dic = json.load(f)
        for doc_id in text_dic:
            input_dic = {'pre_text': text_dic[doc_id]['pre_text'], 'post_text': text_dic[doc_id]['post_text'],
                         'table': text_dic[doc_id]['table']}
            sub_formula_list = []
            for item in text_dic[doc_id]['formula']:
                formula = item['formula']
                explanation = formula_dic[formula]
                sub_formula_list.append({"formula": formula, "explanation": explanation})
            input_dic['formula_list'] = sub_formula_list
            input_dic_str = str(input_dic)
            if doc_id == "451":
                print(input_dic_str)
            # l1 = len(encoding.encode(input_dic_str))
            # l2 = len(encoding.encode(str(sub_formula_list)))
            # if l1 > 3600:
            # print(doc_id + '-' + str(l1) + "-" + str(l2))
            # print(input_dic)

    @staticmethod
    def delete_formula(text):
        system = "There is a Python dictionary structured as follows:{\"pre_text\":[sentence1,sentence2...],\"pro_text\":[sentence1,sentence2...],\"table\":[[word1,word2...],[word1,word2...]...],\"formula_list\":[{\"formula\":formula,\"explanation\":explanation},{\"formula\":formula,\"explanation\":explanation}]}. Where pre_text, pro_text, and table store some financial data, and formula_list stores financial formulas related to pre_text, pro_text, and table, as well as text explaining the formulas. I want to find five formulas from this dictionary. These five formulas can be used to answer financial questions that require data from pre_text, pro_text, and table.The output should be a JSON list only, without any additional text. The output JSON list should be in the following format：[{\"formula\":formula1},{\"formula\":formula2},{\"formula\":formula3},{\"formula\":formula4},{\"formula\":formula5}]\nNote: formula1 to formula5 are directly obtained from the \"formula\" key's value in the \"formula_list\" item. Do not change the original values."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            temperature=0,
        )
        # response_text = response['choices'][0]['text']
        response_text = response['choices'][0]['message']['content']
        return response_text

    @staticmethod
    def run(t_count):
        with open("../output/embedding/merge_embedding_finQA_viewer.json", 'r', encoding='utf8') as f:
            text_dic = json.load(f)
        with open("../output/embedding/formula and explanation.json", 'r', encoding='utf8') as f:
            formula_dic = json.load(f)
        with open("../output/embedding/formula after delete/merge.json", 'r', encoding='utf8') as f:
            finish_list = json.load(f)
        with open("../output/embedding/formula after delete/decoder_error_id.json", 'r', encoding='utf8') as f:
            DeleteFormulaProcess.decoder_error_id = json.load(f)
        t_list = []
        for i in range(t_count):
            t = threading.Thread(target=DeleteFormulaProcess.process,
                                 args=(i, t_count, text_dic, formula_dic, finish_list))
            t_list.append(t)
            t.start()

        for t in t_list:
            t.join()

    @staticmethod
    def process(thread_id, thread_count, text_dic, formula_dic, finish_list):

        # 每个线程执行的doc_id分配
        total = len(text_dic)
        step = total / thread_count
        start = int(thread_id * step)
        end = int(thread_id * step + step)

        # 输出json的字典
        output_dic = {}
        for str_doc_id in text_dic:
            doc_id = int(str_doc_id)

            # 如果是自己线程执行的id 并且不在finish_list，error_list里面
            if start <= doc_id < end and str_doc_id in DeleteFormulaProcess.decoder_error_id:
                # 获取给api的输入
                input_dic = {'pre_text': text_dic[str_doc_id]['pre_text'],
                             'post_text': text_dic[str_doc_id]['post_text'],
                             'table': text_dic[str_doc_id]['table']}
                sub_formula_list = []
                for item in text_dic[str_doc_id]['formula']:
                    formula = item['formula']
                    explanation = formula_dic[formula]
                    sub_formula_list.append({"formula": formula, "explanation": explanation})
                input_dic['formula_list'] = sub_formula_list
                input_dic_str = str(input_dic)

                try:
                    print("Thread-" + str(thread_id) + ":Start Process docID-" + str_doc_id)

                    # 调用API
                    response = DeleteFormulaProcess.delete_formula(input_dic_str)
                    try:

                        # 检查是否是json格式
                        output_list = json.loads(response)

                        # 如果是json，则将api response 加入输出dict
                        output_dic[str_doc_id] = output_list
                        print(output_list)
                    except json.decoder.JSONDecodeError as decode_error:

                        # 若不是则输出并存储response进行检查
                        print("json.decoder.JSONDecodeError in docID-" + str_doc_id + "!!!")

                        # error_response是输出的error response
                        DeleteFormulaProcess.error_response[str_doc_id] = response
                        print(response)
                        with open("../output/embedding/formula after delete/error_response.json", "w",
                                  encoding='utf8') as f:
                            t = json.dumps(DeleteFormulaProcess.error_response, ensure_ascii=False)
                            f.write(t)
                        print(decode_error)

                    # 每执行 3 次保存
                    # if (doc_id - start) % 3 == 2:
                    with open("../output/embedding/formula after delete/" + str(thread_id) + ".json", "w",
                              encoding='utf8') as f:
                        t = json.dumps(output_dic, ensure_ascii=False)
                        f.write(t)

                    print("Thread-" + str(thread_id) + ":Finish Process docID-" + str_doc_id)

                except Exception as e:
                    print("Error in docID-" + str_doc_id + "!!!")
                    print(e)
            else:
                if str_doc_id in finish_list:
                    print(1)
                    # print("finish: doc id-" + str_doc_id)

    @staticmethod
    def merge(doc_count):

        with open("../output/embedding/formula after delete/merge.json", "r", encoding="utf8") as f:
            merge_dic = json.load(f)
        with open("../output/embedding/formula after delete/error_response.json", 'r', encoding='utf8') as f:
            error_response = json.load(f)
        error_list = []

        # 合并
        for i in range(doc_count):
            if os.path.exists("../output/embedding/formula after delete/" + str(i) + ".json"):
                with open("../output/embedding/formula after delete/" + str(i) + ".json", 'r', encoding='utf8') as f:
                    sub_dic = json.load(f)
                for doc_id in sub_dic:
                    merge_dic[doc_id] = sub_dic[doc_id]

        # 添加未测试的
        for i in range(679):
            if str(i) not in merge_dic and str(i) not in error_response:
                error_list.append(str(i))

        # 写入
        with open("../output/embedding/formula after delete/merge.json", "w", encoding="utf8") as f:
            temp = json.dumps(merge_dic)
            f.write(temp)
        with open("../output/embedding/formula after delete/decoder_error_id.json", 'w', encoding='utf8') as f:
            temp = json.dumps(error_list)
            f.write(temp)

        # 检查用到了多少不同的formula
        formula_list = []
        for doc_id in merge_dic:
            for item in merge_dic[doc_id]:
                formula = item['formula']
                if formula not in formula_list:
                    formula_list.append(formula)
        print(1)


class DeleteFormulaProcessV2(object):

    @staticmethod
    def check_formula():
        max_len = 0
        max_id = 0
        embedding_encoding = "cl100k_base"
        encoding = tiktoken.get_encoding(embedding_encoding)
        with open('../output/embedding/embedding_finQA_viewer4.1 (key word embedding).json', 'r', encoding='utf8') as f:
            report_dic = json.load(f)
        for doc_id in report_dic:
            input_dic = report_dic[doc_id]
            for x in input_dic['formula']:
                x.pop('before')
                x.pop('after')
                x.pop('url')
            input_dic['formula_list'] = input_dic['formula']
            input_dic.pop('formula')
            json_input_dic_str = json.dumps(input_dic, indent=4, ensure_ascii=False)
            l2 = len(encoding.encode(str(json_input_dic_str)))
            if l2 > max_len:
                max_len = l2
                max_id = doc_id
        print(max_len)
        print(max_id)
        print(json.dumps(report_dic[max_id], indent=4, ensure_ascii=False))

    @staticmethod
    def delete_formula(text):
        system = "There is a Python dictionary structured as follows:{\"pre_text\":[sentence1,sentence2...],\"pro_text\":[sentence1,sentence2...],\"table\":[[word1,word2...],[word1,word2...]...],\"formula_list\":[{\"formula\":formula,\"explanation\":explanation},{\"formula\":formula,\"explanation\":explanation}]}. Where pre_text, pro_text, and table store some financial data, and formula_list stores financial formulas related to pre_text, pro_text, and table, as well as text explaining the formulas. I want to find five formulas from this dictionary. These five formulas can be used to answer financial questions that require data from pre_text, pro_text, and table.The output should be a JSON list only, without any additional text. The output JSON list should be in the following format：[{\"formula\":formula1},{\"formula\":formula2},{\"formula\":formula3},{\"formula\":formula4},{\"formula\":formula5}]\nNote: formula1 to formula5 are directly obtained from the \"formula\" key's value in the \"formula_list\" item. Do not change the original values."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            temperature=0,
        )
        # response_text = response['choices'][0]['text']
        response_text = response['choices'][0]['message']['content']
        return response_text

    @staticmethod
    def run(t_count):
        finish_list = []
        with open('../output/embedding/embedding_finQA_viewer4.1 (key word embedding).json', 'r', encoding='utf8') as f:
            report_dic = json.load(f)

        for docID in report_dic:
            if os.path.exists('../output/embedding/select 5 formula(gpt4)/' + docID + '.json'):
                finish_list.append(docID)
        t_list = []
        for i in range(t_count):
            t = threading.Thread(target=DeleteFormulaProcessV2.process,
                                 args=(i, t_count, report_dic, finish_list))
            t_list.append(t)
            t.start()

        for t in t_list:
            t.join()

    @staticmethod
    def process(thread_id, thread_count, report_dic, finish_list):

        # 每个线程执行的doc_id分配
        total = len(report_dic)
        step = total / thread_count
        start = int(thread_id * step)
        end = int(thread_id * step + step)

        for doc_id in report_dic:
            int_doc_id = int(doc_id)

            # 如果doc_id在线程范围内且没有运行过
            if start <= int_doc_id < end and doc_id not in finish_list:
                # 获取API input
                input_dic = report_dic[doc_id]
                for x in input_dic['formula']:
                    x.pop('before')
                    x.pop('after')
                    x.pop('url')
                input_dic['formula_list'] = input_dic['formula']
                input_dic.pop('formula')
                input_dic_str = json.dumps(input_dic, indent=4, ensure_ascii=False)

                # 调用API
                try:
                    print("Thread-" + str(thread_id) + ":Start Process docID-" + doc_id)
                    response = DeleteFormulaProcessV2.delete_formula(input_dic_str)
                    output_list = json.loads(response)
                    with open("../output/embedding/select 5 formula(gpt4)/" + doc_id + ".json", "w",
                              encoding='utf8') as f:
                        t = json.dumps(output_list, ensure_ascii=False)
                        f.write(t)
                    print("Thread-" + str(thread_id) + ":Finish Process docID-" + doc_id)
                except Exception as e:
                    print(e)
                    print("Error in docID-" + doc_id + "!!!\n\n\n")


def merge():
    count = 0
    error_list = []
    with open('../output/embedding/formula after delete/merge.json', 'r', encoding='utf8') as f:
        choose_formula = json.load(f)
    with open("../output/embedding/formula and explanation.json", "r", encoding="utf8") as f:
        formula_dic = json.load(f)
    with open('../output/embedding/merge_embedding_finQA_viewer.json', 'r', encoding='utf8') as f:
        output_dic = json.load(f)
    for doc_id in choose_formula:
        output_dic[doc_id].pop('filename')
        output_dic[doc_id].pop('question')
        output_dic[doc_id].pop('answer')
        for index in range(len(choose_formula[doc_id])):

            # 提取出formula
            # 给formula添加explanation
            formula = choose_formula[doc_id][index]['formula']
            choose_formula[doc_id][index]['before'] = ""
            choose_formula[doc_id][index]['after'] = ""
            choose_formula[doc_id][index]['url'] = ""
            try:
                choose_formula[doc_id][index]['explanation'] = formula_dic[formula]
                ori_formula_list = output_dic[doc_id]['formula']
                ori_formula = {}
                for item in ori_formula_list:
                    if item['formula'] == formula:
                        ori_formula = item
                        break
                choose_formula[doc_id][index]['before'] = ori_formula['before']
                choose_formula[doc_id][index]['after'] = ori_formula['after']
                choose_formula[doc_id][index]['url'] = ori_formula['url']

                # 计算有多少不同且存在的formula被用过
                # if formula not in used_formula:
                #     used_formula[formula] = 1
                # else:
                #     used_formula[formula] += 1

            # 如果出现错误，说明formula不存在
            except Exception as e:
                choose_formula[doc_id][index]['before'] = ""
                choose_formula[doc_id][index]['after'] = ""
                choose_formula[doc_id][index]['url'] = ""
                choose_formula[doc_id][index]['explanation'] = ""

                # 打印出不存在的formula
                # 计算有多少个不同的不存在的formula
                if formula not in error_list:
                    error_list.append(formula)
                    print(doc_id)
                    print(formula)
                    print(str(e).replace("'", "\""))
                    count = count + 1
        output_dic[doc_id]['formula'] = choose_formula[doc_id]

    # 测试每个formula被用了几次
    # li = {}
    # for i in used_formula:
    #     if str(used_formula[i]) not in li:
    #         li[str(used_formula[i])] = 1
    #     else:
    #         li[str(used_formula[i])] += 1

    # 测试doc有没有5个formula
    # for doc_id in choose_formula:
    #     if len(choose_formula[doc_id]) != 5:
    #         print("docID" + doc_id + "-" + str(len(choose_formula[doc_id])))

    # 测试用了多少不同的formula
    # formula_list = []
    # for doc_id in choose_formula:
    #     for item in choose_formula[doc_id]:
    #         formula = item['formula']
    #         if formula not in formula_list:
    #             formula_list.append(formula)
    # print(len(formula_list))
    with open("../output/embedding/selected_embedding_finQA_viewer.json", 'w', encoding='utf8') as f:
        temp = json.dumps(output_dic, ensure_ascii=False)
        f.write(temp)
    print(count)
    # 写进“selected_embedding_finQA_viewer”


