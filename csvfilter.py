import pandas, pathlib

def csv_filter(show_column_index_list=None, keyword='', pages=''):
    if show_column_index_list is None:
        return

    original_csv_path = pathlib.Path.cwd().joinpath('static').joinpath(f'104_result_{keyword}x{pages}.csv')
    original_csv = pandas.read_csv(original_csv_path, names=[i for i in range(len(show_column_index_list))])     # 設headers待會好做篩選

    wanted_index =[]         # 如果是 'on'(有選取的 就把index記在 wanted_index)
    for i in range(len(show_column_index_list)):
        if show_column_index_list[i] == 'on':
            wanted_index.append(i)

    filtered_csv = original_csv[wanted_index]   # 建新的篩選過的 dataframe

    filtered_csv_path = pathlib.Path.cwd().joinpath('static').joinpath(f'104_result_filtered_{keyword}x{pages}.csv')
    filtered_csv.to_csv(filtered_csv_path, header=False, index=False, encoding="utf_8_sig")  # 存檔

    return filtered_csv

def main():
    return

if __name__ == '__main__':
    main()