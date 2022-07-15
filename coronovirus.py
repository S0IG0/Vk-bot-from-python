from bs4 import BeautifulSoup
import grequests
from render import render


def parse_russia():
    request, = grequests.map([grequests.get('https://coronavirusstat.ru/country/russia/')])
    soup = BeautifulSoup(request.text, 'lxml')
    # today = soup.find('tbody').find_all('tr')[0]
    today = []
    data = []

    for item in soup.find('tbody').find_all('tr')[0]:
        if item.text.split():
            today.append(item.text.split())

    date, *statistics = zip([item.text for item in soup.find('thead').find_all('th')], today)

    text = f'По состоянию на {date[1][0]}\n'
    for item in statistics:
        text += f'{item[0]}: {item[1][0]}, ({item[1][1]})\n'

    for day in soup.find('tbody').find_all('tr'):
        temp = []
        for item in day:
            if item.text.split():
                temp.append(item.text.split()[0])
        data.append(temp)

    render(data, r'data/plot/data.png')
    return text, r'data/plot/data.png'


def parse_coronavirus(key: str):
    request, = grequests.map([grequests.get('https://coronavirusstat.ru/country/russia/')])
    soup = BeautifulSoup(request.text, 'lxml')

    names = soup.find_all('div', {'class': 'row border border-bottom-0 c_search_row'})
    dict_ = dict()
    for name in names:
        dict_[name.find('a').text.split()[0].lower()] = {
            'link': 'https://coronavirusstat.ru' + name.find('a').get('href'),
            'full-name': name.find('a').text,
        }

    if key in dict_.keys():
        request, = grequests.map([grequests.get(dict_[key]['link'])])
        soup = BeautifulSoup(request.text, 'lxml')
        today = []
        data = []

        for item in soup.find('tbody').find_all('tr')[0]:
            if item.text.split():
                today.append(item.text.split())

        date, *statistics = zip([item.text for item in soup.find('thead').find_all('th')], today)

        text = dict_[key]['full-name'] + "\n"
        text += f'По состоянию на {date[1][0]}\n'
        for item in statistics:
            text += f'{item[0]}: {item[1][0]}, ({item[1][1]})\n'

        for day in soup.find('tbody').find_all('tr'):
            temp = []
            for item in day:
                if item.text.split():
                    temp.append(item.text.split()[0])
            data.append(temp)

        render(data, r'data/plot/data.png')

        return text, r'data/plot/data.png'

    else:
        return


if __name__ == '__main__':
    pass

# row border border-bottom-0 c_search_row
