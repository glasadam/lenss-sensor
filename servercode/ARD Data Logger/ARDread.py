""" LENSS ARDUINO Read Program ==========================

This program reads data from the Arduino that
is connected to the TSL237 sensor.

"""

### Imports / Setup
import serial
import time
from datetime import datetime
import serial.tools.list_ports
import configparser
import  os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import numpy as np

fmt = ['%.2f','%.0f','%.2f','%.1f','%.1f']
dltd = 0
ldltd = 0
starttime = datetime.now().strftime("%H:%M:%S, %Y-%m-%d")

### Function Definitions
def getardport(config):
    """ Returns the port string for the arduino
    """
    try:
        return config['arddatalogger']['arduinoport']
    except:
        exit(1)
        
### Main program

if len(sys.argv) < 2:
    print('WARNING: Must give filepathname to valid config file')
    print('Usage:\n  python SQM_LU_LOGGER.py ../config/serverconfig.ini')
    print('  replace with your own config file as appropriate')
    exit(1)

# Setup configuration
Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

# Setup logging
now=datetime.now()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
hand = TimedRotatingFileHandler(now.strftime(config['logging']['ardlogfile']), when="midnight")
hand.suffix = "%Y-%m-%d.log"
logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
hand.setFormatter(logging.Formatter(logformat))
logger.addHandler(hand)
print(config['arddatalogger']['arduinoport'])

# Open serial connection
if int(config['arddatalogger']['simarduino']):
    # We are simulating the arduino set serial to null
    ser = None
else:
    ser  =  serial . Serial ( port=getardport(config),\
                              baudrate=9600,\
                              parity=serial.PARITY_NONE,\
                              stopbits=serial.STOPBITS_ONE,\
                              bytesize=serial.EIGHTBITS,\
                              timeout=5)
    ser.readline()
        
def serialread(config):
    """ Read the serial value from the arduino and writes
        it to the file.
    """
    time.sleep(1)

    global dltd
    global ldltd
    global starttime

    lvolt = []
    hz = []
    tvolt = []
    tFahr = []
    tCels = []
    sl = [[] for i in range(5)]
    last = time.gmtime().tm_sec

    while True:
        time.sleep(2)
        now=datetime.now()

        #timestring=str(tim[3])+":"+str(tim[4])+":"+str(tim[5])+", "
        timestring=now.strftime("%H:%M:%S")
        if (last > time.gmtime().tm_sec):
            for l in range(len(sl)):
                sl[l].sort()
                sl[l] = sl[l][len(sl[l])//5:-(len(sl[l])//5)]
                sl[l]=fmt[l] % np.mean(sl[l])
            break
        # Read value from Arduino
        if ser:
            read_ser=ser.readline()
            #print(repr(read_ser))
            read_fmtd = read_ser.decode("utf-8")
        else:
            read_fmtd = config['arddatalogger']['simardline']
        # Read data from string
        sdata = read_fmtd.split(",")
        print(sdata)
        if (len(sdata) == 5):
            sdata[4].strip()
            #print(sdata+["Seconds"]) #Testing by second while distinguishing from minutely data
            try:
                for i in range(len(sdata)):
                    sl[i].append(float(sdata[i]))
            except:
                dltd+=1
        else:
            dltd+=1
        print(time.gmtime().tm_sec)
        last = time.gmtime().tm_sec

    read_timed = []
    read_timed.append(timestring)
    read_timed += sl
    text_timed = ",".join(read_timed)
    #print(read_timed)
    print(text_timed)
    print(str(dltd) + " pieces of data deleted")
    # Make filename
    fname = now.strftime(config['arddatalogger']['outfilename'])
    # Save to file
    log = open(fname, 'at')
    log.write(text_timed+"\r\n")
    if (dltd-ldltd >= 100):
        logger.info(str(dltd)+" lines deleted since "+starttime+"\r\n")
        ldltd = dltd
    log.close()
    logger.info('Connected to:' + str(getardport(config)))
    logger.info('Read data line')

while True:

    serialread(config)
    #time.sleep(1)
