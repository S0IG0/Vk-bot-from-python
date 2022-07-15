import pickle
import grequests
import time
import os
import openpyxl
import copy
from parse_links import parse_links
from config import WEEK

path = r'data\table\{}.xlsx'
path_pickle = r'data\pickle\{}.pickle'

time_now = time.strftime('%x', time.gmtime(time.time()))


def parse_timetable(number_course: int, key=False):
    parse_links()
    with open(r'data\data.pickle', 'rb') as file:
        data = pickle.load(file)

    name, link = data['courses'][number_course - 1]
    time_file = time.strftime('%x', time.gmtime(os.path.getmtime(path.format(name))))

    if time_file != time_now or key:
        request, = grequests.map([grequests.get(link)])
        with open(path.format(name), 'wb') as file:
            file.write(request.content)

        book = openpyxl.load_workbook(path.format(name), read_only=True)
        sheet = book.active

        num_cols = sheet.max_column  # количество столбцов

        couples = []
        for index in range(4, 4 * 4, 2):
            number = sheet[index][1].value
            start = sheet[index][2].value
            end = sheet[index][3].value
            couples.append({
                'number': number,
                'start': start,
                'end': end,
                'week_1': dict(subject='', type='', teacher='', auditorium='', link=''),
                'week_2': dict(subject='', type='', teacher='', auditorium='', link=''),
            })

        temp = dict()
        for index in range(4, 4 + 12 * 5 + 1, 12):
            temp[sheet[index][0].value] = {'number_week': index // 12 + 1, 'couples': copy.deepcopy(couples)}

        info_all_group = dict()

        count = 1
        for col in range(5, num_cols, 5):
            group_name = sheet[2][col].value
            if count % 4 != 0 and group_name is not None:
                info_all_group[group_name] = copy.deepcopy(temp)

                for row in range(4, 12 * 6 + 4):
                    week = (row % 2) + 1
                    couple = ((row - 4) % 12) // 2
                    week_name = WEEK[((row - 4) // 12) + 1]
                    subject = sheet[row][col].value
                    type_ = ''
                    teacher = ''
                    auditorium = ''
                    link = ''

                    if subject is not None and (True in [letter.isalpha() for letter in subject]):
                        subject = subject.strip().replace('\n', '')
                        type_ = str(sheet[row][col + 1].value).replace('\n', ' \\ ')
                        teacher = str(sheet[row][col + 2].value).split('\n')[0]
                        auditorium = str(sheet[row][col + 3].value).replace('\n', ' ')
                        link = str(sheet[row][col + 4].value)
                    else:
                        subject = ''

                    info_all_group[group_name][week_name]['couples'][couple][f'week_{week}']['auditorium'] = auditorium
                    info_all_group[group_name][week_name]['couples'][couple][f'week_{week}']['link'] = link
                    info_all_group[group_name][week_name]['couples'][couple][f'week_{week}']['subject'] = subject
                    info_all_group[group_name][week_name]['couples'][couple][f'week_{week}']['teacher'] = teacher
                    info_all_group[group_name][week_name]['couples'][couple][f'week_{week}']['type'] = type_

            count += 1

        with open(path_pickle.format(name), 'wb') as file:
            pickle.dump(info_all_group, file)


if __name__ == '__main__':
    for i in range(4):
        parse_timetable(i + 1, key=False)
