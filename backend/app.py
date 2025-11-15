import requests
import os
from dotenv import load_dotenv
from typing import Any
from fastapi import FastAPI

app = FastAPI()

load_dotenv()

geo_api_key = os.getenv('GEOCODING_API_KEY')
weather_apikey = os.getenv('OPENWEATHER_API_KEY')
#helper function
def convert_kelvin_to_celcius(value: float):
    return round(value - 273.15, 1)

# geocoding api
def convert_cityname_to_coordinate(city):
    url = f"https://api.geoapify.com/v1/geocode/search?text={city}&format=json&apiKey={geo_api_key}"

    response = requests.get(url)
    data = response.json()
    # print(data)
    lon = data['results'][0]['lon']
    lat = data['results'][0]['lat']
    return lat, lon


def weather_info(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_apikey}"

    response = requests.get(url)
    data = response.json()
    return data

def formater(payload: dict[str, Any]):
    weather = payload.get("weather", [{}])[0]
    main = payload.get("main", {})
    wind = payload.get("wind", {})

    return{
        "city": payload.get("name"),
        "country": payload.get("sys", {}).get("country"),
        "coordinates": payload.get("coord"),
        "conditions": {
            "label": weather.get("main"),
            "description": weather.get("description"),
            "icon": weather.get("icon"),
        },
        "temperature": {
            "current_c": convert_kelvin_to_celcius(main.get("temp", 0)),
            "feels_like_c": convert_kelvin_to_celcius(main.get("feels_like", 0)),
            "min_c": convert_kelvin_to_celcius(main.get("temp_min", 0)),
            "max_c": convert_kelvin_to_celcius(main.get("temp_max", 0)),
        },
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "wind": {
            "speed_mps": wind.get("speed"),
            "direction_deg": wind.get("deg"),
            "gust_mps": wind.get("gust"),
        },
        "visibility_m": payload.get("visibility"),
        "cloud_cover_pct": payload.get("clouds", {}).get("all"),
        "timestamp": payload.get("dt"),
        "timezone_offset_s": payload.get("timezone"),
        "source": "openweathermap",
        "raw": payload,
    }

from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/weather")
def weater(city: str):
    lat, lon = convert_cityname_to_coordinate(city)
    payload = weather_info(lat, lon)
    formatted_data = formater(payload) 
    formatted_data['input city'] = city
    return formatted_data

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)