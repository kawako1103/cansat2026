import serial
import time
import RPi.GPIO as GPIO

class LoRaTransmitter:
    """
    A class to handle the transmission of GPS coordinates via LoRa using UART communication with a Raspberry Pi.
    """

    def __init__(self, port, baudrate, reset_pin, file_path, log_file_path):
        """
        Initialize the LoRaTransmitter with the specified UART port, baudrate, reset pin, GPS log file path, and log file path.
        """
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=None)
        self.reset_pin = reset_pin
        self.file_path = file_path
        self.log_file_path = log_file_path
        self.last_index = 0
        self._setup_gpio()

    def _setup_gpio(self):
        """
        Set up the GPIO pin for resetting the LoRa module.
        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.reset_pin, GPIO.OUT)

    def reset(self):
        """
        Reset the LoRa module using the GPIO pin.
        """
        GPIO.output(self.reset_pin, 1)
        time.sleep(0.3)
        #1:0.3 to 2
        #2:2 to 3
        GPIO.output(self.reset_pin, 0)
        time.sleep(2)
        #2:2 to 3

    def send_serial(self, msg: str):
        """
        Send a command to the LoRa module via UART and wait for an "OK" response.
        """
        OK_check = False
        self.ser.write((msg + "\r\n").encode("ascii"))
        
        while not OK_check:
            data = self.ser.readline().rstrip()
            print(f"'{msg}' : {data}")
            
            if b"OK" in data:
                OK_check = True
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()

    def read_latlon(self):
        """
        Read latitude and longitude data from the GPS log file.
        Returns a list of (latitude, longitude) tuples and updates the last read index.
        """
        vec_latlon = []

        with open(self.file_path, "r") as file:
            lines = file.readlines()

            for i in range(self.last_index, len(lines)):
                line = lines[i]
                if '\xb3' in line:
                    continue

                parts = line.strip().split(',')
                if len(parts) >= 2:
                    latitude = parts[0]
                    longitude = parts[1]
                    vec_latlon.append((latitude, longitude))

        self.last_index = len(lines)
        return vec_latlon

    def send_latlon(self, vec_latlon):
        """
        Send the latitude and longitude data to the LoRa module.
        If no data is available, send a default "00000.00000" coordinate.
        Log all sent data to a file.
        """
        with open(self.log_file_path, 'a') as log_file:
            if not vec_latlon:
                lat = "00000.00000"
                lon = "00000.00000"
                output = f"4321FFFD{lat},{lon}\r\n"
                self.ser.write(output.encode('ascii', errors='ignore'))
                log_file.write(output)
                print(output.encode('ascii'))
                time.sleep(0.5)
            else:
                for lat_lon in vec_latlon:
                    last_lat, last_lon = lat_lon
                    output = f"4321FFFD{last_lat},{last_lon}\r\n"
                    self.ser.write(output.encode('ascii', errors='ignore'))
                    log_file.write(output)
                    print(output.encode('ascii', errors='ignore'))
                    time.sleep(1)

    def initialize_device(self):
        """
        Initialize the LoRa module by resetting it and sending the necessary setup commands.
        """
        self.reset()
        data = self.ser.readline().rstrip()
        print("rcv data : {0}".format(data))
        print(data)

        self.send_serial("2")
        self.send_serial("load")
        self.send_serial("bw 6")
        self.send_serial("panid 4321")
        self.send_serial("ownid FFFE")
        self.send_serial("ack 2")
        self.send_serial("rcvid 1")
        self.send_serial("transmode 2")
        self.send_serial("rssi 1")
        self.send_serial("sf 7")
        self.send_serial("save")
        self.send_serial("start")

    def run(self):
        """
        Continuously read GPS coordinates from the log file and transmit them via LoRa.
        """
        while True:
            vec_latlon = self.read_latlon()
            self.send_latlon(vec_latlon)
            time.sleep(0.5)


if __name__ == "__main__":
    # Parameters for the LoRa transmitter
    PORT = "/dev/ttyAMA0"
    BAUDRATE = 115200
    RESET_PIN = 22
    FILE_PATH = "/home/cansat-stu/cansat2024/Op-test_i2c/log_gps.txt"
    LOG_FILE_PATH = "/home/cansat-stu/cansat2024/Op-test_i2c/sent_data_log.txt"  # Path for saving sent data

    # Create a LoRaTransmitter object and initialize it
    lora_tx = LoRaTransmitter(PORT, BAUDRATE, RESET_PIN, FILE_PATH, LOG_FILE_PATH)
    lora_tx.initialize_device()

    # Start the main loop
    lora_tx.run()
