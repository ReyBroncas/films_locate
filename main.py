import re
from geopy.geocoders import Nominatim
import folium
from geopy import distance
import time
import pprint
import pycountry


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
    with open('locations.csv', 'r', encoding="utf-8", errors='ignore') as file:
        line = file.readline()
        while line:
            if line.split(',')[1] == user_year and line.split(',')[1] != 'NO DATA':
                film_set.add(tuple([line.split(',')[0].strip(), line.split(',')[-1].strip()]))
            line = file.readline()
    return film_set


def get_location_coordinates_fromfile(films_set, film_number=0):
    location_dict = {}
    films_list = list(films_set)

    countries = {}
    for country in pycountry.countries:
        countries[country.name] = country.alpha_2
    # MAKING NESTED DICTIONARY IN DICTIONARY WITH COUNTRIES AND CITIES WITH COORDINATES FROM FILE
    # CONVERTING COUNTRY NAME INTO UNIFIED NAME
    with open('city_coordinates.tsv', 'r', encoding="utf-8", errors='ignore') as file:
        line = file.readline()
        line = file.readline()
        while line:
            # TODO: find out why russia cannot be found usiint pycountry
            line_list = line.split('\t')
            if countries.get(line_list[0], 'RU') in location_dict:
                if line_list[1] not in location_dict[countries.get(line_list[0], 'RU')]:
                    location_dict[countries.get(line_list[0], 'RU')].setdefault(line_list[1], (
                        line_list[-2].strip(), line_list[-1].strip()))
            else:
                location_dict.setdefault(countries.get(line_list[0], 'RU'),
                                         {line_list[1]: (line_list[-2].strip(), line_list[-1].strip())})
            line = file.readline()
    pprint.pprint(location_dict)
    # print(films_list[0])

    # CONVERTING GIVEN COUNTRIES INTO UNIFIED NAME
    for i in range(film_number):
        try:
            # MADE AN EXCEPTION FOR UK AS pycountry RECOGNISES IT AS UKRAINE
            if films_list[i][-1].split()[-1] == 'UK':
                country_code = pycountry.countries.search_fuzzy(films_list[i][-1].split()[-2])[0].alpha_2
            else:
                country_code = pycountry.countries.search_fuzzy(films_list[i][-1].split()[-1])[0].alpha_2
        except LookupError:
            continue
        # EXTRACTING CITY NAME
        if country_code == 'GB' and len(films_list[i][-1].split()) > 1:
            city_name = films_list[i][-1].split()[-3]
        elif len(films_list[i][-1].split()) > 1:
            city_name = films_list[i][-1].split()[-2]
        else:
            continue
        # FINDING COORDINATES
        print(country_code, city_name)

    return location_dict


def get_location_coordinates_fromgeopy(films_set, film_number=0):
    """
    Function to get coordinates of given films
    :param films_set: set
    :param film_number: int
    :return: list
    """
    if not film_number:
        film_number = len(films_set)

    films_list = sorted(list(films_set))
    print(f'List has {len(films_list)} films with specified year. '
          f'\nAmount of films to analyze: {film_number} '
          f'\n------------------------------')

    locations_loss = 0
    lost_locations = []
    output_list = []
    coordinates_set = set()
    geoloc = Nominatim(user_agent="map")

    for i in range(film_number):
        if '.' in films_list[i][-1]:
            geo_value = geoloc.geocode(films_list[i][-1]
                                       [films_list[i][-1].find('.'):], timeout=30)
        else:
            geo_value = geoloc.geocode(films_list[i][-1], timeout=30)
        if geo_value is None or \
                (geo_value.latitude, geo_value.longitude) in coordinates_set:
            locations_loss += 1
            lost_locations.append(films_list[i])
            print(films_list[i][-1])
            continue
        time.sleep(1.1)
        coordinates = (geo_value.latitude, geo_value.longitude)
        coordinates_set.add(coordinates)
        output_list.append([films_list[i][0], coordinates])
        print(coordinates)
    print(f"Lost {locations_loss} locations overall, due to geopy", lost_locations)
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
        if len(output_list) >= int(number):
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


# user_year = input('Enter a year: ')
user_year = '2016'
# user_film_analyze_num = int(input('Enter number of films: '))
user_film_analyze_num = 200
# user_markers_num = int(input('Enter number of nearest film markers: '))
user_markers_num = '10'
# user_ilocation = input('Enter specified locaiton: ').split(',')
user_ilocation = ('48.8566', '2.3522')

film_name_location = get_film_locations(user_year)
data_list = get_location_coordinates_fromfile(film_name_location,
                                              film_number=user_film_analyze_num)
data_list = get_nearest_films(data_list, user_markers_num, user_ilocation)
get_html_file(data_list)
