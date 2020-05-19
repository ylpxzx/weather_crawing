import requests
import time
import random
import re
import pypinyin
from bs4 import BeautifulSoup

class PM_DATA:
    '''
    获取天气后报网站城市天气PM数据，单线程版本，未存入excel文件
    date : 2020/03/22
    author : xzx
    '''
    def __init__(self,name):
        self.total_list = []  # 总数据列表
        self.sleep_time = [1,2,3]  # 随机休眠时间列表
        self.name = change_c(name)
        self.main_url = 'http://www.tianqihoubao.com/aqi/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Host': 'www.tianqihoubao.com',
            'Referer': 'http://www.tianqihoubao.com/aqi/'
        }

    def index_request(self):
        '''
        某城市页请求
        :return: HTML数据
        '''
        r = requests.get(self.main_url + self.name + '.html', headers=self.headers)
        if r.status_code == requests.codes.ok:
            print(r.status_code, '请求成功')
            return r.text
        else:
            print(r.status_code, '请求失败')
            return None

    def parse_index_html(self):
        '''
        解析该城市提供的所有PM日期URL链接
        :return: 日期列表
        '''
        date_list = []
        index_html = self.index_request()
        if index_html is None:
            return None
        soup = BeautifulSoup(index_html, 'html.parser')
        try:
            content = soup.select_one('div.box.p').find_all_next('ul')[0]
            son_url = content.find_all('a')
            for attr in son_url:
                # 从HTML的href属性中解析出URL，并对日期进行过滤
                href_str = attr['href']
                fir_date = href_str.split('-')
                fin_date = fir_date[1].split('.')[0]
                if fin_date <= '201912' and fin_date >= '201501':
                    date_list.append(fin_date)
        except:
            print('主HTML解析失败（可能页面被更新过）')
            return None
        return date_list

    def son_request(self):
        '''
        某城市月份PM数据请求
        :return: 获取的总数据 ---> 字典
        '''
        date_list = self.parse_index_html()
        if date_list is None:
            return None
        for date_num in date_list:
            url = self.main_url + self.name + '-' + date_num + '.html'
            print('请求：',url)

            # 随机获取休眠时间，避免反爬
            choice_time = random.choice(self.sleep_time)
            print('避免反爬,设置睡眠时间为：',choice_time,'s')
            time.sleep(choice_time)

            r = requests.get(url,headers = self.headers)
            data_dict = self.parse_son_html(r.text,date_num)
            self.total_list.append(data_dict)
        print(self.total_list)
        return self.total_list

    def parse_son_html(self,son_html,date_num):
        '''
        解析子页面,获取PM数据
        :param son_html: 子页面HTML数据
        :param date_num: 月份
        :return: 月级PM数据 ---> 字典
        '''
        date_dict = {}  # 以月份为键的月数据
        index_list = []  # 保存键名
        result_data = {}  # 一天的PM数据
        soup = BeautifulSoup(son_html, 'html.parser')
        try:
            # 解析HTML中的table  ---> 观察下网页的HTML的结构就了解了
            content = soup.table.find_all('tr')
            for index , value in enumerate(content):
                if index == 0:
                    for i in value.find_all('td'):
                        index_list.append(i.b.string)
                        result_data[i.b.string] = []
                else:
                    for i,j in enumerate(value.find_all('td')):
                        # 清除字符串包含的特殊字符
                        a = re.compile(r'\n|&nbsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020|\t|\r')
                        clean_str = a.sub('', j.string)
                        result_data[index_list[i]].append(clean_str)
                date_dict[date_num] = result_data
            print('数据爬取成功！')
            return date_dict
        except:
            print('子HTML解析失败（可能页面被更新过）')
            return None

def change_c(word):
    '''
    将用户输入的中文转为拼音字母
    :param word:
    :return:
    '''
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s

if __name__ == '__main__':
    str_value = input('请输入城市名：')
    print('城市名拼音：',change_c(str_value))
    PM_DATA(str_value).son_request()