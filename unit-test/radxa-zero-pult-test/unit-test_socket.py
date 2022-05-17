import socket
from test_log import * 
from ast import literal_eval


class ServerMainPult:
    '''
    Класс описывающий систему бекенд- пульта
    log - флаг логирования 
    log cmd - флаг вывода логов с cmd 
    host - хост на котором будет крутиться сервер 
    port- порт для подключения 
    motorpowervalue=1 - программное ограничение мощности моторов 
    joystickrate - частота опроса джойстика 
    '''

    def __init__(self, logger: MedaLogging, debug=False):
        # инициализация атрибутов
        self.JOYSTICKRATE = 0.2
        self.MotorPowerValue = 1
        self.telemetria = False
        self.checkConnect = False
        self.logger = logger
        # выбор режима: Отладка\Запуск на реальном аппарате
        if debug:
            self.HOST = '127.0.0.1'
            self.PORT = 1112
        else:
            self.HOST = '192.168.1.100'
            self.PORT = 1235
            
            
        # настройка сервера
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(1)
        self.user_socket, self.address = self.server.accept()
        self.checkConnect = True

        self.logger.info(f'ROV-Connected - {self.user_socket}')

    def ReceiverProteus(self):
        '''Прием информации с аппарата'''
        if self.checkConnect:
            data = self.user_socket.recv(512)
            if len(data) == 0:
                self.server.close()
                self.checkConnect = False
                self.logger.info(f'ROV-disconnection - {self.user_socket}')
                return None
            data = dict(literal_eval(str(data.decode('utf-8'))))
            if self.telemetria:
                self.logger.debug(f'DataInput - {str(data)}')
            return data

    def ControlProteus(self, data: dict):
        '''Отправка массива на аппарат'''
        if self.checkConnect:
            self.user_socket.send(str(data).encode('utf-8'))
            if self.telemetria:
                self.logger.debug(str(data))
