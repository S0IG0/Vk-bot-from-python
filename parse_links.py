import grequests
from config import link_timetable
from bs4 import BeautifulSoup
import os
import time
import pickle


def parse_links(key=False):
    path = r'data\index.html'

    time_file = time.strftime('%x', time.gmtime(os.path.getmtime(path)))
    time_now = time.strftime('%x', time.gmtime(time.time()))

    if time_file != time_now or key:
        request, = grequests.map([grequests.get(link_timetable)])
        with open(path, 'w', encoding='utf-8') as file:
            print(request.text, file=file)

        with open(path, 'r', encoding='utf-8') as file:
            request = file.read()

        soup = BeautifulSoup(request, 'lxml')

        iit = soup.find_all('div', {'class': 'uk-width-1-1 uk-grid-small'})[4]
        links = [link.get('href') for link in iit.find_all('a', {'class': 'uk-link-toggle'})]
        address = iit.find('div', {'class': 'uk-width-expand@m'}).text.strip()
        name = iit.find_parent().find('a', {'class': 'uk-text-bold'}).text.strip()
        number = list(
            map(lambda x: x.text.strip().replace(' ', '_'),
                iit.find_all('div', {'class': 'uk-link-heading uk-margin-small-top'})
                )
        )

        result = {
            'name': name,
            'address': address,
            'courses': list(zip(number, links))
        }

        with open(r'data/data.pickle', 'wb') as file:
            pickle.dump(result, file)


if __name__ == '__main__':
    parse_links(True)
