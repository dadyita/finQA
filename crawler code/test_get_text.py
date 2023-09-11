from selectolax.parser import HTMLParser
from fake_useragent import UserAgent
import requests
import re


class Test:
    @staticmethod
    def get_text_selectolax(url):
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        res = requests.get(url, headers)
        res.encoding = "utf-8"
        html = res.text
        tree = HTMLParser(html)

        if tree.body is None:
            return None

        for tag in tree.css('script'):
            tag.decompose()
        for tag in tree.css('style'):
            tag.decompose()
        for tag in tree.css('mrow'):
            tag.decompose()

        t = tree.body.text(separator='')
        return t

    @staticmethod
    def get_leatex_selectolax(url):
        l_list = []
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        res = requests.get(url, headers)
        res.encoding = "utf-8"
        html = res.text
        tree = HTMLParser(html)
        if tree.body is None:
            return None

        for tag in tree.css('script'):
            tag.decompose()
        for tag in tree.css('style'):
            tag.decompose()
        for tag in tree.css('mrow'):
            tag.decompose()

        # dl本身+前后覆盖1个
        dl_list = Test.get_dl(tree)
        for i in dl_list:
            if i != '':
                l_list.append(i)

        annotation_dic = Test.get_annotation(tree)
        for i in annotation_dic:
            flag = False
            for j in dl_list:
                if i.replace(" ", "").replace("\n", "") in j.replace(" ", "").replace("\n", ""):
                    flag = True
                    break
            if i != '' and not flag:
                l_list.append(annotation_dic[i][0])
                l_list.append(i)
                l_list.append(annotation_dic[i][1])

        # 获取where前后
        where_list = Test.get_where(tree)
        for i in where_list:
            flag = False
            for j in dl_list:
                if i.replace(" ", "").replace("\n", "") in j.replace(" ", "").replace("\n", ""):
                    flag = True
                    break
            if i != '' and not flag:
                l_list.append(i)

        # 去重
        i = len(l_list) - 1
        while i >= 0:
            j = i - 1
            while j >= 0:
                if l_list[i].replace(" ", "").replace("\n", "") in l_list[j].replace(" ", "").replace("\n", ""):
                    l_list.pop(i)
                    break
                j = j - 1
            i = i - 1

        l_list = [' '.join(x.split()) for x in l_list]
        l_list = [re.sub(r'\[\d+]', '', x) for x in l_list]

        return l_list

    @staticmethod
    def get_where(tree):
        l_list = []
        # 获取 where 前后内容
        for tag in tree.root.traverse():
            text_tag = tag.text(deep=False).replace("\n", "").replace("\t", "").replace(" ", "")
            if "where" == text_tag.lower() or "where:" == text_tag.lower():
                # 前一个
                prev_node = tag.prev
                if prev_node is not None:
                    while prev_node is not None and prev_node.text(strip=True) == "":
                        prev_node = prev_node.prev
                    if prev_node is not None:
                        i = prev_node.text(strip=True, separator=' ')
                        l_list.append(i)
                # 父辈的前一个邻居
                else:
                    parent_node = tag.parent
                    while parent_node.prev is None and parent_node is not None:
                        parent_node = parent_node.parent

                    prev_node = parent_node.prev
                    while prev_node is not None and prev_node.text(strip=True) == "":
                        prev_node = prev_node.prev
                    if prev_node is not None:
                        i = prev_node.text(strip=True, separator=' ')
                        l_list.append(i)

                # 后一个
                next_node = tag.next
                if next_node is not None:
                    while next_node is not None and next_node.text() == "\n":
                        next_node = next_node.next
                    if next_node is not None:
                        i = next_node.text(strip=True, separator=' ')
                        l_list.append(i)
                # 子一个
                else:
                    i = tag.text(strip=True, separator=' ')
                    l_list.append(i)

        i = len(l_list) - 1
        while i >= 0:
            j = i - 1
            while j >= 0:
                if l_list[i] in l_list[j]:
                    l_list.pop(i)
                    break
                j = j - 1
            i = i - 1
        return l_list

    @staticmethod
    def get_dl(tree):
        l_list = []
        # dl本身+前后覆盖1个
        for tag in tree.css("dl"):
            if "=" not in tag.text(strip=True):
                continue
            # 获取前一个
            prev_node = tag.prev
            while prev_node is not None and prev_node.text() == "\n":
                prev_node = prev_node.prev
            if prev_node is not None:
                i = prev_node.text(strip=True, separator=' ')
                if len(i) < 50:
                    prev_node = prev_node.prev
                    while prev_node is not None and prev_node.text() == "\n":
                        prev_node = prev_node.prev
                    if prev_node is not None:
                        j = prev_node.text(strip=True, separator=' ')
                        l_list.append(j)
                    l_list.append(i)
                else:
                    l_list.append(i)

            # 获取本身
            'strip=True可能存在问题'
            l_list.append(tag.text(strip=True, separator=' '))

            # 获取后一个
            next_node = tag.next
            while next_node is not None and next_node.text() == "\n":
                next_node = next_node.next
            if next_node is not None:
                i = next_node.text(strip=True, separator=' ')
                l_list.append(i)
                if len(i) < 50:
                    next_node = next_node.next
                    while next_node is not None and next_node.text() == "\n":
                        next_node = next_node.next
                    if next_node is not None:
                        i = next_node.text(strip=True, separator=' ')
                        l_list.append(i)

        # 去重
        i = len(l_list) - 1
        while i >= 0:
            j = i - 1
            while j >= 0:
                if l_list[i] in l_list[j]:
                    l_list.pop(i)
                    break
                j = j - 1
            i = i - 1
        return l_list

    @staticmethod
    def get_annotation(tree):
        dic = {}
        # 获取 where 前后内容
        for tag in tree.css("annotation"):
            if "=" in tag.text(strip=True) and "\\displaystyle" in tag.text(strip=True):
                index = tag.text(strip=True, separator=" ")
                dic[index] = []
                # 父辈的前一个邻居
                prev_node = tag.parent
                while prev_node is not None:
                    while prev_node.text(deep=False, strip=True) == "" and prev_node.prev is not None:
                        prev_node = prev_node.prev
                    if prev_node.prev is None:
                        prev_node = prev_node.parent
                    else:
                        break

                if prev_node is not None:
                    i = prev_node.text(strip=True, separator=' ')
                    dic[index].append(i)

                # 父辈的后一个邻居
                next_node = tag.parent
                while next_node is not None:
                    while next_node.text(deep=False, strip=True) == "" and next_node.next is not None:
                        next_node = next_node.next
                    if next_node.next is None:
                        next_node = next_node.parent
                    else:
                        break
                if next_node is not None:
                    i = next_node.text(strip=True, separator=' ')
                    if len(i) < 15:
                        next_node = next_node.next
                        while next_node is not None and next_node.text(strip=True) == "":
                            next_node = next_node.next
                        if next_node is not None:
                            i = i + " " + next_node.text(strip=True, separator=' ')
                    dic[index].append(i)

        return dic

    @staticmethod
    def across_formula(t_list):
        add_latex_list = []
        return_list = []
        # 1.去除空白
        # 2.去除空
        # 3.去除纯等号
        t_list = [x for x in t_list if x != '' and not x.isspace() and x.replace(" ", "") != "="]
        for i in range(len(t_list)):
            x = t_list[i]
            if "=" in t_list[i]:
                # text左边为空/空格
                if x[:x.index("=")].isspace() or x[:x.index("=")] == '':
                    before = 1
                    while x[:x.index("=")].isspace() or x[:x.index("=")] == '':
                        x = t_list[i - before] + x
                        before += 1
                    if "\\displaystyle" not in x:
                        return_list.append(x)
                    else:
                        add_latex_list.append(x)
                else:
                    # latex右边为空
                    if x[x.index("="):] == '=}':
                        x = x + t_list[i + 1]
                        add_latex_list.append(x)
                    else:
                        # text右边为空
                        if x[x.index("=") + 1:].isspace() or x[x.index("=") + 1:] == '':
                            x = x + t_list[i + 1]
                            if "\\displaystyle" not in x:
                                return_list.append(x)
                            else:
                                add_latex_list.append(x)
                        # 左右不为空,且含等号
                        else:
                            return_list.append(x)
        return {"add": add_latex_list, "text": return_list}

        # 0.去除制表符并且按换行分组
        # 1.找到一行中含等号的文本，判断此为公式
        # 2.并去除latex公式
        # 3.去除url
        # 4.去除纯等号


a="https://en.wikipedia.org/wiki/CASA_ratio"
# latex_list = Test.get_leatex_selectolax(a)
text = Test.get_text_selectolax(a)
equal_list = [re.sub(r'\[\d+]', '', x) for x in str.splitlines(text)]
equal_list = [x for x in equal_list if not x.isspace() and x != '']
temp = Test.across_formula(equal_list)
f2 = open('test.txt', 'w', encoding='utf8')
f2.write(text)
f2.close()

# # 3.去除[number]格式的子字符串
string = "The quick brown [1] fox jumps over the lazy [2] dog."

# Use a regular expression to replace all substrings in the format of '[number]' with an empty string
new_string = re.sub(r'\[\d+]', '', string)

print(new_string)
