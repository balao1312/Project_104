import requests, csv, urllib, pathlib, json, time
import pandas as pd
from bs4 import BeautifulSoup
import ssl  # mac 需要設定SSL   在使用urllib時

ssl._create_default_https_context = ssl._create_unverified_context


def web_scraping(keyword, pages):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    keyword_url_format = urllib.parse.quote(keyword)  # 中文字轉 url 格式
    url = "https://www.104.com.tw/jobs/search/?keyword=" + keyword_url_format + "&jobsource=2018indexpoc&ro=0&order=1"
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
    specialty_dict = {}  # 字典存技能統計
    edu_req_dict = {'高中以上': 0, '專科以上': 0, '大學以上': 0, '碩士以上': 0, '不拘': 0}  # 字典存學歷需求
    major_req_dict = {}  # 字典存科系要求
    startpage = 1  # 開始頁數
    count = 0  # 資料總筆數
    for i in range(pages):
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        job_name_list = soup.select('article', class_="js-job-item")

        for job in job_name_list:
            try:
                comp_name = job['data-cust-name']
                job_name = job['data-job-name']

                detail_link = 'http:' + job.select_one('a', class_='js-job-link')['href']

                # 取得細項網址
                detail_code = detail_link.split('/')[-1].split('?')[0]
                detail_link_oo = 'https://m.104.com.tw/job/' + detail_code

                # print(detail_link_oo)
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
                detail_list = [comp_name, job_name]  # 公司名稱、職缺名稱

                detail_list.append(detail_link)  # 徵才網址

                detail_list.append(dfs[1].iat[0, 1][:-5])  # 薪水區間
                detail_list.append(dfs[0].iat[1, 1][-2:])  # 工作性質
                detail_list.append(dfs[0].iat[0, 1])  # 工作地點
                detail_list.append(dfs[2].iat[3, 1])  # 管理責任
                detail_list.append(dfs[2].iat[0, 1])  # 出差外派
                detail_list.append(dfs[2].iat[1, 1])  # 上班時段
                detail_list.append(dfs[2].iat[2, 1])  # 休假制度
                detail_list.append(dfs[3].iat[1, 1])  # 可上班日
                detail_list.append(dfs[0].iat[2, 1])  # 需求人數
                detail_list.append(dfs[3].iat[0, 1])  # 接受身份
                detail_list.append(dfs[3].iat[2, 1])  # 工作經歷
                detail_list.append(dfs[3].iat[3, 1])  # 學歷要求

                # 學歷要求統計
                if '不拘' in dfs[3].iat[3, 1]:
                    edu_req_dict['不拘'] += 1
                elif '高中' in dfs[3].iat[3, 1]:
                    edu_req_dict['高中以上'] += 1
                elif '專科' in dfs[3].iat[3, 1]:
                    edu_req_dict['專科以上'] += 1
                elif '大學' in dfs[3].iat[3, 1]:
                    edu_req_dict['大學以上'] += 1
                elif '碩士' in dfs[3].iat[3, 1]:
                    edu_req_dict['碩士以上'] += 1

                # 科系要求
                ffilter = (dfs[3][0] == '科系要求：')
                # print(f'科系要求: \n{dfs[3][ff]}')
                if len(dfs[3][ffilter]):
                    detail_list.append(dfs[3][ffilter].iat[0, 1])
                    # 科系要求統計
                    majors = dfs[3][ffilter].iat[0, 1].split('、')
                    for major in majors:
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
                print(f'目標不符設定 出錯原因 ： \n{e}')
                print('======================')
                continue

            # # 每完成一項職缺的細項抓取 就寫入一列資料到剛剛建好標頭的csv檔 這邊開檔用 a = append
            with open(static_folder.joinpath(f'104_result_{keyword}x{pages}.csv'), 'a',
                      encoding='utf_8_sig') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(detail_list)

            count += 1
            if pages == 1:
                pass
            else:
                time.sleep(0.5)

        # startpage 初始是1
        startpage += 1
        url = 'https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=' + keyword + '&order=15&asc=0&page=' + str(
            startpage) \
              + '&mode=l&jobsource=2018indexpoc'
        print(f'已完成 {i + 1} / {pages} 頁')

    # 處理統計專長的字典 這行是用value排序後回傳一個新的 list, 字典.item() 可以將字典轉成含有 key & value 的 list
    specialty_dict_sorted = sorted(specialty_dict.items(), key=lambda d: d[1], reverse=True)
    edu_req_dict_sorted = sorted(edu_req_dict.items(), key=lambda d: d[1], reverse=True)
    major_req_dict_sorted = sorted(major_req_dict.items(), key=lambda d: d[1], reverse=True)

    print(f'完成處理，總共有 {count} 筆資料')

    # 回傳接下來畫圖需要的變數
    return {'specialty_dict_sorted': specialty_dict_sorted, 'edu_req_dict_sorted': edu_req_dict_sorted,
            'major_req_dict_sorted': major_req_dict_sorted, 'count': count}

