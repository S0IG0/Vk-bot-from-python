import matplotlib.pyplot as plt
from datetime import date
import matplotlib.dates as mdates


def render(data_: list, path):
    data = data_

    events = []
    temp = [list(map(lambda x: int(x), item[0].split('.'))) for item in data]
    for day, month, year in temp:
        events.append(date(day=day, month=month, year=year))

    events.reverse()

    days = mdates.DayLocator()
    time_norm = mdates.DateFormatter('%Y-%m-%d')

    fig, ax = plt.subplots()
    ax.ticklabel_format(style='plain')

    plt.plot(events,
             [int(item[1]) for item in data],
             linestyle='-',
             linewidth=2,
             color='C4',
             marker='o',
             markersize=6,
             )

    plt.plot(events, [int(item[2]) for item in data],
             linestyle='-',
             linewidth=2,
             color='C3',
             marker='v',
             markersize=6,
             )

    plt.plot(events, [int(item[3]) for item in data],
             linestyle='-',
             linewidth=2,
             color='C2',
             marker='1',
             markersize=10,
             )

    plt.plot(events, [int(item[4]) for item in data],
             linestyle='-',
             linewidth=2,
             color='C1',
             marker='*',
             markersize=10,
             )
    ax.legend(['Активных', 'Вылечено', 'Умерло', 'Случаев'])
    plt.grid(True)
    ax.xaxis.set_major_formatter(time_norm)
    ax.xaxis.set_minor_locator(days)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path, dpi=200)


if __name__ == '__main__':
    pass
