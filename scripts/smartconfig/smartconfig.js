#!/usr/bin/env node

//cmd = system("ip route add 255.255.255.255 dev wlan0")
// --> Broadcast must be routed over WIFI
// --> Any other WIFI device needs to be connected during pairing process!

const ssid = "vtrust-flash"
const passwd = "flashmeifyoucan"
const wait_time = 60; // seconds

function sleep(seconds){
    var waitUntil = new Date().getTime() + seconds*1000;
    while(new Date().getTime() < waitUntil) true;
}

const debug = require('debug')('Main');
//const ora = require('ora');

const TuyaLink = require('@tuyapi/link');
const manual = new TuyaLink.manual();

console.log('Put Device in Learn Mode!, sending Smartlink Packets now');

manual.registerSmartLink({region: 'EU',
                           token: '00000000',
                           secret: '0101',
                           ssid: ssid,
                           wifiPassword: passwd});

console.log('Smartlink in progress');
console.log('Sending SSID                  '+ssid);
console.log('Sending wifiPassword          '+passwd);
console.log('Sending Packets and wait '+wait_time+' seconds.');

