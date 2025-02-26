import logging
from data.config import OPENWEATHERMAP_COORDS, OPENWEATHERMAP_API_KEY
from PIL import ImageFont

# variables
pause = 1800                                            # 30

# fonts
FONT_TH = ImageFont.truetype("fonts/Roboto-Medium.ttf", size=20)
FONT_TI = ImageFont.truetype("fonts/Roboto-Medium.ttf", size=21)
FONT_TJ = ImageFont.truetype("fonts/Roboto-Medium.ttf", size=22)
FONT_SM = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=27)
FONT_LG = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=40)

# constants
DEBUG = False
RAD = 140                                               # radius
INNER_ARC_RAD = 41                                      # inner arc
RADIAL_RAD = RAD - 36                                   # radial_radius
TEMP_RAD = RADIAL_RAD - 23                              # temp_radius
RADIAL_WIDTH = RADIAL_RAD - INNER_ARC_RAD               # radial_width
LOG_LEVEL = logging.INFO                                # DEBUG / INFO / WARNING / ERROR / CRITICAL
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (58, 91, 70)
WHITE = (255, 255, 255)
# ORANGE = (255,165,0)
ORANGE = (177,106,73)                                   # saturated palette
BCOLOR = 1                                              # white border                  # BCOLOR = 0 # black border
SATURATION = 1                                          # 0.5 default
BACKGROUND = "weather.png"
SLEEP_IMAGE = "images/inky-sleep.jpg"

# openweathermap
UNITS = "&units=metric"
EXCLUDES = "&exclude=minutely,alerts"                   # daily,hourly
FORECAST_URL = "https://api.openweathermap.org/data/3.0/onecall?"
REQUEST_URL = (FORECAST_URL + OPENWEATHERMAP_COORDS + OPENWEATHERMAP_API_KEY + UNITS + EXCLUDES)   

# getimg.ai and google drive               
GETIMGAI_URL = 'https://api.getimg.ai/v1' 
AUTH_SCOPE = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = "data/service_account.json"

# dictionaries
WEATHER_CODES = {
        "0d" :   "000",
        "0n" :   "000",
        "200d" : "200",
        "200n" : "200",
        "201d" : "200",
        "201n" : "200",
        "202d" : "200",
        "202n" : "200",
        "210d" : "200",
        "210n" : "200",
        "211d" : "200",
        "211n" : "200",
        "212d" : "200",
        "212n" : "200",
        "221d" : "200",
        "221n" : "200",
        "230d" : "200",
        "230n" : "200",
        "231d" : "200",
        "231n" : "200",
        "232d" : "200",
        "232n" : "200",
        "300d" : "300",
        "300n" : "300",
        "301d" : "300",
        "301n" : "300",
        "302d" : "300",
        "302n" : "300",
        "310d" : "300",
        "310n" : "300",
        "311d" : "300",
        "311n" : "300",
        "312d" : "312",
        "312n" : "312",
        "313d" : "312",
        "313n" : "312",
        "314d" : "314",
        "314n" : "314",
        "321d" : "314",
        "321n" : "314",
        "500d" : "312",
        "500n" : "312",
        "501d" : "312",
        "501n" : "312",
        "502d" : "314",
        "502n" : "314",
        "503d" : "314",
        "503n" : "314",
        "504d" : "314",
        "504n" : "314",
        "511d" : "615",
        "511n" : "615",
        "520d" : "520s",
        "520n" : "520n",
        "521d" : "521s",
        "521n" : "521n",
        "522d" : "521s",
        "522n" : "521n",
        "531d" : "521s",
        "531n" : "521n",
        "600d" : "600",
        "600n" : "600",
        "601d" : "600",
        "601n" : "600",
        "602d" : "602",
        "602n" : "602",
        "611d" : "615",
        "611n" : "615",
        "612d" : "612s",
        "612n" : "612n",
        "613d" : "612s",
        "613n" : "612n",
        "615d" : "615",
        "615n" : "615",
        "616d" : "615",
        "616n" : "615",
        "620d" : "620s",
        "620n" : "620s",
        "621d" : "620s",
        "621n" : "620n",
        "622d" : "622s",
        "622n" : "622n",
        "741d" : "741",
        "741n" : "741",
        "800d" : "800s",
        "800n" : "800n",
        "801d" : "801s",
        "801n" : "801n",
        "802d" : "801s",
        "802n" : "801n",
        "803d" : "801s",
        "803n" : "801n",
        "804d" : "805",
        "804n" : "805",
        "805d" : "805",
        "805n" : "805"
    }