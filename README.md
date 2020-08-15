# Stagg EKG Plus
This project uses Python to communicate with the [Fellow Stagg EKG+]() over BLE. A lot of the information used to create this program came from [this post](https://www.reddit.com/r/homeassistant/comments/ek47k2/ble_reverse_engineering_a_fellow_stagg_ekg_kettle/) and additional testing I performed.

This is intended to be used with Homebridge and [my `homebridge-kettle` plugin](https://github.com/calvinmclean/homebridge-kettle).


## Getting Started
Currently, the only change that should be needed is changing the `MAC` variable in `api.py`. I plan to add something with a configuration file or environment variable to make this simpler.

Before running you will need to [install `bluepy`](https://github.com/IanHarvey/bluepy).


## Systemd
I run this on a Raspberry Pi alongside Homebridge, so I cloned this repo at `/root/stagg-ekg-plus` and setup this Systemd Service file to easily handle restarts and log to `syslog`:
```
[Unit]
Description=Python 3 API for Stagg EKG+
After=syslog.target network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 -u /root/stagg-ekg-plus/api.py
Restart=on-failure
RestartSec=10
KillMode=process
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
```
