import network
import uasyncio as asyncio

# Global variable declarations
global wlan_sta
wlan_sta = None           # Will hold the station interface

async def connect(ssid, password):
    """
    Asynchronously connects the ESP32 to a Wi-Fi network using the given SSID and password.
    
    :param ssid: The SSID of the Wi-Fi network.
    :param password: The password of the Wi-Fi network.
    :return: True if connected successfully, False otherwise.
    """

    global wlan_sta

    # Announce station interface activation
    print("wifi_client: Station interface activated.\n")

    # Initialize and activate the station interface
    wlan_sta = network.WLAN(network.STA_IF)
    wlan_sta.active(True)

    # Begin connection
    wlan_sta.connect(ssid, password)

    # Announce the attempt to connect
    print("wifi_client: Attempting to connect to '" + ssid + "' as client.", end='')

    # Wait for connection with a timeout
    timeout = 20  # 10 seconds timeout
    while timeout > 0:
        if wlan_sta.isconnected():
            print("\n\nwifi_client: Connected to '{}' with IP address: {}\n".format(ssid, wlan_sta.ifconfig()[0]))
            return True
        await asyncio.sleep(1)  # Non-blocking wait
        print(".", end='') 
        timeout -= 1

    print("\n\nwifi_client: Failed to connect to '{}'.\n".format(ssid))
    return False

async def stop():
    """
    Asynchronously disconnects the ESP32 from the Wi-Fi network and deactivates the station interface.

    :return: None
    """
    global wlan_sta

    if wlan_sta and wlan_sta.isconnected():
        # Disconnect the station
        wlan_sta.disconnect()
        print("wifi_client: Disconnecting from Wi-Fi network.\n")

        # Wait for disconnection
        timeout = 10  # 10 seconds timeout for disconnection
        while timeout > 0:
            if not wlan_sta.isconnected():
                print("wifi_client: Disconnected successfully.\n")
                break
            await asyncio.sleep(1)  # Non-blocking wait
            timeout -= 1

    # Deactivate the station interface to save power and ensure it's truly disconnected
    if wlan_sta:  # Check if wlan_sta is initialized
        wlan_sta.active(False)
        print("wifi_client: Station interface deactivated.\n")

def get_default_gateway():
    return wlan_sta.ifconfig()[0]