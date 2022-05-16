"""CircuitPython Essentials UART Serial example"""
import board
import busio
import digitalio

# For most CircuitPython boards:
led = digitalio.DigitalInOut(board.LED)
# For QT Py M0:
# led = digitalio.DigitalInOut(board.SCK)
led.direction = digitalio.Direction.OUTPUT

uart = busio.UART(board.GP16, board.GP17, baudrate=57600)

while True:
    try:
        data = uart.readline()  # read up to 32 bytes\
        data = ''.join([chr(b) for b in data])
        print(data)  # this is a bytearray type
    except:
        print(None)
