"""
@file webserver.py
@brief Asynchronous web server for handling Wi-Fi connections and HTTP requests on ESP32.

@details
This file includes asynchronous functions to handle incoming HTTP client connections, process requests,
and serve HTML content. The webserver itself facilitates Wi-Fi network management, allowing the ESP32
to connect to existing networks.

Primary Functions:
- handle_client: Handles incoming HTTP requests and serves responses.
- display_warning_html: Serves the 'warning.html' page.
- display_selection_html: Serves the 'selection.html' page.
- display_password_html: Serves the 'password.html' page.
- display_success_or_failure_html: Serves either the 'selection.html' page or the 'success.html' page.

Project name: Martom
Author:
  - Jindřich Kocman
"""

import network
import uasyncio as asyncio
import ure
from my_network import wifi_ap
from my_network import wifi_client

# Will hold the SSID of the Wi-Fi the ESP32 will be connecting to as station
global ssid
ssid = ''

async def handle_client(reader, writer):
    """
    Asynchronously handle an incoming client connection, processing the HTTP requests and dispatching 
    to appropriate handlers based on the method and path.
    
    :param reader: The stream to read data from the client.
    :param writer: The stream to write data to the client.
    """
   
    try:

        # Read the request line and headers
        request_line = await reader.readline()
        request = request_line.decode('utf-8').strip()
        headers = {}
        content_length = 0

        while True:
            line = await reader.readline()
            if line == b"\r\n" or line == b'': break  # End of headers or empty line
            header_line = line.decode('utf-8').strip()
            header_key, header_value = header_line.split(": ", 1)
            headers[header_key] = header_value

            # Look for the Content-Length header to determine the size of the body
            if header_key.lower() == "content-length":
                content_length = int(header_value)

        # Determine request type
        request_method, path, _ = request.split(' ')

         # Get client's address information
        client_address = writer.get_extra_info('peername')  # Returns a tuple (host, port)
        client_host, client_port = client_address if client_address else ("Unknown", "Unknown")

        # Print the path and client address
        print(f"web_server : Request: '{path}' from {client_host}:{client_port}\n")

        # Initialize variable to hold POST data
        post_data = ""

        # Read the POST data if it's a POST request and has a body
        if request_method == "POST" and content_length > 0:
            post_data_bytes = await reader.readexactly(content_length)
            post_data = post_data_bytes.decode('utf-8')

        # Go to 'warning.html' if not a POST request
        if request_method != "POST":
            #await display_warning_html(writer)
            await display_homepage_html(writer)
        else:
            # Process the POST request based on the URL
            if path == "/":
                await display_warning_html(writer)
            elif path == "/go_to_selection":
                await display_selection_html(writer, None)
            elif path == "/go_to_password":
                await display_password_html(writer, post_data)
            elif path == "/go_to_success_or_failure":
                await display_success_or_failure_html(writer, post_data)
            else:
                await display_warning_html(writer)

    except Exception as e:

        print(f"web_server : Error in handle_client: {e}\n")

    finally:

        # Close the client connection after handling the request
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    

# Helper function to extract information from an URL request
def url_extract(request, key):
    """
    Helper function which extracts a value for a given key
    from a URL-encoded request string.

    :param request: The URL-encoded request string.
    :param key: The key to find in the request.
    :return: The associated value if key is found; None otherwise.
    """
    
    # Search for the key in the request
    search = ure.search(key + "=([^&\s]+)", request)
    
    # Check if an SSID was found
    if search:
        return search.group(1)
    else:
        return


async def send_html_response(writer, html_content):
    """
    Helper function which asynchronously sends an HTML response to the client,
    including headers and the provided HTML content.

    :param writer: The writer stream associated with the client connection.
    :param html_content: The HTML content (as a string) to send in the response body.
    """

    # Construct the response with standard HTTP headers for HTML content
    response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n" + html_content

    # Send the full response
    await writer.awrite(response)


async def display_warning_html(writer):
    """
    Asynchronously loads the 'warning.html' page and sends it to the client.
    
    :param writer: The writer stream associated with the client connection.
    """
    # Load HTML template
    with open('websites/warning.html', 'r') as file:
        html_template = file.read()
    
    # Send the HTML content using the send_html_response function
    await send_html_response(writer, html_template)


