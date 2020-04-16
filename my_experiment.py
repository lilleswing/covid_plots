import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
from pandas.plotting import register_matplotlib_converters

_GRID_LINE_PROPERTIES = dict(color='#bdbdbd', linestyle='--', linewidth=0.5)

US_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
GLOBAL_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
             "/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"


def download_files():
    r = requests.get(US_URL)
    with open('us.csv', 'wb') as fout:
        fout.write(r.content)

    r = requests.get(GLOBAL_URL)
    with open('global.csv', 'wb') as fout:
        fout.write(r.content)


def table_from_dict(d):
    dates, deaths = [], []
    for k, v in d.items():
        try:
            my_date = datetime.datetime.strptime(k, '%m/%d/%y')

            dates.append(my_date)
            deaths.append(list(v.values())[0])
        except:
            pass
    table = pd.DataFrame(list(zip(dates, deaths)))
    table['delta'] = table.diff()[1]
    table['rolling'] = table.rolling(window=3, center=True).mean()['delta']
    return table


def get_nyc_table():
    df = pd.read_csv('us.csv')
    df = df[df['Province_State'] == 'New York']
    df = df[df['Admin2'] == 'New York']
    return table_from_dict(df.to_dict())


def get_us_table():
    df = pd.read_csv("global.csv")
    df = df[df['Country/Region'] == 'US']
    return table_from_dict(df.to_dict())


def save_plots(nyc_table, us_table):
    register_matplotlib_converters()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    fig.autofmt_xdate()

    def plot_on_axis(table, ax, title):
        ax.plot(table[0][-20:], table['delta'][-20:], linewidth=2)
        ax.plot(table[0][-20:], table['rolling'][-20:], linewidth=2)
        ax.legend(["Delta", "3 Day Rolling"])
        ax.grid(**_GRID_LINE_PROPERTIES)
        ax.set_title(title)

    plot_on_axis(nyc_table, ax1, "NYC Deaths Per Day")
    plot_on_axis(us_table, ax2, "US Deaths Per Day")
    plt.savefig('deaths_per_day.png')


def main():
    download_files()
    nyc_table = get_nyc_table()
    us_table = get_us_table()
    save_plots(nyc_table, us_table)


if __name__ == "__main__":
    main()
