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

# Breaking changes:
Remove all entries from configuration.yaml and add devices in integrations  

[![http://www.google.pl](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=fs1pg)

### Manual configuration steps
If the above My button doesn’t work, you can also perform the following steps manually:  
  
Browse to your Home Assistant instance.  
In the sidebar click on  [Configuration](https://my.home-assistant.io/redirect/config).  
From the configuration menu select:  [Integrations](https://my.home-assistant.io/redirect/integrations).  
In the bottom right, click on the  [Add Integration](https://my.home-assistant.io/redirect/config_flow_start?domain=fs1pg) button.  
From the list, search and select “GWF-S171 Smart Wifi Plug”.  
Follow the instruction on screen to complete the set up.  

MAC address can be found in app (ex. WeConn)  
![WeConn screenshot](Screenshot_20181223-235137.jpg)