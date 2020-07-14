import serial
esp = serial.Serial("/dev/ttyUSB1", 115200)
esp.write(bytes("help()\r\n", "utf-8"))
rx = esp.read()
print(rx.decode("utf-8"))