import requests
from bs4 import BeautifulSoup
import csv
import urllib
import json

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
keyword = input('請輸入關鍵字 : ')
# keyword = urllib.parse.quote(input('請輸入關鍵字 : '))
pages= int(input('請輸入要抓取的頁數 : '))
startpage = 1

url = "https://www.104.com.tw/jobs/search/?keyword=" + keyword +"&jobsource=2018indexpoc&ro=0&order=1"
ss = requests.session()

cookies={}
cookies_string = '''__asc=e8e44726170e82e1140262dcf40; __auc=e8e44726170e82e1140262dcf40; luauid=2114195893; _gid=GA1.3.87602258.1584443298; _gaexp=GAX1.3.bWd8w_zQQD6wRapXgYI9bg.18424.1; _hjid=36896220-6ac2-4a4e-9f2a-e02131b76c69; ALGO_EXP_6019=C; job_same_ab=1; cust_same_ab=2; bprofile_history=%5B%7B%22key%22%3A%2275e8xvc%22%2C%22custName%22%3A%22%E4%B8%96%E6%A8%BA%E7%89%99%E9%86%AB%E8%A8%BA%E6%89%80%22%2C%22custLink%22%3A%22https%3A%2F%2Fwww.104.com.tw%2Fcompany%2F75e8xvc%22%7D%2C%7B%22key%22%3A%2213quahyo%22%2C%22custName%22%3A%22%E7%8E%89%E5%B1%B1%E9%8A%80%E8%A1%8C_%E7%8E%89%E5%B1%B1%E5%95%86%E6%A5%AD%E9%8A%80%E8%A1%8C%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8%22%2C%22custLink%22%3A%22https%3A%2F%2Fwww.104.com.tw%2Fcompany%2F13quahyo%22%7D%5D; lup=2114195893.4702989186930.5035849152215.1.4640712161167; lunp=5035849152215; TS016ab800=01180e452d2009051cab3fa79537bfe40fc6dc6bb68c717cf316cb37cb8b06b135fb111d7a19feec0c8e1fab8726198ec0b7fc4bb95c13b2b0004ac8e91b92bdbbef7463ed5d81ae9f435821686a36e8c92473f68deeda1e5cb5838ad9b54ed706c601e4d4; _ga_W9X1GB1SVR=GS1.1.1584443298.1.1.1584449338.60; _ga_FJWMQR9J2K=GS1.1.1584443298.1.1.1584449338.0; _ga=GA1.3.1049900863.1584443298; _dc_gtm_UA-15276226-1=1'''
for cc in cookies_string.split(';'):
        ss.cookies[cc.split('=')[0]] = cc.split('=')[1]

csv_flie = open('./104.csv', 'w', encoding='utf_8_sig')
csv_writer = csv.writer(csv_flie)
datatitle = ['公司名稱', '職缺名稱', '徵才網址', '薪水區間', '薪資下限', '薪資上限', \
             '工作性質', '工作地點', '管理責任', '出差外派', '上班時段',
             '休假制度', '可上班日', '需求人數', '接受身份', '工作經歷', '學歷要求', \
             '科系要求', '語文條件', '擅長工具', '工作技能']
csv_writer.writerow(datatitle)

last_detail_link = ''
for i in range(pages):
    res = ss.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    comp_name_list = soup.select('article', class_="b-block--top-bord job-list-item b-clearfix js-job-item js-job-item--focus b-block--ad")
    for ccc in comp_name_list:
        try:
            comp_name = ccc['data-cust-name']
            job_name = ccc['data-job-name']
            detail_link = 'http:' + ccc.find('a', class_='js-job-link')['href']
            if detail_link == last_detail_link[:]: continue
            last_detail_link = detail_link
            detail_code = detail_link.split('/')[-1].split('?')[0]
            detail_link_content = 'https://www.104.com.tw/job/ajax/content/' + detail_code

            print(comp_name)
            print(job_name)
            print(detail_link + '\n')
            detail_res = ss.get(detail_link_content)
            detail_soup = BeautifulSoup(detail_res.text, 'html.parser').text

            detail_dict = json.loads(detail_soup, encoding='utf-8')

            # 開始建細項list
            detail_list = [comp_name, job_name]                             # 公司名稱、職缺名稱
            detail_list.append(detail_link)                                 # 徵才網址
            detail_list.append(detail_dict['data']['jobDetail']['salary'])  # 薪水區間
            detail_list.append(detail_dict['data']['jobDetail']['salaryMin'])  # 薪水下限
            detail_list.append(detail_dict['data']['jobDetail']['salaryMax'])  # 薪水上限
            detail_list.append('全職' if detail_dict['data']['jobDetail']['jobType'] == 1 else '兼職')  # 工作性質
            detail_list.append(detail_dict['data']['jobDetail']['addressRegion'] + \
                               detail_dict['data']['jobDetail']['addressDetail'] + \
                               detail_dict['data']['jobDetail']['industryArea'])  # 工作地點
            detail_list.append(detail_dict['data']['jobDetail']['manageResp'])  # 管理責任
            detail_list.append(detail_dict['data']['jobDetail']['businessTrip'])  # 出差外派
            detail_list.append(detail_dict['data']['jobDetail']['workPeriod'])  # 上班時段
            detail_list.append(detail_dict['data']['jobDetail']['vacationPolicy'])  # 休假制度
            detail_list.append(detail_dict['data']['jobDetail']['startWorkingDay'])  # 可上班日
            detail_list.append(detail_dict['data']['jobDetail']['needEmp'])  # 需求人數
            sss = ''
            for aaa in detail_dict['data']['condition']['acceptRole']['role']:
                if aaa != detail_dict['data']['condition']['acceptRole']['role'][-1]:
                    sss += aaa['description'] + ', '
                else:
                    sss += aaa['description']

            detail_list.append(sss)  # 接受身份
            detail_list.append(detail_dict['data']['condition']['workExp'])  # 工作經歷
            detail_list.append(detail_dict['data']['condition']['edu'])  # 學歷要求

            sss = ''
            for aaa in detail_dict['data']['condition']['major']:
                if aaa != detail_dict['data']['condition']['major'][-1]:
                    sss += aaa + ', '
                else:
                    sss += aaa
            detail_list.append(sss)  # 科系要求

            sss = ''
            for lll in detail_dict['data']['condition']['language']:
                for llll in list(dict.values(lll)):
                    sss += llll + ' '
                sss += ' , '
            detail_list.append(sss)  # 語文條件

            sss = ''
            for aaa in detail_dict['data']['condition']['specialty']:
                if aaa != detail_dict['data']['condition']['specialty'][-1]:
                    sss += aaa['description'] + ', '
                else:
                    sss += aaa['description']
            detail_list.append(sss)  # 擅長工具

            sss = ''
            for aaa in detail_dict['data']['condition']['skill']:
                if aaa != detail_dict['data']['condition']['skill'][-1]:
                    sss += aaa['description'] + ', '
                else:
                    sss += aaa['description']
            detail_list.append(sss)  # 工作技能
        except KeyError as e :
            print('======================')
            print('目標不符設定 內容 ： ')
            print(ccc)
            print('======================')
            continue
        except json.decoder.JSONDecodeError as e:
            print('======================')
            print('json格式轉換錯誤')
            print('======================')
            continue

        csv_writer.writerow(detail_list)

    startpage += 1
    url = 'https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword='+keyword+'&order=15&asc=0&page='+str(startpage)\
          +'&mode=l&jobsource=2018indexpoc'

csv_flie.close()