from machine import Pin, PWM
from time import sleep

servoPin = PWM(Pin(4))
servoPin.freq(50)

def servo(degrees): # пересчет в диапазоне 0-100
    #50 среднее положение стоим
    if degrees > 100: degrees=100
    if degrees < 0: degrees=0
    # set max and min duty
    maxDuty=6650
    minDuty=3000
    # new duty is between min and max duty in proportion to its value
    newDuty=minDuty+(maxDuty-minDuty)*(degrees/100)
    # servo PWM value is set
    servoPin.duty_u16(int(newDuty))

# разблокировка моторов 
servo(50)
sleep(2)


while True:
    for degree in range(0,51,1):
        servo(degree)
        sleep(0.25)
        print("increasing -- "+str(degree))
    sleep(5)
    for degree in range(50,100,1):
        servo(degree)
        sleep(0.25)
        print("increasing -- "+str(degree))
    sleep(5)
  # start decreasing loop
    for degree in range(100, 50, -1):
        servo(degree)
        sleep(0.25)
        print("decreasing -- "+str(degree))
    sleep(5)
    for degree in range(50, 0, -1):
        servo(degree)
        sleep(0.25)
        print("decreasing -- "+str(degree))
    sleep(5)
        

# не протестированно
exce