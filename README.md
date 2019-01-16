# smarthome-smarthack
Here you can find scripts to upgrade certain IoT-devices using esp8266 to any firmware without soldering etc.
The devices and methods were analyzed and described at the 35c3 conference in Germany.
The talk "Smart home - Smart hack" from Michael Steigerwald can be viewed here:
https://media.ccc.de/v/35c3-9723-smart_home_-_smart_hack

!!! USE THIS SCRIPTS AT YOUR OWN RISK !!!

## REQUIREMENTS
These scripts were tested in 
* Kali-Linux 2018.4 in VMWARE
* a Raspberry Pi 3B+ + USB-WIFI with this image from [here](https://www.offensive-security.com/kali-linux-arm-images/)
	https://images.offensive-security.com/arm-images/kali-linux-2018.4a-rpi3-nexmon-64.img.xz
	
Any Linux with a Wifi which can act as an Access Point should work.
We did not succeed to use the built-in Wifi of a Raspberry Pi 3B+ or 3B

## PROCEDURE
### INSTALLATION
    # git clone https://github.com/vtrust-de/smarthome-smarthack
    # cd smarthome-smarthack
    # ./install_prereq.sh
### FLASH loader firmware + backup
    # ./start_flash.sh

Follow the instructions and our FLASH loader will be installed in the esp8266.
After it will connect with a static IP to the WIFI

    WIFI: vtrust-flash
    PASS: flashmeifyoucan
    IP: 10.42.42.42
A backup of the original firmware will be created and stored locally
### Device information
During loading some information about your device will been shown.
You can see them in a browser or by using following command:

    # curl http://10.42.42.42
### BACKUP only and UNDO
You can use the FLASH loader to create a backup only.
If you want to delete the FLASH loader out of the flash again and go back to the stock software just do following:

    # curl http://10.42.42.42/undo
### FLASH loader to user2
The FLASH loader only allows flashing the thirdparty firmware, if the loader is running in the userspace user2 starting from 0x81000.
This will flash the FLASH loader in user2 if it is not already there.
It will destroy your ability to undo and go back to the original firmware

    # curl http://10.42.42.42/flash2
### FLASH third-party firmware
BE SURE THE FIRMWARE FITS YOUR DEVICE!
Place or link your binary file to ./files/thirdparty.bin

    # curl http://10.42.42.42/flash3
## EXAMPLE
Here you can see a recording of the full process:
https://asciinema.org/a/2aDZweVGfliwc9TjB1ncwmKvm
