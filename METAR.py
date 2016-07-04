"""
Module accepts 3 or 4 letter input from user and attempts to fetch METAR info from flightaware.com
"""
import re
import sys
import time
from bs4 import BeautifulSoup
import requests


def airnav(needsprompt=True):
    """
    Prompts user for airport ID and verifies that airnav.com has that ID
    :return: Text of a webpage
    """
    if needsprompt:
        continue_ = True
        while continue_:
            airport = raw_input("Enter a US airport ID or raw METAR: ")
            if len(airport) <= 4:
                airport = airport.upper()
                url = "http://airnav.com/airport/".format(airport)
                if 'GOING' in requests.get(url).text:
                    print
                    continue_ = False
                    soup = BeautifulSoup(airnav(), "lxml")
                    raw_metar = soup.find(string='METAR').parent.parent.parent.find('table').find('tr').text
                    metar = raw_metar.encode('latin-1').replace('\xa0', ' ')
                    raw_title = soup.title.encode('latin-1')
                    airp = raw_title[22:-8].strip()
                    get_metar(metar, airp)
                else:
                    print '\tError: {} is not a valid US airport ID.'.format(airport.upper())
            else:
                continue_ = False
                print
                metar = airport.strip()
                airp = metar[:metar.find(' ')]
                get_metar(metar, airp)
    else:
        url = "http://airnav.com/airport/".format(sys.argv[1])
        if 'GOING' in requests.get(url).text:
            print
            soup = BeautifulSoup(airnav(), "lxml")
            raw_metar = soup.find(string='METAR').parent.parent.parent.find('table').find('tr').text
            metar = raw_metar.encode('latin-1').replace('\xa0', ' ')
            raw_title = soup.title.encode('latin-1')
            airp = raw_title[22:-8].strip()
            get_metar(metar, airp)
        else:
            print '\tError: {} is not a valid US airport ID.'.format(sys.argv[1].upper())


def flightaware(needsprompt=True):
    """
    Parse FlightAware for a current airport's METAR
    :return: Text of a webpage
    """
    if needsprompt:
        continue_ = True
        while continue_:
            airport = raw_input("Enter an IATA/ICAO airport ID or raw METAR: ")
            if len(airport) <= 4:
                airport = airport.upper()
                url = "http://flightaware.com/resources/airport/{}/weather".format(airport)
                if 'Unknown or Invalid Airport Code' not in requests.get(url).text:
                    print
                    continue_ = False
                    soup = BeautifulSoup(requests.get(url).text, "lxml")
                    placeholder = soup.find('tr', class_='smallrow1 hint ').attrs
                    raw_metar = placeholder['title']
                    metar = raw_metar.encode('latin-1').replace('\xa0', ' ')
                    raw_title = soup.title.text
                    airp = raw_title[:raw_title.index(' Weather')].strip()
                    try:
                        get_metar(metar, airp)
                    except AttributeError:
                        print 'Sorry, couldn\'t parse the METAR. Here\'s the raw METAR: {}'.format(metar)
                    except ValueError:
                        print 'Sorry, couldn\'t parse the METAR. Here\'s the raw METAR: {}'.format(metar)
                else:
                    print '\tError: {} is not a valid airport ID.'.format(airport.upper())
            else:
                print
                continue_ = False
                metar = airport.strip()
                airp = metar[:metar.find(' ')]
                get_metar(metar, airp)
    else:
        url = "http://flightaware.com/resources/airport/{}/weather".format(sys.argv[1])
        if 'Unknown or Invalid Airport Code' not in requests.get(url).text:
            soup = BeautifulSoup(requests.get(url).text, "lxml")
            placeholder = soup.find('tr', class_='smallrow1 hint ').attrs
            raw_metar = placeholder['title']
            metar = raw_metar.encode('latin-1').replace('\xa0', ' ')
            raw_title = soup.title.text
            airp = raw_title[:raw_title.index(' Weather')].strip()
            get_metar(metar, airp)
        else:
            print '\tError: {} is not a valid US airport ID.'.format(sys.argv[1].upper())


def c_to_f(number):
    """
    Given an integer in degrees C, converts to degrees F
    :param number: Integer in degrees C
    :return: Integer in degrees F
    """
    try:
        number = int(number)
        return int(round(number * 9 / 5.0, 0)) + 32
    except ValueError:
        return 'N/A'


