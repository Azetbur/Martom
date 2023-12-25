import network
import uasyncio as asyncio

# Global variable declarations
global wlan_sta
wlan_sta = None           # Will hold the station interface

async def client_connect(ssid, password):
    """
    Asynchronously connects the ESP32 to a Wi-Fi network using the given SSID and password.
    
    :param ssid: The SSID of the Wi-Fi network.
    :param password: The password of the Wi-Fi network.
    :return: True if connected successfully, False otherwise.
    """

    global wlan_sta

    # Initialize and activate the station interface
    wlan_sta = network.WLAN(network.STA_IF)
    wlan_sta.active(True)

    # Begin connection
    wlan_sta.connect(ssid, password)

    # Announce the attempt to connect
    print("Attempting to connect to " + ssid + " as client.")

    # Wait for connection with a timeout
    timeout = 10  # 10 seconds timeout
    while timeout > 0:
        if wlan_sta.isconnected():
            print("Connected to {} with IP address: {}".format(ssid, wlan_sta.ifconfig()[0]))
            return True
        await asyncio.sleep(1)  # Non-blocking wait
        timeout -= 1

    print("Failed to connect to {}".format(ssid))
    return False

def get_default_gateway():
    return wlan_sta.ifconfig()[0]