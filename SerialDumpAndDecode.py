#!/usr/bin/python3
 
import serial
import serial.tools.list_ports as port_list
import time
import os
from os import path
#import crcmod # pip install crcmod

from tkinter import *
from tkinter import filedialog

import pprint

fenster = Tk()
fenster.filename = ""
fenster.filename = filedialog.askopenfilename(initialdir = "./", title = "Logdatei File", filetypes =(("bin files","*.bin"),("all files","*")))
print('Input:  ',fenster.filename)
vPath = fenster.filename
fenster.destroy()

class SmlCrc:
    """ Class for Smart Message Language (SML) CRC calculation. """

    def __init__(self):
        self.crc_table = []
        self.crc_init()

    def crc_init(self):
        """ Init the crc look-up table for byte-wise crc calculation. """
        polynom = 0x8408     # CCITT Polynom reflected
        self.crc_table = []

        for byte in range(256):
            crcsum = byte
            for bit in range(8):  # for all 8 bits
                if crcsum & 0x01:
                    crcsum = (crcsum >> 1) ^ polynom
                else:
                    crcsum >>= 1
            self.crc_table.append(crcsum)

    def crc(self, data):
        """ Calculate CCITT-CRC16 checksum byte by byte. """
        crcsum = 0xFFFF

        for byte in data:
            idx = byte ^ (crcsum & 0xFF)
            crcsum = self.crc_table[idx] ^ (crcsum >> 8)

        return crcsum ^ 0xFFFF
    
Escape   = 0x1B1B1B1B
Version1 = 0x01010101
TL       = {"List" : {"size" : 1 , "value" : 0x70},
            "Unsigned" : {"size" : 1 , "value" : 0x60},
            "Integer" : {"size" : 1 , "value" : 0x50},
            "Boolean" : {"size" : 1 , "value" : 0x40},
            "String" : {"size" : 1 , "value" : 0x00},
            "ExtString" : {"size" : 2 , "value" : 0x80},
            "Other" : {"size" : 2 , "value" : 0xC0}}  # Size 2 bedeutet auch Bit 7

def OpenPacked(aData):
    sml = SmlCrc()
    crcCalc = sml.crc(Data[0:-2])
    crcFile = int.from_bytes(Data[-2:], "little")
    if crcCalc != crcFile:
        return None 
    if int.from_bytes(Data[0:4], "big") != Escape:
        return None
    if int.from_bytes(Data[4:8], "big") != Version1:
        return None
    if int(Data[-4]) != 0x1A:
        return None
    FillBytes = int(Data[-3])
    return aData[8:-(8+FillBytes)]

def ParseTL_Fields(aData):
    offset = 0
    aDict = {}
    msgCRC = SmlCrc()
    aSubdict = aDict
    size = 0
    listsize = 0
    print(len(aData))
    start = offset
    while offset < len(aData):
        byte = aData[offset]
        offset +=1
        print(offset)
        #if offset < len(aData)-2:
        #    if aData[offset+2] == 0:
        #        crcMsg = hex(int.from_bytes(Data[offset:offset+2], "little"))
        #        offset +=2
        #        byte = aData[offset]
        if byte == 0:
            start = offset
            continue   # Message End
        for key in TL.keys():
            if TL[key]["value"] == ((byte) & 0xf0):
                size = (byte & 0x0f) - 1
                if byte & 0x80:
                    byte = aData[offset]
                    offset +=1
                    size = (size + 1) * 16 + ((byte & 0x0f) -1)
                    print("oversize")
                print(size, key)
                if key == "List":
                    if aData[offset] > 1:
                        listsize = size
                        aDict[key+str(offset)] = {}
                        aSubdict = aDict["List"+str(offset)]
                    else:
                        aSubdict = aDict
                        offset +=1
                else:
                    if (key == "Unsigned") and (size == 2) and (aData[offset+2] == 0):
                       crcMsg = hex(int.from_bytes(aData[offset:offset+size], "little")) 
                       print("CRC:", crcMsg , hex(msgCRC.crc(aData[start:offset]))) 
                    else:
                        aSubdict[key+str(offset)] = hex(int.from_bytes(aData[offset:offset+size], "big"))
                        print(aSubdict[key+str(offset)])
                    offset = offset + size
                    if listsize > 0:
                        listsize = listsize - 1
                    else:
                        aSubdict = aDict
                
                #print(offset, key, byte, TL[key]["value"])
    pprint.pprint(aDict)

def DecodePacked(Data):
    Data = OpenPacked(Data)
    ParseTL_Fields(Data)
    if Data:
        offset = 0
        aDict = {}
        Message = int.from_bytes(Data[offset:offset+2], "big")
        offset+=2
        aDict['SML-Message'] = hex(Message)
        size = (Message & 0xFF) - 1
        aDict['transactionId'] = hex(int.from_bytes(Data[offset:offset+size], "big"))
        offset+=size
        aDict['groupNo'] = hex(int.from_bytes(Data[offset:offset+2], "big"))
        offset+=2
        aDict['abortOnError'] = hex(int.from_bytes(Data[offset:offset+2], "big"))
        offset+=2
        aDict['messageBody'] = hex(int.from_bytes(Data[offset:offset+4], "big"))
        offset+=5
        end = offset
        msgCRC = SmlCrc()
        print(hex(msgCRC.crc(Data[0x3D:0xF8])))

        aDict['Verbrauch kW'] = (int.from_bytes(Data[0xb4:0xb8], "big"))
        print(aDict)
    else:
        print("CRC Fehler")

    
if path.exists(vPath):
    with open(vPath, 'rb') as f:
        Data = f.read()

    print(Data) 
    DecodePacked(Data)
else:

    
    # Verfügbare Serielle Ports
    ports = list(port_list.comports())
    print(ports[0].device)
    #port = ports[0].device
     
    # Seriellen Port Konfigurieren:
    ser = serial.Serial()
    # Hier den passenden Port angeben
    ser.port = 'COM3' if os.name=='nt' else '/dev/ttyACM0'
    ser.baudrate = 9600
    ser.timeout = 0.6
     
    # Port öffnen
    ser.open()
    print("Port geöffnet")
    time.sleep(3)





    try:
        n = 0
        while 1:
            # Zeile als Bytestring einlesen und
            # mit decode in normalen string konvertieren.
            string = ser.read(4000)
            n = n + 1
            try:
                print(string)
                Name = 'Log'+str(n)+'.bin'
                with open(Name, 'wb') as f:
                    f.write(string)
                
            except:
                print("Decodierungsfehler")

                
    # Keyboard Interrupt abfangen, zum beenden mit [STRG]+[C].
    except(KeyboardInterrupt, SystemExit):
        print("\nWird Beendet:")
        ser.close()
        print("Com Port geschlossen!")
        print("\nENDE")
