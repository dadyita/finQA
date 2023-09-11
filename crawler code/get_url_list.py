import json
import re
import threading
import requests
from fake_useragent import UserAgent
from treelib import Tree


# 定义一个获取URL_list爬虫类
class UrlSpider(object):
    # 初始化
    # 定义初始页面url
    def __init__(self):
        # url_tree 存储网页和公式
        # 树的属性：tag = url_suffix, identifier = parent_identifier + number of sibling, data = page_list
        # url_tree 子节点代表该网页内含的页面
        # 深度从 0 开始，有data的层数为 0,1,2 层
        self.url_tree = Tree()
        self.url_tree.create_node('Finance', '0')
        self.page_prefix = 'https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtype=page&cmlimit' \
                           '=500&cmtitle=Category:'
        self.subcat_prefix = 'https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtype=subcat' \
                             '&cmlimit=500&cmtitle=Category:'
        self.value_lock = threading.Lock()

    # 请求函数
    def get_html(self, identifier):
        # id获取tree中的tag，作为url_suffix
        url_suffix = self.url_tree.get_node(identifier).tag
        page_url = self.page_prefix + url_suffix
        # print(page_url)
        subcat_url = self.subcat_prefix + url_suffix
        # print(subcat_url)
        ua = UserAgent()
        headers = {'User-Agent': ua.random}

        try:
            # 获取page_html
            res = requests.get(page_url, headers)
            res.encoding = "utf-8"
            page_html = res.text

            # 获取page_html
            res = requests.get(subcat_url, headers)
            res.encoding = "utf-8"
            subcat_html = res.text
            # 解析html并且把网页中的url作为改id对应节点的子节点加入树中
            self.parse_html(page_html, subcat_html, identifier)

            # 有子类则创建线程
            t_list = []
            if self.url_tree.level(identifier) <= 2:
                if self.url_tree.level(identifier) == 0 or len(self.url_tree.children(identifier)) <= 10:
                    for i in self.url_tree.children(identifier):
                        t = threading.Thread(target=UrlSpider.run, args=(self, i.identifier))
                        t_list.append(t)
                        t.start()
                else:
                    print("too much")
            else:
                print("too deep")
            if t_list:
                for t in t_list:
                    t.join()
        except:
            self.get_html(identifier)

    # 解析函数
    def parse_html(self, page_html, subcat_html, parent):
        # print(page_html)
        # 提取page & subcat
        page_re_bds = '<span class="s2">&quot;title&quot;</span><span class="o">:</span> <span class="s2">&quot;(.*?)&quot;</span>'
        subcat_re_bds = '<span class="s2">&quot;title&quot;</span><span class="o">:</span> <span class="s2">&quot;Category:(.*?)&quot;</span>'
        re_obj = re.compile(page_re_bds, re.S)
        page_list = re_obj.findall(page_html)
        re_obj = re.compile(subcat_re_bds, re.S)
        subcat_list = re_obj.findall(subcat_html)
        node = self.url_tree.get_node(parent)
        node.data = page_list
        for i in range(len(subcat_list)):
            with self.value_lock:
                self.url_tree.create_node(subcat_list[i], parent + '-' + str(i), parent)

    def run(self, identifier):
        self.get_html(identifier)

    def process(self):
        # 从 root-finance 开始
        self.get_html('0')

        # 生成json文件
        url_dic = {}
        for i in self.url_tree.all_nodes():
            if i.data:
                i.data = [x.encode('utf-8').decode('unicode_escape') for x in i.data]
                url_dic[i.tag] = i.data
        temp = json.dumps(url_dic, ensure_ascii=False)
        f2 = open('url_list.json', 'w', encoding='utf-8')
        f2.write(temp)
        f2.close()


# spider = UrlSpider()
# spider.process()
with open('economics_url_list.json', 'r',encoding='utf-8') as f:
    data = f.read()

data = data.replace('\\&quot;', '"')

with open('economics_url_list.json', 'w',encoding='utf-8') as f:
    f.write(data)
