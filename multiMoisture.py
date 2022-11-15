# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board

from adafruit_seesaw.seesaw import Seesaw

i2c_bus = board.I2C()

ss1 = Seesaw(i2c_bus, addr=0x36)
ss2 = Seesaw(i2c_bus, addr=0x37)

while True:
    # read moisture level through capacitive touch pad
    touch1 = ss1.moisture_read()
    touch2 = ss2.moisture_read()

    # read temperature from the temperature sensor
    temp1 = ss1.get_temp()
    temp2 = ss2.get_temp()

    print("sensor 1 temp: " + str(temp1) + " | moisture: " + str(touch1))
    print("sensor 2 temp: " + str(temp2) + " | moisture: " + str(touch2) + "\n")
    time.sleep(1)
