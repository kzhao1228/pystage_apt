from serial.tools.list_ports import comports
import platform
import usb
import os
from .port import Port

    
def find_stages():
    serial_ports = [(x[0], x[1], dict(y.split('=', 1) for y in x[2].split(' ') if '=' in y)) for x in comports()]
    #print(serial_ports[0][2]['SER'])
    # expected output is [('/dev/ttyUSB0', 'APT DC Motor Controller', {'VID:PID': '0403:FAF0', 'SER': '83844171', 'LOCATION': '1-1.1'}),
    # ('/dev/ttyAMA0', 'ttyAMA0', {})]
    # each identified serial port is expressed within a tuple, i.e. ('','','').
 
    # The loop below will find all identified stage controllers and
    for dev in usb.core.find(find_all=True, custom_match= lambda x: x.bDeviceClass != 9):
        try:
            #FIXME: this avoids an error related to https://github.com/walac/pyusb/issues/139
            #FIXME: this could maybe be solved in a better way?
            dev._langids = (1033, )
            # KDC101 3-port is recognized as FTDI in newer kernels
            if not (dev.manufacturer == 'Thorlabs' or dev.manufacturer == 'FTDI'):
                raise Exception('No manufacturer found')
        except usb.core.USBError:
            print("No stage controller found: make sure your device is connected")
            break
        
        if platform.system() == 'Linux':
            # this is to check if the operating system is Linux, if not the code won't work. N.B. codename of MacOS
            # is Darwin.
            port_candidates = [x[0] for x in serial_ports if x[2].get('SER', None) == dev.serial_number]
            # expected value for port_candidates is:
            # ['/dev/ttyUSB0'], which is the serial port to communicate with the controller through
        
        else:
            raise NotImplementedError("Your operating system is not supported. " \
                "PyStage_APT only works on Linux.")
        
        # we make sure at each iteration only one port entry is contained in port candidates
        # i.e. the ports are accessed one by one NOT all at one go.
        assert len(port_candidates) == 1
        
        port = port_candidates[0]
        p = Port.create(port, dev.serial_number)
        for stage in p.get_stages().values():
            # generator type
            yield stage
            
        
if __name__ == '__main__':
    print(list(find_stages()))

# Example device:
# Manufacturer                1. Thorlabs
# Product                     2. APT DC Motor Controller
# Serial No.                  3. 83844171
