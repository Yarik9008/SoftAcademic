import os
import pygame
import logging
import threading
import configparser
from time import sleep
from datetime import datetime
import serial

DEBUG = False
PATH_CONFIG = '/home/rock/SoftAcademic/raspberry-pult/config_rov.ini'
PATH_LOG = '/home/rock/SoftAcademic/raspberry-pult/log/PULT_LOG_' + \
            '-'.join('-'.join('-'.join(str(datetime.now()).split()
                                       ).split('.')).split(':')) + '.log'

class PULT_Logging:
    '''Класс отвечающий за логирование. Логи пишуться в файл, так же выводться в консоль'''

    def __init__(self):
        self.mylogs = logging.getLogger(__name__)
        self.mylogs.setLevel(logging.DEBUG)
        # обработчик записи в лог-файл
        name = PATH_LOG
        self.file = logging.FileHandler(name)
        self.fileformat = logging.Formatter(
            "%(asctime)s:%(levelname)s:%(message)s")
        self.file.setLevel(logging.DEBUG)
        self.file.setFormatter(self.fileformat)
        # обработчик вывода в консоль лог файла
        self.stream = logging.StreamHandler()
        self.streamformat = logging.Formatter(
            "%(levelname)s\t:  %(asctime)s : %(module)s : %(message)s")
        self.stream.setLevel(logging.DEBUG)
        self.stream.setFormatter(self.streamformat)
        # инициализация обработчиков
        self.mylogs.addHandler(self.file)
        self.mylogs.addHandler(self.stream)
        self.mylogs.info('start-logging')

    def debug(self, message):
        '''сообщения отладочного уровня'''
        self.mylogs.debug(message)

    def info(self, message):
        '''сообщения информационного уровня'''
        self.mylogs.info(message)

    def warning(self, message):
        '''не критичные ошибки'''
        self.mylogs.warning(message)

    def error(self, message):
        '''ребята я сваливаю ща рванет !!!!'''
        self.mylogs.error(message)


