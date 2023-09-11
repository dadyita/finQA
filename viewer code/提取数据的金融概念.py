import os
import json
import time
import openai
import threading

# yilun's key: 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
# my key: sk-jOM3RhzjthMGY7tSLteST3BlbkFJXHnGjZ1fKA2uVRQ2yP0w
# new'key: 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
openai.api_key = "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"

finish_list = []


class GetKeyWord(object):
    @staticmethod
    def get_word(text, index):
        system = ["""A financial report represented by a python dictionary, and the structure of the dictctionary is as follows.
{
"pre_text":[sentece1,sentence2...],
"post_text":[[sentece1,sentence2...],
"table":[[word1,word2...],[word1,word2...]...]
}
Where 
- "pre_text" is a list representing the text before table  in the financial report and each item is a sentence.
- "table" is a nested list representing a table in the financial report, each item of the outer list is an inner list representing a row of the table and the first inner list represents the first row, the second inner list represents the second row, and so on. Each item of inner list is the value of a cell of the table.
- "post_text" is a list representing the text after table  in the financial report and each item is a sentence.

There are Numerical value in the financial report, help me find out what financial concepts these value correspond to. And list those financial concepts (do not need explanation)""",
                  "The following is a financial report consist of table(Markdown format) and text. There are Numerical value in the financial report, help me find out what financial concepts these value correspond to. And list those financial concepts and their corresponding values(do not need explanation)"]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system[index]},
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
            if os.path.exists("../output/embedding/key_word/" + str_doc_id + ".json"):
                finish_list.append(i)
        with open("../output/embedding/embedding_finQA_viewer3.0 (select 5 formula and add explanation).json", 'r',
                  encoding='utf8') as f:
            text_dic = json.load(f)
        for docID in text_dic:
            text_dic[docID].pop("formula")
        t_list = []
        for i in range(t_count):
            t = threading.Thread(target=GetKeyWord.process,
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

        for str_doc_id in text_dic:
            doc_id = int(str_doc_id)
            # 如果是自己线程执行的id 并且不在finish_list，error_list里面
            if start <= doc_id < end and doc_id not in finish_list:
                # 获取给api的输入
                input_dic = text_dic[str_doc_id]
                input_dic_str = json.dumps(input_dic, indent=4, ensure_ascii=False)
                try:
                    print("Thread-" + str(thread_id) + ":Start Process docID-" + str_doc_id)
                    # 调用API
                    response = GetKeyWord.get_word(input_dic_str, 0)
                    with open("../output/embedding/key_word/" + str_doc_id + ".json", "w",
                              encoding='utf8') as f:
                        f.write(response)
                    print("Thread-" + str(thread_id) + ":Finish Process docID-" + str_doc_id)
                except Exception as e:
                    print("Error in docID-" + str_doc_id + "!!!")
                    print(e)
                    time.sleep(60)
