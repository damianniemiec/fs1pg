# GWF-S171 Smart Wifi Plug component for Home Assistant

# Install
## Manual
Copy fs1pg to custom_components folder

## HACS
URL: https://github.com/damianniemiec/fs1pg
type: integration

## Tested on:
* Ferguson Smart WiFi Plug FS1PG (http://ferguson-digital.eu/inteligentny-dom-ferguson/inteligentna-wtyczka-smart-w-fi-plug/)
### Could work with (not tested):
* Ogemray
* WeConn
* iSmartAlarm

**Sample configuration (configuration.yaml):**
```
switch:
  - platform: fs1pg
    device_name: device_name # name
    ip: "XXX.XXX.XXX.XXX" # plug ip address (could be network broadcast address like 192.168.0.255)
    broadcast: false # set to true if broadcst
    mac: "XX:XX:XX:XX:XX:XX" # plug MAC address
    scan_interval: 10 # update interval
```

MAC address can be found in app (ex. WeConn)
![WeConn screenshot](Screenshot_20181223-235137.jpg)