import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import sqlite3
from sqlite3 import Error
from datetime import datetime

GPIO.setmode(GPIO.BCM)

pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x76)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MIN)


radio.enableDynamicPayloads()
##radio.enableAckPayload()
#radio.setAutoAck(True)
#
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])
#radio.printDetails()
#
radio.printDetails()
##radio.stopListening()

def calculateChecksum(sum):
    res = 0
    numbers = [ord(c) for c in sum]
    for i in range(0, 4):
        res = res + int((((numbers[4 * i + 0] * (4 * i + 1)) +
                      (numbers[4 *i + 1] * (4 * i + 2))) * ((numbers[4 * i + 2] *
                      (4 * i + 3)) + (numbers[4 * i + 3] * (4 * i + 4)))))
    return res

def parse(message):
    b = []


    if(len(message) != 24):
        print("Length of message is wrong. Rejection.")
        return -1
    try:

        b.append(int(message[:4]))
        b.append(int(message[4:8]))
        b.append(float(message[8:16]))
        b.append(int(message[16:24]))
    except ValueError:
        print("Invalid message!")
        return -1

    controlSum = calculateChecksum(message)
    print(controlSum)
    if b[3] != controlSum:
        print("Error during sending message.")
        return -1
    return b

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
		
        return sqlite3.connect(db_file)
        
    except Error as e:
        print(e)


conn = create_connection("/home/pi/Desktop/NRF24L01/pythonsqlite.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Arduino_devices
(ID INTEGER PRIMARY KEY UNIQUE, Password INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS Temperatures
(ID INTEGER PRIMARY KEY AUTOINCREMENT, Date TEXT,
Temperature REAL, Device_ID INTEGER,
FOREIGN KEY(Device_ID) REFERENCES Arduino_devices(ID))''')
conn.commit()


print("Baza utworzona")
start = time.time()
i =1
while(1):
    # ackPL = [1]
    radio.stopListening()
    print("wysylam wiad")
    time.sleep(6)
    status = radio.write(str(i) +"wiadomosc")
    print(status)
    i=i+1
        
    radio.startListening();
    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    start = time.time()
    
    print("Received message is ", receivedMessage)
    
    s = ""
    s = s.join(chr(i) for i in receivedMessage)


    #print("Translating the receivedMessage into unicode characters")
    print("Original message is ", s)
    #receivedMessage="5432987685.1878604246566"
    message = parse(s)
    #print("Translating the receivedMessage into unicode characters")
    print("Message is ", message)
    #receivedMessage="5432987685.1878604246566"

 #   for row in c:
 #       print(row)
        
  #  string = ""
   # for n in receivedMessage:
        # Decode into standard unicode set
    #    if (n >= 32 and n <= 126):
    #        string += chr(n)
    #print("Out received message decodes to: {}".format(string))
    
    
connection.close()
    
    


