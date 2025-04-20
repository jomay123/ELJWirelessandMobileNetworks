from digi.xbee.devices import XBeeDevice

# Update with your port and baud rate
PORT = '/dev/tty.usbserial-AB0OPCCX'
BAUD_RATE = 9600

device = XBeeDevice(PORT, BAUD_RATE)

try:
    device.open()
    print("Listening for data in API mode...")

    def data_receive_callback(xbee_message):
        print(f"From {xbee_message.remote_device.get_64bit_addr()}: {xbee_message.data.decode()}")

    device.add_data_received_callback(data_receive_callback)

    input("Press Enter to stop...\n")

finally:
    if device.is_open():
        device.close()

