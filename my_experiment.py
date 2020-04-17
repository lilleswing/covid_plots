import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
from pandas.plotting import register_matplotlib_converters

_GRID_LINE_PROPERTIES = dict(color='#bdbdbd', linestyle='--', linewidth=0.5)

US_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
GLOBAL_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
             "/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

NYT_COUNTY_URL = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
NYT_US_URL = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv"


def download_files():
    r = requests.get(US_URL)
    with open('us.csv', 'wb') as fout:
        fout.write(r.content)

    r = requests.get(GLOBAL_URL)
    with open('global.csv', 'wb') as fout:
        fout.write(r.content)

    r = requests.get(NYT_COUNTY_URL)
    with open('nyt-county.csv', 'wb') as fout:
        fout.write(r.content)

    r = requests.get(NYT_US_URL)
    with open('nyt-us.csv', 'wb') as fout:
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
    table.columns = ['date', 'deaths']
    return table


def add_delta_and_rolling_columns(df):
    df['delta'] = df['deaths'].diff()
    df['rolling'] = df.rolling(window=3, center=True).mean()['delta']
    return df


def parse_dates_nyt(df):
    df['date'] = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in df['date']]
    return df


def get_nyc_table():
    df = pd.read_csv('us.csv')
    df = df[df['Province_State'] == 'New York']
    df = df[df['Admin2'] == 'New York']
    jhu_table = table_from_dict(df.to_dict())
    jhu_table = add_delta_and_rolling_columns(jhu_table)

    df = pd.read_csv('nyt-county.csv')
    df = df[df['state'] == 'New York']
    df = df[df['county'] == 'New York City']
    nyt_table = add_delta_and_rolling_columns(df)
    nyt_table = parse_dates_nyt(nyt_table)

    nyc_df = jhu_table.merge(nyt_table, on='date', suffixes=('_jhu', '_nyt'))
    nyc_df['smooth'] = ((nyc_df['delta_jhu'] + nyc_df['delta_nyt']) / 2).rolling(window=3, center=True).mean()
    return nyc_df


def get_us_table():
    df = pd.read_csv("global.csv")
    df = df[df['Country/Region'] == 'US']
    jhu_table = table_from_dict(df.to_dict())
    jhu_table = add_delta_and_rolling_columns(jhu_table)

    df = pd.read_csv('nyt-us.csv')
    df = add_delta_and_rolling_columns(df)
    df = parse_dates_nyt(df)

    df = jhu_table.merge(df, on='date', suffixes=('_jhu', '_nyt'))
    df['smooth'] = ((df['delta_jhu'] + df['delta_nyt']) / 2).rolling(window=3, center=True).mean()
    return df


def save_plots(nyc_table, us_table):
    register_matplotlib_converters()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    fig.autofmt_xdate()

    def plot_on_axis(table, ax, title):
        ax.plot(table['date'][-20:], table['delta_jhu'][-20:], linewidth=1)
        ax.plot(table['date'][-20:], table['delta_nyt'][-20:], linewidth=1)
        ax.plot(table['date'][-20:], table['smooth'][-20:], linewidth=3)
        ax.legend(['JHU Daily Deaths', 'NYT Daily Deaths', 'Smoothed Average'])
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
