import re
import time
import requests
from digi.xbee.devices import XBeeDevice

# === CONFIGURATION ===
PORT            = '/dev/tty.usbserial-AB0OPCCX'  # adjust as needed
BAUD_RATE       = 9600
THINGSPEAK_URL  = "https://api.thingspeak.com/update"
API_KEY         = "L6JIYNKEH9LIRPYD"
RATE_LIMIT_S    = 15   # seconds between uploads

# track last upload time
last_upload = 0.0

# set up XBee device
device = XBeeDevice(PORT, BAUD_RATE)

def data_receive_callback(xbee_message):
    global last_upload

    raw = xbee_message.data.decode("utf-8", errors="ignore").strip()
    if not raw:
        return

    print(f"Received from {xbee_message.remote_device.get_64bit_addr()}: {raw}")

    # extract first numeric substring (int or float)
    m = re.search(r"(\d+\.?\d*)", raw)
    if not m:
        print("⚠️  No numeric data found.")
        return
    value = m.group(1)

    # enforce rate limit
    now = time.time()
    if now - last_upload < RATE_LIMIT_S:
        print(f"⌛ Waiting {RATE_LIMIT_S - (now - last_upload):.1f}s before next upload.")
        return

    # upload to ThingSpeak
    params = {
        "api_key": API_KEY,
        "field1":  value
    }
    try:
        resp = requests.get(THINGSPEAK_URL, params=params, timeout=5)
        if resp.status_code == 200:
            print(f"✅ Uploaded: {value}")
        else:
            print(f"❌ Upload failed: HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ Error uploading: {e}")

    last_upload = now

try:
    device.open()
    print("Listening for data in API mode...")

    device.add_data_received_callback(data_receive_callback)

    input("Press Enter to stop...\n")

finally:
    if device.is_open():
        device.close()
