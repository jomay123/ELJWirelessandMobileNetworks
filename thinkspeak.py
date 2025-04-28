import serial
import requests
import time
import re

# === CONFIGURATION ===
PORT            = "/dev/tty.usbserial-AB0OPCCX"  # adjust as needed
BAUD            = 9600
THINGSPEAK_URL  = "https://api.thingspeak.com/update"
API_KEY         = "L6JIYNKEH9LIRPYD"
RATE_LIMIT_S    = 15   # seconds between uploads

# === SETUP SERIAL ===
ser = serial.Serial(PORT, BAUD, timeout=1)
print("Listening for data from XBee...")

buf = ""

try:
    while True:
        # read any available bytes
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting).decode("utf-8", errors="ignore")

        # process any complete lines
        if "\n" in buf:
            lines = buf.split("\n")
            for raw in lines[:-1]:
                raw = raw.strip()
                if not raw:
                    continue

                print(f"Received: {raw}")

                # 1) extract first numeric substring (e.g. "1.60")
                m = re.search(r"[-+]?\d*\.\d+|\d+", raw)
                if not m:
                    print("⚠️  No numeric data found, skipping.")
                    continue
                reading = m.group(0)
                print(f"→ Parsed value: {reading}")

                # 2) build and show the full URL for debugging
                req = requests.Request(
                    method="GET",
                    url=THINGSPEAK_URL,
                    params={
                        "api_key": API_KEY,
                        "field1": reading
                    }
                ).prepare()
                print("→ URL:", req.url)

                # 3) send the request
                try:
                    resp = requests.get(req.url, timeout=5)
                    print(f"Status: {resp.status_code}, Body: '{resp.text}'")
                    if resp.status_code == 200 and resp.text != "0":
                        print("✔ Successfully queued on ThingSpeak")
                    else:
                        print("✖ ThingSpeak didn’t update a field (resp='0')")
                except requests.RequestException as e:
                    print("✖ Request error:", e)

                # 4) obey rate limit
                time.sleep(RATE_LIMIT_S)

            # keep leftover partial line
            buf = lines[-1]

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    ser.close()
    print("Serial port closed.")