class PULT_Controller():
    def __init__(self, config) -> None:

        os.environ["SDL_VIDEODRIVER"] = "dummy"

        self.pygame = pygame
        self.pygame.init()

        self.config = config

        joysticks = []
        for i in range(self.pygame.joystick.get_count()):
            joysticks.append(self.pygame.joystick.Joystick(i))
        for self.joystick in joysticks:
            self.joystick.init()

        self.DataPult = {'j1-val-y': 0, 'j1-val-x': 0,
                         'j2-val-y': 0, 'j2-val-x': 0,
                         'man': 90, 'servoCam': 90,
                         'led': 0}

        self.camera_up = int(self.config['JOYSTICK'][self.config['JOYSTICK']['camera_up']])

        self.camera_down = int(self.config['JOYSTICK'][self.config['JOYSTICK']['camera_down']])

        self.arm_up =  int(self.config['JOYSTICK'][self.config['JOYSTICK']['arm_up']])

        self.arm_down =  int(self.config['JOYSTICK'][self.config['JOYSTICK']['arm_down']])

        self.led_up = int(self.config['JOYSTICK'][self.config['JOYSTICK']['led_up']])

        self.led_down = int(self.config['JOYSTICK'][self.config['JOYSTICK']['led_down']])

        self.nitro_up =  int(self.config['JOYSTICK'][self.config['JOYSTICK']['nitro_up']])

        self.nitro_down =  int(self.config['JOYSTICK'][self.config['JOYSTICK']['nitro_down']])

        self.sleep_listen = float(self.config['JOYSTICK']['time_sleep'])

        self.power_motor = float(self.config['JOYSTICK']['power_motor'])

        self.forward_back_nitro = float(self.config['JOYSTICK']['forward_back_nitro']) * self.power_motor * 32767

        self.cor_forward_back_nitro = float(self.config['JOYSTICK']['cor_forward_back_nitro'])

        self.forward_back_defolt = float(self.config['JOYSTICK']['forward_back_defolt']) * self.power_motor * 32767

        self.cor_forward_back_defolt = float(self.config['JOYSTICK']['cor_forward_back_defolt'])

        self.min_value = float(self.config['JOYSTICK']['min_value'])

        self.move_forward_back = int(self.config['JOYSTICK'][self.config['JOYSTICK']['move_forward_back']])

        self.left_right_nitro = float(self.config['JOYSTICK']['left_right_nitro']) * self.power_motor * 32767

        self.left_right_defolt = float(self.config['JOYSTICK']['left_right_defolt']) * self.power_motor * 32767
        
        self.cor_left_right_nitro =  float(self.config['JOYSTICK']['cor_left_right_nitro'])

        self.cor_left_right_defolt = float(self.config['JOYSTICK']['cor_left_right_defolt'])

        self.move_left_right = int(self.config['JOYSTICK'][self.config['JOYSTICK']['move_left_right']])

        self.move_up_down = int(self.config['JOYSTICK'][self.config['JOYSTICK']['move_up_down']])

        self.up_down_nitro = float(self.config['JOYSTICK']['up_down_nitro']) * self.power_motor * 32767

        self.cor_up_down_nitro = float(self.config['JOYSTICK']['cor_up_down_nitro'])

        self.up_down_defolt = float(self.config['JOYSTICK']['up_down_defolt']) * self.power_motor * 32767

        self.cor_up_down_defolt = float(self.config['JOYSTICK']['cor_up_down_defolt'])

        self.move_turn_left_turn_righ = int(self.config['JOYSTICK'][self.config['JOYSTICK']['move_turn-left_turn-righ']])

        self.turn_left_turn_righ_nitro = float(self.config['JOYSTICK']['turn-left_turn-righ_nitro']) * self.power_motor * 32767

        self.cor_turn_left_turn_righ_nitro = float(self.config['JOYSTICK']['cor_turn-left_turn-righ_nitro'])

        self.turn_left_turn_righ_defolt = float(self.config['JOYSTICK']['turn-left_turn-righ_defolt']) * self.power_motor * 32767

        self.cor_turn_left_turn_righ_defolt = float(self.config['JOYSTICK']['cor_turn-left_turn-righ_defolt'])

        self.nitro = True
        self.running = True

    def listen(self):
        cor_servo_cam = 0
        while self.running:
            for event in self.pygame.event.get():
                # опрос нажания кнопок
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == self.camera_up:
                        cor_servo_cam = 1

                    if event.button == self.camera_down:
                        cor_servo_cam = -1

                    if event.button == self.arm_up:
                        self.DataPult['man'] = 180

                    if event.button == self.arm_down:
                        self.DataPult['man'] = 0

                    if event.button == self.led_up:
                        self.DataPult['led'] = 1

                    if event.button == self.led_down:
                        self.DataPult['led'] = 0

                    if event.button == self.nitro_up:
                        self.nitro = True

                    if event.button == self.nitro_down:
                        self.nitro = False

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == self.camera_up:
                        cor_servo_cam = 0

                    if event.button == self.camera_down:
                        cor_servo_cam = 0

                # опрос стиков
                if event.type == pygame.JOYAXISMOTION and abs(event.value) > self.min_value:
                    if event.axis == self.move_forward_back:
                        if self.nitro:
                            self.DataPult['j1-val-y'] = int(round(event.value, 2) * self.forward_back_nitro) - self.cor_forward_back_nitro
                        else:
                            self.DataPult['j1-val-y'] = int(round(event.value, 2) * self.forward_back_defolt) - self.cor_forward_back_defolt

                    if event.axis == self.move_left_right:
                        if self.nitro:
                            self.DataPult['j1-val-x'] = int(round(event.value, 2) * self.left_right_nitro ) - self.cor_left_right_nitro
                        else:
                            self.DataPult['j1-val-x'] = int(round(event.value, 2) * self.left_right_defolt) - self.cor_left_right_defolt

                    if event.axis == self.move_up_down:
                        if self.nitro:
                            self.DataPult['j2-val-y'] = int(round(event.value, 2) * self.up_down_nitro) - self.cor_up_down_nitro
                        else:
                            self.DataPult['j2-val-y'] = int(round(event.value, 2) * self.up_down_defolt) - self.cor_up_down_defolt

                    if event.axis == self.move_turn_left_turn_righ:
                        if self.nitro:
                            self.DataPult['j2-val-x'] = int(round(event.value, 2) * self.turn_left_turn_righ_nitro) - self.cor_turn_left_turn_righ_nitro
                        else:
                            self.DataPult['j2-val-x'] = int(round(event.value, 2) * self.turn_left_turn_righ_defolt) - self.cor_turn_left_turn_righ_defolt
                else:
                    self.DataPult['j1-val-y'], self.DataPult['j2-val-y'], self.DataPult['j1-val-x'], self.DataPult['j2-val-x'] = 0, 0, 0, 0

                # повторная инициализация джойстика после отключения
                
                joysticks = []
                for i in range(self.pygame.joystick.get_count()):
                    joysticks.append(self.pygame.joystick.Joystick(i))
                for self.joystick in joysticks:
                    self.joystick.init()
                    break

            # рассчет положения положения полезной нагрузки
            self.DataPult['servoCam'] += cor_servo_cam
            if self.DataPult['servoCam'] > 180:
                self.DataPult['servoCam'] = 180
            elif self.DataPult['servoCam'] < 0:
                self.DataPult['servoCam'] = 0

            sleep(0.05)
            # print(self.DataPult)

    def stop_listen(self):
        self.running = False


