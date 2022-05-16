import serial
from time import sleep
from datetime import datetime
from ast import While, literal_eval

'''
Описание протокола передачи:
    С поста управлеия:
        [motor0, motor1, motor2, motor3, motor4, motor5, ServoCam, Arm, led0, led1]
        по умолчанию:
        [50, 50, 50, 50, 50, 50, 90, 0, 0, 0]
    C аппарата:
        [напряжение(V), ток потребления(А), курс(градусы), глубина(м)]
        [0,0,0,0]
'''

DEBUG = False


class PULT_Logging:
    def __init__(self) -> None:
        pass

    def critical(*args):
        pass

    def debug(*args):
        pass

    def warning(*args):
        pass


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

    def Receiver_tnpa(self):
        global DEBUG
        '''прием информации с аппарата'''
        data = None

        while data == None or data == b'':
            try:
                data = self.serial_port.readline()
            except: pass

        try:
            print(str(data)[159:-4])
            dataout = list(map(lambda x: float(x), str(data)[159:-4].split(', ')))
        except:
            self.logger.warning('Error converting data')
            return None

        if DEBUG:
            self.logger.debug(f'Receiver data : {str(data)}')
        return dataout

    def Control_tnpa(self, data:list=[0, 0, 0, 0, 0, 0, 90, 0, 0, 0]):
        global DEBUG
        '''отправка массива на аппарат'''
        try:
            self.serial_port.write((f'{str(data)}\n').encode('utf-8'))
            if DEBUG:
                self.logger.debug('Send data: ' + str(data))
        except:
            self.logger.warning('Error send data')

test_log = PULT_Logging()
test_pult = PULT_SerialPort()

if __name__ == '__main__':
    while True:
        test_pult.Control_tnpa()
        print('In', test_pult.Receiver_tnpa())
        sleep(1)
