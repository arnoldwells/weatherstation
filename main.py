import sys
import signal
import logging
import schedule
from time import sleep
from gpiozero import Button
from datetime import datetime
from data.env import pause, SLEEP_IMAGE, LOG_LEVEL
from modules.getimgai import getimg
from modules.display_image import show_image
from modules.mqtt_manager import MqttClient
from modules.weather_data import WeatherData                 # from modules.weather_data import WeatherData 
from modules.display_weather import show_weather
from modules.operations_handler import OperationsHandler

logger = logging.getLogger(__name__)
logging.basicConfig(filename='/tmp/weatherapp.log', level=LOG_LEVEL, 
                    format='%(asctime)s●%(name)s●%(levelname)s●%(message)s')            # delimiters: ⁑ ‖ ☀
sys.stderr.write = logging.critical                                                     # redirect stderr exceptions to logging # (Elasticsearch exceptions)

def scheduled_task():
    handler.art_images = getimg(current_weather.summary)                                # generate artimage
    handler.latest_file = handler.art_images[0][0]
    logger.info(f"handler.art_images: {handler.art_images}")
    logger.info(f"handler.latest_file: {handler.latest_file}")
    
schedule.every().day.at("09:01").do(scheduled_task)
button_a, button_b, button_c, button_d = Button(5), Button(6), Button(16), Button(24)

mqtt_client = MqttClient()
handler = OperationsHandler()
handler.get_latest_file()
button_a.when_pressed = handler.a_pressed
button_b.when_pressed = handler.b_pressed
button_c.when_pressed = handler.c_pressed
button_d.when_pressed = handler.d_pressed
signal.signal(signal.SIGINT, handler.int_handler)                                       # handle ctrl-c

while True:
    logger.info(f"start of loop - mode: <{handler.mode}>")
    schedule.run_pending()
    mqtt_client.read_lux_sensor()
    mqtt_client.publish_lux()  

    current_weather = WeatherData()
    current_weather.now = datetime.now() 
    current_weather.ow_request(mqtt_client.outside_conditions)                          # fetch openweather

    if "openweather" in current_weather.weather_source: 
        mqtt_client.publish_outside_data()

    now = int(current_weather.now.strftime("%H%M"))                                     # used by the while loop

    if now < 100: break                                                                 # exit after midnight
    
    elif handler.art_images and handler.iterations == 0:
        handler.iterations = 1                                                          # for total of 2 iterations 
        show_image(*handler.art_images.pop(0))                                          # unpack first tuple for (image, background)

    elif handler.iterations > 0: handler.iterations -= 1

    elif 700 < now:
        pause = 900                                                                     # 900 / 15
        handler.mode = "weather"

        current_weather.m5_date = mqtt_client.m5_date
        current_weather.m5_volts = mqtt_client.subscriptions["sensors/m5stack/voltage"]
        temp_humid_list = mqtt_client.get_sensor_data()

        show_weather(current_weather, temp_humid_list)

    logger.info(f"sleeping for {int(pause / 60)} minutes, "
                f"iterations: {handler.iterations}, " 
                f"images: {len(handler.art_images)}")
    sleep(pause)

show_image(SLEEP_IMAGE, background="white")
