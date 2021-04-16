import serial
import serial.tools.list_ports

def get_arduino_port():

    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'CH340' in p.description or 'Arduino' in p.description
    ]



    return arduino_ports
