#!/usr/bin/env python3
"""
Module accepts 3 or 4 letter input from user and attempts to fetch METAR info from flightaware.com

NOTE: NOT FOR FLIGHT PLANNING

LAST UPDATED: 30 MAR 2019
"""
import re
import sys
import datetime as datet
from bs4 import BeautifulSoup
import requests


class Airport(object):
    """
    Airport object. Initialize with 3 or 4 letter identifier (e.g. kfjk = Airport("KJFK") )
    """

    def __init__(self, identifier):
        self.elevation = 'N/A'
        self.identifier = identifier.upper()
        self.find_elevation()
        self.name = 'None'
        self.day = 'None'
        self.metar = 'None'
        self.mmetar = 'None'
        self.time = 'None'
        self.wind = 'None'
        self.visibility = 'None'
        self.clouds = []
        self.temperature = 'None'
        self.dewpoint = 'None'
        self.altimeter = 'None'
        self.weather = []
        self.obsfucation = []
        self.refresh()

    def find_elevation(self):
        url = 'https://www.airnav.com/airport/{}'.format(self.identifier)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)\
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95'}

        response = requests.get(url, headers=headers).text

        if 'Examples' not in response and 'Browse by country/territory' not in response:
            elevationfinder = re.compile(r'(\d)+.(\d)+ ft')
            elevation_str = elevationfinder.search(response).group()
            self.elevation = elevation_str.replace(' ft', '')

    def refresh(self):
        """
        Refresh airport's METAR
        # :param airport: 3 or 4 letter airport identifier
        :return: None
        """

        def get_metar():
            """
            Get METAR and initialize all attribtues
            :return: None
            """
            self.set_day_and_time()
            self.set_wind()
            self.set_visibility()
            self.set_clouds()
            self.set_temp_and_dewpoint()
            self.set_altimeter()
            self.set_weather()
            self.set_obsfucation()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)\
                     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95'}
        url = "https://flightaware.com/resources/airport/{}/weather".format(self.identifier)
        response = requests.get(url, headers=headers).text
        if 'Unknown or Invalid Airport Code' not in response:
            soup = BeautifulSoup(response, "html.parser")
            try:
                placeholder = soup.find('tr', class_='smallrow1 hint ')
                raw_metar = placeholder['title']
                metar = str(raw_metar)
            except TypeError:
                placeholder_text = response[response.find('<tr class="smallrow1 hint " style="background-color'):]
                placeholder_text = placeholder_text[:placeholder_text.find('<td>')]
                metar = placeholder_text[placeholder_text.find('title="'):].replace('title="', '').replace('">', '')
            mmetar = metar[4:].strip()
            try:
                mmetar = re.sub(r'\dnm [A-Z][A-Z]', '', metar[:metar.index('RMK')])
            except ValueError:
                mmetar = re.sub(r'\dnm [A-Z][A-Z]', '', mmetar)
            self.mmetar = mmetar
            raw_title = soup.title.text
            airp = raw_title[:raw_title.index(' Weather')].strip()
            self.name = airp
            self.metar = metar
            get_metar()

    def set_altimeter(self):
        """
        Get altimeter, set self.altimeter
        :return: None
        """
        try:
            altifinder = re.compile(r'A\d\d\d\d')
            altim = altifinder.search(self.mmetar)
            altim = altim.group().replace('A', '')
            altim = altim[0:2] + '.' + altim[2:4]
        except AttributeError:
            altifinder = re.compile(r'Q\d\d\d\d')
            altim = altifinder.search(self.mmetar)
            altim = altim.group().replace('Q', '')
            altim += ' QNH'

        self.altimeter = altim

    def set_obsfucation(self):
        """
        Set self.obsfucation
        :return: None
        """
        obsfinder = re.compile(r'\b[FBDSVHP][GRUAZY]\b')
        self.obsfucation = obsfinder.findall(self.mmetar)

    def set_weather(self):
        """
        Set self.weather
        :return: None
        """
        weatherfinder = re.compile(r' [+-]?[RSIGUDP][ANCRPZGES]\b|[+-]?TSRA')
        weather_list = weatherfinder.findall(self.mmetar)
        self.weather = [x.strip() for x in weather_list]

    def set_temp_and_dewpoint(self):
        """
        Set self.temperature and self.dewpoint
        :return: None
        """
        tempfinder = re.compile(r'(M)?\d\d/(M)?\d\d ')
        temps = tempfinder.search(self.mmetar)
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

        self.temperature = temp
        self.dewpoint = dewpoint.strip()

    def set_clouds(self):
        """
        Set self.clouds
        :return: None
        """
        cloudfinder = re.compile(r'[A-Z]{2}[CRWTN]\d\d\d|CLR')
        self.clouds = cloudfinder.findall(self.mmetar)

    def set_visibility(self):
        """
        Set self.visibility
        :return: None
        """
        try:
            visibilityfinder = re.compile(r'(\d \d/)?\d+SM|\d/\dSM')
            vis = visibilityfinder.search(self.mmetar)
            vis = vis.group().replace('SM', ' miles')
            if vis.count(' ') == 1:
                tmp = vis.split(' ')
                if tmp[0] == '1' and len(tmp[0]) == 1:
                    vis = '1 mile'
        except AttributeError:
            visibilityfinder = re.compile(r' \d\d\d\d ')
            vis = visibilityfinder.search(self.mmetar)
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
                if 'CAVOK' in self.mmetar:
                    vis = 'Clear'
                else:
                    vis = 'N/A'
            except AttributeError:
                if 'CAVOK' in self.mmetar:
                    vis = 'Clear'
                else:
                    vis = 'N/A'
        self.visibility = vis

    def set_wind(self):
        """
        Set self.wind
        :return: None
        """
        try:
            windfinder = re.compile(r'\d\d\d\d\d(G\d\d)?KT')
            wind = windfinder.search(self.mmetar)
            wind = wind.group()
            winddirection = wind[:3]
            windspeed = wind[3:5]
            if 'G' in wind:
                windspeed = wind[3:wind.index('K')]

            if windspeed == '00':
                windspeed = 'None'
            elif windspeed[0] == '0':
                windspeed = windspeed.replace('0', '')

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
                windprint = '{0} degrees at {1} knots'.format(winddirection, windspeed)

            self.wind = '{} {}'.format(windprint, gust)
        except AttributeError:
            self.wind = 'Light & Variable'

    def set_day_and_time(self):
        """
        Set self.day and self.time
        :return: None
        """
        datetimefinder = re.compile(r'\d\d\d\d\d\dZ')
        datetime = datetimefinder.search(self.mmetar)
        datetime = datetime.group()
        self.day = datetime[:2]
        self.time = '{0}:{1}'.format(datetime[2:4], datetime[4:6])

    def __str__(self):
        """
        Override the default to_string
        :return: str of all of the airport's METAR information
        """
        utc = '{0:%H:%M}'.format(datet.datetime.utcnow())
        date = {'1': 'st', '2': 'nd', '3': 'rd', '21': 'st', '22': 'nd', '23': 'rd', '31': 'st'}
        try:
            eenth = '{}{}'.format(self.day, date[self.day])
        except KeyError:
            eenth = '{}th'.format(self.day)

        cloudlist = []
        cloud_info = {'BKN': 'Broken', 'OVC': 'Overcast', 'FEW': 'Few',
                      'CLR': 'Clear', 'SCT': 'Scattered'}
        for elem in self.clouds:
            if any(elem[0:3] in cloud_info.keys() for elem in self.clouds):
                if 'CLR' in elem[0:3]:
                    info = cloud_info[elem[0:3]]
                else:
                    info = '{} clouds at {} feet'.format(cloud_info[elem[0:3]], int(elem[3:]) * 100)
                cloudlist.append(info)
        allclouds = ', '.join(elem for elem in cloudlist)
        if not allclouds:
            allclouds = 'None'

        preciplist = []
        precip_info = {'RA': 'rain', 'SN': 'snow', 'IC': 'ice', 'GR': 'hail',
                       'DZ': 'drizzle', 'SG': 'snow grains', 'PE': 'ice pellets', 'GS': 'small hail',
                       'UP': 'unknown precipitation', 'TSRA': 'thundershowers', 'DU': 'dust'}
        if self.weather:
            for elem in self.weather:
                if '+' in elem:
                    before = "Heavy "
                elif '-' in elem:
                    before = "Light "
                else:
                    before = "Moderate "
                tmp = elem.replace('-', '').replace('+', '').strip()
                if tmp in precip_info.keys():
                    preciplist.append(before + precip_info[tmp])
            allweather = ', '.join(elem for elem in preciplist)
        else:
            allweather = 'None'

        obs_info = {'FG': 'Fog', 'BR': 'Mist', 'DU': 'Widespread dust', 'SA': 'Sand',
                    'VA': 'Volcanic Ash', 'HZ': 'Haze', 'FU': 'Smoke', 'PY': 'Spray'}
        obsf_list = []
        if self.obsfucation:
            for elem in self.obsfucation:
                if elem in obs_info.keys():
                    obsf_list.append(obs_info[elem])
            obsfprint = ', '.join(elem for elem in obsf_list)
        else:
            obsfprint = 'None'

        if self.temperature == '1':
            temperature_ = '1 degree C'
        else:
            temperature_ = '{} degrees C'.format(self.temperature)

        if self.dewpoint == '1':
            dewpoint = '1 degree C'
        else:
            dewpoint = '{} degrees C'.format(self.dewpoint)

        try:
            if float(self.density_alt()) < (float(self.elevation) + 500.0):
                density = ''
            else:
                density = 'Density altitude = {} ft'.format(self.density_alt())
        except ValueError:
            density = ''

        toreturn = '-'*16

        toreturn += '''\n{} Information ({})
Elevation = {} ft   {}
METAR issued at {} Z (current time {} Z) on the {} of the month
Wind: {}
Visibility: {}
Altimeter: {}
Clouds: {}
Precipitation: {}
Obsfucation: {}
Temperature: {} ({} deg F)
Dewpoint: {} ({} deg F)
METAR: {}\n'''.format(self.name, self.identifier,
                      self.elevation, density,
                      self.time, utc, eenth,
                      self.wind,
                      self.visibility,
                      self.altimeter,
                      allclouds,
                      allweather,
                      obsfprint,
                      temperature_, c_to_f(self.temperature),
                      dewpoint, c_to_f(self.dewpoint),
                      self.metar)
        toreturn += '-'*16
        return toreturn

    def report(self):
        """
        Call __str__
        :return: None
        """
        print(self)

    def density_alt(self):
        """
        Calculate the density altitude
        :return: Int of density altitude
        """
        try:
            alt = float(self.elevation)
            altim = float(self.altimeter)
            temp = float(self.temperature)
            pressure_altitude = (29.92 - altim)*1000 + alt
            density_altitude = pressure_altitude + 120*(temp - -(2*alt/1000 - 15))
            return '%5.2f' % density_altitude
        except ValueError:
            return 'N/A'

    def __eq__(self, other):
        """
        Two airports are equal if their names are the same and their times are the same
        :param other: Airport type
        :return: bool
        """
        return self.name == other.name and self.time == other.time

    __repr__ = __str__


def c_to_f(temp: str):
    """
    Convert Celsius temperature to Fahrenheight
    :param temp: Temperature (str)
    :return: Temperature in F (float)
    """
    try:
        celsius = float(temp)
        return round((9/5)*celsius + 32)
    except ValueError:
        return 'N/A'


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(Airport(sys.argv[1]))
    else:
        while True:
            air = input("Input a IATA or ICAO airport identifier: ")
            if len(air) <= 4:
                break
        Airport(air).report()
