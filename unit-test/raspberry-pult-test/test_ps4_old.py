from pyPS4Controller.controller import Controller


class MyController(Controller):
    '''
    Класс для взаимодействия с джойстиком PS4 
    (работает только из под линукса из под винды управление только с помощью клавиатуры)

    правый джойтик вперед - движение вперед 
    правый джойстик вбок - движение лагом 

    левый джойстик вперед - всплытие
    левый джойстик вбок - разворот на месте 

    кнопки - корректировка нулевого положения для противодействия течениям и прочей ериси 

    кнопка ps - обнуление корректировок 
    '''

    def __init__(self):
        Controller.__init__(self, interface="/dev/input/js0",
                            connecting_using_ds4drv=False)
        self.DataPult = {'j1-val-y': 0, 'j1-val-x': 0,
                         'j2-val-y': 0, 'j2-val-x': 0,
                         'ly-cor': 0, 'lx-cor': 0,
                         'ry-cor': 0, 'rx-cor': 0,
                         'man': 90, 'servoCam': 90,
                         'led': False, 'auto-dept': False}
        self.log = True
        self.telemetria = True
        self.optionscontrol = False
        self.nitro = False
    # переключение режимов корректировок

    def on_options_press(self):
        self.optionscontrol = not self.optionscontrol
    # функция перевода данных с джойстиков

    def transp(self, value):
        return -1 * (value // 328)

    # блок опроса джойстиков
    def on_L3_up(self, value):
        '''погружение'''
        self.DataPult['j2-val-y'] =  value
        if self.telemetria:
            print('forward')

    def on_L3_down(self, value):
        '''всплытие'''
        self.DataPult['j2-val-y'] =  value
        if self.telemetria:
            print('back')

    def on_L3_y_at_rest(self):
        '''Обнуление'''
        self.DataPult['j2-val-y'] = 0
        if self.telemetria:
            print('back')

    def on_L3_left(self, value):
        '''Движение влево (лаг) '''
        if self.nitro:
            self.DataPult['j2-val-x'] =   value 
        else:
            self.DataPult['j2-val-x'] = value // 2
        if self.telemetria:
            print('left')

    def on_L3_right(self, value):
        '''Движение вправо (лаг) '''
        if self.nitro:
            self.DataPult['j2-val-x'] =   value 
        else:
            self.DataPult['j2-val-x'] = value // 2
        if self.telemetria:
            print('right')

    def on_L3_x_at_rest(self):
        '''Обнуление'''
        self.DataPult['j2-val-x'] = 0
        if self.telemetria:
            print('right')

    def on_R3_up(self, value):
        '''Вперед'''
        if self.nitro:
            print(value)
            self.DataPult['j1-val-y'] = -1*  value 
        else:
            self.DataPult['j1-val-y'] = -1 * value // 2
        if self.telemetria:
            print('up')

    def on_R3_down(self, value):
        '''назад'''
        if self.nitro:
            print(value)
            self.DataPult['j1-val-y'] = -1* value 
        else:
            self.DataPult['j1-val-y'] = -1 * value // 2
        if self.telemetria:
            print('down')

    def on_R3_y_at_rest(self):
        '''Обнуление'''
        self.DataPult['j1-val-y'] = 0
        if self.telemetria:
            print('down')

    def on_R3_left(self, value):
        '''Разворот налево'''
        if self.nitro:
            self.DataPult['j1-val-x'] =  value // 3
        else:
            self.DataPult['j1-val-x'] = value // 6
        if self.telemetria:
            print('turn-left')

    def on_R3_right(self, value):
        '''Разворот направо'''
        if self.nitro:
            self.DataPult['j1-val-x'] =  value // 3
        else:
            self.DataPult['j1-val-x'] = value // 6
        if self.telemetria:
            print('turn-righ')

    def on_R3_x_at_rest(self):
        '''Обнуление'''
        self.DataPult['j1-val-x'] = 0
        if self.telemetria:
            print('turn-left')

    # блок внесения корректировок с кнопок и управления светом, поворотом камеры, манипулятором
    def on_x_press(self):
        '''Нажатие на крестик'''
        if self.optionscontrol:
            if self.DataPult['ry-cor'] >= - 50:
                self.DataPult['ry-cor'] -= 10
        else:
            if self.DataPult['servoCam'] <= 170:
                self.DataPult['servoCam'] += 10

    def on_triangle_press(self):
        '''Нажатие на триугольник'''
        if self.optionscontrol:
            if self.DataPult['ry-cor'] <= 50:
                self.DataPult['ry-cor'] += 10
        else:
            if self.DataPult['servoCam'] >= 10:
                self.DataPult['servoCam'] -= 10

    def on_square_press(self):
        '''Нажатие на круг'''
        if self.optionscontrol:
            if self.DataPult['rx-cor'] <= 50:
                self.DataPult['rx-cor'] += 10
        else:
            if self.DataPult['man'] <= 150:
                self.DataPult['man'] = 180

    def on_circle_press(self):
        '''Нажатие на квадрат'''
        if self.optionscontrol:
            if self.DataPult['rx-cor'] >= -50:
                self.DataPult['rx-cor'] -= 10
        else:
            if self.DataPult['man'] >= 40:
                self.DataPult['man'] = 0

    def on_up_arrow_press(self):
        if self.optionscontrol:
            if self.DataPult['ly-cor'] >= -50:
                self.DataPult['ly-cor'] -= 10
        else:
            self.DataPult['led'] = not self.DataPult['led']

    def on_down_arrow_press(self):
        if self.optionscontrol:
            if self.DataPult['ly-cor'] <= 50:
                self.DataPult['ly-cor'] += 10
        else:
            self.DataPult['auto-dept'] = not self.DataPult['auto-dept']

    def on_left_arrow_press(self):
        if self.optionscontrol:
            if self.DataPult["lx-cor"] >= -50:
                self.DataPult["lx-cor"] -= 10
        else:
            self.nitro = not self.nitro

    def on_right_arrow_press(self):
        if self.optionscontrol:
            if self.DataPult['lx-cor'] <= 50:
                self.DataPult['lx-cor'] += 10

    def on_playstation_button_press(self):
        '''Отмена всех корректировок'''
        self.DataPult['ly-cor'] = 0
        self.DataPult['lx-cor'] = 0
        self.DataPult['rx-cor'] = 0
        self.DataPult['ry-cor'] = 0
        '''Приведение всех значений в исходное положение'''
        self.DataPult['auto-dept'] = False
        self.DataPult['servoCam'] = 90
        self.DataPult['man'] = 90
        self.DataPult['led'] = False
        self.nitro = False


if __name__ == '__main__':
    controller = MyController()
    controller.listen()