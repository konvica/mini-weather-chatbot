# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import datetime
# This is a simple example for a custom action which utters "Hello World!"
import os
from typing import Any, Text, Dict, List

import requests
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

load_dotenv()  # take environment variables from .env.

url = "https://api.tomorrow.io/v4/timelines"
weather_codes = {
    "1000": "Clear",
    "1001": "Cloudy",
    "1100": "Mostly Clear",
    "1101": "Partly Cloudy",
    "1102": "Mostly Cloudy",
    "2000": "Fog",
    "2100": "Light Fog",
    "3000": "Light Wind",
    "3001": "Wind",
    "3002": "Strong Wind",
    "4000": "Drizzle",
    "4001": "Rain",
    "4200": "Light Rain",
    "4201": "Heavy Rain",
    "5000": "Snow",
    "5001": "Flurries",
    "5100": "Light Snow",
    "5101": "Heavy Snow",
    "6000": "Freezing Drizzle",
    "6001": "Freezing Rain",
    "6200": "Light Freezing Rain",
    "6201": "Heavy Freezing Rain",
    "7000": "Ice Pellets",
    "7101": "Heavy Ice Pellets",
    "7102": "Light Ice Pellets",
    "8000": "Thunderstorm",
    "0": "Unknown"
}


class ActionAskWeather(Action):
    def __init__(self):
        super().__init__()
        self.geocoder = Nominatim(user_agent="mini-weather-chatbot")
        self.logger = logging.getLogger("rasa.action_server.action_logger")
        self.logger.setLevel(logging.INFO)

    def name(self) -> Text:
        return "action_ask_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # print("tracker.get_slot",tracker.get_slot('city'))
        self.logger.info("tracker entities"+str(tracker.latest_message.get("entities", [])))

        city_spacy = next(tracker.get_latest_entity_values("GPE"), None)
        city_diet = next(tracker.get_latest_entity_values("city"), None)
        self.logger.info([city_spacy, city_diet])
        if (city_spacy is None) and (city_diet is None):
            text = f"Unable to retrieve weather (unable to find city)"
        else:
            city = city_spacy if city_spacy else city_diet
            location = self.geocoder.geocode(city)
            querystring: Dict[str, str] = {
                'location': f'{location.latitude},{location.longitude}',
                'apikey': os.environ["CLIMACELL_API_KEY"],  # type: ignore
                'fields': ["cloudCover", "temperature", "humidity", "windSpeed", "weatherCode", "particulateMatter10"],
                "units": "metric",
                "timesteps": "1h",
                'startTime': datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z',
                'endTime': (datetime.datetime.now() + datetime.timedelta(hours=1)).replace(
                    microsecond=0).isoformat() + 'Z'
            }

            headers = {"Accept": "application/json"}

            response = requests.request("GET", url, headers=headers, params=querystring)
            # response = requests.get(url + urlencode(payload))
            self.logger.info(response.text)
            if (response.status_code == 200):
                data: Dict = response.json()['data']
                current: Dict = data['timelines'][0]['intervals'][0]['values']

                temperature: str = current['temperature']
                cloud_cover: str = current['cloudCover']
                humidity: str = current['humidity']
                wind_speed: str = current['windSpeed']
                conditions: str = current['weatherCode']

                # text = f"<b>{location.address}</b>\n" \
                #        f"<b>🌡️ Temperate</b>: {temperature}° C\n<b>☁ Cloud Cover</b>: {cloud_cover}%\n<b>💦 " \
                #        f"Humidity</b>: {humidity}%\n<b>🛰️ Weather</b>: {weather_codes[str(conditions)]}\n\n💨 Wind " \
                #        f"gusts up to {wind_speed} m/s "\
                #        f""

                text = """
                Weather in {address} is '{condition}': 
                Temperature: {temperature}
                Cloud cover: {cloud_cover}
                Humidity: {humidity}
                Wind: {wind_speed}
                """.format(
                    address=location.address, temperature=temperature, cloud_cover=cloud_cover,
                    humidity=humidity, wind_speed=wind_speed, condition=weather_codes.get(str(conditions), "Unknown")
                )

            else:
                text = f"Unable to retrieve weather (error code {response.status_code})"

        dispatcher.utter_message(text=text)
        return []

# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
