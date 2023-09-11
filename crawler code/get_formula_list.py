import json
import re
import threading
import requests
from fake_useragent import UserAgent
from selectolax.parser import HTMLParser
import time


# 定义一个爬虫类
class FormulaSpider(object):
    # 初始化
    # 定义初始页面url
    def __init__(self):
        self.url_list = []
        self.url_dic = {}
        self.url_prefix = "https://en.wikipedia.org/wiki/"
        self.formula_dic = {}
        self.vale_lock = threading.Lock()
        self.retry_count = 0
        self.RETRY_count = 0

    # 请求函数
    def get_html(self, url):
        if url == "https://en.wikipedia.org/wiki/CASA ratio":
            print("1")
        # 获取html
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        try:
            res = requests.get(url, headers)
            res.encoding = "utf-8"
            html = res.text
            self.parse_formula(html, url)
        except Exception as e:
            print(e)
            time.sleep(5)
            print("RETRY-" + str(self.RETRY_count) + "-" + url)
            self.RETRY_count += 1
            self.get_html(url)

    # 爬取公式
    def parse_formula(self, html, url):

        latex_list = self.get_latex_formula(html, url)
        temp_dict = self.get_text_formula(html)
        text_list = temp_dict['text_list']
        add_list = temp_dict['add_list']
        # abt_dic存储text_formula的前后内容
        abt_dic = temp_dict['abt_dic']
        if add_list:
            # add_list去重
            for j in latex_list:
                add_list = [x for x in add_list if
                            x.replace(" ", "").replace("\n", "") not in j.replace(" ", "").replace("\n", "")]
            for x in add_list:
                latex_list.append(x)
        # 如果list不为空，将公式列表加入节点中
        sub_dic = {}

        # text_list若存在于latex_list，去重
        for j in latex_list:
            text_list = [x for x in text_list if
                         x.replace(" ", "").replace("\n", "") not in j.replace(" ", "").replace("\n", "")]

        # 将text_list以及前后内容加入
        if text_list:
            final_text_list = []
            for i in text_list:
                final_text_list.append(abt_dic[i]['before'])
                final_text_list.append(i)
                final_text_list.append(abt_dic[i]['after'])

            # 去重
            i = len(final_text_list) - 1
            while i >= 0:
                j = i - 1
                while j >= 0:
                    if final_text_list[i] in final_text_list[j]:
                        final_text_list.pop(i)
                        break
                    j = j - 1
                i = i - 1
            sub_dic["text_formula"] = final_text_list
        if latex_list:
            sub_dic["latex_formula"] = latex_list
        if sub_dic:
            with self.vale_lock:
                self.formula_dic[url] = sub_dic

    def get_latex_formula(self, html, url):
        # wiki在防止频繁访问时会出现error page
        # 此时没有main_html
        # 等待一段时间后重新访问
        latex_list = []
        main_html = re.findall(r'<main id="content" class="mw-body" role="main">(.*?)</main>', html, re.S)
        if main_html:
            latex_list = FormulaSpider.get_latex_selectolax(html)
            # latex_list = re.findall(r'<span class="mwe-math-element">.*?alttext="(.*?)">', main_html[0],
            # re.S) 1.latex 公式不含等号，删除 2.替换 html 中的 &amp; 3.删除“=}” latex_list = [x.replace('&amp;', '&') for x in
            # latex_list if ('=' in x)] latex_list = [x for x in latex_list if not x[x.index("="):] == "=}"]
            # latex_list = [x.replace('&amp;', '&') for x in latex_list] latex_list = [x for x in latex_list if (
            # x.__contains__("=") and not x[x.index("="):] == "=}") or not x.__contains__("=")]
        else:
            time.sleep(5)
            print("retry-" + str(self.retry_count) + "-" + url)
            self.retry_count += 1
            self.get_html(url)
        return latex_list

    @staticmethod
    def get_latex_selectolax(html):
        l_list = []
        tree = HTMLParser(html)
        if tree.body is None:
            return None

        for tag in tree.css('script'):
            tag.decompose()
        for tag in tree.css('style'):
            tag.decompose()
        for tag in tree.css('mrow'):
            tag.decompose()

        # dl本身+前后
        dl_list = FormulaSpider.get_dl(tree)
        for i in dl_list:
            if i != '':
                l_list.append(i)

        # annotation本身+前后
        # annotation_dic = FormulaSpider.get_annotation(tree)

        # 去重并加入
        '''for i in annotation_dic:
            flag = False
            for j in dl_list:
                if i.replace(" ", "").replace("\n", "") in j.replace(" ", "").replace("\n", ""):
                    flag = True
                    break
            if i != '' and not flag:
                l_list.append(annotation_dic[i][0])
                l_list.append(i)
                l_list.append(annotation_dic[i][1])'''

        # 获取where前后
        where_list = FormulaSpider.get_where(tree)
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
                else:
                    dic[index].append('')

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
                else:
                    dic[index].append('')

        return dic

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
                    while next_node is not None and next_node.text(strip=True) == "":
                        next_node = next_node.next
                    if next_node is not None:
                        i = next_node.text(strip=True, separator=' ')
                        l_list.append(i)
                # 子一个
                else:
                    i = tag.text(strip=True, separator=' ')
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
    def get_dl(tree):
        l_list = []
        # dl本身+前后覆盖1个
        for tag in tree.css("dl"):
            if "=" not in tag.text(strip=True):
                continue
            # 获取前一个
            prev_node = tag.prev
            while prev_node is not None and prev_node.text(strip=True) == "":
                prev_node = prev_node.prev
            if prev_node is not None:
                i = prev_node.text(strip=True, separator=' ')
                if len(i) < 50:
                    prev_node = prev_node.prev
                    while prev_node is not None and prev_node.text(strip=True) == "":
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
            while next_node is not None and next_node.text(strip=True) == "":
                next_node = next_node.next
            if next_node is not None:
                i = next_node.text(strip=True, separator=' ')
                l_list.append(i)
                if len(i) < 15:
                    next_node = next_node.next
                    while next_node is not None and next_node.text(strip=True) == "":
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

    def get_text_formula(self, html):
        # 提取文本
        text = self.get_text_selectolax(html)
        # 0.去除制表符并且按换行分组
        # 1.去除空白
        # 2.去除空
        # 3.去除纯等号
        # 4.去除[number]格式的子字符串（参考链接）
        text_list = [x.replace("\t", "") for x in str.splitlines(text)]
        text_list = [re.sub(r'\[\d+]', '', x) for x in text_list]
        text_list = [x for x in text_list if x != '' and not x.isspace() and x.replace(" ", "") != "="]
        text_list = [' '.join(x.split()) for x in text_list]
        # 1.提取跨latex和text的公式，并且得到含等号且左右不为空的text
        temp_dic = self.across_formula(text_list)
        text_list = temp_dic["text"]
        add_list = temp_dic["add"]
        abt_dic = temp_dic["abt_dic"]
        # 2.提取公式
        text_list = [x for x in text_list if self.if_text_formula(x)]
        return {'text_list': text_list, 'add_list': add_list, "abt_dic": abt_dic}

    @staticmethod
    def get_text_selectolax(html):
        tree = HTMLParser(html)

        if tree.body is None:
            return None

        for tag in tree.css('script'):
            tag.decompose()
        for tag in tree.css('style'):
            tag.decompose()
        for tag in tree.css('mrow'):
            tag.decompose()

        text = tree.body.text(separator='')
        return text

    @staticmethod
    def across_formula(t_list):
        add_latex_list = []
        return_list = []
        abt_dic = {}
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
                        abt_dic[x] = {"before": t_list[i - before], "after": t_list[i + 1]}
                    else:
                        add_latex_list.append(x)
                else:
                    # text右边为空格
                    if x[x.index("=") + 1:].isspace() or x[x.index("=") + 1:] == '':
                        x = x + t_list[i + 1]
                        if "\\displaystyle" not in x:
                            return_list.append(x)
                            abt_dic[x] = {"before": t_list[i - 1], "after": t_list[i + 2]}
                        else:
                            add_latex_list.append(x)
                    # 左右不为空,且含等号
                    else:
                        return_list.append(x)
                        abt_dic[x] = {"before": t_list[i - 1], "after": t_list[i + 1]}
        return {"add": add_latex_list, "text": return_list, "abt_dic": abt_dic}

    # text公式判断
    @staticmethod
    def if_text_formula(x):
        # 1.保留小于120个字符以及等号左边小于50个字符的
        bool1 = x.index("=") < 40 or len(x) < 100
        # 2.并去除latex公式
        bool2 = "\\displaystyle" not in x
        # 3.去除url
        bool3 = "http" not in x
        # 4.去除^开头的
        if x.__contains__("^"):
            bool4 = x.index("^") != 0
        else:
            bool4 = True
        # 5.公式，则左右必定都包含字母
        left = False
        right = False
        for char in x[:x.index("=")]:
            # Check if the character is an alphabetic character
            if char.isalpha():
                left = True
                break
        for char in x[x.index("="):]:
            # Check if the character is an alphabetic character
            if char.isalpha():
                right = True
                break
        bool5 = left and right
        # 6.去除左边为纯数字+空格的
        bool6 = not (x[:x.index("=")].replace(" ", "").isdecimal())
        return bool1 and bool2 and bool3 and bool4 and bool5 and bool6

    # 跨行公式

    # 以脚本方式启动
    # 捕捉异常错误
    def run(self, index, start, end):
        count = index + start
        while start <= count < end:
            print(end - count)
            url = self.url_prefix + self.url_list[count]
            # print(url)
            self.get_html(url)
            count = count + 100

    def process(self):
        # 读取url_list
        f = open('economics_url_list.json', 'r', encoding='utf-8')
        content = f.read()
        self.url_dic = json.loads(content)
        f.close()

        # 把URL存到self.url_list中
        for i in self.url_dic:
            # j为page_list里的元素
            for j in self.url_dic[i]:
                if not self.url_list.__contains__(j):
                    self.url_list.append(j)

        j = 7
        total = len(self.url_list)
        step = total / 10
        base_sleep_time = 60
        while j < 10:
            # 线程遍历
            t_list = []
            for i in range(100):
                t = threading.Thread(target=FormulaSpider.run, args=(self, i, int(j * step), int((j + 1) * step)))
                t_list.append(t)
                t.start()

            for t in t_list:
                t.join()

            print("第" + str(j) + "次结束")
            j += 1
            self.retry_count = 0
            # 存到json
            temp = json.dumps(self.formula_dic, ensure_ascii=False)
            f2 = open('economics_formula_list_' + str(j) + '.json', 'w', encoding='utf-8')
            f2.write(temp)
            f2.close()
            time.sleep(base_sleep_time * int(self.retry_count / 80 + 1))


spider = FormulaSpider()
spider.process()
