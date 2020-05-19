import requests
import time
import random
import re
import pypinyin
import pandas as pd
from bs4 import BeautifulSoup

class PM_DATA:
    '''
    获取天气后报网站城市天气PM数据,单线程版本，存入excel文件
    date : 2020/03/22
    author : xzx
    '''
    def __init__(self,name):
        self.index_list = ['日期','质量等级','AQI指数','当天AQI排名','PM2.5','PM10','So2','No2','Co','O3']
        self.total_list = {}
        self.total_list['日期'] = []
        self.total_list['质量等级'] = []
        self.total_list['AQI指数'] = []
        self.total_list['当天AQI排名'] = []
        self.total_list['PM2.5'] = []
        self.total_list['PM10'] = []
        self.total_list['So2'] = []
        self.total_list['No2'] = []
        self.total_list['Co'] = []
        self.total_list['O3'] = []
        self.sleep_time = [1,2,3]  # 随机休眠时间列表
        self.name = change_c(name)
        self.main_url = 'http://www.tianqihoubao.com/aqi/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
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
                if fin_date <= '201912' and fin_date >= '201911': # 设置爬取的时间段
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

            # 随机获取休眠时间，降低被反爬的概率
            # choice_time = random.choice(self.sleep_time)
            # print('避免反爬,设置睡眠时间为：',choice_time,'s')
            # time.sleep(choice_time)

            r = requests.get(url,headers = self.headers)
            self.parse_son_html(r.text)
        print('存入excel')
        my_df = pd.DataFrame.from_dict(self.total_list,orient='index').T
        print(my_df)
        # writer_to = pd.ExcelWriter('data_pm.xlsx')
        my_df.to_excel('data.xlsx',index=False)
        # my_df.to_excel(writer_to, index=False)
        print('写人成功')


    def parse_son_html(self,son_html):
        '''
        解析子页面,获取PM数据
        :param son_html: 子页面HTML数据
        :param date_num: 月份
        :return: 月级PM数据 ---> 字典
        '''
        soup = BeautifulSoup(son_html, 'html.parser')
        try:
            # 解析HTML中的table
            content = soup.table.find_all('tr')
            for index , value in enumerate(content):
                if index == 0:
                    pass
                else:
                    for i,j in enumerate(value.find_all('td')):
                        # 清除字符串包含的特殊字符
                        a = re.compile(r'\n|&nbsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020|\t|\r')
                        clean_str = a.sub('', j.string)
                        self.total_list[self.index_list[i]].append(clean_str)
            print('数据爬取成功！')
        except:
            print('子HTML解析失败（可能页面被更新过）')

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
    print('城市名：',change_c(str_value))
    PM_DATA(str_value).son_request()