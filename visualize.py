import pandas, pathlib, matplotlib
import matplotlib.pyplot as plt
import numpy as np

def init():
    global static_path
    static_path = pathlib.Path.cwd().joinpath('static')

    plt.rcParams['font.sans-serif'] = 'PingFang HK'  # 設字型
    plt.rcParams['axes.titlepad'] = 20  # 設定 title 與主圖的距離
    matplotlib.use('agg')  # 為了在flask裡不跳警告

#畫圓餅圖
def visualize_pie(a_list=None, keyword='', count='', pages=''):
    if a_list is None:
        return
    init()

    if a_list:
        specialty_to_show = 10
        if len(a_list) < specialty_to_show : specialty_to_show = len(a_list)   # 如果排名少於10個 幾個就幾個
        a_list = a_list[:specialty_to_show]

        specialty_rank_tilte = [i[0] for i in a_list]       # 獨立出 技能名 跟 數量 成兩個list
        specialty_rank_num = [i[1] for i in a_list]

        # 找出python的排名位置
        python_index = -1
        for i in range(len(a_list)):
            if a_list[i][0] == 'Python':
                python_index = i

        s = pandas.Series(specialty_rank_num, index=specialty_rank_tilte, name='')  # 2個 list 當參數畫圓餅圖
        explode = [0 for i in range(len(a_list))]
        explode[0] = 0.1        # 排名第一的強調一下

        # 如果排名裡有 python 就也強調，如果已經是第一名就不多增加(離太遠不好看)
        if python_index > -1:
            if python_index != 0:
                explode[python_index] = 0.15

        s.plot.pie(explode=explode, labeldistance=1.1, title=f'{keyword} 技能需求 資料總數 : {count}', autopct='%.2f%%')
    else:   # 萬一搜尋結果一項技能需求都沒有
        ss = ['沒有技能需求']
        sss = [1]
        s = pandas.Series(sss, index=ss, name='')
        s.plot.pie(title=f'{keyword} 技能需求 資料總數 : {count}', autopct='%.2f%%')
    plt.savefig(static_path.joinpath(f'skill_req_{keyword}x{pages}'), dpi=250)
    # plt.show()
    plt.close()

#畫直方圖
def visualize_bar(a_list=None, keyword='', count='', pages=''):
    if a_list is None:
        return 
    init()
    
    edu = [i[0] for i in a_list]        # 獨立出 教育程度 跟 數量 成兩個list
    numbers = [i[1] for i in a_list]

    plt.title(label=f'{keyword} 教育程度需求 資料總數 : {count}')
    plt.bar(edu, numbers,  color=['orangered', 'goldenrod', 'green', 'blue', 'cyan'])
    plt.xticks(rotation=45)     # X刻度文字旋轉
    plt.subplots_adjust(bottom=0.2)     #與底部邊界
    plt.savefig(static_path.joinpath(f'edu_req_{keyword}x{pages}'), dpi=250)
    # plt.show()
    plt.close()

#畫直方圖(橫)
def visualize_barh(a_list=None, keyword='', count='', pages=''):
    if a_list is None:
        return
    init()

    if a_list:
        majors = [i[0] for i in a_list[:11]]
        numbers = [i[1] for i in a_list[:11]]

        df = pandas.Series(numbers, index=majors)
        colors = matplotlib.cm.RdYlGn(np.linspace(0, 1, len(df)))
        df.plot(kind='barh', color=colors, title=f'{keyword} 科系要求 資料總數 : {count}')
        plt.gca().invert_yaxis()
        plt.subplots_adjust(left=0.3)
    else:
        ss = ['沒有科系要求']
        sss = [1]
        s = pandas.Series(sss, index=ss, name='')
        s.plot.pie(title=f'{keyword} 科系要求 資料總數 : {count}', autopct='%.2f%%')
    plt.savefig(static_path.joinpath(f'major_req_{keyword}x{pages}'), dpi=250)
    # plt.show()
    plt.close()

def main():
    visualize_bar([()])
    return

if __name__ == '__main__':
    main()