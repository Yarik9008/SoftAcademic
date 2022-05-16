from machine import I2C, Pin, UART, PWM, ADC
from time import sleep

'''
Описание протокола передачи:
    С поста управлеия:
        [motor0, motor1, motor2, motor3, motor4, motor5, ServoCam, Arm, led0, led1]
        по умолчанию:
        [0, 0, 0, 0, 0, 0, 90, 0, 0, 0]
    C аппарата:
        [напряжение(V), ток потребления(А), курс(градусы), глубина(м), тумпература(градусы цельсия)]
        [0,0,0,0,0]
'''

DEBUG = False


class TNPA_SerialPort:
    def __init__(self):
        self.serial_port = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17))

    def receiver_data(self):
        global DEBUG
        '''прием информации с поста управления'''
        data = None
        while data == None or data == b'':
            try:
                data = self.serial_port.read(100)
            except: pass

        print(data)

        try:
            return list(map(lambda x: float(x), str(data)[3:-4].split(', ')))
        except:
            return None
        
    def dispatch_data(self, data: list = [0, 0, 0, 0, 0]):
        '''Отправка телеметрии на пост управления'''
        try:
            self.serial_port.write((f'{str(data)}\n').encode())
        except: pass


test_tnpa = TNPA_SerialPort()
while True:
    data = test_tnpa.receiver_data()
    print(data)
    sleep(0.1)
    test_tnpa.dispatch_data()

# протестированно
