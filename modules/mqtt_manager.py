import board
import logging
import adafruit_bh1750  
from datetime import datetime
from paho.mqtt import client as mqtt
from data.config import PORT, MQTT_BROKER, CLIENT_ID, USERNAME, PASSWORD

logger = logging.getLogger(__name__)

class MqttClient:

    def __init__(self):
        self.lux = 0
        self.m5_date = datetime(2020, 1, 1)
        self.outside_conditions = {
            "humidity": 0,
            "temperature": 0
        }
        self.subscriptions = {
            "sensors/livingroom/humidity": 0,
            "sensors/livingroom/temperature": 0,
            "sensors/bedroom/humidity": 0,
            "sensors/bedroom/temperature": 0,
            "sensors/m5stack/humidity": 0,
            "sensors/m5stack/temperature": 0,
            "sensors/m5stack/voltage": 0,
        }
        self.client = mqtt.Client(client_id=CLIENT_ID)
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connected = False
        self.client.loop_start()
        self.client.connect(MQTT_BROKER, PORT)

    def on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            logger.info("mqtt connected")
            client.connected = True
            for topic in self.subscriptions.keys():
                client.subscribe(topic)        
        else:
            logger.error(f"mqtt could not connect, return code: {return_code}")
            client.connected = False

    def get_sensor_data(self):
        return [(self.outside_conditions["temperature"],
                 self.outside_conditions["humidity"]
        ),
                (self.subscriptions["sensors/bedroom/temperature"],
                 self.subscriptions["sensors/bedroom/humidity"]
        ),
                (self.subscriptions["sensors/m5stack/temperature"],
                 self.subscriptions["sensors/m5stack/humidity"]
        ),
                (self.subscriptions["sensors/livingroom/temperature"],
                 self.subscriptions["sensors/livingroom/humidity"]
        )]

    def read_lux_sensor(self):
        try:
            i2c = board.I2C()                                   # uses board.SCL and board.SDA  # i2c = busio.I2C(board.SCL, board.SDA)
            bh1750 = adafruit_bh1750.BH1750(i2c)
            self.lux = bh1750.lux
        except Exception as e:
            logger.error(f"Exception: bh1750 sensor not working {e}")

    def publish(self, value, topic):
        try:
            assert self.client.connected
            self.client.publish(topic,'%0.1f' %(value))                                 # retain=True
            logger.info(f"published: {topic} {value}")
        except AssertionError:
            logger.error("mqtt broker not connected")
        except Exception as e:
            logger.error(f"Exception {e}")

    def publish_outside_data(self):
        self.publish(self.outside_conditions["humidity"], "sensors/outside/humidity")
        self.publish(self.outside_conditions["temperature"], "sensors/outside/temperature")

    def publish_lux(self):
        self.publish(self.lux, "sensors/livingroom/lux")

    def on_message(self, client, userdata, message):
        topic = message.topic
        value = str(message.payload.decode("utf-8"))
        logger.info(f"received: {topic} {value}")
        self.subscriptions[topic] = float(value)
        if topic == "sensors/m5stack/voltage": self.m5_date = datetime.now()
