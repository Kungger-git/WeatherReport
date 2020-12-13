import requests
from bs4 import BeautifulSoup as soup
from pathlib import Path
import pandas as pd


def main():
    name_of_file_one = 'td_forecast.csv'
    name_of_file_two = 'hr_forecast.csv'
    name_of_file_three = 'dl_forecast.csv'
    checkFile(name_of_file_one, name_of_file_two, name_of_file_three)

    try:
        req = requests.get(
            'https://weather.com/', timeout=1
        )
        req.raise_for_status()
        page_soup = soup(req.text, 'html.parser')
        getInfo(page_soup)
        writeFile(name_of_file_one, name_of_file_two,
                name_of_file_three, page_soup)
    except requests.exceptions.HTTPError as err:
        print('Something went wrong! ', err)


def getInfo(locator):
    # prints out the region
    header = [header.text.strip() for header in locator.findAll(
        'h1', {'class': 'CurrentConditions--location--1Ayv3'})[0:]]
    for ent in header[0:]:
        print('\n\n' + ent)

    # prints out the time
    time = [time.text.strip() for time in locator.findAll(
        'div', {'class': 'CurrentConditions--timestamp--1SWy5'})[0:]]
    for tm in time[0:]:
        print(tm)

    # gets current temp and situation
    for container in locator.findAll('div', {'class': 'CurrentConditions--primary--3xWnK'})[0:]:
        tmp, stn = container.find('span').text, container.find('div').text
        print('\n\n' + tmp + ' = ' + stn + ' weather')

    # gets chance of rain
    for chance in locator.findAll('div', {'data-testid': 'precipPhrase'})[0:]:
        print('\n' + chance.text + '\n\n')

    # gets air quality index
    for qualities in locator.findAll('div', {'class': 'AirQuality--AirQualityCard--Ipx5M'})[0:]:
        idx, rtg, sty = qualities.find('text').text, qualities.find(
            'span').text, qualities.find('p').text
        print('Level: ' + idx + ' = ' + rtg + '\nSeverity: ' + sty + '\n\n')


def checkFile(filename_one, filename_two, filename_three):
    try:
        if Path(filename_one).exists() and Path(filename_two).exists() and Path(filename_three).exists():
            print('\n{' + filename_one + ' and ' + filename_two + ' and ' +
                  filename_three + '} exists... Proceeding to Data Collection.')
    except FileNotFoundError as ioerr:
        print('Directory/File does not exist! ', ioerr)
    

def writeFile(filename_one, filename_two, filename_three, locator):
    with open(filename_one, 'w') as f:
        headers = 'Morning, Afternoon, Evening, Overnight\n'
        f.write(headers)
        for info in locator.findAll('div', {'class': 'TodayWeatherCard--TableWrapper--13jpa'})[0:]:
            temps = [temps.text.strip().replace('°', '') for temps in info.findAll(
                'span', {'data-testid': 'TemperatureValue'})[0:]]
            mo, af, ev, ov = temps[0], temps[1], temps[2], temps[3]
            f.write(mo + 'C,' + af + 'C,' + ev + 'C,' + ov + 'C\n')
        f.close()
        update1 = pd.read_csv(filename_one)
        pd.set_option('display.max_rows', None)
        section_title = locator.findAll('h2', {'class':'Card--cardHeading--3et4e'})[0]
        print('Updated Data Frames:\n\n' + section_title.text + ': \n')
        print(update1)

    with open(filename_two, 'w') as f:
        headers = 'Now, Hour 1, Hour 2, Hour 3, Hour 4\n'
        f.write(headers)
        for container in locator.findAll('div', {'class': 'HourlyWeatherCard--TableWrapper--2kboH'})[0:]:
            time = [time.text.strip() for time in container.findAll(
                'span', {'class': 'Ellipsis--ellipsis--lfjoB'})[0:]]
            nw, st, nd, rd, th = time[0], time[1], time[2], time[3], time[4]

            tmp = [tmp.text.strip().replace('°', '') for tmp in container.findAll(
                'span', {'data-testid': 'TemperatureValue'})[0:]]
            nwC, stC, ndC, rdC, thC = tmp[0], tmp[1], tmp[2], tmp[3], tmp[4]

            rCh = [rCh.text.strip() for rCh in container.findAll(
                'span', {'class': 'Column--precip--2H5Iw'})[0:]]
            nwP, stP, ndP, rdP, thP = rCh[0], rCh[1], rCh[2], rCh[3], rCh[4]
            f.write(nw + ',' + st + ',' + nd + ',' + rd + ',' + th + '\n')
            f.write(nwC + 'C,' + stC + 'C,' + ndC +
                    'C,' + rdC + 'C,' + thC + 'C\n')
            f.write(nwP + ',' + stP + ',' + ndP + ',' + rdP + ',' + thP + '\n')
        f.close()
        update2 = pd.read_csv(filename_two)
        pd.set_option('display.max_rows', None)
        section_title = locator.findAll('h2', {'class':'Card--cardHeading--3et4e'})[2]
        print('\n\n' + section_title.text + ': \n')
        print(update2)

    with open(filename_three, 'w') as f:
        headers = 'Today, Day 1, Day 2, Day 3, Day 4\n'
        f.write(headers)
        for container in locator.findAll('div', {'class': 'DailyWeatherCard--TableWrapper--12r1N'})[0:]:
            dates = [dates.text.strip() for dates in container.findAll(
                'span', {'class': 'Ellipsis--ellipsis--lfjoB'})[0:]]
            td, dst, dnd, drd, dth = dates[0], dates[1], dates[2], dates[3], dates[4]

            high_temp = [high_temp.text.strip().replace('°', '') for high_temp in container.findAll(
                'div', {'class': 'Column--temp--2v_go'})[0:]]
            ttd, tst, tnd, trd, tth = high_temp[0], high_temp[1], high_temp[2], high_temp[3], high_temp[4]

            low_temp = [low_temp.text.strip().replace('°', '') for low_temp in container.findAll(
                'div', {'class': 'Column--tempLo--19O32'})[0:]]
            ltd, lst, lnd, lrd, lth = low_temp[0], low_temp[1], low_temp[2], low_temp[3], low_temp[4]

            prain = [prain.text.strip() for prain in container.findAll(
                'div', {'class': 'Column--precip--2H5Iw'})[0:]]
            ptd, pst, pnd, prd, pth = prain[0], prain[1], prain[2], prain[3], prain[4]
            f.write(td + ',' + dst + ',' + dnd + ',' + drd + ',' + dth + '\n')
            f.write(ttd + 'C,' + tst + 'C,' + tnd +
                    'C,' + trd + 'C,' + tth + 'C\n')
            f.write(ltd + 'C,' + lst + 'C,' + lnd +
                    'C,' + lrd + 'C,' + lth + 'C\n')
            f.write(ptd + ',' + pst + ',' + pnd + ',' + prd + ',' + pth + '\n')
        f.close()
        update3 = pd.read_csv(filename_three)
        pd.set_option('display.max_rows', None)
        section_title = locator.findAll('h2', {'class':'Card--cardHeading--3et4e'})[3]
        print('\n\n' + section_title.text + ': \n')
        print(update3)


if __name__ == '__main__':
    main()
