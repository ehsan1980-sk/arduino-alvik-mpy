from arduino_alvik import ArduinoAlvik
from time import sleep_ms
import sys

alvik = ArduinoAlvik()

alvik.run()
sleep_ms(100)
alvik.reset_hw()


while True:
    try:
        alvik.set_speed(10, 10)
        sleep_ms(1000)

        alvik.set_speed(30, 60)
        sleep_ms(1000)

        alvik.set_speed(60, 30)
        sleep_ms(1000)
    except KeyboardInterrupt as e:
        print('over')
        alvik.set_speed(0, 0)
        sys.exit()
