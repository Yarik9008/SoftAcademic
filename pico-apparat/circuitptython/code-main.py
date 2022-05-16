from time import sleep
import board
import busio
import pwmio
import neopixel
from adafruit_motor import servo
from analogio import AnalogIn

### INIT CONFIG ###
# отладочные выводы
DEBAG = False
# опрос вольтматра и амперметра
CHECK_SENSOR = True
# использование адресных светодиодов
CHECK_NEOPIX = True
###################


def literal_eval(data):
    '''Функция-парсер принятых данных'''
    data = ''.join([chr(b) for b in data])[1:-2]
    data = [i.strip().split(':') for i in (str(data)).split(',')]
    print(data)
    dataout = {}
    for a in data:
        try:
            dataout[a[0][1:-1]] = int(a[1].strip())
        except ValueError:
            try:
                dataout[a[0][1:-1]] = float(a[1].strip())
            except ValueError:
                try:
                    dataout[a[0][1:-1]] = bool(a[1].strip())
                except:
                    dataout[a[0][1:-1]] = str(a[1].strip())
    return dataout


class TNPA_Neopix:
    def __init__(self):
        # установка кол-во пикселей
        num_pixels = 6
        # установка мощности 0-100
        self.output_power = 100
        self.pixels = neopixel.NeoPixel(board.GP15, num_pixels)
        self.pixels.brightness = 0.5

        for pix in range(6):
            self.pixels[pix] = (0, 0, 255)
            sleep(0.1)
            self.pixels[pix] = (0, 0, 0)

        for pix in range(6):
            self.pixels[5 - pix] = (0, 255, 0)
            sleep(0.1)
            self.pixels[5 - pix] = (0, 0, 0)

        self.pixels.fill((255, 0, 0))
        sleep(0.2)
        self.pixels.fill((0, 255, 0))
        sleep(0.2)
        self.pixels.fill((0, 0, 255))
        sleep(0.2)
        self.pixels.fill((0, 0, 0))

    def show_debag_motor(self, data: dict):
        try:
            m0 = ((data['motor0'] - 50) * 5 * (self.output_power // 100)) // 1
            m1 = ((data['motor1'] - 50) * 5 * (self.output_power // 100)) // 1
            m2 = ((data['motor2'] - 50) * 5 * (self.output_power // 100)) // 1
            m3 = ((data['motor3'] - 50) * 5 * (self.output_power // 100)) // 1
            m4 = ((data['motor4'] - 50) * 5 * (self.output_power // 100)) // 1
            m5 = ((data['motor5'] - 50) * 5 * (self.output_power // 100)) // 1
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


class TNPA_SerialPort:
    def __init__(self):
        self.serial_port = busio.UART(
            board.GP16, board.GP17,
            baudrate=115200)

    def receiver_data(self):
        '''прием информации с поста управления'''
        data = self.serial_port.readline()
        if len(data) == 0:
            if DEBAG:
                print(None)
            return None
        else:
            return literal_eval(data)

    def dispatch_data(self, data: dict):
        '''Отправка телеметрии на пост управления'''
        self.serial_port.write((str(data)).encode())


class TNPA_PwmControl:
    '''управление двигателями, сервоприводами, светильниками с помощью PWM'''
    def __init__(self):
        # диапазон шим модуляции
        self.pwmMin = 1000
        self.pwmMax = 2000
        self.massPinOut = [
            board.GP4,
            board.GP5,
            board.GP6,
            board.GP7,
            board.GP8,
            board.GP9,
        ]
        # коофиценты корректировки мощности на каждый мотор
        self.CorDrk0 = 1
        self.CorDrk1 = 1
        self.CorDrk2 = 1
        self.CorDrk3 = 1
        self.CorDrk4 = 1
        self.CorDrk5 = 1
        # инициализация платы
        self.pwm0 = pwmio.PWMOut(self.massPinOut[0], frequency=50)
        self.drk0 = servo.ContinuousServo(
            self.pwm0, min_pulse=self.pwmMin, max_pulse=self.pwmMax)
        self.pwm1 = pwmio.PWMOut(self.massPinOut[1], frequency=50)
        self.drk1 = servo.ContinuousServo(
            self.pwm1, min_pulse=self.pwmMin, max_pulse=self.pwmMax)
        self.pwm2 = pwmio.PWMOut(self.massPinOut[2], frequency=50)
        self.drk2 = servo.ContinuousServo(
            self.pwm2, min_pulse=self.pwmMin, max_pulse=self.pwmMax)
        self.pwm3 = pwmio.PWMOut(self.massPinOut[3], frequency=50)
        self.drk3 = servo.ContinuousServo(
            self.pwm3, min_pulse=self.pwmMin, max_pulse=self.pwmMax)
        self.pwm4 = pwmio.PWMOut(self.massPinOut[4], frequency=50)
        self.drk4 = servo.ContinuousServo(
            self.pwm4, min_pulse=self.pwmMin, max_pulse=self.pwmMax)
        self.pwm5 = pwmio.PWMOut(self.massPinOut[5], frequency=50)
        self.drk5 = servo.ContinuousServo(
            self.pwm5, min_pulse=self.pwmMin, max_pulse=self.pwmMax)

        self.mass_motor = [self.drk0, self.drk1,
                           self.drk2, self.drk3, self.drk4, self.drk5]

        # взаимодействие с манипулятором
        self.pwm_man = pwmio.PWMOut(
            board.GP19, duty_cycle=2 ** 15, frequency=50)
        self.man = servo.Servo(self.pwm_man)
        self.man.angle = 0

        # взаимодействие с сервоприводом камеры
        self.pwm_cam = pwmio.PWMOut(
            board.GP18, duty_cycle=2 ** 15, frequency=50)
        self.cam = servo.Servo(self.pwm_man)
        self.cam.angle = 90

        # взаимодействие с светильником
        self.pwm_led = pwmio.PWMOut(
            board.GP26, duty_cycle=2 ** 15, frequency=50)
        self.led = servo.Servo(self.pwm_man)
        self.led.angle = 0

        # for mot in self.mass_motor:

        # инициализация моторов
        self.drk0.throttle = 1.0
        self.drk1.throttle = 1.0
        self.drk2.throttle = 1.0
        self.drk3.throttle = 1.0
        self.drk4.throttle = 1.0
        self.drk5.throttle = 1.0
        sleep(2)
        self.drk0.throttle = -1.0
        self.drk1.throttle = -1.0
        self.drk2.throttle = -1.0
        self.drk3.throttle = -1.0
        self.drk4.throttle = -1.0
        self.drk5.throttle = -1.0
        sleep(2)
        self.drk0.throttle = 0.0
        self.drk1.throttle = 0.0
        self.drk2.throttle = 0.0
        self.drk3.throttle = 0.0
        self.drk4.throttle = 0.0
        self.drk5.throttle = 0.0
        sleep(3)

    def ControlMotor(self, mass: dict):
        try:
            # установка шим моторов
            self.drk0.throttle = mass['motor0'] * 0.02 - 1
            self.drk1.throttle = mass['motor1'] * 0.02 - 1
            self.drk2.throttle = mass['motor2'] * 0.02 - 1
            self.drk3.throttle = mass['motor3'] * 0.02 - 1
            self.drk4.throttle = mass['motor4'] * 0.02 - 1
            self.drk5.throttle = mass['motor5'] * 0.02 - 1
        except:
            print('error-motor')
            pass

    def ControlCamera(self, mass: dict):
        try:
            # установка шим манипулятора
            self.cam.angle = mass['servoCam']
        except:
            pass

    def ControlMan(self, mass: dict):
        try:
            # установка шим сервопривода камеры
            self.man.angle = mass['man']
        except:
            pass

    def ControlLed(self, mass: dict):
        try:
            # установка шим светильника
            if mass['led']:
                self.led.angle = 180
            else:
                self.led.angle = 0
        except:
            pass


class TNPA_Acp:
    # TODO  при получении плат провести калибровку датчиков
    def __init__(self):
        # инициализация аналоговых датчиков
        self.amper = AnalogIn(board.GP28)
        self.volt = AnalogIn(board.GP27)

    def ReqestAmper(self):
        # TODO  матан для перевода значений - отсылается уже в амперах
        massout = {}
        massout['amper'] = self.volt.value
        massout['volt'] = self.amper.value
        return massout


class TNPA_ReqiestSensor:
    '''класс-адаптер обьеденяющий в себе сбор информации с всех сенсоров'''
    def __init__(self):
        self.acp = TNPA_Acp()  # обект класса ацп

    def reqiest(self):
        # опрос датчиков; возвращает обьект класса словарь
        massacp = self.acp.ReqestAmper()
        return massacp


class MainApparat:
    # TODO 
    def __init__(self):
        global CHECK_NEOPIX, CHECK_SENSOR
        self.DataInput = {'led': False,  # управление светом
                          'man': 0,  # Управление манипулятором
                          'servoCam': 0,  # управление наклоном камеры
                          'motor0': 0, 'motor1': 0,  # значения мощности на каждый мотор
                          'motor2': 0, 'motor3': 0,
                          'motor4': 0, 'motor5': 0}
        # массив отсылаемый на аппарат
        self.DataOutput = {'volt': 0, 'amper': 0}
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
                data = {'led': False,  # управление светом
                        'man': 0,  # Управление манипулятором
                        'servoCam': 0,  # управление наклоном камеры
                        'motor0': 0, 'motor1': 0,  # значения мощности на каждый мотор
                        'motor2': 0, 'motor3': 0,
                        'motor4': 0, 'motor5': 0}
            # отправка управляющих сигналов  на полузную нагрузку
            self.comandor.ControlMotor(data)
            self.comandor.ControlCamera(data)
            self.comandor.ControlMan(data)
            self.comandor.ControlLed(data)
            if CHECK_NEOPIX:
                # отпарвка принятого массива на адресные светодиоды
                self.neopix_led.show_debag_motor(data)
            if CHECK_SENSOR:
                # сбор информации с датчиков и отправка на пост управления
                self.serial_port.dispatch_data(self.sensor.reqiest())
            else:
                self.serial_port.dispatch_data({'amper': 0, 'volt': 0})


if __name__ == '__main__':
    apparat = MainApparat()
    apparat.RunMainApparat()
