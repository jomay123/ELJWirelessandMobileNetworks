import serial

PORT = "/dev/tty.usbserial-AB0OPCCX"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
print("Listening for ints from XBee...")

try:
    while True:
        # read one line (up to '\n')
        raw = ser.readline()
        if not raw:
            continue

        # strip whitespace and decode
        s = raw.strip().decode("utf-8", errors="ignore")
        if not s:
            continue

        # try to parse as int
        try:
            value = int(s)
            print(f"Received int: {value}")
        except ValueError:
            # not an integer—ignore or log
            print(f"Ignored non‑int data: '{s}'")

except KeyboardInterrupt:
    print("\nStopping.")

finally:
    ser.close()
    print("Serial port closed.")

