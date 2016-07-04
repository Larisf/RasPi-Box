#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import re
import subprocess
import os
import MCP3008 


def bytestomb(b):
    mb = round(float(b) / (1024*1024),2)
    return mb

def get_ram():
    "Returns a tuple (total ram, available ram) in megabytes. See www.linuxatemyram.com"
    try:
        s = subprocess.check_output(["free","-m"])
        lines = s.split('\n')       
        return ( int(lines[1].split()[1]), int(lines[2].split()[3]) )
    except:
        return 0

def get_up_stats():
    "Returns a tuple (uptime, 5 min load average)"
    try:
        s = subprocess.check_output(["uptime"])
        load_split = s.split('load average: ')
        load_five = float(load_split[1].split(',')[1])
        up = load_split[0]
        up_pos = up.rfind(',',0,len(up)-4)
        up = up[:up_pos].split('up ')[1]
        return ( up , load_five )       
    except:
        return ( "" , 0 )

def get_sysload():
        s = os.getloadavg()

def get_network_bytes(interface):
    output = subprocess.Popen(['ifconfig', interface], stdout=subprocess.PIPE).communicate()[0]
    rx_bytes = re.findall('RX bytes:([0-9]*) ', output)[0]
    tx_bytes = re.findall('TX bytes:([0-9]*) ', output)[0]
    return (bytestomb(rx_bytes), bytestomb(tx_bytes))

def get_temperature():
    "Returns the temperature in degrees C"
    try:
        s = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"])
        return float(s.split('=')[1][:-3])
    except:
        return 0

def get_cpu_speed():
    "Returns the current CPU speed"
    f = os.popen('/opt/vc/bin/vcgencmd get_config arm_freq')
    cpu = f.read()
    return cpu[9:]


# Zuordnung der GPIO Pins (ggf. anpassen)
DISPLAY_RS = 22
DISPLAY_E  = 8
DISPLAY_DATA4 = 25  
DISPLAY_DATA5 = 24
DISPLAY_DATA6 = 23
DISPLAY_DATA7 = 18
CLK = 11
DIN = 9
DOUT = 10
CS = 7
adCh= 0


DISPLAY_WIDTH = 16 	# Zeichen je Zeile
DISPLAY_LINE_1 = 0x80 	# Adresse der ersten Display Zeile
DISPLAY_LINE_2 = 0xC0 	# Adresse der zweiten Display Zeile
DISPLAY_CHR = True
DISPLAY_CMD = False
E_PULSE = 0.00005
E_DELAY = 0.00005


def main():
	while True:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(DISPLAY_E, GPIO.OUT)
		GPIO.setup(DISPLAY_RS, GPIO.OUT)
		GPIO.setup(DISPLAY_DATA4, GPIO.OUT)
		GPIO.setup(DISPLAY_DATA5, GPIO.OUT)
		GPIO.setup(DISPLAY_DATA6, GPIO.OUT)	
		GPIO.setup(DISPLAY_DATA7, GPIO.OUT)
		GPIO.setup(CLK, GPIO.OUT)
		GPIO.setup(DIN, GPIO.OUT)
		GPIO.setup(DOUT, GPIO.IN)
		GPIO.setup(CS, GPIO.OUT)

		wert = MCP3008.getAnalogData(adCh, CLK, DIN, DOUT, CS)/float(310)
		ref = 15/float(3.3)
		wert12v = wert * ref
		wertg = round(wert12v, 3)

		display_init()

		rx_bytes, tx_bytes = get_network_bytes('eth0')
		rx1_bytes, tx1_bytes = get_network_bytes('wlan0')
	
		lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
		lcd_string('Home - '+get_up_stats()[0])
	
		lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)
		lcd_string('Free: '+str(get_ram()[1])+'/'+str(get_ram()[0])+'MB')
		time.sleep(5)

		lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
		lcd_string('C: '+str(get_temperature())+chr(223)+'C '+str(get_cpu_speed()[:3])+'MHz')

		lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)
		#lcd_string('Ld: '+str(os.getloadavg()[:2]))
		lcd_string(str(wertg) + " Volt")

		time.sleep(5)
	
		lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
		lcd_string('Eth0 send/rec.')

		lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)
		lcd_string(str(rx_bytes)+'/'+str(tx_bytes)+' MB')

		time.sleep(5)

		lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
		lcd_string('WLAN0 send/rec.')

		lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)
		lcd_string(str(rx1_bytes)+'/'+str(tx1_bytes)+' MB')
		time.sleep(5)

		
def display_init():
	lcd_byte(0x33,DISPLAY_CMD)
	lcd_byte(0x32,DISPLAY_CMD)
	lcd_byte(0x28,DISPLAY_CMD)
	lcd_byte(0x0C,DISPLAY_CMD)  
	lcd_byte(0x06,DISPLAY_CMD)
	lcd_byte(0x01,DISPLAY_CMD)  

def lcd_string(message):
	message = message.ljust(DISPLAY_WIDTH," ")  
	for i in range(DISPLAY_WIDTH):
	  lcd_byte(ord(message[i]),DISPLAY_CHR)

def lcd_byte(bits, mode):
	GPIO.output(DISPLAY_RS, mode)
	GPIO.output(DISPLAY_DATA4, False)
	GPIO.output(DISPLAY_DATA5, False)
	GPIO.output(DISPLAY_DATA6, False)
	GPIO.output(DISPLAY_DATA7, False)
	if bits&0x10==0x10:
	  GPIO.output(DISPLAY_DATA4, True)
	if bits&0x20==0x20:
	  GPIO.output(DISPLAY_DATA5, True)
	if bits&0x40==0x40:
	  GPIO.output(DISPLAY_DATA6, True)
	if bits&0x80==0x80:
	  GPIO.output(DISPLAY_DATA7, True)
	time.sleep(E_DELAY)    
	GPIO.output(DISPLAY_E, True)  
	time.sleep(E_PULSE)
	GPIO.output(DISPLAY_E, False)  
	time.sleep(E_DELAY)      
	GPIO.output(DISPLAY_DATA4, False)
	GPIO.output(DISPLAY_DATA5, False)
	GPIO.output(DISPLAY_DATA6, False)
	GPIO.output(DISPLAY_DATA7, False)
	if bits&0x01==0x01:
	  GPIO.output(DISPLAY_DATA4, True)
	if bits&0x02==0x02:
	  GPIO.output(DISPLAY_DATA5, True)
	if bits&0x04==0x04:
	  GPIO.output(DISPLAY_DATA6, True)
	if bits&0x08==0x08:
	  GPIO.output(DISPLAY_DATA7, True)
	time.sleep(E_DELAY)    
	GPIO.output(DISPLAY_E, True)  
	time.sleep(E_PULSE)
	GPIO.output(DISPLAY_E, False)  
	time.sleep(E_DELAY)   

if __name__ == '__main__':
	main()


