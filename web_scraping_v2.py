import requests, csv, urllib, pathlib, json
import pandas as pd
from bs4 import BeautifulSoup
import ssl  # mac 需要設定SSL   在使用urllib時

ssl._create_default_https_context = ssl._create_unverified_context

def web_scraping(kk, pp):
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    keyword = kk
    keyword_url_format = urllib.parse.quote(keyword)    # 中文字轉 url 格式
    pages= pp

    url = "https://www.104.com.tw/jobs/search/?keyword=" + keyword_url_format +"&jobsource=2018indexpoc&ro=0&order=1"

    static_folder = pathlib.Path.cwd().joinpath('static')

    # 寫入 csv 檔的標頭
    with open(static_folder.joinpath(f'104_result_{keyword}x{pages}.csv'), 'w', encoding='utf_8_sig') as csv_file:
        csv_writer = csv.writer(csv_file)
        datatitle = ['公司名稱', '職缺名稱', '徵才網址', '薪水區間', \
                     '工作性質', '工作地點', '管理責任', '出差外派', '上班時段',
                     '休假制度', '可上班日', '需求人數', '接受身份', '工作經歷', '學歷要求', \
                     '科系要求', '語文條件', '擅長工具']
        csv_writer.writerow(datatitle)

    # 迴圈前初始化變數
    specialty_dict = {}         # 字典存技能統計
    edu_req_dict = {'高中以上':0, '專科以上':0, '大學以上':0, '碩士以上':0, '不拘':0}       # 字典存學歷需求
    major_req_dict = {}         # 字典存科系要求
    startpage = 1               # 開始頁數
    count = 0                   # 資料總筆數
    last_detail_link = ''  # 為了防止偶發的重覆
    for i in range(pages):

        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        job_name_list = soup.select('article', class_="js-job-item")

        for job in job_name_list:
            try:
                comp_name = job['data-cust-name']
                job_name = job['data-job-name']

                detail_link = 'http:' + job.select_one('a', class_='js-job-link')['href']
                # if detail_link == last_detail_link: continue      # 如果等於上一次的連結 (重複) 就跳過此筆資料
                # last_detail_link = detail_link

                # 取得細項網址
                detail_code = detail_link.split('/')[-1].split('?')[0]
                detail_link_oo = 'https://m.104.com.tw/job/' + detail_code

                print(comp_name)
                print(job_name)
                print(detail_link)
                print(detail_link_oo)

                dfs = pd.read_html(detail_link_oo)
                # print(len(dfs))
                # for ii,dd in enumerate(dfs):
                #     print(ii)
                #     print(dd)
                #     print('-'*40)

                # 開始建細項list
                detail_list = [comp_name, job_name]                             # 公司名稱、職缺名稱

                detail_list.append(detail_link)                                 # 徵才網址

                detail_list.append(dfs[1].iat[0,1][:-5])  # 薪水區間
                detail_list.append(dfs[0].iat[1,1][-2:])  # 工作性質
                detail_list.append(dfs[0].iat[0,1])  # 工作地點
                detail_list.append(dfs[2].iat[3,1])  # 管理責任
                detail_list.append(dfs[2].iat[0,1]) # 出差外派
                detail_list.append(dfs[2].iat[1,1])  # 上班時段
                detail_list.append(dfs[2].iat[2,1])  # 休假制度
                detail_list.append(dfs[3].iat[1,1])  # 可上班日
                detail_list.append(dfs[0].iat[2,1])  # 需求人數
                detail_list.append(dfs[3].iat[0,1])  # 接受身份
                detail_list.append(dfs[3].iat[2,1])  # 工作經歷
                detail_list.append(dfs[3].iat[3,1])  # 學歷要求

                # 學歷要求統計
                if '不拘' in dfs[3].iat[3,1]:
                    edu_req_dict['不拘']+=1
                elif    '高中' in dfs[3].iat[3,1]:
                    edu_req_dict['高中以上']+=1
                elif '專科' in dfs[3].iat[3,1]:
                    edu_req_dict['專科以上']+=1
                elif '大學' in dfs[3].iat[3,1]:
                    edu_req_dict['大學以上']+=1
                elif '碩士' in dfs[3].iat[3,1]:
                    edu_req_dict['碩士以上']+=1

                # 科系要求
                ffilter = (dfs[3][0] == '科系要求：')
                #print(f'科系要求: \n{dfs[3][ff]}')
                if len(dfs[3][ffilter]):
                    detail_list.append(dfs[3][ffilter].iat[0,1])
                    # 科系要求統計
                    majors = dfs[3][ffilter].iat[0,1].split('、')
                    for major in majors :
                        if not major in major_req_dict:
                            major_req_dict[major] = 1
                        else:
                            major_req_dict[major] += 1
                else:
                    detail_list.append('不拘')

                # 語文條件
                ffilter = (dfs[3][0] == '語文條件：')
                # print(f'科系要求: \n{dfs[3][ff]}')
                if len(dfs[3][ffilter]):
                    detail_list.append(dfs[3][ffilter].iat[0, 1])
                else:
                    detail_list.append('不拘')

                # 擅長工具
                ffilter = (dfs[3][0] == '擅長工具：')
                # print(f'科系要求: \n{dfs[3][ff]}')
                if len(dfs[3][ffilter]):
                    detail_list.append(dfs[3][ffilter].iat[0, 1])
                    # 擅長工具統計
                    specialtys = dfs[3][ffilter].iat[0, 1].split('、')
                    for specialty in specialtys:
                        if not specialty in specialty_dict:
                            specialty_dict[specialty] = 1
                        else:
                            specialty_dict[specialty] += 1
                else:
                    detail_list.append('不拘')

            except Exception as e:
                print('======================')
                print('目標不符設定 內容 ： ')
                print(e)
                print('======================')
                continue

            # print()
            # print(detail_list)
            # print(edu_req_dict)
            # print(major_req_dict)
            # print(specialty_dict)
            # print(len(detail_list))

            # # 每完成一項職缺的細項抓取 就寫入一列資料到剛剛建好標頭的csv檔 這邊開檔用 a = append
            with open(static_folder.joinpath(f'104_result_{keyword}x{pages}.csv'), 'a', encoding='utf_8_sig') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(detail_list)

            count +=1

        #startpage 初始是1
        startpage += 1
        url = 'https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword='+keyword+'&order=15&asc=0&page='+str(startpage)\
              +'&mode=l&jobsource=2018indexpoc'
        print(f'已完成 {i+1} / {pages} 頁')

    # 處理統計專長的字典 這行是用value排序後回傳一個新的 list, 字典.item() 可以將字典轉成含有 key & value 的 list
    specialty_dict_sorted = sorted(specialty_dict.items(), key=lambda d:d[1] ,reverse=True)
    edu_req_dict_sorted = sorted(edu_req_dict.items(), key=lambda d:d[1] ,reverse=True)
    major_req_dict_sorted = sorted(major_req_dict.items(), key=lambda d: d[1], reverse=True)

    print(f'完成處理，總共有 {count} 筆資料')

    #回傳接下來畫圖需要的變數
    return {'specialty_dict_sorted':specialty_dict_sorted, 'edu_req_dict_sorted':edu_req_dict_sorted,
            'major_req_dict_sorted':major_req_dict_sorted, 'count':count}

if __name__ == '__main__':
    web_scraping('資訊',1)