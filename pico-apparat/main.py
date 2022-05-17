from machine import I2C, Pin, UART, PWM, ADC
from math import pi, atan2
from time import sleep

### INIT CONFIG ###
# отладочные выводы
DEBAG = True
# опрос вольтматра и амперметра
CHECK_SENSOR = True
# использование адресных светодиодов
CHECK_NEOPIX = False
# использование датчика глубины
CHECK_DEPT_AND_TEMP = False
# использование датчика ориентации
CHECK_SENSOR_ORIENTATION = False
###################

if CHECK_NEOPIX:
    from neopixel import Neopixel

if CHECK_DEPT_AND_TEMP:
    import ms5837

if CHECK_SENSOR_ORIENTATION:
    from mpu9250 import MPU9250


class TNPA_SerialPort:
    def __init__(self):
        self.serial_port = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17))
        self.check_cor = False
        
    def receiver_data(self):
        global DEBUG
        '''прием информации с поста управления'''
        data = None
        while data == None or data == b'':
            try:
                data = self.serial_port.read(100)
            except: pass


        try:
            self.check_cor = True
            return list(map(lambda x: float(x), str(data)[3:-4].split(', ')))
            
        except:
            self.check_cor = False
            return None
            
    def dispatch_data(self, data: list = [0, 0, 0, 0]):
        '''Отправка телеметрии на пост управления'''
        try:
            if self.check_cor:
                self.serial_port.write((f'{str(data)}\n').encode())
        except: pass


class TNPA_PwmControl:
    '''управление двигателями, сервоприводами, светильниками с помощью PWM'''

    def pwm_motor_out(self, pin, command):  # пересчет в диапазоне 0-100
        # 50 среднее положение стоим
        if command > 100:
            command = 100
        if command < 0:
            command = 0
        # set max and min duty
        maxDuty = 6650
        minDuty = 3000
        # new duty is between min and max duty in proportion to its value
        newDuty = minDuty+(maxDuty-minDuty)*(command/100)
        # servo PWM value is set
        pin.duty_u16(int(newDuty))

    def pwm_servo_out(self, pin, degrees):
        if degrees > 180:
            degrees = 180
        if degrees < 0:
            degrees = 0
        
        maxDuty=9000
        minDuty=1000
        
        newDuty=minDuty+(maxDuty-minDuty)*(degrees/180)
        pin.duty_u16(int(newDuty))

    def __init__(self):
        # диапазон шим модуляции
        self.pwmMin = 1000
        self.pwmMax = 2000
        self.massPinOut = [Pin(4), Pin(5),
                           Pin(6), Pin(7),
                           Pin(8), Pin(9)]
        # коофиценты корректировки мощности на каждый мотор
        self.CorDrk0 = 1
        self.CorDrk1 = 1
        self.CorDrk2 = 1
        self.CorDrk3 = 1
        self.CorDrk4 = 1
        self.CorDrk5 = 1
        # инициализация плат
        self.drk0 = PWM(self.massPinOut[0])
        self.drk0.freq(50)
        self.drk1 = PWM(self.massPinOut[1])
        self.drk0.freq(50)
        self.drk2 = PWM(self.massPinOut[2])
        self.drk2.freq(50)
        self.drk3 = PWM(self.massPinOut[3])
        self.drk3.freq(50)
        self.drk4 = PWM(self.massPinOut[4])
        self.drk4.freq(50)
        self.drk5 = PWM(self.massPinOut[5])
        self.drk5.freq(50)

        self.mass_motor = [self.drk0, self.drk1,
                           self.drk2, self.drk3, self.drk4, self.drk5]

        # взаимодействие с манипулятором
        self.man = PWM(Pin(19))
        self.man.freq(50)
        self.pwm_servo_out(self.man, 0)

        # взаимодействие с сервоприводом камеры
        self.cam = PWM(Pin(18))
        self.man.freq(50)
        self.pwm_servo_out(self.cam, 90)

        # взаимодействие с светильником
        self.led = PWM(Pin(26))
        self.led.freq(50)
        self.pwm_servo_out(self.led, 90)

        # инициализация моторов
        self.pwm_motor_out(self.drk0, 50)
        self.pwm_motor_out(self.drk1, 50)
        self.pwm_motor_out(self.drk2, 50)
        self.pwm_motor_out(self.drk3, 50)
        self.pwm_motor_out(self.drk4, 50)
        self.pwm_motor_out(self.drk5, 50)
        sleep(3)

    def ControlMotor(self, mass: list = [50, 50, 50, 50, 50, 50]):
        print(mass)
        try:
            # установка шим моторов
            self.pwm_motor_out(self.drk0, mass[0])
            self.pwm_motor_out(self.drk1, mass[1])
            self.pwm_motor_out(self.drk2, mass[2])
            self.pwm_motor_out(self.drk3, mass[3])
            self.pwm_motor_out(self.drk4, mass[4])
            self.pwm_motor_out(self.drk5, mass[5])
        except:
            print('error-motor')
            pass

    def ControlCamera(self, command: int = 90):
        try:
            # установка шим манипулятора
            self.pwm_servo_out(self.cam, int(command))
        except:
            pass

    def ControlMan(self, command: int = 0):
        try:
            # установка шим сервопривода камеры
            self.pwm_servo_out(self.man, int(command))
        except:
            pass

    def ControlLed(self, command: int = 0):
        try:
            # установка шим светильника
            if command:
                self.pwm_servo_out(self.led, 180)
            else:
                self.pwm_servo_out(self.led, 0)
        except:
            pass


