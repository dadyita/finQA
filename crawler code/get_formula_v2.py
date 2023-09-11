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

    @staticmethod
    def check_inside(item, parent):
        check_string = ""
        for i in parent:
            check_string += i
            for j in parent[i]:
                check_string += parent[i][j]
        check_string = check_string.replace(u'\xa0', '').replace(" ", "").replace("\n", "")
        item = item.replace(u'\xa0', '').replace(" ", "").replace("\n", "")
        return item not in check_string

    # 爬取公式
    def parse_formula(self, html, url):
        latex_dic = self.get_latex_formula(html, url)
        temp_dict = self.get_text_formula(html)

        # abt_dic存储text_formula的前后内容
        abt_dic = temp_dict['abt_dic']
        text_list = temp_dict['text_list']
        add_list = temp_dict['add_list']

        # add去重
        add_list = [x for x in add_list if FormulaSpider.check_inside(x, latex_dic)]
        add_dic = {item: {"before": "", "after": ""} for item in add_list}

        # text_list去重
        text_list = [x for x in text_list if FormulaSpider.check_inside(x, latex_dic)]
        abt_dic = {key: value for key, value in abt_dic.items() if
                   key.replace(' ', '').replace("\n", "") in [i.replace(' ', '').replace("\n", "") for i in
                                                              text_list]}

        latex_dic.update(add_dic)
        latex_dic.update(abt_dic)

        if latex_dic:
            with self.vale_lock:
                self.formula_dic[url] = latex_dic

    def get_latex_formula(self, html, url):
        # wiki在防止频繁访问时会出现error page
        # 此时没有main_html
        # 等待一段时间后重新访问
        latex_dic = {}
        main_html = re.findall(r'<main id="content" class="mw-body" role="main">(.*?)</main>', html, re.S)
        if main_html:
            latex_dic = FormulaSpider.get_latex_selectolax(html)
        else:
            time.sleep(5)
            print("retry-" + str(self.retry_count) + "-" + url)
            self.retry_count += 1
            self.get_html(url)
        return latex_dic

    @staticmethod
    def get_latex_selectolax(html):

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
        dl_dic = FormulaSpider.get_dl(tree)
        # 获取where前后
        where_dic = FormulaSpider.get_where(tree)
        where_dic = {key: value for key, value in where_dic.items() if FormulaSpider.check_inside(key, dl_dic)}
        # annotation本身+前后
        annotation_dic = FormulaSpider.get_annotation(tree)
        annotation_dic = {key: value for key, value in annotation_dic.items() if
                          FormulaSpider.check_inside(key, dl_dic)}

        dl_dic.update(where_dic)
        dl_dic.update(annotation_dic)
        return dl_dic

    @staticmethod
    def get_where(tree):
        sub_dic = {}
        # 获取 where 前后内容
        for tag in tree.root.traverse():
            text_tag = tag.text(deep=False).replace("\n", "").replace("\t", "").replace(" ", "")
            if "where" == text_tag.lower() or "where:" == text_tag.lower():
                index = ""
                before = ""
                after = ""
                # 前一个
                prev_node = tag.prev
                if prev_node is not None:
                    while prev_node is not None and prev_node.text(strip=True) == "":
                        prev_node = prev_node.prev
                    if prev_node is not None:
                        i = prev_node.text(strip=True, separator=' ')
                        index = i

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
                        index = i

                # 后一个
                next_node = tag.next
                if next_node is not None:
                    while next_node is not None and next_node.text(strip=True) == "":
                        next_node = next_node.next
                    if next_node is not None:
                        i = next_node.text(strip=True, separator=' ')
                        after = i
                # 子一个
                else:
                    i = tag.text(strip=True, separator=' ')
                    after = i
                sub_dic[index] = {"before": before, "after": after}

        # 去重

        return sub_dic

    @staticmethod
    def get_dl(tree):
        sub_dic = {}
        # dl本身+前后覆盖1个
        for tag in tree.css("dl"):
            if "=" not in tag.text(strip=True):
                continue
            index = tag.text(strip=True, separator=' ')
            before = ""
            after = ""
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
                        before += j
                    before += i
                else:
                    before += i

            # 获取后一个
            next_node = tag.next
            while next_node is not None and next_node.text(strip=True) == "":
                next_node = next_node.next
            if next_node is not None:
                i = next_node.text(strip=True, separator=' ')
                after += i
                if len(i) < 15:
                    next_node = next_node.next
                    while next_node is not None and next_node.text(strip=True) == "":
                        next_node = next_node.next
                    if next_node is not None:
                        i = next_node.text(strip=True, separator=' ')
                        after += i

            sub_dic[index] = {"before": before, "after": after}

        return sub_dic

    @staticmethod
    def get_annotation(tree):
        dic = {}

        for tag in tree.css("span"):
            if tag.attributes.get('class') == 'mwe-math-element' and "=" in tag.text(
                    strip=True) and "\\displaystyle" in tag.text(strip=True):
                if tag.parent.text(strip=True) != tag.text(strip=True):
                    continue
                before = ""
                after = ""
                # 父辈的前一个邻居
                flag = True
                prev_node = tag.parent
                while prev_node is not None:
                    if prev_node.prev is not None:
                        flag = False
                        prev_node = prev_node.prev
                    else:
                        prev_node = prev_node.parent

                    # flag 说明一直向上，没有往左边，prev_node是直系
                    if flag:
                        if prev_node.text(strip=True, deep=False) != "":
                            break
                    else:
                        if prev_node.text(strip=True) != '':
                            break

                if prev_node is not None:
                    if flag:
                        i = prev_node.text(strip=True, deep=False, separator=' ')
                    else:
                        i = prev_node.text(strip=True, separator=' ')
                    before += i

                # 父辈的后一个邻居
                flag = True
                next_node = tag.parent
                while next_node is not None:
                    if next_node.next is not None:
                        flag = False
                        next_node = next_node.next
                    else:
                        next_node = next_node.parent

                    # flag 说明一直向上，没有往右边，prev_node是直系
                    if flag:
                        if next_node.text(strip=True, deep=False) != "":
                            break
                    else:
                        if next_node.text(strip=True) != '':
                            break

                if next_node is not None:
                    if flag:
                        i = next_node.text(strip=True, deep=False, separator=' ')
                    else:
                        i = next_node.text(strip=True, separator=' ')
                    if len(i) < 15:
                        next_node = next_node.next
                        while next_node is not None and next_node.text(strip=True) == "":
                            next_node = next_node.next
                        if next_node is not None:
                            i = i + " " + next_node.text(strip=True, separator=' ')
                    after += i
                dic[tag.text(strip=True, separator=" ")] = {"before": before, "after": after}
        return dic

    def get_text_formula(self, html):
        # 提取文本
        text = self.get_text_selectolax(html)
        # 0.去除制表符并且按换行分组
        # 1.去除空白
        # 2.去除空
        # 3.去除纯等号
        # 4.去除[number]格式的子字符串（参考链接）
        text_list = [x.replace("\t", "") for x in str.splitlines(text)]
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

    @staticmethod
    def tidy_load(dic, j):
        print("第" + str(j) + "次结束")

        for url in dic:
            dic[url] = {' '.join(key.split()): value for key, value in dic[url].items()}
            dic[url] = {re.sub(r'\[\d+]', '', key): value for key, value in dic[url].items()}
            for formula in dic[url]:
                for item in dic[url][formula]:
                    dic[url][formula][item] = ' '.join(dic[url][formula][item].split())
                    dic[url][formula][item] = re.sub(r'\[\d+]', '', dic[url][formula][item])

        temp = json.dumps(dic, ensure_ascii=False)
        f2 = open('new.json', 'w', encoding='utf-8')
        f2.write(temp)
        f2.close()
        return dic

    def run(self, index, start, end):
        count = index + start
        while start <= count < end:
            print(end - count)
            url = self.url_list[count]
            # print(url)
            self.get_html(url)
            count = count + 100

    def process(self):
        # 读取url_list
        f = open('output/add/add_format_formula.json', 'r', encoding='utf-8')
        content = f.read()
        self.url_dic = json.loads(content)
        f.close()

        # 把URL存到self.url_list中
        for i in self.url_dic:
            self.url_list.append(i)

        j = 0
        total = len(self.url_list)
        step = total
        base_sleep_time = 60

        # 线程遍历
        while j < 1:
            t_list = []
            for i in range(100):
                t = threading.Thread(target=FormulaSpider.run, args=(self, i, int(j * step), int((j + 1) * step)))
                t_list.append(t)
                t.start()
            for t in t_list:
                t.join()

            # 存到json
            FormulaSpider.tidy_load(self.formula_dic, j)
            time.sleep(base_sleep_time * int(self.retry_count / 80 + 1))
            self.retry_count = 0
            j += 1


spider = FormulaSpider()
spider.get_html("https://en.wikipedia.org/wiki/TRevPAR")
# spider.process()
