import RPi.GPIO as GPIO
import logging
import time
import os
from datetime import datetime

from .server import BaseServer

logger = logging.getLogger('homebase.buttons')

SW1 = 21
SW2 = 16
SW3 = 20
SW4 = 19
SW5 = 26

# Check for HAT version, remap switches if necessary
hatdir = '/proc/device-tree/hat'
proddir = os.path.join(hatdir, 'product')
venddir = os.path.join(hatdir, 'vendor')
if os.path.exists(proddir) and os.path.exists(venddir):
    with open(proddir, 'r') as f:
        prod = f.read()
    with open(venddir, 'r') as f:
        vend = f.read()
else:
    prod = ''
    vend = ''

if prod.find('PaPiRus ePaper HAT') == 0 and vend.find('Pi Supply') == 0:
    logger.info('Detected PaPiRus HAT')
    SW1 = 16
    SW2 = 26
    SW3 = 20
    SW4 = 21
    SW5 = None
else:
    logger.info('Assuming PaPiRus PHAT')

buttons = (SW1, SW2, SW3, SW4, SW5)
buttons = [button for button in buttons if button is not None]
GPIO.setmode(GPIO.BCM)
for button in buttons:
    GPIO.setup(button, GPIO.IN)


class ButtonServer(BaseServer):

    def __init__(self):
        self.logger = logging.getLogger('homebase.buttons.ButtonServer')
        self.last_button_time = datetime.fromtimestamp(0)
        self.debounce = 0.25
        super(ButtonServer, self).__init__()

    def run(self):
        while not self.stop_request.isSet():
            for (idx, button) in enumerate(buttons):
                if not GPIO.input(button):
                    dt = (datetime.now() - self.last_button_time)
                    if dt.total_seconds() > self.debounce:
                        self.q.put(idx)
                        self.new_info.set()
                        self.logger.info('Button {} pressed'.format(idx))
                        self.last_info = idx
                        self.last_button_time = datetime.now()
            time.sleep(0.1)
