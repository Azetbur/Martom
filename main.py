
# Announce successfull boot completion
print("\nmain       : ESP32 boot cycle completed successfully\n")

import uasyncio as asyncio
import wifi_ap

AP_SSID = "ESP32"
AP_PASSWORD = "S-Max120"

asyncio.run(wifi_ap.create_and_run(AP_SSID, AP_PASSWORD))
