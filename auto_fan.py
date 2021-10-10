import sys
import os
import time
import machine
import micropython
from dht import DHT11
from oled import SSD1306_I2C

#
# init 
#
time.sleep_ms(2000)
print('auto fan v1 .1)')

MIN_TEMP = 35
MAX_TEMP = 45
FAN_HIGH = 100
FAN_LOW = 30
FAN_OFF = 0

# onboard led
pin_led = machine.Pin(25, machine.Pin.OUT)

# pwm for fan
pin_pwm = machine.Pin(26, machine.Pin.OUT)
pwm = machine.PWM(pin_pwm)

# temperature sensor
pin_dht = machine.Pin(22, machine.Pin.OUT, machine.Pin.PULL_DOWN)
dht = DHT11(pin_dht)

# oled on i2c
WIDTH  = 128                                            
HEIGHT = 32 
i2c = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16), freq=200000)       # Init I2C using pins GP8 & GP9 (default I2C0 pins)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def get_temperature():
    temperature = 100
    for i in range(1, 11):
        try:
            temperature = dht.temperature
            break
        except Exception:
            # print(f'retry {i}')
            time.sleep_ms(i * 50)
    return temperature    


def get_humidity():
    humidity = 100
    for i in range(1, 11):
        try:
            humidity = dht.humidity
            break
        except Exception:
            # print(f'retry {i}')
            time.sleep_ms(i * 50)
    return humidity 

def print_oled(speed, temperature=None, humidity=None):
    if temperature is None:
        temperature = get_temperature()
    if humidity is None:
        humidity = get_humidity()
    oled.fill(0)
    oled.text(f'{temperature:.1f}', 0, 0)
    oled.text(" C", 30, 0)
    oled.text(f'{humidity:.0f}', 70, 0)
    oled.text(" %", 100, 0)
    oled.text("fan", 0, 20)
    oled.text(str(speed), 70, 20)
    oled.text(" %", 100, 20)
    oled.show()

# speed : 0 .. 100
def set_fan_speed(speed):
    # print('debug speed:', speed)
    if speed > 100:
        speed = 100
    elif speed < 20:
        speed = 0

    pwm_duty = (65025 * speed) // 100
    pwm.duty_u16(pwm_duty)

#
# debug and self test
#
print('sys version', sys.version)
print('files:', os.listdir())
print(f"Temperature: {dht.temperature}")
print(f"Humidity: {dht.humidity}")
try:
    print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
    print("I2C Configuration: "+str(i2c))
except Exception:
    print('error i2c bus. is the display connected?')   

print('increase fan speed...')
for speed in range(0, 101, 20):
    set_fan_speed(speed)
    print_oled(speed)
    time.sleep_ms(200)

print('decrease fan speed...')
for speed in range(100, -1, -20):
    set_fan_speed(speed)
    print_oled(speed)
    time.sleep_ms(200)


def handleFanSpeed(debug=False):
    temperature = get_temperature()

    if temperature < MIN_TEMP:
        speed = FAN_OFF
    elif temperature > MAX_TEMP:
        speed = FAN_HIGH

    else:
        step = (FAN_HIGH - FAN_LOW) / (MAX_TEMP - MIN_TEMP)   
        speed = FAN_LOW  +  round((temperature - MIN_TEMP) * step)
    
    set_fan_speed(speed)

    print_oled(speed, temperature=temperature)

    if debug:
        print('debug temperature / speed:', temperature, speed)

    return 

#
# main
#
print('main programm started')
while True:
    handleFanSpeed(debug=False)
    pin_led.toggle()
    time.sleep_ms(2000)