import tkinter as tk
import requests
from bs4 import BeautifulSoup
import csv
import urllib
import json
import pathlib
import matplotlib.pyplot as plt
import pandas

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
ss = requests.session()

window = tk.Tk()
window.title('104 Query')
window.geometry('800x200')
window.configure(background='black')

def go_crawling():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    ss = requests.session()

    keyword = str(keyword_entry.get())
    keyword_url_format = urllib.parse.quote(keyword)
    pages = int(pages_entry.get())
    startpage = 1
    count = 1
    url = "https://www.104.com.tw/jobs/search/?keyword=" + keyword_url_format + "&jobsource=2018indexpoc&ro=0&order=1"
    cur_path = pathlib.Path.cwd()
    csv_file = open(cur_path / f'{keyword}_{pages}頁.csv', 'w', encoding='utf_8_sig', newline='')
    csv_writer = csv.writer(csv_file)
    datatitle = ['公司名稱', '職缺名稱', '徵才網址', '薪水區間', '薪資下限', '薪資上限', \
                 '工作性質', '工作地點', '管理責任', '出差外派', '上班時段',
                 '休假制度', '可上班日', '需求人數', '接受身份', '工作經歷', '學歷要求', \
                 '科系要求', '語文條件', '擅長工具', '工作技能']
    csv_writer.writerow(datatitle)

    specialty_dict = {}
    last_detail_link = ''
    for i in range(pages):
        res = ss.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        comp_name_list = soup.select('article', class_="js-job-item")

        for ccc in comp_name_list:
            try:
                comp_name = ccc['data-cust-name']
                job_name = ccc['data-job-name']
                detail_link = 'http:' + ccc.select_one('a', class_='js-job-link')['href']
                if detail_link == last_detail_link: continue
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
                detail_list = [comp_name, job_name]  # 公司名稱、職缺名稱
                detail_list.append(detail_link)  # 徵才網址
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

                    # 統計各專長
                    # print(aaa['description'])
                    if not aaa['description'] in specialty_dict:
                        specialty_dict[aaa['description']] = 1
                    else:
                        specialty_dict[aaa['description']] += 1
                detail_list.append(sss)  # 擅長工具

                sss = ''
                for aaa in detail_dict['data']['condition']['skill']:
                    if aaa != detail_dict['data']['condition']['skill'][-1]:
                        sss += aaa['description'] + ', '
                    else:
                        sss += aaa['description']
                detail_list.append(sss)  # 工作技能
            except KeyError as e:
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

            pp(f'已抓取 {count:4}筆\n已處理 {i + 1} / {pages} 頁')
            count += 1
            csv_writer.writerow(detail_list)

        startpage += 1
        url = 'https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=' + keyword + '&order=15&asc=0&page=' + str(
            startpage) + '&mode=l&jobsource=2018indexpoc'
        print(f'已完成 {i + 1} / {pages} 頁')
    csv_file.close()

    specialty_dict_sorted = sorted(specialty_dict.items(), key=lambda d: d[1], reverse=True)

    columns = ['技能名稱', '出現次數']
    specialty_csv_file = open(cur_path / f'{keyword}_{pages}頁_specialty.csv', 'w', encoding='utf_8_sig', newline='')
    s_csv_writer = csv.writer(specialty_csv_file)
    s_csv_writer.writerow(columns)
    for ii in specialty_dict_sorted:
        s_csv_writer.writerow(ii)
    # df = pandas.DataFrame(data=data, columns=columns)
    # df.to_csv(f'./{keyword}_{pages}頁_specialty.csv', index=False, encoding='utf_8_sig')
    # df.to_excel(f'./{keyword}_{pages}頁_specialty.xlsx', index=False, encoding='utf_8_sig')
    print('\n本次查尋結果的技能統計將會生成 csv 與 excel 檔')

    pp(f'已抓取 {count:4}筆\n已處理 {i + 1} / {pages} 頁\n處理完畢！\n本次查尋結果將存放在 {cur_path}/{keyword}_{pages}頁.csv\n技能統計次數將存放在 {cur_path}/{keyword}_{pages}頁_specialty.csv')


    font = 'PingFang HK'
    plt.rcParams['font.sans-serif'] = font
    how_many_specialty_wanted = 8
    specialty_rank_tilte = [i[0] for i in specialty_dict_sorted[:how_many_specialty_wanted]]
    specialty_rank_num = [i[1] for i in specialty_dict_sorted[:how_many_specialty_wanted]]

    print(specialty_rank_tilte)
    print(specialty_rank_num)
    s = pandas.Series(specialty_rank_num, index=specialty_rank_tilte, name='')
    explode = [0 for i in range(how_many_specialty_wanted)]
    explode[0] = 0.1
    s.plot.pie(explode=explode, labeldistance=1.2, title=keyword + '_技能需求分佈', autopct='%.2f%%')
    plt.savefig(f'{keyword}_{pages}頁_技能需求分佈', dpi=300)
    plt.show()

header_label = tk.Label(window, text='104人力銀行資料搜尋整合')
header_label.configure(background='black', fg='white')
header_label.pack()

keyword_frame = tk.Frame(window, background='black')
keyword_frame.pack(side=tk.TOP)
keyword_label = tk.Label(keyword_frame, text='請輸入關鍵字 : ', background='black', fg='white')
keyword_label.pack(side=tk.LEFT)
keyword_entry = tk.Entry(keyword_frame, background='black', fg='white')
keyword_entry.pack(side=tk.LEFT)

pages_frame = tk.Frame(window, background='black')
pages_frame.pack(side=tk.TOP)
pages_label = tk.Label(pages_frame, text='搜尋頁數 : ', background='black', fg='white')
pages_label.pack(side=tk.LEFT)
pages_entry = tk.Entry(pages_frame, background='black', fg='white', width=5)
pages_entry.pack(side=tk.LEFT)

calculate_btn = tk.Button(window, text='開始處理', background='black', command=go_crawling)
calculate_btn.pack()

str_obj = tk.StringVar()
result_label = tk.Label(window, background='black', fg='white', textvariable = str_obj)
result_label.pack()

def pp(text):
    str_obj.set(text)
    window.update()

window.mainloop()