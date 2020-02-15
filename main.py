import re
from geopy.geocoders import Nominatim
import folium

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


def get_location_coordinates(films_set, film_number=0):
    """
    Function to get coordinates of given films
    :param films_set: set
    :param film_number: int
    :return: None
    """
    if not film_number:
        film_number = len(films_set)
    locations_loss = 0
    lost_locations = []
    output_list = []
    geolocator = Nominatim(user_agent="map")
    films_list = sorted(films_set)
    print(f'List has {len(films_list)} items')
    for x in range(film_number):
        coordinates = geolocator.geocode(films_list[x][0], timeout=15)
        if coordinates is None:
            locations_loss += 1
            lost_locations.append(films_list[x][0])
            continue
        print(coordinates.latitude, coordinates.longitude)
        output_list.append([films_list[x][0], (coordinates.latitude, coordinates.longitude), films_list[x][-1]])
    print(f"Lost {locations_loss} locations overall, due to geopy", lost_locations)
    print(films_list)
    return output_list


def get_html_file(films_list):
    print(films_list)
    m = folium.Map(
        location=[48.8589507, 2.2770201],
        zoom_start=5,
        tiles='Stamen Terrain'
    )
    for each in films_list:
        folium.Marker(each[1], popup=f'<i>{each[0]}</i>', tooltip=each[2]).add_to(m)
    m.save('index.html')

get_html_file(get_location_coordinates(get_film_locations(input()), film_number=30))
