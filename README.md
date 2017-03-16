# METAR Scraper
Scrapes FlightAware for an airport's METAR. User inputs desired airport either as a commandline argument or through the terminal. Supports ICAO and IATA airport identifiers.

Currently scrapes METARs for:

* Visibility
* Temperature
* Dewpoint
* Wind direction and speed
* Precipitation
* Weather pheomena
* Altimeter
* Sky condition
* Calculates density altitude and displays it if it is > 500 feet than the elevation

## Example:

    >>> kjfk = Airport('kjfk')
    >>> kjfk.metar
    'KJFK 160351Z 29016G26KT 10SM FEW046 SCT250 M03/M11 A2988 RMK AO2 PK WND 29033/0324 SLP119 T10281106 $'
    >>> kjfk.altimeter
    '29.88'
    >>> kjfk.weather
    []
    >>> kjfk.visibility
    '10 miles'
    >>> kjfk.wind
    '290 degrees at 16 knots gusting 26 knots'
    >>> kjfk.temperature
    '-3'
    >>> kjfk.obsfucation
    []
    >>> kjfk.elevation
    12.7 ft
    >>> kjfk.time
    '03:51'
    >>> kjfk.clouds
    ['FEW046', 'SCT250']
    >>> print(kjfk)
    John F Kennedy Intl Airport Information (KJFK)
    Elevation = 12.7 ft   
    METAR issued at 03:51 Z (current time 04:35 Z) on the 16th of the month
    Wind: 290 degrees at 16 knots gusting 26 knots
    Visibility: 10 miles
    Altimeter: 29.88
    Clouds: Few clouds at 4600 feet, Scattered clouds at 25000 feet
    Precipitation: None
    Obsfucation: None
    Temperature: -3 degrees C
    Dewpoint: -11 degrees C
    METAR: KJFK 160351Z 29016G26KT 10SM FEW046 SCT250 M03/M11 A2988 RMK AO2 PK WND 29033/0324 SLP119 T10281106 $

It dumps the raw METAR at the end so user can verify/crosscheck the decoding.
