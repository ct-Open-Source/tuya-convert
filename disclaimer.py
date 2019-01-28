#!/usr/bin/python3
# encoding: utf-8

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def show():
    disclaimer_text = color.BOLD + """
======================================================
TUYA-CONVERT
======================================================
""" + color.END + """

https://github.com/ct-Open-Source/tuya-convert

TUYA-CONVERT was developed by Michael Steigerwald from the IT security company VTRUST (https://www.vtrust.de/) in collaboration with the techjournalists Merlin Schumacher, Pina Merkert, Andrijan Möcker and Jan Mahn at c't Magazine. (https://www.ct.de/)
""" + color.RED + """
======================================================
PLEASE READ THIS CAREFULLY!
======================================================
""" + color.END + """

TUYA-CONVERT creates a fake update server environment for ESP8266/85 based tuya devices. It enables you to backup your devices firmware and upload an alternative one (e.g. ESPEasy, Tasmota, Espurna) without the need to open the device and solder a serial connection (OTA, Over-the-air).

Please make sure that you understand the consequences of flashing an alternative firmware, since you might lose functionality!

""" + color.RED + """
Flashing an alternative firmware can cause unexpected device behavior and/or render the device unusable. Be aware that you do use this software at YOUR OWN RISK! Please acknowledge that VTRUST and c't Magazine (or Heise Medien GmbH & Co. KG) CAN NOT be held accountable for ANY DAMAGE or LOSS OF FUNCTIONALITY by typing """+color.END + color.BOLD + """yes + Enter""" + color.END

    print(disclaimer_text)

def acknowledge():
    ack = input()
    if ack != "yes": quit()
