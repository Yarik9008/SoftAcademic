import os
import pygame
import logging
from datetime import datetime
from time import sleep
import configparser
from pprint import pprint



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

        self.nitro = True
        self.running = True

    def listen(self):
        cor_servo_cam = 0
        while self.running:
            for event in self.pygame.event.get():
                # опрос нажания кнопок
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['camera_up']]):
                        cor_servo_cam = 1

                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['camera_down']]):
                        cor_servo_cam = -1

                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['arm_up']]):
                        self.DataPult['man'] = 180

                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['arm_down']]):
                        self.DataPult['man'] = 0

                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['led_up']]):
                        self.DataPult['led'] = 1

                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['led_down']]):
                        self.DataPult['led'] = 0

                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['nitro_up']]):
                        self.nitro = True

                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['nitro_down']]):
                        self.nitro = False

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['camera_up']]):
                            cor_servo_cam = 0

                    if event.button == int(self.config['JOYSTICK'][self.config['JOYSTICK']['camera_down']]):
                            cor_servo_cam = 0

                # опрос стиков
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == int(self.config['JOYSTICK'][self.config['JOYSTICK']['move_forward_back']]):
                        if self.nitro:
                            self.DataPult['j1-val-y'] = int(round(event.value, 2) * float(
                                self.config['JOYSTICK']['forward_back_nitro']) * float(self.config['JOYSTICK']['power_motor']) * 32767) - float(self.config['JOYSTICK']['cor_forward_back_nitro'])
                        else:
                            self.DataPult['j1-val-y'] = int(round(event.value, 2) * float(
                                self.config['JOYSTICK']['forward_back_defolt']) * float(self.config['JOYSTICK']['power_motor']) * 32767) - float(self.config['JOYSTICK']['cor_forward_back_defolt'])

                    if event.axis == int(self.config['JOYSTICK'][self.config['JOYSTICK']['move_left_right']]):
                        if self.nitro:
                            self.DataPult['j1-val-x'] = int(round(event.value, 2) * float(
                                self.config['JOYSTICK']['left_right_nitro']) * float(self.config['JOYSTICK']['power_motor']) * 32767) - float(self.config['JOYSTICK']['cor_left_right_nitro'])
                        else:
                            self.DataPult['j1-val-x'] = int(round(event.value, 2) * float(
                                self.config['JOYSTICK']['left_right_defolt']) * float(self.config['JOYSTICK']['power_motor']) * 32767) - float(self.config['JOYSTICK']['cor_left_right_defolt'])

                    if event.axis == int(self.config['JOYSTICK'][self.config['JOYSTICK']['move_up_down']]):
                        if self.nitro:
                            self.DataPult['j2-val-y'] = int(round(event.value, 2) * float(
                                self.config['JOYSTICK']['up_down_nitro']) * float(self.config['JOYSTICK']['power_motor']) * 32767) - float(self.config['JOYSTICK']['cor_up_down_nitro'])
                        else:
                            self.DataPult['j2-val-y'] = int(round(event.value, 2) * float(
                                self.config['JOYSTICK']['up_down_defolt']) * float(self.config['JOYSTICK']['power_motor']) * 32767) - float(self.config['JOYSTICK']['cor_up_down_defolt'])

                    if event.axis == int(self.config['JOYSTICK'][self.config['JOYSTICK']['move_turn-left_turn-righ']]):
                        if self.nitro:
                            self.DataPult['j2-val-x'] = int(round(event.value, 2) * float(
                                self.config['JOYSTICK']['turn-left_turn-righ_nitro']) * float(self.config['JOYSTICK']['power_motor']) * 32767) - float(self.config['JOYSTICK']['cor_turn-left_turn-righ_nitro'])
                        else:
                            self.DataPult['j2-val-x'] = int(round(event.value, 2) * float(
                                self.config['JOYSTICK']['turn-left_turn-righ_defolt']) * float(self.config['JOYSTICK']['power_motor']) * 32767) - float(self.config['JOYSTICK']['cor_turn-left_turn-righ_defolt'])
                


                # повторная инициализация джойстика после отключения
                joysticks = [] 
                for i in range(self.pygame.joystick.get_count()):
                    joysticks.append(self.pygame.joystick.Joystick(i))
                for self.joystick in joysticks:
                    self.joystick.init()


            # рассчет положения положения полезной нагрузки
            self.DataPult['servoCam'] += cor_servo_cam
            if self.DataPult['servoCam'] > 180:
                self.DataPult['servoCam'] = 180
            elif self.DataPult['servoCam'] < 0:
                self.DataPult['servoCam'] = 0


            

            sleep(float(self.config['JOYSTICK']['time_sleep']))
            print(self.DataPult)

    def stop_listen(self):
        self.running = False


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/home/rock/SoftAcademic/unit-test/radxa-zero-pult-test/config_rov.ini')

    controller = PULT_Controller(config)
    controller.listen()