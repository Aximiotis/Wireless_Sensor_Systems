import serial
import tkinter as tk
import threading
import re

arduino_port = '/dev/ttyACM0'
baud_rate = 9600

ser = serial.Serial(arduino_port, baud_rate, timeout=1)

root = tk.Tk()
root.title("Ανίχνευση Χρώματος")
root.geometry("320x380")

color_display = tk.Label(root, text="Χρώμα", font=("Arial", 18), width=20, height=10, bg="black", fg="white")
color_display.pack(pady=10)

rgb_label = tk.Label(root, text="RGB: ---", font=("Arial", 12))
rgb_label.pack()

distance_label = tk.Label(root, text="Απόσταση: --- cm", font=("Arial", 12))
distance_label.pack(pady=10)

def update_color():
    current_distance = "---"
    rgb_buffer = {}

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            # Εντοπισμός απόστασης
            if re.fullmatch(r"\d+", line):
                current_distance = int(line)
                distance_label.config(text=f"Απόσταση: {current_distance} cm")
                continue

            # Εντοπισμός RGB
            if "Red =" in line:
                match = re.search(r"Red\s*=\s*(\d+)", line)
                if match:
                    rgb_buffer["R"] = int(match.group(1))
            if "Green =" in line:
                match = re.search(r"Green\s*=\s*(\d+)", line)
                if match:
                    rgb_buffer["G"] = int(match.group(1))
            if "Blue =" in line:
                match = re.search(r"Blue\s*=\s*(\d+)", line)
                if match:
                    rgb_buffer["B"] = int(match.group(1))

            # Αν έχουμε και τα 3, εμφανίζουμε χρώμα
            if all(k in rgb_buffer for k in ("R", "G", "B")):
                r, g, b = rgb_buffer["R"], rgb_buffer["G"], rgb_buffer["B"]
                rgb_label.config(text=f"RGB: ({r}, {g}, {b})")
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                color_display.config(bg=hex_color)
                rgb_buffer.clear()

        except Exception as e:
            print("Error:", e)

def start_thread():
    thread = threading.Thread(target=update_color, daemon=True)
    thread.start()

start_thread()
root.mainloop()
