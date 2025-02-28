import threading
import time
import os
from pyxhook import HookManager
import requests
from requests.exceptions import RequestException
import socket

# Configurations
HOMEASSISTANT_NAME = "homeassistant.local"
HASS_API_URL = f"http://{HOMEASSISTANT_NAME}:8123/api/states/input_number.last_millis_on_desktop_pc"
# Token is stored with the systemctl service definition
HASS_TOKEN = os.getenv("HASS_API_TOKEN");


last_activity = time.time()
last_update = time.time()

def current_milli_time():
    return round(time.time() * 1000)

def is_connected_to_home_network():
    """Check if the device is connected to the home network with a 3 second timeout."""
    try:
        # Attempt to resolve a known hostname in the home network
        socket.setdefaulttimeout(3)
        socket.gethostbyname(HOMEASSISTANT_NAME)
        return True
    except socket.gaierror:
        return False

def update_homeassistant():
    global last_update
    last_update = time.time()
    headers = {"Authorization": f"Bearer {HASS_TOKEN}", "Content-Type": "application/json"}
    data = {"state": current_milli_time()}

    retry_count = 0
    while retry_count < 3:  # Retry up to 3 times
        try:
            if is_connected_to_home_network():
                response = requests.post(HASS_API_URL, headers=headers, json=data, timeout=10)
                response.raise_for_status()  # Raise exception for HTTP errors
                print(f"Successfully updated Home Assistant at {current_milli_time()}")
                break
            else:
                print("Not connected to home network. Skipping update.")
                break
        except RequestException as e:
            retry_count += 1
            print(f"Failed to update Home Assistant (attempt {retry_count}): {e}")
            time.sleep(10)  # Wait for 10 seconds before retrying
    else:
        print("Max retries reached. Giving up.")

def reset_activity(x):
    global last_activity
    global last_update
    last_activity = time.time()
    if time.time() - last_update > 30:
        update_homeassistant()
    return True

# Hook into keyboard and mouse events
hookman = HookManager()
hookman.HookKeyboard()
hookman.HookMouse()
hookman.KeyDown = reset_activity
hookman.MouseAllButtonsDown = reset_activity
hookman.MouseMovement = reset_activity  # Hook mouse movement as activity

def start_hookman():
    try:
        hookman.start()
    except Exception as e:
        print(f"Failed to start hookman: {e}")

# Start hookman in a separate thread
hookman_thread = threading.Thread(target=start_hookman, daemon=True)
hookman_thread.start()

try:
    while True:
        try:
            time.sleep(10)
            if last_activity > last_update:
                update_homeassistant()
        except Exception as e:
            print(f"Main loop crashed: {e}")
            time.sleep(5) # Prevent rapid crash restarting

except KeyboardInterrupt:
    hookman.cancel()
