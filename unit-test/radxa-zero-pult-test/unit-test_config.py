import configparser

config = configparser.ConfigParser()
config.read('unit-test/raspberry-pult-test/config_rov.ini')

print(float(config['JOYSTICK']['test_2']))