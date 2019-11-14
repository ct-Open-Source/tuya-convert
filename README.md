
# TUYA-CONVERT

A Chinese company named Tuya offers a free-to-brand turnkey smart home solution to anyone. Using their offer is dead-simple, since everything can be done by clicking through the [Tuya web page](https://en.tuya.com/), from choosing your pre-designed products or pre-programmed wifi-modules (mostly ESP8266) to building your own app. In the end, this has resulted in as they claim over 11 000 devices 'made' by over 10 000 vendors using Tuyas firmware and cloud services.

Aside from that, they claim their cloud solution has 'military grade security'. Michael Steigerwald, founder of the German IT security startup VTRUST, was able to disprove this claim and presented his results in the "Smart home - Smart hack" talk at 35C3 in Leipzig: https://media.ccc.de/v/35c3-9723-smart_home_-_smart_hack

In the following days, VTRUST and the German tech magazine c't decided to work together. Since reflashing devices using the ESP8266/85 is widespread among DIY smart home enthusiasts, we wanted to provide an easy way for everyone to free their devices from the cloud without the need for a soldering iron. 

Please make sure to visit VTRUST (https://www.vtrust.de/), since the hack is their work.

## 🚨WARNING🚨
Please be sure that you understand what you're doing before using this software. Flashing an alternative firmware can lead to unexpected behavior and/or render the device unusable, so that it might be permanently damaged (highly unlikely) or require soldering a serial connection to the processor in order to reflash it (likely). 

### ⚠️ Be aware that you use this software at your own risk so neither VTRUST nor c't/heise can be held accountable for any damage done or loss of functionality. ⚠️ 

TUYA-CONVERT only provides with the means to backup the original and flash an alternative firmware. Please do not ask for hardware support for your favorite alternative firmware in this repository, rather open an issue in the corresponding repository.

## DOCUMENTATION
Since Tuya devices are spread around the world with likely a vast amount of different brand names, please tell the community if you find one! There is a device list in the wiki that you can help extend. Please at least add the device model number, brand name, geographical area where you have bought the device and its flash mode (as seen in the device information). Add the GPIO assignments as well if you have found them to save the developers of alternative firmwares some time. Please note that we do not develop or maintain alternative firmwares and so post installation issues should be directed to the respective project.

[![asciicast](https://asciinema.org/a/2aDZweVGfliwc9TjB1ncwmKvm.png)](https://asciinema.org/a/2aDZweVGfliwc9TjB1ncwmKvm
)

## REQUIREMENTS
* Linux computer with a wifi adapter
* Secondary wifi device (e.g. smartphone)
* Dependencies will be installed by `install_prereq.sh`

These scripts were tested in 
* Kali-Linux 2018.4 in VMWARE
* a Raspberry Pi 3B / 3B+ with Raspbian Stretch and its internal Wifi chip
* a Raspberry Pi 3B+ + USB-WIFI with this image from [here](https://www.offensive-security.com/kali-linux-arm-images/)
	https://images.offensive-security.com/arm-images/kali-linux-2018.4a-rpi3-nexmon-64.img.xz
	
Any Linux with a Wifi adapter which can act as an Access Point should also work. Please note that we have tested the Raspberry Pi with clean installations only. If you use your Raspberry Pi for anything else, we recommend using another SD card with a clean installation.

## PROCEDURE

On January 28th, 2019, Tuya started [distributing a patch](https://www.heise.de/newsticker/meldung/Smart-Home-Hack-Tuya-veroeffentlicht-Sicherheitsupdate-4292028.html) that prevented older versions of tuya-convert from completing successfully. We have since developed a work around to enable OTA flashing once again, but there is always the possibility that Tuya will respond with yet another patch. To ensure the best chance of success, **do not connect your device with the official app** as it may automatically update the device, preventing you from flashing with tuya-convert. It is up to the individual brands to update their firmware, so some devices may be affected sooner than others.

### INSTALLATION
    # git clone https://github.com/ct-Open-Source/tuya-convert
    # cd tuya-convert
    # ./install_prereq.sh
### flash loader firmware + backup
    # ./start_flash.sh

Follow the instructions in the start_flash script. It will install our flash loader onto the ESP and connect to the access point created by your wifi adapter.

    WIFI: vtrust-flash
    IP: 10.42.42.42
A backup of the original firmware will be created and stored locally

### Device information
After the firmware backup procedure, the retrieved device information will be shown.
Please make sure to write down your devices flash mode and size!
You can show this information again by executing:

    # curl http://10.42.42.42
### BACKUP only and UNDO
You can use the flash loader to create a backup only.
If you want to go back to the stock software just do following:

    # curl http://10.42.42.42/undo
### FLASH third-party firmware
BE SURE THE FIRMWARE FITS YOUR DEVICE!
1. Place or link your binary file to ./files/thirdparty.bin.

	Currently a Tasmota [v7.0.0.3](https://github.com/arendst/Tasmota/releases) `tasmota-wifiman.bin` build is included. You can update to a [current version](http://thehackbox.org/tasmota) via OTA after the Tuya-Convert process completes successfully. Please note that while we include this for your convenience, we are not affiliated with the Tasmota project and cannot provide support for post installation issues. Please refer to [the respective project](https://github.com/arendst/Tasmota) for configuration and support.
	
	An ESPurna [1.13.5](https://github.com/xoseperez/espurna/releases/tag/1.13.5) binary is also included (`espurna-base.bin`). Like before, the binary included does not have any specific hardware defined. Once flashed using Tuya-Convert you can update to the device-specific version via any of the means that ESPurna provides (OTA, web interface update, update via telnet or MQTT). Please refer to the [ESPurna project page](http://espurna.io) for more info and support.

	Binary requirements:
	* full binary including first-stage bootloader (tested with Arduino eboot and Open-RTOS rBoot)
	* maximum filesize 512KB for first flash

2. Start flashing process

        # curl http://10.42.42.42/flash

	Alternatively you can request a certain file to be requested and flashed by the device:

        # curl http://10.42.42.42/flash?url=http://10.42.42.1/files/certain_file.bin

3. Initial Configuration

	If you flashed the included Tasmota firmware file, it will broadcast a `tasmota-xxxx` access point (AP) when the device boots. Connect to this AP and open the browser to 192.168.4.1 to configure the device's Wi-Fi credentials. When entering the Wi-Fi password, click the checkbox to view the password you enter to ensure that it is correct and that your mobile device has not inadvertently capitalized the first letter if it is supposed to be lower case nor autocorrected what you entered. ~~Double~~ **Triple check the Wi-Fi credentials** before clicking **Save** to apply the settings.

	If you flashed the included ESPurna firmware file, the procedure will be very similar. The device will broadcast a `ESPURNA-XXXXXX` access point. You will have to connect to it using the default password: `fibonacci`. Once connected open the browser to 192.168.4.1 and follow the initial configuration instructions. Then go to the WIFI tab and configure your home WiFi connection (remember to save) or go to the ADMIN tab to upgrade the firmware to the device-specific image. 

## CONTRIBUTING

This project is currently maintained by Colin Kuebler @kueblc

Significant time and resources are devoted to supporting and maintaining this project. Research, development, and testing requires obtaining and often breaking IoT devices and related hardware. To help offset costs and support the developers who make this project possible, please consider making a one-time or recurring donation. This allows us to spend less time worrying about putting food on the table and more time making great software accessible to everyone.

- [Become a Patron](https://www.patreon.com/kueblc)
- [Buy Me A Coffee](https://www.buymeacoffee.com/kueblc)
- [PayPal](https://paypal.me/kueblc)

You can also give back by providing or improving documentation, tutorials, issue support, bug reports, feature requests, and pull requests. When planning to contribute major code changes, please post your intention beforehand so we can coordinate, avoid redundant contributions and ensure the changes match project philosophy. Any major PR should be made against the `development` branch.

## RELATED WORKS
- [TuyAPI](https://github.com/codetheweb/tuyapi) NPM library for LAN control of Tuya devices with stock firmware
- [TuyOTA](https://github.com/SynAckFin/TuyOTA) Perl based Tuya flashing script using a similar strategy
- [MockTuyaCloud](https://github.com/kueblc/mocktuyacloud) Framework replicating much of the Tuya cloud functionality

