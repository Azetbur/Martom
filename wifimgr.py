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


def get_connection():
    """return a working WLAN(STA_IF) instance or None"""

    # First check if there already is any connection:
    if wlan_sta.isconnected():
        return wlan_sta

    connected = False
    try:
        # ESP connecting to WiFi takes time, wait a bit and try again:
        time.sleep(3)
        if wlan_sta.isconnected():
            return wlan_sta

        # Read known network profiles from file
        profiles = read_profiles()

        # Search WiFis in range
        wlan_sta.active(True)
        networks = wlan_sta.scan()

        AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}
        for ssid, bssid, channel, rssi, authmode, hidden in sorted(networks, key=lambda x: x[3], reverse=True):
            ssid = ssid.decode('utf-8')
            encrypted = authmode > 0
            print("ssid: %s chan: %d rssi: %d authmode: %s" % (ssid, channel, rssi, AUTHMODE.get(authmode, '?')))
            if encrypted:
                if ssid in profiles:
                    password = profiles[ssid]
                    connected = do_connect(ssid, password)
                else:
                    print("skipping unknown encrypted network")
            else:  # open
                connected = do_connect(ssid, None)
            if connected:
                break

    except OSError as e:
        print("exception", str(e))

    # start web server for connection manager:
    if not connected:
        connected = start()

    return wlan_sta if connected else None


def read_profiles():
    with open(NETWORK_PROFILES) as f:
        lines = f.readlines()
    profiles = {}
    for line in lines:
        ssid, password = line.strip("\n").split(";")
        profiles[ssid] = password
    return profiles


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


def display_password_html(client):
    
    # Load HTML template
    with open('password.html', 'r') as file:
        html_template = file.read()
        
    # Send the header and HTML content
    send_header(client)
    client.sendall(html_template)

def handle_configure(client, request):
    match = ure.search("ssid=([^&]*)&password=(.*)", request)

    if match is None:
        send_response(client, "Parameters not found", status_code=400)
        return False
    # version 1.9 compatibility
    try:
        ssid = match.group(1).decode("utf-8").replace("%3F", "?").replace("%21", "!")
        password = match.group(2).decode("utf-8").replace("%3F", "?").replace("%21", "!")
    except Exception:
        ssid = match.group(1).replace("%3F", "?").replace("%21", "!")
        password = match.group(2).replace("%3F", "?").replace("%21", "!")
        
    print("Password: " + password)

    if len(ssid) == 0:
        send_response(client, "SSID must be provided", status_code=400)
        return False

    if do_connect(ssid, password):
        response = """\
            <html>
                <center>
                    <br><br>
                    <h1 style="color: #5e9ca0; text-align: center;">
                        <span style="color: #ff0000;">
                            ESP successfully connected to WiFi network %(ssid)s.
                        </span>
                    </h1>
                    <br><br>
                </center>
            </html>
        """ % dict(ssid=ssid)
        send_response(client, response)
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
                <center>
                    <h1 style="color: #5e9ca0; text-align: center;">
                        <span style="color: #ff0000;">
                            ESP could not connect to WiFi network %(ssid)s.
                        </span>
                    </h1>
                    <br><br>
                    <form>
                        <input type="button" value="Go back!" onclick="history.back()"></input>
                    </form>
                </center>
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
            elif url == "connect_to_wifi":
                display_password_html(client)
                # handle_configure(client, request)
            else:
                handle_not_found(client, url)

        finally:
            client.close()

