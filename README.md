
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
* a Raspberry Pi Zero W with Rasbian
* a Raspberry Pi 3B / 3B+ / 4B with Raspbian Stretch and its internal Wifi chip
* a Raspberry Pi 3B / 3B+ Raspberry Pi OS Buster (previously called Raspbian) and its internal Wifi chip
* a Raspberry Pi 3B+ + USB-WIFI with an image from [here](https://www.offensive-security.com/kali-linux-arm-images/)
* Ubuntu 18.04.3 64Bit in VirtualBox on Win10 with a cheap RTL8188CU Wifi Adapter connected to the VM
* Ubuntu Mate 18.04.5 32bit in VirtualBox on Win 10 with cheap Ralink 802.11n WLAN (MediaTek RT5370) WiFi Adapter connected to VM

Any Linux with a Wifi adapter which can act as an Access Point should also work. Please note that we have tested the Raspberry Pi with clean installations only. If you use your Raspberry Pi for anything else, we recommend using another SD card with a clean installation.

## PROCEDURE

On January 28th, 2019, Tuya started [distributing a patch](https://www.heise.de/newsticker/meldung/Smart-Home-Hack-Tuya-veroeffentlicht-Sicherheitsupdate-4292028.html) that prevented older versions of tuya-convert from completing successfully. We have since developed a work around to enable OTA flashing on some newer devices, but Tuya has since released [yet another patch](https://github.com/ct-Open-Source/tuya-convert/issues/483).

To ensure the best chance of success, **do not connect your device with the official app** as it may automatically update the device, preventing you from flashing with tuya-convert. It is up to the individual brands to update their firmware, so some devices may be affected sooner than others.

Unfortunately many devices have already been shipping with the new patched firmware, evident by a PSK ID beginning with 02 in smarthack-psk.log. There is no workaround at this time. Additionally, manufacturers have been silently switching from the ESP82xx based modules to other chipsets, making it impossible to install alternative ESP firmware on these devices.

### INSTALLATION
    # git clone https://github.com/ct-Open-Source/tuya-convert
    # cd tuya-convert
    # ./install_prereq.sh

### FLASH third-party firmware
BE SURE THE FIRMWARE FITS YOUR DEVICE!
1. Place your binary file in the `/files/` directory or use one of the included firmware images.

	Currently a [Tasmota](https://github.com/arendst/Tasmota) `tasmota-lite.bin` build is included in the Tuya-Convert package. You can easily update to the [current maintenance release](http://thehackbox.org/tasmota) via OTA **after** the flashing process completes successfully. The included binary does not have any specific hardware configured. Once flashed using Tuya-Convert you will need to configure your device(s) properly. Please note that while we include this firmware for your convenience, we are not affiliated with the Tasmota project and cannot provide support for post installation issues. Please refer to the [Tasmota project](https://github.com/arendst/Tasmota) and [its documentation](http://tasmota.com) for configuration and support. **IMPORTANT:** If you still want to update the tasmota binary before using Tuya-Convert, always pickup `tasmota-lite.bin`. **Never ever** use `tasmota-minimal.bin` as you will brick your device.

	An ESPurna [1.13.5](https://github.com/xoseperez/espurna/releases/tag/1.13.5) binary is also included (`espurna-base.bin`). Like before, the binary included does not have any specific hardware defined. Once flashed using Tuya-Convert you can update to the device-specific version via any of the means that ESPurna provides (OTA, web interface update, update via telnet or MQTT). Please refer to the [ESPurna project page](http://espurna.io) for more info and support.

	Binary requirements:
	* full binary including first-stage bootloader (tested with Arduino eboot and Open-RTOS rBoot)
	* maximum filesize 512KB for first flash

2. Start flashing process

	Execute `./start_flash.sh` and follow the instructions.
	It will install our flash loader onto the ESP and connect to the access point created by your wifi adapter.
	A backup of the original firmware will be automatically downloaded and stored locally.
	You can then proceed to flash your desired firmware or revert to the stock firmware.

3. Initial Configuration

	If you flashed the included Tasmota firmware file, it will broadcast a `tasmota-xxxx` access point (AP) when the device boots. Connect to this AP and open the browser to 192.168.4.1 to configure the device's Wi-Fi credentials. When entering the Wi-Fi password, click the checkbox to view the password you enter to ensure that it is correct and that your mobile device has not inadvertently capitalized the first letter if it is supposed to be lower case nor autocorrected what you entered. ~~Double~~ **Triple check the Wi-Fi credentials** before clicking **Save** to apply the settings.

	If you flashed the included ESPurna firmware file, the procedure will be very similar. The device will broadcast a `ESPURNA-XXXXXX` access point. You will have to connect to it using the default password: `fibonacci`. Once connected open the browser to 192.168.4.1 and follow the initial configuration instructions. Then go to the WIFI tab and configure your home WiFi connection (remember to save) or go to the ADMIN tab to upgrade the firmware to the device-specific image.

## USING DOCKER
You may want to use a docker image instead. Advantage of this solution: You don't have to install anything on your host (except docker), everything goes into the docker image.
Requirements:
* Linux computer with a wifi adapter
* Secondary wifi device (e.g. smartphone)
* docker is installed
* docker-compose is installed

Preparations:
* git clone https://github.com/ct-Open-Source/tuya-convert
* cd tuya-convert
* if you have already cloned this repo just cd into the directory and execute `git pull`
* cp .env-template .env 
* adjust the created .env-file, it contains usage information as comments

Building and running your container:
* `docker-compose build && docker-compose run --rm tuya`
* This directly starts into tuya. If you press ctrl+break or exit tuya after flashing, your container is closed and deleted

Troubleshooting:
* Q: Where are my logs after flashing? A: The folder can be adjusted in .env with LOCALBACKUPDIR, the path here may be relative or absolute
* Q: I don't want that my container is deleted after running tuya, I need this for troubleshooting! How do I accomplish this? A: Just remove --rm from `docker-compose run --rm tuya`
* Q: I want to start the container, but instead of starting tuya immediately I want to get into bash. Is this possible? A: Yes just start the container with `docker-compose run --entrypoint bash tuya`.
* Q: I want to rebuild my docker-image, even if there are no changes. Is this possible? A: Just start `docker-compose build --no-cache` instead of `docker-compose build`! Don't do this all the time, this is a time consuming process ...
* Q: I can't connect to my USB, PCI, ... network card. How do I get this working? A: You may have an error in your .env-File. The WLAN-variable should reflect the name of your network interface on your host. Execute ifconfig and look through your interfaces.
* Q: I can't get an IP-address and or connection on my phone, what's the problem? A: You may look into smarthack-wifi.log (location is set in .env with LOCALBACKUPDIR) or possible stop your firewall (e.g. NixOS seems to have a problem here). It may be a problem with a wrongly set network interface (see previous question)
* Q: The tool gets stuck on starting AP in a screen...? Ensure the WiFi card used for the procedure is not connected to any other WiFi network (disconnect and disable auto-connect / remove saved networks), and use a different network adapter (e.g., LAN or another WiFi card) for SSH access if needed.

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
