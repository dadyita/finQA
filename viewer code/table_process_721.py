# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities to visualize a ToTTo example."""
import json
import os
import random
import 提取数据的金融概念
import embedding_v2
from openai.embeddings_utils import cosine_similarity

# compare cosine similarity of embedding array of formula and data
# and search the most similar_count relevant formula
similar_count = 20


class AbstractKeyWord:
    @staticmethod
    def run():
        result = []
        with open('../dataset/source/select.json', 'r', encoding='utf8') as f:
            select = json.load(f)
        for doc in select:
            sub_list = []
            for item in doc:
                response = 提取数据的金融概念.GetKeyWord.get_word(item, 1)
                print(response)
                sub_list.append(response)
            result.append(sub_list)
        with open('../dataset/source/report key word.json', 'w', encoding='utf8') as f:
            temp = json.dumps(result, ensure_ascii=False)
            f.write(temp)


class GetSimilarity:
    @staticmethod
    def embedding_report():
        with open('../dataset/source/report key word.json', 'r', encoding='utf8') as f:
            key_word = json.load(f)
        result = []
        count = 0
        for doc in key_word:
            sub_list = []
            for item in doc:
                similarity = embedding_v2.get_embedding(item)
                sub_list.append(similarity)
                count += 1
                print(count)
            result.append(sub_list)
        with open('../dataset/source/Similarity/report_simi.json', 'w', encoding='utf8') as f:
            temp = json.dumps(result, ensure_ascii=False)
            f.write(temp)

    @staticmethod
    def similar():
        formula_embedding_list = []
        with open('../dataset/source/Similarity/report_simi.json', 'r', encoding='utf8') as f:
            report_embedding_list = json.load(f)

        # 先测两个
        report_embedding_list = report_embedding_list[0]
        # for reportID in range(679):
        #     with open("../output/useless/embedding/similarity/report/" + str(reportID) + ".json", "r",
        #               encoding="utf8") as f:
        #         temp = json.load(f)
        #         report_embedding_list.append(temp)
        for formulaID in range(1141):
            with open("../output/useless/embedding/similarity/formula(explanation+formula)/" + str(formulaID) + ".json",
                      "r", encoding="utf8") as f:
                temp = json.load(f)
                formula_embedding_list.append(temp)
        with open("../output/formula in list (gpt4 explanation).json", "r", encoding="utf8") as f:
            formula_list = json.load(f)

        for reportID in range(len(report_embedding_list)):
            report_embedding = report_embedding_list[reportID]
            similar_index = GetSimilarity.search_formula(formula_embedding_list, report_embedding)
            temp_list = []
            for index in similar_index:
                item = formula_list[index]
                temp_list.append(item)
            with open('../dataset/source/Similarity/' + str(reportID) + '.json', 'w', encoding='utf8') as f:
                temp = json.dumps(temp_list, ensure_ascii=False)
                f.write(temp)

    @staticmethod
    def search_formula(formula_embedding, text_embedding, n=similar_count):
        similarity = [cosine_similarity(x, text_embedding) for x in formula_embedding]
        # 对列表进行排序并获取前 similar_count 个元素的索引
        top_indices = sorted(range(len(similarity)), key=lambda i: similarity[i], reverse=True)[:n]
        return top_indices


class GetHtmlString:
    @staticmethod
    def get_table_style():
        return """<style>
                 table { border-collapse: collapse; }
                 th, td {
                   word-wrap: break-word;
                   max-width: 100%;
                   font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
                   border-bottom: 1px solid #ddd;
                   padding: 5px;
                   text-align: left;
                 }
                tr:hover {background: #f4f4f4;}
                tr:hover .highlighted {background: repeating-linear-gradient(
                        45deg,
                        #ffff99,
                        #ffff99 10px,
                        #f4f4f4 10px,
                        #f4f4f4 20px
                      );}
               .highlighted { background-color: #ffff99; }
              </style>"""

    @staticmethod
    def get_cell_html(cell, highlight):
        """Get html string for a table cell."""
        if highlight:
            color_str = """ class="highlighted" """
        else:
            color_str = ""

        is_header = cell["header"]
        cell_symbol = "td"

        if is_header:
            cell_symbol = "th"

        start_marker = "<%s%s>" % (cell_symbol, color_str)
        end_marker = "</%s>" % cell_symbol

        col_span = cell["colspan"]
        row_span = cell["rowspan"]
        start_marker = "<%s%s colspan=%d rowspan=%d >" % (cell_symbol, color_str,
                                                          col_span, row_span)

        val = cell["value"]
        cell_html = start_marker + " " + val + " " + end_marker
        return cell_html

    @staticmethod
    def get_table_html(table, highlighted_cells):
        """Get html for a table and a subset of highlighted cells."""
        table_str = "<table>\n"
        for r_index, row in enumerate(table):
            row_str = "<tr> "
            for c_index, cell in enumerate(row):
                if [r_index, c_index] in highlighted_cells:
                    cell_html = GetHtmlString.get_cell_html(cell, True)
                else:
                    cell_html = GetHtmlString.get_cell_html(cell, False)
                row_str += cell_html

            row_str += "</tr>\n"
            table_str += row_str

        table_str += "</table>"
        return table_str

    @staticmethod
    def get_html_header(title):
        style_str = GetHtmlString.get_table_style()
        header = "<!doctype html> <html> <head>%s</head><body><h2>%s</h2><br>" % (
            style_str, title)
        return header


