from flask import Flask, request, render_template
from web_scraping_v2 import web_scraping
import csvfilter, time, pathlib
import visualize as v

app = Flask(__name__, static_url_path='/static', static_folder='./static')
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1                 #設置瀏覽器不緩存

occupied = False

@app.route('/', methods=['GET', 'POST'])
def start_here():

    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        global occupied
        if occupied == True:
            return render_template('hold.html')
        occupied = True
        tt1 = time.time()       # 計時的開始時間
        keyword = request.form.get('keyword')       # 從表格中取得使用者輸入
        pages = int(request.form.get('pages'))

        returned_dict = web_scraping(keyword, pages)    # 從爬蟲函式取得排名名單 呼叫畫圖函式

        v.visualize_pie(returned_dict['specialty_dict_sorted'], keyword, returned_dict['count'], pages)
        v.visualize_barh(returned_dict['major_req_dict_sorted'], keyword, returned_dict['count'], pages)
        v.visualize_bar(returned_dict['edu_req_dict_sorted'], keyword, returned_dict['count'], pages)
        count = returned_dict['count']

        # 把表格中的每個欄位checkbox取得後存在 show_column 的 list 變數 (有勾的值會是 'on'，沒勾是 None)
        # 再呼叫 csv_filter 函式去生成一個新的使用者客製的表格
        job_name = request.form.get('job_name')
        detail_link = request.form.get('detail_link')
        salary = request.form.get('salary')
        jobType = request.form.get('jobType')

        workloc = request.form.get('workloc')
        manageResp = request.form.get('manageResp')
        businessTrip = request.form.get('businessTrip')
        workPeriod = request.form.get('workPeriod')
        vacationPolicy = request.form.get('vacationPolicy')

        startWorkingDay = request.form.get('startWorkingDay')
        needEmp = request.form.get('needEmp')
        role = request.form.get('role')
        workExp = request.form.get('workExp')
        edu = request.form.get('edu')

        major = request.form.get('major')
        language = request.form.get('language')
        specialty = request.form.get('specialty')
        #skill = request.form.get('skill')

        # 原始表格有19欄，公司名設定成永遠顯示，所以設'on'
        show_column = ['on', job_name, detail_link, salary, jobType,
                       workloc, manageResp, businessTrip, workPeriod, vacationPolicy,
                       startWorkingDay, needEmp, role, workExp, edu,
                       major, language, specialty]

        filter_csv = csvfilter.csv_filter(show_column, keyword, pages)

        tt2 = time.time()   # 計時的結束時間
        t1 = f'{tt2 - tt1:.4f}'
        print(t1)
        occupied = False
        return render_template('gg.html',t1=t1, keyword=keyword, filter_csv= filter_csv, count=count, pages=pages)
                                                     # 導向結果網頁，把需要的變數一併傳出

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = 5000)
