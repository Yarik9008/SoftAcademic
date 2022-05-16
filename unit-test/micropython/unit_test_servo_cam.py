from machine import Pin, PWM
from time import sleep

servoPin = PWM(Pin(18))
servoPin.freq(50)

def servo(degrees):
    if degrees > 110:
        degrees=110
    if degrees < 40:
        degrees=40
    
    maxDuty=9000
    minDuty=1000
    
    newDuty=minDuty+(maxDuty-minDuty)*(degrees/180)
    servoPin.duty_u16(int(newDuty))
    
while True:
    servo(100)
    print("increasing -- 100")
    sleep(2)
    servo(40)
    print("increasing -- 40")
    sleep(2)


# протестированно 