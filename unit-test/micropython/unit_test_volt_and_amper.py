from machine import I2C, Pin, UART, PWM, ADC


class TNPA_Acp:
    # TODO  при получении плат провести калибровку датчиков
    def __init__(self):
        # инициализация аналоговых датчиков
        self.amper = ADC(Pin(28)) 
        self.volt = ADC(Pin(27)) 



    def Reqest(self):
        # TODO  матан для перевода значений - отсылается уже в амперах
        massout = {}
        massout['amper'] = round((self.amper.read_u16()-50100)/ 850, 2)
        #massout['amper'] = self.volt.read_u16()
        massout['volt'] = round((self.volt.read_u16() * 5) / 9256, 2)
        return massout


a = TNPA_Acp()
print(a.Reqest())

# протестированно
