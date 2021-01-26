#!/bin/bash

NON_ESP_WARNING="WARNING: it appears this device does not use an ESP82xx and therefore cannot install ESP based firmware"

get_macs_from_wifi_log () {
	grep AP-STA-CONNECTED smarthack-wifi.log |
	cut -d ' ' -f3 |
	sort | uniq
}

get_ouis_from_wifi_log () {
	get_macs_from_wifi_log |
	tr -d : | grep -Po "^.{6}"
}

psk_02 () {
	grep -q "ID: 02" smarthack-psk.log
}

web_non_esp () {
	grep -q "$NON_ESP_WARNING" smarthack-web.log
}

udp_non_esp () {
	grep -q "$NON_ESP_WARNING" smarthack-udp.log
}

esp_oui () {
	get_ouis_from_wifi_log | grep -iqf- oui/esp.txt
}

non_esp_oui () {
	get_ouis_from_wifi_log | grep -iqf- oui/nonesp.txt
}

check_for_common_issues () {
	if psk_02; then
		echo "Your device's firmware is too new."
		echo "Tuya patched the PSK vulnerability that we use to establish a connection."
		echo "You might still be able to flash this device over serial."
		echo "For more information and to follow progress on solving this issue see:"
		echo "https://github.com/ct-Open-Source/tuya-convert/wiki/Collaboration-document-for-PSK-Identity-02"
		exit 1
	fi
	if web_non_esp || udp_non_esp || non_esp_oui; then
		echo "Your device does not use an ESP82xx."
		echo "This means you cannot flash custom ESP firmware even over serial."
		exit 1
	fi
	if esp_oui; then
		echo "An ESP82xx based device connected according to your wifi log."
		echo "If this is the device you are trying to flash, another issue may be preventing it from flashing."
		echo "Otherwise, it could be that the device does not use an ESP82xx or it did not connect."
	else
		echo "No ESP82xx based devices connected according to your wifi log."
		echo "Here is a list of all the MAC addresses that connected:"
		get_macs_from_wifi_log
		echo
		echo "If you see your IoT device in this list, it is not an ESP82xx based device."
		echo "Otherwise, another issue may be preventing it from connecting."
	fi
	echo "For additional information, check the *.log files inside the scripts folder."
	echo "Please include these logs when opening a new issue on our GitHub issue tracker."
}

check_for_common_issues

