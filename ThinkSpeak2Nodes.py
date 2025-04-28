import re
import time
import requests
from digi.xbee.devices import XBeeDevice

# === CONFIGURATION ===
PORT               = '/dev/tty.usbserial-AB0OPCCX'  # adjust as needed
BAUD_RATE          = 9600
THINGSPEAK_URL     = "https://api.thingspeak.com/update"
API_KEY_CHANNEL_1  = "L6JIYNKEH9LIRPYD"
API_KEY_CHANNEL_2  = "1LLEJD4N9HEK32N9"      # placeholder
RATE_LIMIT_S       = 15   # seconds between uploads

# placeholders for your modules’ 64-bit addresses
NODE1_MAC = "0013A200420153E8"
NODE2_MAC = "0013A20041CFE9A1"

# track last upload times per channel
last_upload = {
    API_KEY_CHANNEL_1: 0.0,
    API_KEY_CHANNEL_2: 0.0
}

# set up XBee device
device = XBeeDevice(PORT, BAUD_RATE)

def data_receive_callback(xbee_message):
    # get the sender’s 64-bit address as a string
    remote_addr = str(xbee_message.remote_device.get_64bit_addr())
    raw         = xbee_message.data.decode("utf-8", errors="ignore").strip()
    if not raw:
        return

    print(f"Received from {remote_addr}: {raw}")

    # select API key & channel based on sender
    if remote_addr == NODE1_MAC:
        api_key, channel = API_KEY_CHANNEL_1, 1
    elif remote_addr == NODE2_MAC:
        api_key, channel = API_KEY_CHANNEL_2, 2
    else:
        print(f"⚠️  Unknown device {remote_addr}, skipping upload.")
        return

    # extract first number and cast to int
    m = re.search(r"(\d+\.?\d*)", raw)
    if not m:
        print("⚠️  No numeric data found.")
        return
    try:
        value = float(m.group(1))
    except ValueError:
        print("⚠️  Failed to convert to int.")
        return

    # enforce per-channel rate limit
    now  = time.time()
    last = last_upload[api_key]
    if now - last < RATE_LIMIT_S:
        wait = RATE_LIMIT_S - (now - last)
        print(f"⌛ Channel {channel}: waiting {wait:.1f}s before next upload.")
        return

    # upload to ThingSpeak
    params = {"api_key": api_key, "field1": value}
    try:
        resp = requests.get(THINGSPEAK_URL, params=params, timeout=5)
        if resp.status_code == 200:
            print(f"✅ Uploaded {value} to channel {channel}")
            last_upload[api_key] = now
        else:
            print(f"❌ Upload failed to channel {channel}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ Error uploading to channel {channel}: {e}")

try:
    device.open()
    print("Listening for data in API mode...")
    device.add_data_received_callback(data_receive_callback)
    input("Press Enter to stop...\n")
finally:
    if device.is_open():
        device.close()