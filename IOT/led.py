
'''
import serial
import time

# Replace with your actual COM port (e.g., "COM3" on Windows or "/dev/ttyUSB0" on Linux)
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

def led_on():
    arduino.write(b'1')

def led_off():
    arduino.write(b'0')

# Example usage
led_on()
time.sleep(2)
led_off()
'''

# iot.py

import serial
import time

# Adjust COM port as needed
try:
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to reset
except serial.SerialException as e:
    arduino = None
    print(f"Failed to connect to Arduino: {e}")

def led_on():
    if arduino:
        arduino.write(b'1')

def led_off():
    if arduino:
        arduino.write(b'0')
