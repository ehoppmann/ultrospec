#!/usr/bin/env python

import serial
import time
import numpy
import sys
def rem_matches(the_list, val):
   return [value for value in the_list if value != val]

ser = serial.Serial(
	'/dev/ttyS0',
	baudrate = 19200
)
# print ser
ref = int(raw_input("Is Cell 1 a referance? 0=no 1=yes: "))
num = int(raw_input("Number of samples (including ref): "))
wnb = int(raw_input("Wavelength Start: "))
wne = int(raw_input("Wavelength End: "))
if wne-wnb>800:
        print("Wavelength range too large for this version of scanUltrospecCSV.py (>800 nm)")
        sys.exit()

fn = raw_input("Output Filename: ")

print ('Opening Serial')
ser.write("control\r\n")
time.sleep(2)
ser.timeout=10

if wnb < 325:
	print("Sending command to light deuterium lamp for UV")
	ser.write("DON\r\n")
	print("If this is the first use of the lamp, wait at least 30s for warmup")
	raw_input("Press enter to continue...")

print('Reading Data')
# READ IN DATA
ser.flushInput()
s = ""

if wne-wnb > 400:
	wnm = wne-400
        for i in range(1,num+1):
		ser.write("CELL " + str(i) + "\r\n")
		ser.write("SCAN " + str(wnb) + "," + str(wnm) + " TEXT\r\n")
		time.sleep(10)
		il=ser.inWaiting()
		snew1=ser.read(il)
		ser.write("SCAN " + str(wnm+1) + "," + str(wne) + " TEXT\r\n")
		time.sleep(10)
		il=ser.inWaiting()
		snew2=ser.read(il)
		snew=snew1+snew2
		snew=snew.replace('E00\r\n', '')
		s=s+snew
else:
	for i in range(1,num+1):
		ser.write("CELL " + str(i) + "\r\n")
		ser.write("SCAN " + str(wnb) + "," + str(wne) + " TEXT\r\n")
		time.sleep(10)
		il=ser.inWaiting()
		snew=ser.read(il)
		s=s+snew

print('processing')
wlen=range(wnb,wne+1)
wlen=list(wlen)
sl=wlen+str.splitlines(s)
#sl=str.splitlines(s)
sl=rem_matches(sl,"E00 OK")
sl=rem_matches(sl,"E00")
array=numpy.asarray(sl)
array.shape = (num+1, len(sl)/(num+1))

array=numpy.float32(array)

# BACKGROUND SUBTRACTION
if ref == 1: 
	for i in range(2,num+1):
		array[i,] = array[i,] - array [1,]
else:
	print 'No BG subtraction'

# SAVE DATA
numpy.savetxt("/cygdrive/c/Users/DA/Desktop/"+fn+".csv", numpy.transpose(array), delimiter = ",",newline='\r\n')

ser.write("release\r\n")
ser.close()