async def display_selection_html(writer, alert):
    """
    Asynchronously scans for available Wi-Fi networks using the station interface, 
    constructs an HTML page with the network list and the 'selection.html' page,
    and sends it to the client.

    :param writer: The writer stream associated with the client connection.
    """

    # Initialize and set up station interface to scan for networks
    wlan_sta = network.WLAN(network.STA_IF)
    wlan_sta.active(True)
    
    # Scan for available Wi-Fi networks and sort them alphabetically by SSID
    ssids = sorted(ssid.decode('utf-8') for ssid, *_ in wlan_sta.scan())

    # Turn off the station interface
    wlan_sta.active(False)

    # Load HTML template
    with open('websites/selection.html', 'r') as file:
        html_template = file.read()

    # Determine what to display based on the availability of networks
    html_insert = ''
    
    if ssids:
        for index, ssid in enumerate(ssids):
            # Create a unique ID for each radio button
            ssid_id = "wifi{}".format(index)
        
            # Add radio button to the HTML template
            html_insert += """
                <input type="radio" id="{ssid_id}" name="wifi" value="{ssid}">
                <label for="{ssid_id}">{ssid}</label><br>
            """.format(ssid_id=ssid_id, ssid=ssid)
    else:
        html_insert = '<p>Nebyla nalezena žádná síť Wi-Fi.</p>'

    # Replace the '{html_insert}' placeholder with actual content
    html_output = html_template.replace('{html_insert}', html_insert)
    
    # Replace '{script_insert}' placeholder with actual content
    if alert:
        html_output = html_output.replace('{script_insert}', 'alert("' + alert + '");')

    # Send the HTML content using the send_html_response function
    await send_html_response(writer, html_output)


async def display_password_html(writer, post_data):
    """
    Asynchronously receives the selected SSID from the client's request,
    loads a password HTML template, replaces necessary placeholders, 
    and sends it back to the client.

    :param writer: The writer stream associated with the client connection.
    :param request: The full request received from the client.
    """

    global ssid

    # Extract SSID from the HTML request
    ssid = url_extract(post_data, "wifi")
    
    # Check if an SSID was found, if not, go to 'warning.html'
    if ssid is None:
        await display_warning_html(writer)
        return

    # Load HTML template
    with open('websites/password.html', 'r') as file:
        html_template = file.read()
        
    # Replace placeholder in HTML with the actual SSID
    html_output = html_template.replace('{address_insert}', ssid)
        
    # Send the HTML content using the send_html_response function
    await send_html_response(writer, html_output)

async def display_success_or_failure_html(writer, post_data):
    """
    Asynchronously checks for successful connection and displays an HTML page
    indicating success or failure.

    :param writer: The writer stream associated with the client connection.
    :param request: The full request received from the client.
    """

    # Get password from HTML request
    password = url_extract(post_data, "password")
    
    # Check if a password was found
    if not password:
        await display_warning_html(writer)
        return
    
    # Assuming do_connect is an existing function that attempts to connect to a network
    if await wifi_client.connect(ssid, password):
        
        # Load HTML template
        with open('websites/success.html', 'r') as file:
            html_template = file.read()
        
        # Replace placeholders in HTML with actual content
        html_output = html_template.replace('{network_insert}', ssid)
        html_output = html_output.replace('{address_insert}', wifi_client.get_default_gateway())
        
        # Send the HTML content using the send_html_response function
        await send_html_response(writer, html_output)

        # Here, consider what operations need to be asynchronous and use asyncio.sleep
        await asyncio.sleep(1)
    
        await wifi_ap.stop()
    
    else:

        await wifi_client.stop()
        
        await display_selection_html(writer, "Nepodařilo se připojit k síti " + ssid + ". Zkuste to prosím znovu.")
        
"""async def display_warning_html(writer):
    
    Asynchronously loads the 'homepage.html' page along with associated CSS and JavaScript files, and sends them to the client.
    
    :param writer: The writer stream associated with the client connection.
    
    # Load HTML template
    with open('websites/homepage/homepage.html', 'r') as file:
        html_template = file.read()
    
    # Load CSS content
    with open('websites/homepage/homepage.css', 'r') as file:
        css_homepage = file.read()
        
     with open('websites/homepage/homepage.css', 'r') as file:
        css_timer = file.read()   

    # Load JavaScript content
    with open('websites/homepage/homepage.js', 'r') as file:
        js_homepage = file.read()

    with open('websites/homepage/picker.js', 'r') as file:
        js_picker = file.read()
        
    # Load image files
    
    
    # Replace relevant placeholders in HTML template with CSS content
    html_template = html_template.replace('<link rel="stylesheet" href="./homepage.css" />', f'<style>{css_homepage}</style>')
    html_template = html_template.replace('<link rel="stylesheet" href="./timer.css" />', f'<style>{css_timer}</style>')
    
    # Replace relevant placeholders in HTML template with JavaScript content
    html_template = html_template.replace('<script src="./homepage.js"></script>', f'<script>{js_homepage}</script>')
    html_template = html_template.replace('<script src="./picker.js"></script>', f'<script>{js_picker}</script>')
    
    # Replace relevant placeholders in HTML template with SVG image content
    html_template = html_template.replace('<img src="image1.svg">', '<object type="image/svg+xml" data="websites/image1.svg"></object>')

    # Send the HTML content using the send_html_response function
    await send_html_response(writer, html_template)
"""
    
async def display_homepage_html(writer):
    """
    Asynchronously loads the 'warning.html' page and sends it to the client.
    
    :param writer: The writer stream associated with the client connection.
    """
    # Load HTML template
    with open('websites/homepage/homepage.html', 'r') as file:
        html_template = file.read()
    
    # Send the HTML content using the send_html_response function
    await send_html_response(writer, html_template)
    

#EOF
