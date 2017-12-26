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

radio.setPayloadSize(32)
radio.setChannel(0x76)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MIN)

radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openReadingPipe(1, pipes[1])
#radio.printDetails()
radio.startListening()

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
while(1):
    # ackPL = [1]
    end = time.time()
    while not radio.available(0):
        pass
    receivedMessage = []
    
    print("czas")
    print(end-start)
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    start = time.time()
    s = ""
    s = s.join(chr(i) for i in receivedMessage)


    #print("Translating the receivedMessage into unicode characters")

    #receivedMessage="5432987685.1878604246566"
    message = parse(s)
    #jezeli parse zwraca -1 to co wtedy
    c.execute("SELECT * from Arduino_devices ")
    test = c.fetchone()
 #   print("test")
 #   print(test)
    for row in c:
        print(row)

    print(message)
    c.execute("SELECT * from Arduino_devices WHERE ID = '%s'" % message[0])
    conn.commit()
    arduino =c.fetchone()
 #   print("mamaa")
 #   print(arduino)
    if arduino != None and message[1]==arduino[1]:
     #   print("Urządzenie istnieje wprowadz sam pomiar")
         pass
        
    elif arduino != None and message[1]!=arduino[1]:
        print("Cos zle dziala")
    else:
        c.execute("INSERT INTO Arduino_devices VALUES (?, ?)",
                  (message[0], message[1]))
        conn.commit()
     #   print("Dodano nowe urządzenie")
    c.execute("INSERT INTO Temperatures (Date, Temperature,Device_ID ) VALUES (?, ?, ?)",
                  (str(datetime.now()), message[2], message[0]))
    
    conn.commit()
    c.execute("SELECT * from Temperatures")
    conn.commit()

 #   for row in c:
 #       print(row)
        
  #  string = ""
   # for n in receivedMessage:
        # Decode into standard unicode set
    #    if (n >= 32 and n <= 126):
    #        string += chr(n)
    #print("Out received message decodes to: {}".format(string))
    
    
connection.close()
    
    
