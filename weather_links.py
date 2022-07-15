import grequests
from config import token_weather, WEEK
from yandex_translate import translate
import PIL.Image as Image
import datetime

from pprint import pprint

INTERVALS = ['Утро', 'День', 'Вечер', 'Ночь', ]


def merger_img(paths: list, path_out: str) -> str:
    img = Image.new('RGBA', (60 * len(paths), 60))
    img_all = []
    for index, path in enumerate(paths):
        img_all.append(Image.open(path).resize((60, 60)))
        img.paste(img_all[index], (60 * index, 0))
    img.save(path_out)

    return path_out


def type_wind(digit: float) -> str:
    if 0 <= digit <= 0.2:
        digit = 'штиль'
    elif 0.3 <= digit <= 1.5:
        digit = 'тихий'
    elif 1.5 <= digit <= 3.3:
        digit = 'лёгкий'
    elif 3.3 <= digit <= 5.4:
        digit = 'слабый'
    elif 5.4 <= digit <= 7.9:
        digit = 'умеренный'
    elif 7.9 <= digit <= 10.7:
        digit = 'свежий'
    elif 10.7 <= digit <= 13.8:
        digit = 'сильный'
    elif 13.8 <= digit <= 17.1:
        digit = 'крепкий'
    elif 17.1 <= digit <= 20.7:
        digit = 'очень крепкий'
    elif 20.7 <= digit <= 24.4:
        digit = 'шторм'
    elif 24.4 <= digit <= 28.4:
        digit = 'сильный шторм'
    elif 28.4 <= digit <= 32.6:
        digit = 'жестокий шторм'
    else:
        digit = 'ураган'

    return digit


def NSEW(deg: int) -> str:
    if deg in (list(range(348, 361)) + list(range(0, 12))):
        deg = 'север'
    elif deg in range(12, 34):
        deg = "северо-северо-восток"
    elif deg in range(34, 57):
        deg = 'северо-восток'
    elif deg in range(57, 79):
        deg = 'восток-северо-восток'
    elif deg in range(79, 102):
        deg = 'восток'
    elif deg in range(102, 124):
        deg = 'восток-юго-восток'
    elif deg in range(124, 147):
        deg = 'юго-восток'
    elif deg in range(147, 169):
        deg = 'юго-юго-восток'
    elif deg in range(169, 192):
        deg = 'юг'
    elif deg in range(192, 214):
        deg = 'юго-юго-запад'
    elif deg in range(214, 237):
        deg = 'юго-запад'
    elif deg in range(237, 259):
        deg = 'запад-юго-запад'
    elif deg in range(259, 282):
        deg = 'запад'
    elif deg in range(282, 304):
        deg = 'запад-северо-запад'
    elif deg in range(304, 327):
        deg = 'северо-запад'
    elif deg in range(327, 348):
        deg = 'северо-северо-запад'

    return deg


def parse_weather_def_now(city='moscow', units='metric', lang='en') -> [str, str]:
    city = translate(translate(city, 'en'), 'ru')
    link = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={token_weather}&units={units}&lang={lang}'
    request, = grequests.map([grequests.get(link)])
    data = request.json()
    text = 'Город не найден'
    if data['cod'] == 200:
        png = f'http://openweathermap.org/img/wn/{data["weather"][0]["icon"]}.png'
        request_img, = grequests.map([grequests.get(png)])
        with open(r'data/weather_img/now/photo.png', 'wb') as file:
            file.write(request_img.content)

        deg = NSEW(data["wind"]["deg"])
        type_ = type_wind(float(data["wind"]["speed"]))
        text = translate(translate(f'Погода в {data["name"]} {data["weather"][0]["main"].lower()}.\n'
                                   f'On the street {data["weather"][0]["description"]}.\n'
                                   f'Температура колеблется от {data["main"]["temp_min"]} '
                                   f'до {data["main"]["temp_max"]}°C.\n'
                                   f'Давление {(data["main"]["pressure"] * 100 * 0.007501):.0f} мм рт.ст.\n'
                                   f'Влажность {data["main"]["humidity"]}%\n'
                                   f'Ветер:\n'
                                   f'ᅠ* направление: {deg}, \n'
                                   f'ᅠ* скорость: {data["wind"]["speed"]} м/с ({type_}).',
                                   'en'), 'ru')
    return text, 'data/weather_img/now/photo.png'