class PreProcess:
    @staticmethod
    def get_source_data(folder_path):
        # 用于存储所有source.json的内容
        source_data = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file == 'source.json':
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf8') as f:
                        data = json.load(f)
                        source_data.append(data)
        return source_data

    @staticmethod
    def get_table_gpt(table):
        # 传入table
        table_str = ''
        # 处理一个table to str
        for row in table:
            for cell in row:
                colspan = cell['colspan']
                value = cell['value']
                if value == '':
                    value = '—'
                table_str += (value + ' | ') * colspan
            table_str = table_str[0:len(table_str) - 3] + '\n'

        # 转成table string
        return table_str

    @staticmethod
    def add_gpt_html():
        # 获取数据源，放入一个list
        # 结构如下
        # [
        #   {report1},
        #   {report2},
        #   ...
        # ]
        source_data_list = PreProcess.get_source_data('../dataset/examples/')

        # 获取gpt，html格式的table
        all_gpt_table_list = []
        all_html_table_list = []

        # 遍历source_data_list的每个report
        # 即report_dic
        for report_dic in source_data_list:

            # 获取每个report的table list
            report_table_list = report_dic["tables"]
            report_gpt_table = []
            report_html_table = []
            for index, table in enumerate(report_table_list):
                # 获取html table
                report_html_table.append(GetHtmlString.get_table_html(table, []))
                # 获取gpt table
                report_gpt_table.append(PreProcess.get_table_gpt(table))

            report_dic["gpt_tables"] = report_gpt_table
            report_dic['html_tables'] = report_html_table

        # 把加入gpt,html table之后的表source data重写
        with open('../dataset/source/source.json', 'w', encoding='utf8') as f:
            temp = json.dumps(source_data_list, ensure_ascii=False)
            f.write(temp)

    @staticmethod
    def select(report, gpt_table, html_table, report_index):
        # 获取每个doc的table count
        table_count = len(report['tables'])
        # 获取report的text
        text = report['text']
        # 已经遍历过得table ID
        used_table_id = []
        select_para = []

        # 选择 min(2, table_count) 个table片段
        for _ in range(min(2, table_count)):
            # 无限循环，随机选择一个table+前5段+后5段
            # 直到选出片段内≤2个table
            while True:
                # 随机获取没遍历过的table序号
                while True:
                    rand_num = random.randint(0, table_count - 1)
                    if rand_num not in used_table_id:
                        table_index = rand_num
                        break
                used_table_id.append(table_index)

                # 获取table在text中的index
                # 因为table_text_index从1开始，table_index从0开始
                # 所以要table_index + 1
                table_text_index = text.index("##table" + str(table_index + 1) + "##")

                # 选出table+前5段+后5段
                ori_string_list = text[table_text_index - 5:table_text_index + 6]

                # 判断有几个table
                count = 0
                for sentence in ori_string_list:
                    if sentence.startswith("##table"):
                        count += 1

                # 如果小于两个table，则把gpt，html加入，生成select片段
                if count <= 2:
                    # 获取选择片段的相关信息并加入
                    item_select = {}
                    gpt_string = ""
                    select_table_index = []
                    html_table
                    for i in range(table_text_index - 5, table_text_index + 6):
                        # 获取每句话
                        item = text[i]
                        # 数字或字母结尾，则加上句号
                        if item[-1].isalnum():
                            item += '.'
                        if item.startswith('##table'):
                            # 获取str_table_index(table_index+1)
                            # table表示为'##table'+digit+'##'格式
                            # digit = re.search(r'(?<=##table)\d+(?=##)', item)
                            str_table_index = item[7:len(item) - 2]
                            table_index = int(str_table_index) - 1

                            # 把table_index加入used_table_id,select_table_index
                            used_table_id.append(table_index)
                            select_table_index.append(table_index)

                            # 将table转成gpt格式并加入
                            item = gpt_table[table_index]
                            item += '\n'
                            gpt_string += item
                        else:
                            item += '\n'
                            gpt_string += item

                    # 把信息加入
                    item_select['report_index'] = report_index
                    item_select['gpt_string'] = gpt_string
                    item_select['ori_string_list'] = ori_string_list
                    item_select['select_table_index'] = select_table_index
                    select_para.append(item_select)
                    break
        return select_para

    @staticmethod
    def todo():
        # 获取所有source_doc
        with open('../dataset/source/source.json', 'r', encoding='utf8') as f:
            source_data = json.load(f)

        select_paragraph = []

        # 遍历每个doc,并出片段
        for index, report in enumerate(source_data):
            temp_select = PreProcess.select(report, report['gpt_tables'], report['html_tables'], index)
            for i in temp_select:
                select_paragraph.append(i)

        with open('../dataset/source/select.json', 'w', encoding='utf8') as f:
            temp = json.dumps(select_paragraph, ensure_ascii=False)
            f.write(temp)
        print(select_paragraph)


if __name__ == "__main__":
    PreProcess.todo()
