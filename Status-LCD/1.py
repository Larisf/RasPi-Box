import time
import MCP3008
import RPi.GPIO as GPIO

adCh = 0
CLK = 11
DIN = 9
DOUT = 10
CS = 7
TRESHOLD = 3



GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(DIN, GPIO.OUT)
GPIO.setup(DOUT, GPIO.IN)
GPIO.setup(CS, GPIO.OUT)





while True:

	wert = MCP3008.getAnalogData(adCh, CLK, DIN, DOUT, CS)/float(310)
	#float(310) = 1023/310 = 3.3
	ref = 15/float(3.3)
	wert12v = wert * ref
	wertg = round(wert12v, 3)
	print str(wertg)
