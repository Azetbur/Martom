"""
@file wifi_ap.py
@brief Creates and manages an access point with a web server.

@details
This script includes functions to asynchronously create and run an access point with a given SSID and password,
using the ESP32's networking capabilities. It also contains functionality to start a simple web server that can serve
web pages and handle HTTP requests.

Primary Functions:
- ap_create_and_run: Sets up and runs the access point and web server.
- ap_stop: Stops the access point and server, deactivating the network interface.

Project name: Martom
Author:
  - Jindřich Kocman
"""

import network
import uasyncio as asyncio
import webserver

# Global variable declarations
global ap, server, is_shutting_down
ap = None           # Will hold the access point interface
server = None       # Will hold the server object
is_shutting_down = False    # Flag to indicate shutdown

async def create_and_run(ssid, password):
    """
    Asynchronously creates and runs an access point with the given SSID and password, and starts a simple web server.

    This function initializes and configures a new wireless access point using the provided
    SSID and password. It then activates the access point to allow devices to connect. After
    the access point is active, it starts an asynchronous web server listening on port 80.
    The server handles incoming HTTP requests and serves web pages.

    :param ssid: The SSID (name) of the access point to create.
    :param password: The password for securing the access point.

    :note: This function is asynchronous and should be awaited. It continuously runs the web server
           in an infinite loop, handling incoming client connections and serving web content.

    :note: Ensure that the function 'handle_client' for handling client connections is defined
           and properly set up to manage incoming HTTP requests.
    """

    global ap, server

    # Create an access point interface
    ap = network.WLAN(network.AP_IF)  

    # Activate the interface
    ap.active(True)

    # Set the SSID, password and authmode
    ap.config(essid=ssid, password=password, authmode=3) # authmode=3 means WPA2

    # Wait until the AP is active
    while not ap.active():
        await asyncio.sleep(1)

    # Announce access point activation
    print("Acess point created with successfully with the following parameters:")
    print("  ssid: " + ssid)
    print("  password: " + password)
    print("  default gateway: ")

    """
    # Setup socket server for handling webpages
    server = await asyncio.start_server(webserver.handle_client, '0.0.0.0', 80)
    async with server:
        await server.serve_forever()
    """
    
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(webserver.handle_client, '0.0.0.0', 80)
    server = loop.run_until_complete(coro)

    loop.run_forever()

async def stop():
    """
    Asynchronously stops the access point and the server.

    This function deactivates the wireless access point and shuts down the server,
    closing any existing client connections. It's meant to provide a clean shutdown
    procedure.

    :note: This function is asynchronous and should be awaited.
    """

    global ap, server, is_shutting_down

    # Signal that shutdown is in progress
    is_shutting_down = True

    # Stop the server
    if server:
        server.close()  # Stop the server from accepting new connections
        await server.wait_closed()  # Wait until the server is closed

    # Deactivate the access point interface
    if ap:
        ap.active(False)

    print("Server and Access Point have been stopped.")

# EOF
