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

It dumps the raw METAR at the end so user can verify/crosscheck the decoding.