class TNPA_Neopix:
    def __init__(self):
        # установка кол-во пикселей
        num_pixels = 6
        # установка мощности 0-100
        self.output_power = 100
        self.pixels = NeoPixel(Pin(15), num_pixels)
        self.pixels.brightness = 0.5

        for pix in range(6):
            self.pixels[pix] = (0, 0, 255)
            sleep(0.1)
            self.pixels[pix] = (0, 0, 0)
            self.pixels.write()

        for pix in range(6):
            self.pixels[5 - pix] = (0, 255, 0)
            sleep(0.1)
            self.pixels[5 - pix] = (0, 0, 0)
            self.pixels.write()

        for pix in range(6):
            self.pixels[pix] = (255, 0, 0)
        self.pixels.write()
        sleep(0.2)
        for pix in range(6):
            self.pixels[pix] = (0, 255, 0)
        self.pixels.write()
        sleep(0.2)
        for pix in range(6):
            self.pixels[pix] = (0, 0, 255)
        self.pixels.write()
        sleep(0.2)
        for pix in range(6):
            self.pixels[pix] = (0, 0, 0)
        self.pixels.write()

    def show_debag_motor(self, data:list=[0,0,0,0,0,0]):
        try:
            m0 = ((data[0] - 50) * 5 * (self.output_power // 100)) // 1
            m1 = ((data[1] - 50) * 5 * (self.output_power // 100)) // 1
            m2 = ((data[2] - 50) * 5 * (self.output_power // 100)) // 1
            m3 = ((data[3] - 50) * 5 * (self.output_power // 100)) // 1
            m4 = ((data[4] - 50) * 5 * (self.output_power // 100)) // 1
            m5 = ((data[5] - 50) * 5 * (self.output_power // 100)) // 1
        except:
            m0, m1, m2, m3, m4, m5 = 0, 0, 0, 0, 0, 0
        mass = [m0, m1, m2, m3, m4, m5]
        # print(mass)
        for i in range(6):
            if mass[i] < 0:
                self.pixels[i] = (mass[i] * -1, 0, 0)
            elif mass[i] > 0:
                self.pixels[i] = (0, mass[i], 0)
            else:
                self.pixels[i] = (0, 0, 0)
        self.pixels.write()


class TNPA_Acp:
    # TODO  при получении плат провести калибровку датчиков
    def __init__(self):
        # инициализация аналоговых датчиков
        self.amper = ADC(Pin(28))
        self.volt = ADC(Pin(27))

    def reqiest(self):
        # TODO  матан
        massout = []
        massout.append(round((self.volt.read_u16() * 5) / 9256, 2))
        massout.append(round((self.amper.read_u16()-50100) / 850, 2))

        return massout


class TNPA_Depth_and_term:
    # TODO  при получении плат провести калибровку датчиков
    def __init__(self):
        self.sensor = ms5837.MS5837_30BA()
        density = 1000
        # илициализация сенсора
        self.sensor = ms5837.MS5837_30BA()
        if self.sensor.init():
            self.sensor.setFluidDensity(ms5837.DENSITY_SALTWATER)
            self.sensor.setFluidDensity(density)

    def reqiest(self):
        # опрос датчика давления
        if self.sensor.read():
            massout = []
            massdepth = [self.sensor.depth() for i in range(100)]
            masstemp = [self.sensor.temperature() for i in range(100)]
            massout.append(round(sum(massdepth) / 100, 3))
            massout.append(round(sum(masstemp) / 100, 3))
            return massout
        else:
            return [-100, -100]


class TNPA_Orientation:
    def __init__(self):
        i2c = I2C(1, scl=Pin(3), sda=Pin(2))
        self.sensor = MPU9250(i2c)

    def reqiest(self):
        data = self.sensor.gyro
        return[(round((atan2(data[0], data[1]) * 180 / pi), 3))]


class TNPA_ReqiestSensor:
    '''класс-адаптер обьеденяющий в себе сбор информации с всех сенсоров'''

    def __init__(self):
        global CHECK_DEPT_AND_TEMP, CHECK_SENSOR_ORIENTATION
        self.acp = TNPA_Acp()  # обект класса ацп
        if CHECK_DEPT_AND_TEMP:
            self.dept_and_temp = TNPA_Depth_and_term()
        if CHECK_SENSOR_ORIENTATION:
            self.orientation = TNPA_Orientation()

    def reqiest(self):
        global CHECK_DEPT_AND_TEMP, CHECK_SENSOR_ORIENTATION
        # опрос датчиков; возвращает обьект класса словарь
        acp = self.acp.reqiest()
        if CHECK_DEPT_AND_TEMP:
            depth_temp = self.dept_and_temp.reqiest()
        else:
            depth_temp = [-100, -100]
        if CHECK_SENSOR_ORIENTATION:
            orientation = self.orientation.reqiest()
        else:
            orientation = [0]

        return acp + depth_temp + orientation




class MainApparat:
    def __init__(self):
        global CHECK_NEOPIX, CHECK_SENSOR
        # массив отсылаемый на аппарат
        self.DataOutput = [0, 0, 0, 0, 0]
        # создание экземпляра класса для общения по uart
        self.serial_port = TNPA_SerialPort()
        # создание экземляра класса для управления полузной нагрузкой по шим
        self.comandor = TNPA_PwmControl()
        if CHECK_NEOPIX:
            # создание экземпляра класса для работя с адресными светодиодами
            self.neopix_led = TNPA_Neopix()
        if CHECK_SENSOR:
            # создание экземпляра класса для опроса датчиков
            self.sensor = TNPA_ReqiestSensor()

    def RunMainApparat(self):
        '''
        - прием информации с поста управления 
        - отработка по принятой информации 
        - сбор информации с датчиков 
        - отправка телеметрии на пост управления
        '''
        if DEBAG:
            print('start_code')
        while True:
            # прием информации с поста управления
            try:
                data = self.serial_port.receiver_data()
            except:
                data = None
            if data == None:
                # если не принято корректной информации то возвращаем все в начальное положение
                data = [50, 50, 50, 50, 50, 50, 90, 0, 0, 0]
            # отправка управляющих сигналов  на полузную нагрузку
            self.comandor.ControlMotor(data[:6])
            self.comandor.ControlCamera(data[6])
            self.comandor.ControlMan(data[7])
            self.comandor.ControlLed(data[8])
            if CHECK_NEOPIX:
                # отпарвка принятого массива на адресные светодиоды
                self.neopix_led.show_debag_motor(data[:6])
            if CHECK_SENSOR:
                # сбор информации с датчиков и отправка на пост управления
                self.serial_port.dispatch_data(self.sensor.reqiest())
            else:
                self.serial_port.dispatch_data([0, 0, 0, 0, 0])


if __name__ == '__main__':
    apparat = MainApparat()
    apparat.RunMainApparat()
