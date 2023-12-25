"""
@file boot.py
@brief A program which controls led lightning strips via pwm with the option to configure certain
parameters of the lightning via either a webserver of a knob and a dot matrix display.

@details
TODO: complete

Project name: Martom
Author:
  - Jindřich Kocman
"""

# Announce successfull boot completion
print("\nmain       : ESP32 boot cycle completed successfully\n")

import uasyncio as asyncio
import wifi_ap

AP_SSID = "ESP32"
AP_PASSWORD = "S-Max120"

asyncio.run(wifi_ap.create_and_run(AP_SSID, AP_PASSWORD))
