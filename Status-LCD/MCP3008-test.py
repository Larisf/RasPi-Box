#Python Timerklasse importieren
import time
#Python Raspberry Pi GPIO Klasse importieren
import RPi.GPIO as GPIO

# Festlegung der Nutzung der vorgegebenen Nummerierung der GPIOs
GPIO.setmode(GPIO.BCM)

# Namen von True und False zum besseren Verstaendnis festlegen (Klarnamen)
HIGH = True  # 3,3V Pegel (high)
LOW  = False # 0V Pegel (low)



# SCI Funktion
def getAnalogData(adCh, CLKPin, DINPin, DOUTPin, CSPin):
    # Pegel definieren
    GPIO.output(CSPin,   HIGH)    
    GPIO.output(CSPin,   LOW)
    GPIO.output(CLKPin, LOW)
        
    cmd = adCh
    cmd |= 0b00011000 # Kommando zum Abruf der Analogwerte des Datenkanals adCh

    # Bitfolge senden
    for i in range(5):
        if (cmd & 0x10): # 4. Bit pruefen und mit 0 anfangen
            GPIO.output(DINPin, HIGH)
        else:
            GPIO.output(DINPin, LOW)
        # Clocksignal negative Flanke erzeugen  
        GPIO.output(CLKPin, HIGH)
        GPIO.output(CLKPin, LOW)
        cmd <<= 1 # Bitfolge eine Position nach links verschieben
            
    # Datenabruf
    adchvalue = 0 # Wert auf 0 zuruecksetzen
    for i in range(11):
        GPIO.output(CLKPin, HIGH)
        GPIO.output(CLKPin, LOW)
        adchvalue <<= 1 # 1 Postition nach links schieben
        if(GPIO.input(DOUTPin)):
            adchvalue |= 0x01
    time.sleep(1)
    return adchvalue

# Konfiguration Eingangskanal und GPIOs Raspi-Belegung
#CH = 0  # Analog/Digital-Channel
CLK     = 11 # Clock  alles GPIO-Nummern GPIO1
DIN     = 9 # Digital in
DOUT    = 10 # Digital out
CS      = 7  # Chip-Select


# Pin-Programmierung
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(DIN, GPIO.OUT)
GPIO.setup(DOUT, GPIO.IN)
GPIO.setup(CS,   GPIO.OUT)


try:
  while True:
    for z in range (1):
      if (z ==0 or z==1):
        print "Kanal " + str(z) + ": " + str(getAnalogData(z, CLK, DIN, DOUT, CS))
      
      else:
        print "FEHLER "
      
#except KeyboardInterrupt:
finally:
  GPIO.cleanup()
