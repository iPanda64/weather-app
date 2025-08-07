import python_weather
import datetime
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

city: str = None


def get_time_by_city(city_name):
    geolocator = Nominatim(user_agent="city_time_locator")
    location = geolocator.geocode(city_name)
    if not location:
        raise ValueError(f"Could not find location for city: {city_name}")

    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(
        lat=location.latitude, lng=location.longitude)
    if not timezone_str:
        raise ValueError(f"Could not determine timezone for: {city_name}")

    tz = pytz.timezone(timezone_str)
    city_time = datetime.datetime.now(tz).time()
    return city_time


def day_switch(day_name):
    switch = {
        "Monday": "It's Monday!",
        "Tuesday": "It's Tuesday!",
        "Wednesday": "It's Wednesday!",
        "Thursday": "It's Thursday!",
        "Friday": "It's Friday!",
        "Saturday": "It's Saturday!",
        "Sunday": "It's Sunday!",
    }
    return switch.get(day_name, "Unknown day")


today_name = datetime.datetime.today().strftime("%A")


_weather = None


async def fetch_weather(city: str = city):
    global _weather
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        _weather = await client.get(city)
    return _weather


def get_today_exclusive():
    if _weather is None:
        raise RuntimeError(
            "Weather data not fetched yet. Call fetch_weather first.")

    result = {
        "humidity": _weather.humidity,
        "wind_direction": _weather.wind_direction.emoji,
        "wind_speed": _weather.wind_speed,
        "visibility": _weather.visibility,
        "feels_like": _weather.feels_like,
    }
    return result


def get_all_days():
    if _weather is None:
        raise RuntimeError(
            "Weather data not fetched yet. Call fetch_weather first.")
    result = []
    for daily in _weather:
        daily_info = {
            "time": daily.date.strftime("%d/%m/%y"),
            "weekday": daily.date.strftime("%A"),
            "temperature": daily.temperature,
            "moon": daily.moon_phase.emoji,
        }
        result.append(daily_info)
    return result


def get_today():
    if _weather is None:
        raise RuntimeError(
            "Weather data not fetched yet. Call fetch_weather first.")
    combined = get_today_exclusive()
    combined.update(get_all_days()[0])
    return combined


def kind_to_string(kind):
    from python_weather.enums import Kind

    match kind:
        case Kind.CLOUDY | Kind.PARTLY_CLOUDY | Kind.VERY_CLOUDY:
            return "cloudy"
        case Kind.FOG:
            return "fog"
        case Kind.HEAVY_SHOWERS | Kind.HEAVY_RAIN:
            return "heavy rain"
        case Kind.HEAVY_SNOW | Kind.HEAVY_SNOW_SHOWERS:
            return "heavy snow"
        case (
            Kind.LIGHT_SHOWERS
            | Kind.LIGHT_RAIN
            | Kind.LIGHT_SLEET
            | Kind.LIGHT_SLEET_SHOWERS
        ):
            return "light snow"
        case Kind.SUNNY:
            return "sunny"
        case (
            Kind.THUNDERY_HEAVY_RAIN
            | Kind.THUNDERY_SHOWERS
            | Kind.THUNDERY_SNOW_SHOWERS
        ):
            return "thundery"
        case _:
            return "cloudy"


def get_all_days_kind():
    result = []
    for index, daily in enumerate(_weather):
        for hourly in daily:
            if hourly.time.hour == 12:
                day_kind = kind_to_string(hourly.kind)
                break
        result.append(day_kind)
    return result


def get_hour(day_index):
    if _weather is None:
        raise RuntimeError(
            "Weather data not fetched yet. Call fetch_weather first.")
    result = []
    for index, daily in enumerate(_weather):
        if day_index == index:
            for hourly in daily:
                hourly_info = {
                    "time": hourly.time,
                    "kind": kind_to_string(hourly.kind),
                    "temperature": hourly.temperature,
                    "humidity": hourly.humidity,
                }
                result.append(hourly_info)
    return result


def get_hours():
    if _weather is None:
        raise RuntimeError(
            "Weather data not fetched yet. Call fetch_weather first.")

    result = []
    for day_index in range(len(_weather.daily_forecasts)):
        day_hours = get_hour(day_index)
        result.append(day_hours)

    return result


def get_current_hour():
    hour_info_list = get_hour(0)
    current_time = get_time_by_city(city)
    for hourly_info in hour_info_list:
        if hourly_info["time"] < current_time:
            result = hourly_info
    return result
