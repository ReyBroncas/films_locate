from geopy.geocoders import Nominatim
import folium
from geopy import distance
import time


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


def get_location_coordinates(films_set, film_number=0):
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
    print('Loading...')
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
            # print(films_list[i][-1])
            continue
        time.sleep(1.1)
        coordinates = (geo_value.latitude, geo_value.longitude)
        coordinates_set.add(coordinates)
        output_list.append([films_list[i][0], coordinates])
        # print(coordinates)
    print(f"Lost {locations_loss} locations overall, due to geopy", lost_locations)
    return output_list


def get_nearest_films(films_list, number, user_location):
    """
    Function finds the nearest films near user specified location
    :param films_list: list
    :param number: int
    :return: list
    """
    output_list = []
    for film_data in films_list:
        film_dist = int(distance.distance(film_data[1], user_location).km)
        film_data.append(film_dist)
        output_list.append(film_data)
        output_list.sort(key=lambda x: x[-1])
        if len(output_list) >= int(number):
            output_list.pop()
    dist_list = [film[-1] for film in output_list]
    print(f'Closest film distance: {dist_list[0]} km.')
    print(f'Furthest film distance: {dist_list[-1]} km.')
    return output_list


def get_html_file(films_list, user_location):
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
    folium.Marker(user_location, popup=f'<i>User location</i>',
                  icon=folium.Icon(color='red', icon='info-sign')).add_to(map)
    folium.TileLayer('stamentoner').add_to(map)
    fg_pp=folium.FeatureGroup(name="Population")
    fg_pp.add_to(map)
    fg_pp.add_child(folium.GeoJson(data=open('world.json', 'r',
            encoding='utf-8-sig').read(),style_function=lambda x:
            {'fillColor':'yellow' if x['properties']['POP2005'] < 10000000 else
            'pink' if 10000000 <= x['properties']['POP2005'] < 20000000 else 'purple'}))
    folium.LayerControl().add_to(map)
    map.save('index.html')

# user_year = input('Enter a year: ')
user_year = '2016'
# user_film_analyze_num = int(input('Enter number of films: '))
user_film_analyze_num = 20
# user_markers_num = int(input('Enter number of nearest film markers: '))
user_markers_num = '10'
# user_ilocation = input('Enter specified locaiton: ').split(',')
user_location = ('48.8566', '2.3522')


film_name_location = get_film_locations(user_year)
data_list = get_location_coordinates(film_name_location,
                                     film_number=user_film_analyze_num)
data_list = get_nearest_films(data_list, user_markers_num, user_location)
get_html_file(data_list, user_location)

