import re
from geopy.geocoders import Nominatim
import folium
from geopy import distance


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

    print(f'List has {len(films_list)} films with specified year. '
          f'\nAmount of films to analyze: {film_number} '
          f'\n------------------------------')

    for x in range(film_number):
        coordinates = geolocator.geocode(films_list[x][0], timeout=30)
        if coordinates is None:
            locations_loss += 1
            lost_locations.append(films_list[x][0])
            continue
        print(coordinates.latitude, coordinates.longitude)
        output_list.append([films_list[x][0], (coordinates.latitude, coordinates.longitude), films_list[x][-1]])
    print(f"Lost {locations_loss} locations overall, due to geopy", lost_locations)
    # print(films_list)
    return output_list


def item_insertion(input_list, film):
    """
    Function to sort films with distance
    :param input_list: list
    :param film: list
    :return: list
    """
    input_list.insert(0, film)
    for i in range(1, len(input_list)):
        # print(input_list, i)
        for j in range(0, i):
            if input_list[i][-1] < input_list[j][-1]:
                input_list[i][-1], input_list[j][-1] = input_list[j][-1], input_list[i][-1]
    return input_list


def get_nearest_films(films_list, number, user_location):
    """
    Function finds the nearest films near user specified location
    :param films_list: list
    :param number: int
    :return: list
    """
    output_list = []
    for film_data in films_list:
        film_dist = distance.distance(film_data[1], user_location).km
        film_data.append(film_dist)
        output_list = item_insertion(output_list, film_data)
        if len(output_list) >= number:
            output_list.pop()
    dist_list = [film[-1] for film in output_list]
    print(f'Closest film distance: {dist_list[0]}')
    print(f'Furthest film distance: {dist_list[-1]}')
    return output_list


def get_html_file(films_list):
    """
    Function generates html file with map
    :param films_list: list
    :return: None
    """
    map = folium.Map(
        location=[48.8589507, 2.2770201],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    for each in films_list:
        folium.Marker(each[1], popup=f'<i>{each[0]}</i>', tooltip=each[2]).add_to(map)
    folium.TileLayer('stamentoner').add_to(map)
    folium.LayerControl().add_to(map)
    map.save('index.html')


user_year = input('Enter a year: ')
user_film_analyze_num = int(input('Enter number of films: '))
user_markers_num = int(input('Enter number of nearest film markers: '))
# user_ilocation = input('Enter specified locaiton: ').split(',')
user_ilocation = ('40.8326046', '20.8721529')


film_name_location = get_film_locations(user_year)
data_list = get_location_coordinates(film_name_location,
                                     film_number=user_film_analyze_num)
data_list = get_nearest_films(data_list, user_markers_num, user_ilocation)
get_html_file(data_list)

