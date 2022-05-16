import board
import neopixel
from time import sleep

'''
num_pixels = 30
 

pixels = neopixel.NeoPixel(board.GP15, num_pixels)
pixels.brightness = 0.5
 
while True:
    pixels.fill((10, 0, 0))
    sleep(2)
    pixels.fill((0,10,0))
    sleep(2)
    pixels.fill((0,0,10))
    sleep(2)
'''

class TNPA_Neopix:
    def __init__(self):
        # установка кол-во пикселей
        num_pixels = 6
        # установка мощности 0-100
        self.output_power = 100
        self.pixels = neopixel.NeoPixel(board.GP15, num_pixels)
        self.pixels.brightness = 0.5

        for pix in range(6):
            self.pixels[pix] = (0,0,255)
            sleep(0.1)
            self.pixels[pix] = (0,0,0)
            
        for pix in range(6):
            self.pixels[5 - pix] = (0,255,0)
            sleep(0.1)
            self.pixels[5 - pix] = (0,0,0)
        self.pixels.fill((255,0,0))
        sleep(0.5)
        self.pixels.fill((0,255,0))
        sleep(0.5)
        self.pixels.fill((0,0,255))
        sleep(0.5)
        self.pixels.fill((0,0,0))


    
    def show_debag_motor(self, data:dict):
        m0 = data['motor0'] * 5
        m1 = data['motor1'] * 5
        m2 = data['motor2'] * 5
        m3 = data['motor3'] * 5
        m4 = data['motor4'] * 5
        m5 = data['motor5'] * 5

        mass = [m0, m1, m2, m3, m4, m5]

a = TNPA_Neopix()