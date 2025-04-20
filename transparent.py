import serial

PORT = "/dev/tty.usbserial-AB0OPCCX"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
print("Listening for data from XBee...")

buf = ""                          

try:
    while True:
        if ser.in_waiting:                        
            buf += ser.read(ser.in_waiting).decode("utf‑8", errors="ignore")

            if "\n" in buf:                        #
                lines = buf.split("\n")            
                for line in lines[:-1]:            
                    print(f"Received: {line.strip()}")
                buf = lines[-1]                  

except KeyboardInterrupt:
    pass
finally:
    ser.close()
