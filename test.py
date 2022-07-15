import copy
import time

from config import START_EDUCATION, WEEK, PARITY_WEEK, COUPLES
import pickle
import imgkit
import datetime
import math
from numba import njit
import multiprocessing

from html2image import Html2Image

path_pickle = r'data\pickle\{}_курс.pickle'


def check_in_keys(group: str) -> bool:
    all_group = []
    for number in range(4):
        with open(path_pickle.format(number + 1), 'rb') as file:
            all_group += pickle.load(file).keys()

    return group in all_group


def check_in_keys_teachers(teacher: str) -> bool:
    with open(r'data/pickle/teachers/teachers.pickle', 'rb') as file:
        teachers = pickle.load(file).keys()
    return teacher in teachers


def get_schedule(group: str) -> dict:
    for number in range(4):
        with open(path_pickle.format(number + 1), 'rb') as file:
            group_dict = pickle.load(file)
            if group in group_dict.keys():
                break
    return group_dict[group]


def get_teacher(teacher: str) -> dict:
    with open(r'data/pickle/teachers/teachers.pickle', 'rb') as file:
        teachers = pickle.load(file)
    return teachers[teacher]


def get_teacher_list(teacher: str) -> list:
    temp = []
    with open(r'data/pickle/teachers/teachers.pickle', 'rb') as file:
        teachers = pickle.load(file)

    for name in teachers:
        if teacher in name.lower():
            temp.append(name)

    return temp


def create_image_teachers(name_group: str, key_week_1: str, name_week_=None):
    with open(r"template/teacher/start.txt", "r", encoding='utf-8') as file:
        start = file.read()
    with open(r"template/teacher/end.txt", "r", encoding='utf-8') as file:
        end = file.read()
    group = get_teacher(name_group)

    if name_week_ is None:
        for name_week in list(WEEK.values())[:-1]:
            sections = ''
            for item in group[name_week]["couples"]:
                section = f"<tr><td>{item['number']}</td>\n" \
                          f"<td>{item['start']}</td>\n" \
                          f"<td>{item['end']}</td>\n" \
                          f"<td>{item[key_week_1]['subject']}</td>\n" \
                          f"<td>{item[key_week_1]['type']}</td>\n" \
                          f"<td>{item[key_week_1]['teacher']}</td>\n" \
                          f"<td>{item[key_week_1]['auditorium']}</td>\n" \
                          f"<td>{item[key_week_1]['link']}</td></tr>\n"

                sections += section
            with open(r"template/teacher/table.html", "w", encoding='utf-8') as file:
                file.write(start + sections + end)
            render_table(r"template/teacher/table.html", fr'data/image_data/teachers/{name_week}.png',
                         r'template/teacher/style.css')
    else:
        sections = ''
        for item in group[name_week_]["couples"]:
            section = f"<tr><td>{item['number']}</td>\n" \
                      f"<td>{item['start']}</td>\n" \
                      f"<td>{item['end']}</td>\n" \
                      f"<td>{item[key_week_1]['subject']}</td>\n" \
                      f"<td>{item[key_week_1]['type']}</td>\n" \
                      f"<td>{item[key_week_1]['teacher']}</td>\n" \
                      f"<td>{item[key_week_1]['auditorium']}</td>\n" \
                      f"<td>{item[key_week_1]['link']}</td></tr>\n"

            sections += section
        with open(r"template/teacher/table.html", "w", encoding='utf-8') as file:
            file.write(start + sections + end)
        render_table(r"template/teacher/table.html", fr'data/image_data/teachers/{name_week_}.png',
                     r'template/teacher/style.css')


