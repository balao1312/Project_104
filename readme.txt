服務名稱：104人力銀行關鍵字查詢統計分析

服務目的：經由Python套件Flask生成網頁，輸入關鍵字及搜尋頁數後，將資料統計分析後視覺化呈現

使用技術：Python、Flask、BeautifulSoup、Matplotlib

使用方法：執行 app.py 後開啟瀏覽器連線至本地端 localhost:5000

所需套件安裝方法：
在執行境環的terminal輸入
pip install -r requirements.txt
等待安裝完成即可


檔案描述：
app.py => 主程式，介接前端網頁
web_scraping.py => 爬蟲及統計，生成csv檔
visualize.py => matplotlib 繪圖
Csvfilter.py => 篩選使用者所需欄位並存檔
