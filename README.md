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
* (US airports only) Calculates density altitude and displays it if it is > 500 feet than the elevation

It dumps the raw METAR at the end so user can verify/crosscheck the decoding.

Two `Airports` are equal if the `name` and `time` are equal, regardless of the type of identifier used (ICAO vs IATA).

## Example:

    >>> from METAR import Airport
    >>> kjfk = Airport('kjfk')
    >>> kjfk.metar
    'KJFK 160051Z 29016G26KT 10SM FEW046 SCT250 M03/M11 A2988 RMK AO2 PK WND 29033/0324 SLP119 T10281106 $'
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
    METAR issued at 00:51 Z (current time 00:35 Z) on the 16th of the month
    Wind: 290 degrees at 16 knots gusting 26 knots
    Visibility: 10 miles
    Altimeter: 29.88
    Clouds: Few clouds at 4600 feet, Scattered clouds at 25000 feet
    Precipitation: None
    Obsfucation: None
    Temperature: -3 degrees C
    Dewpoint: -11 degrees C
    METAR: KJFK 160351Z 29016G26KT 10SM FEW046 SCT250 M03/M11 A2988 RMK AO2 PK WND 29033/0324 SLP119 T10281106 $
    >>> egll = Airport('EGLL')
    >>> egll.altimeter
    '1026 QNH'
    >>> egll.visibility
    '40.0 km'
    >>> egll
    London Heathrow Airport Information (EGLL)
    Elevation = N/A ft   
    METAR issued at 00:20 Z (current time 00:53 Z) on the 16th of the month
    Wind: 200 degrees at 5 knots 
    Visibility: 40.0 km
    Altimeter: 1026 QNH
    Clouds: None
    Precipitation: None
    Obsfucation: Fog
    Temperature: 6 degrees C
    Dewpoint: 6 degrees C
    METAR: EGLL 160420Z 20005KT 4000 0800W R27R/P1500 FG NSC 06/06 Q1026
    >>> lhr = Airport('LHR')
    >>> egll == lhr
    True