def create_image(name_group: str, key_week_1: str, name_week_=None):
    with open(r"template/start.txt", "r", encoding='utf-8') as file:
        start = file.read()
    with open(r"template/end.txt", "r", encoding='utf-8') as file:
        end = file.read()
    group = get_schedule(name_group)

    if name_week_ is None:
        for name_week in list(WEEK.values())[:-1]:
            sections = ''
            for item in group[name_week]["couples"]:
                section = f"<tr><td>{item['number']}</td>\n" \
                          f"<td>{item['start']}</td>\n" \
                          f"<td>{item['end']}</td>\n" \
                          f"<td>{item[key_week_1]['subject']}</td>\n" \
                          f"<td>{item[key_week_1]['type']}</td>\n" \
                          f"<td>{item[key_week_1]['teacher']}</td>\n" \
                          f"<td>{item[key_week_1]['auditorium']}</td>\n" \
                          f"<td>{item[key_week_1]['link']}</td></tr>\n"

                sections += section
            with open(r"template/table.html", "w", encoding='utf-8') as file:
                file.write(start + sections + end)
            render_table(r"template/table.html", fr'data/image_data/{name_week}.png', r'template/style.css')
    else:
        sections = ''
        for item in group[name_week_]["couples"]:
            section = f"<tr><td>{item['number']}</td>\n" \
                      f"<td>{item['start']}</td>\n" \
                      f"<td>{item['end']}</td>\n" \
                      f"<td>{item[key_week_1]['subject']}</td>\n" \
                      f"<td>{item[key_week_1]['type']}</td>\n" \
                      f"<td>{item[key_week_1]['teacher']}</td>\n" \
                      f"<td>{item[key_week_1]['auditorium']}</td>\n" \
                      f"<td>{item[key_week_1]['link']}</td></tr>\n"

            sections += section
        with open(r"template/table.html", "w", encoding='utf-8') as file:
            file.write(start + sections + end)
        render_table(r"template/table.html", fr'data/image_data/{name_week_}.png', r'template/style.css')


# def create_image_all_week(name_group: str, key_week_1: str):
#     temp = multiprocessing.Process(target=f, args=(name_group, key_week_1))
#     temp.start()
#     temp.join()
#
#
# def f(name_group: str, key_week_1: str):
#     process = []
#     for name in list(WEEK.values())[:-1]:
#         temp = multiprocessing.Process(target=create_image, args=(name_group, key_week_1, name))
#         process.append(temp)
#         temp.start()


def render_table(path_in: str, path_out: str, style_path: str):
    try:
        options = {
            'quality': '100'
        }
        imgkit.from_file(path_in, path_out, css=style_path, options=options)
    except OSError:
        pass


def get_current_week() -> int:
    return math.ceil((datetime.date.today() - START_EDUCATION).days / 7)


def all_teacher():
    template = dict()
    for key, value in list(WEEK.items())[:-1]:
        template[value] = {
            'number_week': key,
            'couples': [{
                'number': i + 1,
                'start': COUPLES[i + 1][0],
                'end': COUPLES[i + 1][1],
                'week_1': dict(subject='', type='', teacher='', auditorium='', link=''),
                'week_2': dict(subject='', type='', teacher='', auditorium='', link=''),
            } for i in range(6)]
        }

    courses = []
    teachers = []
    for number in range(4):
        with open(path_pickle.format(number + 1), 'rb') as file:
            courses.append(pickle.load(file))

    for course in courses:
        for group in course:
            for name_week in course[group]:
                for couple in course[group][name_week]['couples']:
                    for key_week in PARITY_WEEK.values():
                        teacher = couple[key_week]['teacher']
                        if teacher != '' and teacher != 'None':
                            teachers.append(teacher)
    teachers = list(set(teachers))
    teachers_dict = dict()

    for teacher in teachers:
        teachers_dict[teacher] = copy.deepcopy(template)

    for course in courses:
        for group in course:
            for name_week in course[group]:
                for index, couple in enumerate(course[group][name_week]['couples']):
                    for key_couple in couple:
                        if key_couple in ['week_1', 'week_2']:
                            teacher = couple[key_couple]['teacher']
                            if teacher in teachers_dict:
                                for key in couple[key_couple]:
                                    if key == 'teacher':
                                        val = group
                                    else:
                                        val = couple[key_couple][key]
                                    teachers_dict[teacher][name_week]['couples'][index][key_couple][key] = val
    print(teachers_dict.keys())
    with open(r'data/pickle/teachers/teachers.pickle', 'wb') as file:
        pickle.dump(teachers_dict, file)


if __name__ == '__main__':
    x = range(200)