class PULT_SerialPort:
    def __init__(self,
                 logger: PULT_Logging = PULT_Logging,
                 port: str = '/dev/ttyAML0',
                 bitrate: int = 115200
                 ):
        global DEBUG
        # инициализация переменных
        self.check_connect = False
        self.logger = logger
        # открытие порта
        self.serial_port = serial.Serial(
            port=port,
            baudrate=bitrate,
            timeout=0.1)
        self.check_cor = False

    def Receiver_tnpa(self):
        global DEBUG
        '''прием информации с аппарата'''
        data = None

        while data == None or data == b'':
            data = self.serial_port.readline()

        try:
            dataout = list(
                map(lambda x: float(x), str(data)[3:-4].split(', ')))
        except:
            self.logger.warning('Error converting data')
            return None

        if DEBUG:
            self.logger.debug(f'Receiver data : {str(data)}')
            
        return dataout

    def Control_tnpa(self, data: list = [50, 50, 50, 50, 50, 50, 90, 0, 0, 0]):
        global DEBUG
        '''отправка массива на аппарат'''
        try:
            self.serial_port.write((f'{str(data)}\n').encode())
            if DEBUG:
                self.logger.debug('Send data: ' + str(data))
        except:
            self.logger.warning('Error send data')


class PULT_Main:
    def __init__(self):
        self.DataInput = []

        self.config = configparser.ConfigParser()
        self.config.read(PATH_CONFIG)

        # self.lcd = LCD()
        # def safe_exit(signum, frame):
        #     exit(1)

        # try:
        #     signal(SIGTERM, safe_exit)
        #     signal(SIGHUP, safe_exit)
        #     self.lcd.text("Hello,", 1)
        #     self.lcd.text("Command Post!", 2)
        # except:
        #     pass
        # finally:
        #     self.lcd.clear()

        self.lodi = PULT_Logging()

        self.serial_port = PULT_SerialPort(self.lodi)  # поднимаем сервер
        #self.lodi.info('ServerMainPult - init')

        self.Controllps4 = PULT_Controller(self.config)  # поднимаем контролеер
        #self.lodi.info('MyController - init')
        self.DataPult = self.Controllps4.DataPult
        # частота оптправки
        self.RateCommandOut = 0.1
        # запись получаемой и отправляемой информации в лог файл
        self.telemetria = False
        #
        self.CHECK_CONNECT = False
        self.correct = True

        self.lodi.info('MainPost-init')

    def RunController(self):
        '''запуск на прослушивание контроллера ps4'''
        # self.lodi.info('MyController-listen')
        self.Controllps4.listen()

    def RunCommand(self, CmdMod=True):
        self.lodi.info('MainPost-RunCommand')
        '''
        Движение вперед - (1 вперед 2 вперед 3 назад 4 назад) 
        Движение назад - (1 назад 2 назад 3 вперед 4 вперед)
        Движение лагом вправо - (1 назад 2 вперед 3 вперед 4 назад)
        Движение лагом влево - (1 вперед 2 назад 3 назад 4 вперед)
        Движение вверх - (5 вниз 6 вниз)
        Движение вниз - (5 вверх 6 вверх)

        Описание протокола передачи:
            С поста управлеия:
                [motor0, motor1, motor2, motor3, motor4, motor5, ServoCam, Arm, led0, led1]
                по умолчанию:
                [0, 0, 0, 0, 0, 0, 90, 0, 0, 0]
            C аппарата:
                [напряжение(V), ток потребления(А), курс(градусы), глубина(м)]
                [0,0,0,0]
        '''
        def transformation(value: int):
            # Функция перевода значений АЦП с джойстика в проценты
            value = (32768 - value) // 655
            return value

        def defense(value: int):
            '''Функция защиты от некорректных данных'''
            if value > 100:
                value = 100
            elif value < 0:
                value = 0
            return value

        while True:
            dataout = []
            # запрос данный из класса пульта (потенциально слабое место)
            data = self.DataPult

            # математика преобразования значений с джойстика в значения для моторов
            if self.telemetria:
                self.lodi.debug(f'DataPult-{data}')

            if self.correct:
                J1_Val_Y = transformation(data['j1-val-y'])
                J1_Val_X = transformation(data['j1-val-x'])
                J2_Val_Y = transformation(data['j2-val-y'])
                J2_Val_X = transformation(data['j2-val-x'])
            else:
                J1_Val_Y = transformation(data['j1-val-y'])
                J1_Val_X = transformation(data['j1-val-x'])
                J2_Val_Y = transformation(data['j2-val-y'])
                J2_Val_X = transformation(data['j2-val-x'])

            # Подготовка массива для отправки на аппарат
            dataout.append(defense(J1_Val_Y + J1_Val_X + J2_Val_X - 100))
            dataout.append(defense(J1_Val_Y - J1_Val_X - J2_Val_X + 100))
            dataout.append(defense((-1 * J1_Val_Y) -
                           J1_Val_X + J2_Val_X + 100))
            dataout.append(100 - defense((-1 * J1_Val_Y) +
                           J1_Val_X - J2_Val_X + 100))

            dataout.append(defense(J2_Val_Y))
            dataout.append(100 - defense(J2_Val_Y))

            dataout.append(data['servoCam'])

            if data['man'] > 80:
                data['man'] = 80
            if data['man'] < 55:
                data['man'] = 55

            dataout.append(data['man'])

            dataout.append(data['led'])
            dataout.append(data['led'])

            # Запись управляющего массива в лог
            if self.telemetria:
                self.lodi.debug('DataOutput - {dataout}')
            # отправка и прием сообщений
            self.serial_port.Control_tnpa(dataout)
            self.DataInput = self.serial_port.Receiver_tnpa()

            if self.DataInput == None:
                self.CHECK_CONNECT = False
                self.lodi.warning('DataInput - NONE')
            else:
                self.CHECK_CONNECT = True
            # Запись принятого массива в лог
            if self.telemetria:
                self.lodi.debug('DataInput - {self.DataInput}')
            # возможность вывода принимаемой информации в соммандную строку
            if CmdMod:
                print(self.DataInput)

            sleep(self.RateCommandOut)

    def RunMain(self):
        self.ThreadJoi = threading.Thread(target=self.RunController)
        self.ThreadCom = threading.Thread(target=self.RunCommand)

        self.ThreadJoi.start()
        self.ThreadCom.start()


if __name__ == '__main__':
    post = PULT_Main()
    post.RunMain()