def get_metar(metar, airp):
    """
    Prompts user for 4 letter airport code, and prints METAR information to console
    :return: None
    """
    date, time_, winddirection, windspeed, vis, clouds, temp, \
    dewpoint, altim, precip, obsf, metar = parse_metar(metar)

    if time.localtime().tm_isdst == 0:
        timevar = 5
    else:
        timevar = 4

    if int(time_[:time_.index(':')]) - timevar < 0:
        local = str(int(time_[:time_.index(':')]) - timevar + 12) + time_[time_.index(':'):]
    else:
        local = str(int(time_[:time_.index(':')]) - timevar) + time_[time_.index(':'):]
    if date[1] == '1':
        date += 'st'
    elif date[1] == '2':
        date += 'nd'
    elif date[1] == '3':
        date += 'rd'
    elif date[0:2] == ('13' or '12' or '11'):
        date += 'th'
    else:
        date += 'th'
    if date[0] == '0':
        date = date.replace("0", '')

    if 'G' in windspeed:
        gust = 'gusting {} knots'.format(windspeed[windspeed.index('G') + 1:])
        windspeed = windspeed[:windspeed.index('G')]
    else:
        gust = ''
    if windspeed == 'None':
        windprint = 'None'
    elif winddirection == 'Variable':
        windprint = 'Light and variable'
    else:
        windprint = '{0} at {1} knots'.format(winddirection, windspeed)

    cloudlist = []
    cloud_info = {'BKN': 'Broken', 'OVC': 'Overcast', 'FEW': 'Few',
                  'CLR': 'Clear', 'SCT': 'Scattered'}
    for elem in clouds:
        if any(elem[0:3] in cloud_info.keys() for elem in clouds):
            if 'CLR' in elem[0:3]:
                info = cloud_info[elem[0:3]]
            else:
                info = '{} clouds at {} feet'.format(cloud_info[elem[0:3]], int(elem[3:]) * 100)
            cloudlist.append(info)
    allclouds = '\n\t'.join(elem for elem in cloudlist)
    if allclouds == '':
        allclouds = 'None'

    preciplist = []
    precip_info = {'RA': 'rain', 'SN': 'snow', 'IC': 'ice', 'GR': 'hail',
                   'DZ': 'drizzle', 'SG': 'snow grains', 'PE': 'ice pellets', 'GS': 'small hail',
                   'UP': 'unknown precipitation', 'TSRA': 'thundershowers', 'DU': 'dust'}
    if precip:
        for elem in precip:
            if len(elem) == 2:
                before = "Moderate "
            elif '-' in elem:
                before = "Light "
            else:
                before = "Heavy "
            tmp = elem.replace('-', '').replace('+', '').strip()
            if tmp in precip_info.keys():
                preciplist.append(before + precip_info[tmp])
        newtmp = '\n\t'.join(elem for elem in preciplist)
        allweather = 'Weather:\n\t' + newtmp + '\n'
    else:
        allweather = ''

    obs_info = {'FG': 'Fog', 'BR': 'Mist', 'DU': 'Widespread dust', 'SA': 'Sand',
                'VA': 'Volcanic Ash', 'HZ': 'Haze', 'FU': 'Smoke', 'PY': 'Spray'}
    obsf_list = []
    if obsf:
        for elem in obsf:
            if elem in obs_info.keys():
                obsf_list.append(obs_info[elem])
        obsf_all = '\n\t'.join(elem for elem in obsf_list)
        obsfprint = 'Other Weather:\n\t' + obsf_all + '\n'
    else:
        obsfprint = ''

    print '{} Information:\n{} Zulu ({} local) on the {} of the month\n' \
          'Wind:\n\t{} {}\nVisibility:\n\t{}\nAltimeter:\n\t{}\nClouds:\n\t{}\n' \
          '{}{}' \
          'Temperature:\n\t{} degrees C ({} degrees F)\nDewpoint:\n\t{} degrees C ({} degrees F)' \
          '\nRaw METAR: {}'.format(airp, time_, local, date,
                                   windprint,
                                   gust,
                                   vis,
                                   altim,
                                   allclouds,
                                   allweather,
                                   obsfprint,
                                   temp, c_to_f(temp),
                                   dewpoint, c_to_f(dewpoint),
                                   metar)


