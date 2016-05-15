import serial
import logging

LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 5000

MONGO_URI = "mongodb://<user>:<password>@<host>:<port>/<db>"
DEBUG = True
DEBUG_LEVEL = logging.DEBUG

PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200 
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE
TIMEOUT = 0.7
WRITE_TIMEOUT = 0.7
MAX_ATTEMPT=24

PASSWORD="1"
ADMIN_PASSWORD="30"
