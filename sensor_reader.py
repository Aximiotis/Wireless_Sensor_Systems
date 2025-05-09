import serial
import threading

class SensorReader:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
        except Exception as e:
            print(f"[ERROR] Δεν ήταν δυνατή η σύνδεση με τη θύρα {port}: {e}")
            raise

        self.latest_temp = 0.0
        self.latest_humidity = 0.0
        self.running = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()

    def read_loop(self):
        while self.running:
            try:
                line = self.ser.readline().decode().strip()
                if ',' in line:
                    temp_str, hum_str = line.split(",")
                    self.latest_temp = float(temp_str)
                    self.latest_humidity = float(hum_str)
            except Exception as e:
                print(f"[WARNING] Αποτυχία ανάγνωσης: {e}")
                continue

    def get_data(self):
        return self.latest_temp, self.latest_humidity

    def stop(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()