def web_scraping_demo():
    specialty_dict_sorted = [('MS SQL', 104), ('MySQL', 96), ('Linux', 71), ('Python', 63), ('Oracle', 63), ('Excel', 56), ('Word', 51),
     ('Java', 48), ('C#', 46), ('PowerPoint', 41), ('JavaScript', 38), ('PL/SQL', 33), ('PHP', 31), ('HTML', 30),
     ('AutoCAD', 28), ('ASP.NET', 28), ('C++', 26), ('Windows Server 2012', 22), ('jQuery', 22), ('Vmware', 21),
     ('Outlook', 19), ('Shell', 18), ('ETL', 18), ('AWS', 18), ('Windows 10', 16), ('PostgreSQL', 16), ('C', 15),
     ('CSS', 15), ('Database Management', 14), ('UNIX', 14), ('TCP/IP', 13), ('Windows 7', 12),
     ('Windows Server 2008', 12), ('hadoop', 12), ('Project', 12), ('Database Administrator', 11), ('IIS', 10),
     ('C++.Net', 10), ('AIX', 8), ('Firewall', 8), ('Windows 8', 8), ('Adobe Acrobat', 7), ('R', 7),
     ('Power BI\u200b', 7), ('Github', 7), ('RDBMS', 7), ('Internet Explorer', 7), ('鼎新', 7), ('Sun Solaris', 7),
     ('AJAX', 7), ('Visual C#', 7), ('Windows XP', 6), ('Informatica', 6), ('OLAP', 6), ('ANSI SQL', 6),
     ('Visual Studio', 6), ('Solaris', 6), ('Hive', 6), ('VPN', 6), ('Android', 6), ('iOS', 6),
     ('Visual Basic .net', 6), ('HP-UX', 6), ('Visual Studio .net', 6), ('DataStage', 5), ('Django', 5), ('Spring', 5),
     ('Tableau', 5), ('SAS', 5), ('LAN', 5), ('VBA', 5), ('FreeBSD', 5), ('VERITAS', 5), ('Load Balancing', 5),
     ('Tomcat', 5), ('AutoCad 2D', 4), ('Data Modeling', 4), ('Git', 4), ('JDBC', 4), ('中文打字20~50', 4), ('Struts', 4),
     ('Microsoft Exchange', 4), ('FTP', 4), ('SUN OS', 4), ('BS7799', 4), ('Go', 4), ('DNS', 4), ('Ethernet', 4),
     ('Mac OS', 4), ('WAN', 4), ('VLAN', 4), ('Access', 3), ('AutoCad 3D', 3), ('Scala', 3), ('OOP', 3), ('Cognos', 3),
     ('ASP', 3), ('ODBC', 3), ('SAP', 3), ('英文打字20~50', 3), ('HTTP', 3), ('Visual Basic', 3),
     ('Systems Administration', 3), ('LDAP', 3), ('ssh', 3), ('Delphi', 3), ('Visio', 3), ('Windows 2000', 3),
     ('Windows 2003', 3), ('Windows 95', 3), ('Windows 98', 3), ('Node.js', 2), ('DB2', 2), ('Data Marts', 2),
     ('Matlab', 2), ('Teradata', 2), ('COBOL', 2), ('AS/400', 2), ('D3.js', 2), ('Toad', 2), ('Oracle Forms', 2),
     ('Systems Analysis', 2), ('Dreamweaver', 2), ('Cisco', 2), ('SAN', 2), ('SAN/NAS', 2), ('Adobe Photoshop', 2),
     ('Visual C++', 2), ('DOS', 2), ('Perl', 2), ('Hubs/ Routers', 2), ('Routers', 2), ('J2EE', 2), ('Ghost', 2),
     ('JSP', 2), ('Web Master/Developer', 2), ('鼎基 ERP', 2), ('Data Architect', 1), ('OOAD', 1), ('VueJS', 1),
     ('XML Web services', 1), ('ADO', 1), ('Brio', 1), ('ISO14000', 1), ('ISO9000', 1), ('TS16949', 1),
     ('中文打字75~100', 1), ('Microsoft SharePoint', 1), ('SNA', 1), ('英文打字50~75', 1), ('IE工業工程', 1), ('MES', 1),
     ('Oracle ERP', 1), ('MCU', 1), ('DVR數位視頻錄像', 1), ('LabVIEW', 1), ('TIBCO', 1), ('Wordperfect', 1), ('SOAP', 1),
     ('ArcGis', 1), ('GIS', 1), ('MapGIS', 1), ('SPSS', 1), ('PBX', 1), ('VoIP', 1), ('VM', 1), ('Servlets', 1),
     ('Xmind', 1), ('CADAM', 1), ('EDA', 1), ('FPGA', 1), ('VBScript', 1), ('Google Analytics', 1), ('WLAN', 1),
     ('UDP', 1), ('XML', 1), ('PLC', 1), ('AngularJS', 1), ('ReactNative', 1), ('英文打字75~100', 1), ('英文打字100~125', 1),
     ('Mac/Macintosh', 1), ('Apple', 1), ('Windows NT', 1), ('Windows Vista', 1), ('Windows Mobile', 1),
     ('iptables', 1), ('PPPoE', 1), ('NetWare', 1), ('Juniper', 1), ('DHCP', 1), ('LanServer', 1), ('中文打字50~75', 1),
     ('PowerBuilder', 1)]
    edu_req_dict_sorted = [('大學以上', 270), ('專科以上', 241), ('高中以上', 32), ('碩士以上', 30), ('不拘', 19)]
    major_req_dict_sorted = [('資訊工程相關', 242), ('資訊管理相關', 204), ('電機電子工程相關', 61), ('數學及電算機科學學科類', 41), ('其他數學及電算機科學相關', 39), ('數理統計相關', 24), ('土木工程相關', 20), ('工程學科類', 19), ('統計學相關', 15), ('建築相關', 15), ('工業工程相關', 9), ('機械工程相關', 8), ('商業及管理學科類', 8), ('電機電子維護相關', 8), ('應用數學相關', 5), ('一般數學相關', 5), ('建築及都市規劃學科類', 4), ('醫藥衛生學科類', 3), ('機械維護相關', 3), ('測量工程相關', 3), ('企業管理相關', 3), ('會計學相關', 3), ('自然科學學科類', 2), ('財稅金融相關', 2), ('其他建築及都市規劃學類', 2), ('食品營養相關', 1), ('食品科學相關', 1), ('汽車汽修相關', 1), ('通信學類', 1), ('其他工程相關', 1), ('環境工程相關', 1), ('工業技藝及機械學科類', 1), ('光電工程相關', 1), ('景觀設計相關', 1), ('河海或船舶工程相關', 1), ('其他工業技藝相關', 1), ('銀行保險相關', 1), ('一般商業學類', 1)]
    count = 592

    return {'specialty_dict_sorted': specialty_dict_sorted, 'edu_req_dict_sorted': edu_req_dict_sorted,
            'major_req_dict_sorted': major_req_dict_sorted, 'count': count}

if __name__ == '__main__':
    web_scraping('資訊工程', 3)
