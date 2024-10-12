from flask import Flask, render_template, request
import swisseph as swe
from geopy.geocoders import Nominatim
import pytz
from datetime import datetime
from timezonefinder import TimezoneFinder

app = Flask(__name__)

# Set the path to the Swiss Ephemeris data files
swe.set_ephe_path('E:/Jyotish/swisseph-master/swisseph-master/ephe')

planet_names = {
    swe.SUN: 'Sun',
    swe.MOON: 'Moon',
    swe.MERCURY: 'Mercury',
    swe.VENUS: 'Venus',
    swe.MARS: 'Mars',
    swe.JUPITER: 'Jupiter',
    swe.SATURN: 'Saturn',
    swe.URANUS: 'Uranus',
    swe.NEPTUNE: 'Neptune',
    swe.PLUTO: 'Pluto',
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        time_of_birth = request.form['time_of_birth']
        place_of_birth = request.form['place_of_birth']

        # Geocode the place of birth to get latitude and longitude
        latitude, longitude = geocode_place(place_of_birth)

        # Calculate planetary positions
        planets = calculate_planets(date_of_birth, time_of_birth, latitude, longitude, place_of_birth)

        # Calculate Chara Karakas
        chara_karakas = calculate_chara_karakas(planets)

        # Generate D1 and D9 charts
        d1_chart = generate_d1_chart(planets)
        d9_chart = generate_d9_chart(planets)

        return render_template('chart.html', name=name, d1_chart=d1_chart, d9_chart=d9_chart,
                               chara_karakas=chara_karakas)
    return render_template('index.html')


def geocode_place(place_name):
    geolocator = Nominatim(user_agent="jyotish_app")
    location = geolocator.geocode(place_name)
    return location.latitude, location.longitude


def calculate_planets(date_str, time_str, lat, lon, place_name):
    # Parse date and time
    naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    # Get timezone of place
    timezone = get_timezone(place_name)
    local_dt = timezone.localize(naive_dt)
    utc_dt = local_dt.astimezone(pytz.utc)
    # Calculate Julian Day
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute / 60.0)
    # Calculate planetary positions
    planets = {}
    for planet in range(swe.SUN, swe.PLUTO + 1):
        lon, lat = swe.calc_ut(jd, planet)
        # print(f"Longi: {lon} - Lati - {lat}")
        planets[planet] = lon[0] % 360
    return planets


def get_timezone(place_name):
    # Use geopy and timezonefinder to get timezone
    geolocator = Nominatim(user_agent="jyotish_app")
    location = geolocator.geocode(place_name)
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
    return pytz.timezone(timezone_str)


def calculate_chara_karakas(planets):
    # Sort planets by degrees to assign karakas
    sorted_planets = sorted(planets.items(), key=lambda x: x[1], reverse=True)
    karaka_names = ['Atma Karaka', 'Amatya Karaka', 'Bhatri Karaka', 'Matri Karaka',
                    'Putra Karaka', 'Gnati Karaka', 'Dara Karaka']
    chara_karakas = {karaka_names[i]: sorted_planets[i] for i in range(len(karaka_names))}
    return chara_karakas


def generate_d1_chart(planets):
    # Generate the Rasi chart based on planetary positions
    # Placeholder function
    return planets


def generate_d9_chart(planets):
    # Generate the Navamsa chart based on planetary positions
    # Placeholder function
    return planets


@app.context_processor
def utility_processor():
    def get_planet_name(planet_id):
        return planet_names.get(planet_id, 'Unknown')
    return dict(get_planet_name=get_planet_name)


if __name__ == '__main__':
    app.run(debug=True)
