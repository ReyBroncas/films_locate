import re


def get_location_name(line):
    """
    Function extracts location name from string line
    :param line: string
    :return: string
    """
    output_list = []
    line = line.split('\t')
    for i in range(-1, -(len(line) + 1), -1):
        if '(' in line[i]:
            continue
        elif not line[i]:
            break
        output_list.append(line[i])
    return ' '.join(output_list).rstrip()


def get_film_year(line):
    """
    Function extracts film year from string line
    :param line: string
    :return: string
    """
    num = re.compile(r'\d\d\d\d')
    film_year = num.findall(line[0])
    if film_year:
        return film_year[0]
    else:
        return 0


def get_film_locations(user_year):
    """
    Function reads data from location.list file
    :param user_year: string
    :return: set
    """
    film_set = set()
    with open('locations.list', 'r', encoding="utf-8", errors='ignore') as file:
        cnt = 1
        line = file.readline()
        while line:
            if cnt > 14:
                line_spl = line.split('				')
                film_year = get_film_year(line_spl)
                film_name = line_spl[0][:line_spl[0].find('(')]
                film_location = get_location_name(line)
                if film_year == user_year:
                    film_set.add((film_location, film_year, film_name))
            if not file.readline():
                break
            line = file.readline()
            cnt += 1
    return film_set


print(get_film_locations('2016'))
loc = "Naples, Campania, Italy"
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="map")
location = geolocator.geocode(loc, timeout=15)
print((location.latitude, location.longitude))