def parse_weather_def_day(city='moscow', units='metric', lang='en', cnt=8):
    city = translate(translate(city, 'en'), 'ru')
    link = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units={units}&lang={lang}&cnt={cnt}&appid={token_weather}'
    request, = grequests.map([grequests.get(link)])
    data = request.json()
    text = 'Город не найден'
    paths = []
    if int(data['cod']) == 200:
        text = ''
        for index, name in zip(([_ for _ in range(2, cnt, 2)] + [cnt - 1, ]), INTERVALS):
            deg = NSEW(data['list'][index]["wind"]["deg"])
            type_ = type_wind(float(data['list'][index]["wind"]["speed"]))
            text += name + '\n'
            text += (translate(translate(f"ᅠ- {data['list'][index]['weather'][0]['description'].capitalize()}, "
                                         f"температура:"
                                         f" {data['list'][index]['main']['temp_min']}"
                                         f" - {data['list'][index]['main']['temp_max']}°C.\n"
                                         f'ᅠ- Давление'
                                         f' {(data["list"][index]["main"]["pressure"] * 100 * 0.007501):.0f} '
                                         f'мм рт.ст.\n'
                                         f'ᅠ- Влажность {data["list"][index]["main"]["humidity"]}%\n'
                                         f'ᅠ- Ветер:\n'
                                         f'ᅠᅠᅠ* направление: {deg}, \n'
                                         f'ᅠᅠᅠ* скорость: {data["list"][index]["wind"]["speed"]} м/с ({type_}).\n',
                                         'en'), 'ru'))

            png = f'http://openweathermap.org/img/wn/{data["list"][index]["weather"][0]["icon"]}.png'
            request_img, = grequests.map([grequests.get(png)])
            with open(rf'data/weather_img/today/{name}.png', 'wb') as file:
                paths.append(rf'data/weather_img/today/{name}.png')
                file.write(request_img.content)

    return text, merger_img(paths, r'data/weather_img/today/photo.png')


def parse_weather_def_tomorrow(city='moscow', units='metric', lang='en', cnt=16):
    city = translate(translate(city, 'en'), 'ru')
    link = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units={units}&lang={lang}&cnt={cnt}&appid={token_weather}'
    request, = grequests.map([grequests.get(link)])
    data = request.json()
    text = 'Город не найден'
    paths = []
    if int(data['cod']) == 200:
        text = ''
        for index, name in zip(([_ for _ in range(10, cnt, 2)] + [cnt - 1, ]), INTERVALS):
            deg = NSEW(data['list'][index]["wind"]["deg"])
            type_ = type_wind(float(data['list'][index]["wind"]["speed"]))
            text += name + '\n'
            text += (translate(translate(f"ᅠ- {data['list'][index]['weather'][0]['description'].capitalize()}, "
                                         f"температура:"
                                         f" {data['list'][index]['main']['temp_min']}"
                                         f" - {data['list'][index]['main']['temp_max']}°C.\n"
                                         f'ᅠ- Давление'
                                         f' {(data["list"][index]["main"]["pressure"] * 100 * 0.007501):.0f} '
                                         f'мм рт.ст.\n'
                                         f'ᅠ- Влажность {data["list"][index]["main"]["humidity"]}%\n'
                                         f'ᅠ- Ветер:\n'
                                         f'ᅠᅠᅠ* направление: {deg}, \n'
                                         f'ᅠᅠᅠ* скорость: {data["list"][index]["wind"]["speed"]} м/с ({type_}).\n',
                                         'en'), 'ru'))

            png = f'http://openweathermap.org/img/wn/{data["list"][index]["weather"][0]["icon"]}.png'
            request_img, = grequests.map([grequests.get(png)])
            with open(rf'data/weather_img/tomorrow/{name}.png', 'wb') as file:
                paths.append(rf'data/weather_img/tomorrow/{name}.png')
                file.write(request_img.content)

    return text, merger_img(paths, r'data/weather_img/tomorrow/photo.png')


def parse_weather_def_5_days(city='moscow', units='metric', lang='en', cnt=40):
    city = translate(translate(city, 'en'), 'ru')
    link = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units={units}&lang={lang}&cnt={cnt}&appid={token_weather}'
    request, = grequests.map([grequests.get(link)])
    data = request.json()
    text = 'Город не найден'
    paths = []
    if int(data['cod']) == 200:
        text = ''
        for index in range(0, cnt, 8):
            index += 5
            year, month, day = (data['list'][index]['dt_txt'].split()[0].split('-'))
            temp = datetime.datetime(year=int(year), month=int(month), day=int(day))
            name = WEEK[temp.weekday() + 1]

            text += name + '\n'
            text += (translate(translate(f"ᅠ- Днем: {data['list'][index - 1]['weather'][0]['description'].capitalize()}, "
                                         f"{data['list'][index - 1]['main']['temp_max']}°C.\n"
                                         f"ᅠ- Ночью: {data['list'][index + 2]['weather'][0]['description'].capitalize()}, "
                                         f"{data['list'][index + 2]['main']['temp_max']}°C.\n",
                                         'en'), 'ru'))

            png = f'http://openweathermap.org/img/wn/{data["list"][index]["weather"][0]["icon"]}.png'
            request_img, = grequests.map([grequests.get(png)])
            with open(rf'data/weather_img/5_days/{name}.png', 'wb') as file:
                paths.append(rf'data/weather_img/5_days/{name}.png')
                file.write(request_img.content)

    return text, merger_img(paths, r'data/weather_img/5_days/photo.png')


def parse_weather_now(*args):
    return parse_weather_def_now(*args)


def parse_weather_day(*args):
    return parse_weather_def_day(*args)


def parse_weather_day_tomorrow(*args):
    return parse_weather_def_tomorrow(*args)


def parse_weather_day_5_days(*args):
    return parse_weather_def_5_days(*args)


if __name__ == '__main__':
    # print(parse_weather_now())
    # parse_weather_def_tomorrow()
    print(parse_weather_def_5_days()[0])