def parse_metar(metar):
    """
    Parses airnav's METAR reporter for airport weather information
    :param metar: String in METAR format
    :return: Date, time, wind direction, wind speed, visibility, cloud information, temperature,
    dewpoint, altim, precip, obscurations, and the raw METAR
    """
    metars = metar
    metar = metar[4:]
    try:
        metar = re.sub(r'\dnm [A-Z][A-Z]', '', metar[:metar.index('RMK')])
    except ValueError:
        metar = re.sub(r'\dnm [A-Z][A-Z]', '', metar)

    datetimefinder = re.compile(r'\d\d\d\d\d\dZ')
    datetime = datetimefinder.search(metar)
    datetime = datetime.group()
    date = datetime[:2]
    time_ = '{0}:{1}'.format(datetime[2:4], datetime[4:6])

    try:
        windfinder = re.compile(r'\d\d\d\d\d(G\d\d)?KT')
        wind = windfinder.search(metar)
        wind = wind.group()
        winddirection = wind[:3]
        windspeed = wind[3:5]
        if 'G' in wind:
            windspeed = wind[3:wind.index('K')]

        if windspeed == '00':
            windspeed = 'None'
        elif windspeed[0] == '0':
            windspeed = windspeed.replace('0', '')
    except AttributeError:
        winddirection = 'Variable'
        windspeed = ''

    try:
        visibilityfinder = re.compile(r'(\d \d/)?\d+SM|\d/\dSM')
        vis = visibilityfinder.search(metar)
        vis = vis.group().replace('SM', ' miles')
    except AttributeError:
        visibilityfinder = re.compile(r' \d\d\d\d ')
        vis = visibilityfinder.search(metar)
        try:
            vis = vis.group()
            vis = int(vis)
            if vis == 9999:
                vis = 'Greater than 10 km'
            elif vis == 0000:
                vis = 'Less than 50 meters'
            else:
                vis /= 100
                vis = '{} km'.format(vis)
        except ValueError:
            if 'CAVOK' in metar:
                vis = 'Clear'
            else:
                vis = 'N/A'
        except AttributeError:
            if 'CAVOK' in metar:
                vis = 'Clear'
            else:
                vis = 'N/A'

    cloudfinder = re.compile(r'[A-Z]{2}[CRWTN]\d\d\d|CLR')
    clouds = cloudfinder.findall(metar)

    tempfinder = re.compile(r'(M)?\d\d/(M)?\d\d ')
    temps = tempfinder.search(metar)
    temps = temps.group()
    temp, dewpoint = temps.split("/")
    if temp[0] == '0' or (temp[1] == '0' and 'M' in temp):
        if '00' in temp or 'M00' in temp:
            temp = '0'
        else:
            temp = temp.replace('0', '')
    if dewpoint[0] == '0' or (dewpoint[1] == '0' and 'M' in dewpoint):
        if '00' in dewpoint or 'M00' in dewpoint:
            dewpoint = '0'
        else:
            dewpoint = dewpoint.replace('0', '')
    try:
        if 'M' in temp:
            temp = temp.replace('M', '')
            temp = '-' + temp
        if 'M' in dewpoint:
            dewpoint = dewpoint.replace('M', '')
            dewpoint = '-' + dewpoint
    except ValueError:
        dewpoint = '0'
    try:
        altifinder = re.compile(r'A\d\d\d\d')
        altim = altifinder.search(metar)
        altim = altim.group().replace('A', '')
        altim = altim[0:2] + '.' + altim[2:4]
    except AttributeError:
        altifinder = re.compile(r'Q\d\d\d\d')
        altim = altifinder.search(metar)
        altim = altim.group().replace('Q', '')
        altim += ' QNH'

    weatherfinder = re.compile(r' [+-]?[RSIGUDP][ANCRPZGES]\b|[+-]?TSRA')
    weather = weatherfinder.findall(metar)

    obsfinder = re.compile(r'\b[FBDSVHP][GRUAZY]\b')
    obsf = obsfinder.findall(metar)
    return date, time_, winddirection, windspeed, vis, clouds, \
           temp, dewpoint, altim, weather, obsf, metars


if __name__ == '__main__':
    if len(sys.argv) > 1:
        flightaware(False)
    else:
        flightaware()
