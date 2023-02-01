import requests
import json
from random import randint
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY

url = "https://api.pexels.com/v1/search/"


def get_photo(city: str, state: str):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": f"{city} {state}"}
    res = requests.get(
        url,
        params=params,
        headers=headers,
    )
    result = json.loads(res.text)
    length = len(result["photos"])
    index = randint(0, length)
    return result["photos"][index]["url"]


def get_weather_data(city: str, state: str):
    url_1 = "http://api.openweathermap.org/geo/1.0/direct"
    url_2 = "https://api.openweathermap.org/data/2.5/weather"
    OPEN_WEATHER_API_KEY = "e1c6f7a24d083249d6902ce008284934"

    params_1 = {"q": f"{city}, {state}, USA", "appid": OPEN_WEATHER_API_KEY}
    res_1 = requests.get(url_1, params=params_1)
    result_1 = json.loads(res_1.text)
    lat = result_1[0]["lat"]
    lon = result_1[0]["lon"]

    params_2 = {
        "lat": lat,
        "lon": lon,
        "appid": OPEN_WEATHER_API_KEY,
        "units": "imperial",
    }
    res_2 = requests.get(url_2, params=params_2)
    result_2 = json.loads(res_2.text)

    temp = round(result_2["main"]["temp"])
    description = result_2["weather"][0]["description"]
    summary = {"temp": temp, "description": description}
    return summary
