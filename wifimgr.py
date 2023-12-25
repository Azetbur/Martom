import network
import socket
import ure
import time

ap_ssid = "ESP32"
ap_password = "S-Max120"
ap_authmode = 3  # WPA2

NETWORK_PROFILES = 'wifi.dat'

wlan_ap = network.WLAN(network.AP_IF)
wlan_sta = network.WLAN(network.STA_IF)

server_socket = None

# SSID of the network the ESP32 will be connecting to
ssid = ''




def write_profiles(profiles):
    lines = []
    for ssid, password in profiles.items():
        lines.append("%s;%s\n" % (ssid, password))
    with open(NETWORK_PROFILES, "w") as f:
        f.write(''.join(lines))


def do_connect(ssid, password):
    wlan_sta.active(True)
    if wlan_sta.isconnected():
        return None
    print('Trying to connect to %s...' % ssid)
    wlan_sta.connect(ssid, password)
    for retry in range(200):
        connected = wlan_sta.isconnected()
        if connected:
            break
        time.sleep(0.1)
        print('.', end='')
    if connected:
        print('\nConnected. Network config: ', wlan_sta.ifconfig())
        
    else:
        print('\nFailed. Not Connected to: ' + ssid)
    return connected


def send_header(client, status_code=200, content_length=None ):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: text/html\r\n")
    if content_length is not None:
      client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")


def send_response(client, payload, status_code=200):
    content_length = len(payload)
    send_header(client, status_code, content_length)
    if content_length > 0:
        client.sendall(payload)
    client.close()

# Helper function to extract information from an URL request
def url_extract(request, key):
    
    # Decode the byte string to a regular string
    decoded_request = request.decode()
    
    # Search for the key in the request
    search = ure.search(key + "=([^&\s]+)", decoded_request)
    
    # Check if an SSID was found
    if search:
        return search.group(1)
    else:
        return
    
    
def display_warning_html(client):
    
    # Load HTML template
    with open('warning.html', 'r') as file:
        html_template = file.read()
        
    # Send the header and HTML content
    send_header(client)
    client.sendall(html_template)


def display_selection_html(client):
    
    # Make sure the WLAN interface is active to to scan for networks
    wlan_sta.active(True)
    
    # Scan for available Wi-Fi networks and sort them alphabetically by SSID
    ssids = sorted(ssid.decode('utf-8') for ssid, *_ in wlan_sta.scan())

    # Load HTML template
    with open('selection.html', 'r') as file:
        html_template = file.read()

    # Determine what to display based on the availability of networks
    html_insert = ''
    
    if ssids:
        for index, ssid in enumerate(ssids):
        
            # Create a unique ID for each radio button
            ssid_id = "wifi{}".format(index)
        
            # Add radio buton to the HTML template
            html_insert += """
                <input type="radio" id="{ssid_id}" name="wifi" value="{ssid}">
                <label for="{ssid_id}">{ssid}</label><br>
            """.format(ssid_id=ssid_id, ssid=ssid)
        
    else:
        html_insert = '<p>Nebyla nalezená žádná Wi-Fi síť.</p>'
    

    # Replace the placeholders with the actual content
    html_output = html_template.replace('{html_insert}', html_insert)

    # Send the header and HTML content
    send_header(client)
    client.sendall(html_output)


def display_password_html(client, request):
    
    global ssid
    
    # Get SSID from HTML request
    ssid = url_extract(request, "wifi")
    
    # Check if an SSID was found
    if ssid is None:
        # Go to the start of the control flow
        display_warning_html(client)
        return
    
    print("Selected ssid: " + ssid)

    # Load HTML template
    with open('password.html', 'r') as file:
        html_template = file.read()
        
    # Replace placeholder in HTML with actual content
    html_output = html_template.replace('{address_insert}', ssid)
        
    # Send the header and HTML content
    send_header(client)
    client.sendall(html_output)


def display_success_or_failure_html(client, request):
    
    # Get password from HTML request
    password = url_extract(request, "password")
    
    # Check if a password was found
    if not password:
        # Go to the start of the control flow
        display_warning_html(client)
        return
        
    print("Trying to connect to SSID: " + ssid)
    
    if do_connect(ssid, password):
        
        # Load HTML template
        with open('success.html', 'r') as file:
            html_template = file.read()
        
        # Replace placeholders in HTML with actual content
        html_output = html_template.replace('{network_insert}', ssid)
        html_output = html_output.replace('{address_insert}', wlan_sta.ifconfig()[0])
        
        # Send the header and HTML content
        send_header(client)
        client.sendall(html_output)
        
        time.sleep(1)
    
        wlan_ap.active(False)
        
        try:
            profiles = read_profiles()
        except OSError:
            profiles = {}
            
        profiles[ssid] = password
        write_profiles(profiles)

        time.sleep(5)

        return True
    
    else:
        response = """\
            <html>
            </html>
        """ % dict(ssid=ssid)
        send_response(client, response)
        return False

def handle_not_found(client, url):
    send_response(client, "Path not found: {}".format(url), status_code=404)


def stop():
    global server_socket

    if server_socket:
        server_socket.close()
        server_socket = None


def start(port=80):
    global server_socket

    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

    stop()

    wlan_sta.active(True)
    wlan_ap.active(True)

    wlan_ap.config(essid=ap_ssid, password=ap_password, authmode=ap_authmode)

    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)

    print('Connect to WiFi ssid ' + ap_ssid + ', default password: ' + ap_password)
    print('and access the ESP via your favorite web browser at 192.168.4.1.')
    print('Listening on:', addr)

    while True:
        if wlan_sta.isconnected():
            wlan_ap.active(False)
            return True

        client, addr = server_socket.accept()
        print('client connected from', addr)
        try:
            client.settimeout(5.0)

            request = b""
            try:
                while "\r\n\r\n" not in request:
                    request += client.recv(512)
            except OSError:
                pass

            # Handle form data from Safari on macOS and iOS; it sends \r\n\r\nssid=<ssid>&password=<password>
            try:
                request += client.recv(1024)
                print("Received form data after \\r\\n\\r\\n(i.e. from Safari on macOS or iOS)")
            except OSError:
                pass

            print("Request is: {}".format(request))
            if "HTTP" not in request:  # skip invalid requests
                continue

            # version 1.9 compatibility
            try:
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).decode("utf-8").rstrip("/")
            except Exception:
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).rstrip("/")
            print("URL is {}".format(url))

            if url == "":
                display_warning_html(client)
            elif url == "go_to_selection":
                display_selection_html(client)
            elif url == "go_to_password":
                display_password_html(client, request)
            elif url == "go_to_success_or_failure":
                display_success_or_failure_html(client, request)
            else:
                handle_not_found(client, url)

        finally:
            client.close()

