import logging
import requests
from datetime import datetime
from data.env import REQUEST_URL

logger = logging.getLogger(__name__)

class WeatherData:
    def __init__(self):
        logger.info(f"instantiating object of class: {self.__class__.__name__}")
        self.summary = "nice weather"
        self.rain = False  
          
    def set_defaults(self):
        self.uv_high = 0
        self.wind_deg = 360
        self.wind_speed = 0
        self.sunset = datetime.fromtimestamp(1704139200)                                # 20:00
        self.sunrise_0 = datetime.fromtimestamp(1704096000)                             # 08:00
        self.sunrise_1 = datetime.fromtimestamp(1704153600)                             # 00:00
        self.weather_source = ["error"]
        self.forecast = {
            'daily': [
                {
                    'temp': {'min': -1, 'max': -1},
                    'weather': [{'id': 0}]
                }
                for _ in range(5)
            ],
            'hourly': [
                {
                    'dt': 1704110400 + (hour * 3600),
                    'pop': 0,
                    'uvi': 0,
                    'temp': -1,
                    'weather': [{'id': 0}]
                }
                for hour in range(12)
            ]
        }
        logger.debug(self.forecast)

    def ow_request(self, outside_conditions):                                           # request forecast from api.openweathermap
        try:                                                   
            response = requests.get(REQUEST_URL)
            self.forecast = response.json() 
            assert 'current' in self.forecast.keys()
        except AssertionError:
            self.summary = f"{self.forecast['cod']}:{self.forecast['message']}"[:80]    # truncate response message
            self.set_defaults()
        except Exception as error: 
            self.summary = f"api.openweathermap.org error\n{error}"
            self.set_defaults()
        else:
            self.weather_source = ["openweather"]
            self.uv_high = self.forecast['daily'][0]['uvi']
            self.wind_deg = (180 - self.forecast['current']['wind_deg']) % 360
            self.wind_speed = self.forecast['current']['wind_speed']      
            self.sunset = datetime.fromtimestamp(self.forecast['daily'][0]['sunset'])
            self.sunrise_0 = datetime.fromtimestamp(self.forecast['daily'][0]['sunrise'])
            self.sunrise_1 = datetime.fromtimestamp(self.forecast['daily'][1]['sunrise'])
            
            summaries = (self.forecast['daily'][0]['summary'], 
                         "+" + self.forecast['daily'][1]['summary'])
            day = int(self.now.strftime("%H")) // 20
            self.summary = summaries[day]                                               # use summary from today/tomorrow
            
            outside_conditions["humidity"] = self.forecast['current']['humidity']
            outside_conditions["temperature"] = self.forecast['current']['temp']
            logger.info(f"set outside_conditions to: {outside_conditions}")
        finally:
            try: logger.info(f"ow_request response status code: {response.status_code}")
            except: pass
