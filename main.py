# SPDX-FileCopyrightText: 2021 Ladyada for Adafruit Industries
# SPDX-FileCopyrightText: 2022 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
import time
import ssl
from random import randint
import microcontroller
import socketpool
import wifi
import board
import neopixel
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT
from adafruit_seesaw.seesaw import Seesaw
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())
i2c_bus = board.I2C()
ss = Seesaw(i2c_bus, addr=0x36)

try:
    from secrets import secrets
except ImportError:
    print("WiFi and Adafruit IO credentials are kept in secrets.py - please add them there!")
    raise

# Add your Adafruit IO Username and Key to secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need to obtain your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

# WiFi
try:
    print("Connecting to %s" % secrets["ssid"])
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print("Connected to %s!" % secrets["ssid"])
# Wi-Fi connectivity fails with error messages, not specific errors, so this except is broad.
except Exception as e:  # pylint: disable=broad-except
    print("Failed to connect to WiFi. Error:", e, "\nBoard will hard reset in 30 seconds.")
    time.sleep(30)
    microcontroller.reset()



# Define callback functions which will be called when certain events happen.
def connected(client):
    print("Connected to Adafruit IO!")
    # Subscribe to Adafruit IO feed called "neopixel"
    client.subscribe("motor-control")


def message(client, feed_id, payload):  # pylint: disable=unused-argument
    print("Feed {0} received new value: {1}".format(feed_id, payload))
    if feed_id == "motor-control":
        kit.motor1.throttle = float(payload)


# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Initialize Adafruit IO MQTT "helper"
io = IO_MQTT(mqtt_client)

# Set up the callback methods above
io.on_connect = connected
io.on_message = message

timestamp = 0
while True:
    # read moisture level through capacitive touch pad
    touch = ss.moisture_read()

    # read temperature from the temperature sensor
    temp = ss.get_temp()

    if touch <= 400:
        kit.motor1.throttle = 1.0
    else:
        kit.motor1.throttle = 0

    try:
        # If Adafruit IO is not connected...
        if not io.is_connected:
            # Connect the client to the MQTT broker.
            print("Connecting to Adafruit IO...")
            io.connect()

        # Explicitly pump the message loop.
        io.loop()
        if (time.monotonic() - timestamp) >= 10:
            print("temp: " + str(temp) + "  moisture: " + str(touch))
            print("motor status: " + str(kit.motor1.throttle))
            io.publish("water", touch)
            io.publish("motor", kit.motor1.throttle)
            timestamp = time.monotonic()

    # Adafruit IO fails with internal error types and WiFi fails with specific messages.
    # This except is broad to handle any possible failure.
    except Exception as e:  # pylint: disable=broad-except
        print("Failed to get or send data, or connect. Error:", e,
              "\nBoard will hard reset in 30 seconds.")
        time.sleep(30)
        microcontroller.reset()

