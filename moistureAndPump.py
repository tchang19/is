# Write your code here :-)
# Write your code here :-)
import time
import board
from adafruit_seesaw.seesaw import Seesaw
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())
i2c_bus = board.I2C()
ss1 = Seesaw(i2c_bus, addr=0x36)
ss2 = Seesaw(i2c_bus, addr=0x37)

while True:
    prev_time = time.time()

    # read moisture level through capacitive touch pad
    touch1 = ss1.moisture_read()
    touch2 = ss2.moisture_read()

    # read temperature from the temperature sensor
    temp1 = ss1.get_temp()
    temp2 = ss2.get_temp()

    if touch1 <= 400:
        kit.motor1.throttle = 1.0
    else:
        kit.motor1.throttle = 0

    if touch2 <= 400:
        kit.motor2.throttle = 1.0
    else:
        kit.motor2.throttle = 0

    if prev_time != time.time():
        print("sensor 1 temp: " + str(temp1) + " | moisture: " + str(touch1))
        print("sensor 2 temp: " + str(temp2) + " | moisture: " + str(touch2) + "\n")

