<p align="center">
  <img src="./images/blinkOS.png" alt="description of image" width="500"/>
</p>

# Automated Color-Based Sorting System 🤖

This project is an automated conveyor belt system designed to sort objects based on their color. It was developed for the university course, **"Application of Wireless Network Systems."**

The system uses a two-node wireless architecture with two Arduino boards communicating via RF to separate sensing tasks from actuation logic.

## 🎯 Project Goal

The primary goal is to create a functional production line prototype that can automatically identify an object placed at the start of a conveyor belt via different parameters and sort it into a specific path at the end of the line.

---
## ⌨️ Authors
* Dimitris Axiomiotis - @Aximiotis
* Vasileios Koudounis - @Vasileios-Koudounis
* Amalia Konstantinou - @amaliaks123
* Nikos Toulkeridis   - @ntoylker

---

## ⚙️ System Architecture

The system is split into two main components that communicate wirelessly.

### Node A: The Sensor Hub
This Arduino is responsible for gathering all environmental and object data.
* **Role:** Senses the object and transmits raw data.
* **Sensors:**
    * **Color Sensor:** Measures the object's color.
    * **Distance Sensor:** Triggers the color sensor only when an object is in place, reducing noise.
    * **Temperature & Humidity Sensor:** Monitors ambient conditions.
    * **Servo Motor:** Stops the object in order to successfully measure its color
* **Communication:** Uses an RF transmitter to send all sensor data to Node B.

### Node B: The Control Unit
This Arduino is the "brain" of the operation, responsible for operational logic and mechanical control.
* **Role:** Receives data, processes it, and controls the sorting mechanics.
* **Actuators:**
    * **Sorting Servo Motor:** Rotates to a specific angle based on the color data received from Node A, guiding the object to its correct path.
    * **DC Motors (x2):** Powers the conveyor belt, creating the production line.
* **Communication:** Uses an RF receiver to get data from Node A.

---

## 🚀 How It Works

The operational flow follows these steps:

1.  **Object Placement:** An object is placed at the beginning of the conveyor belt. A servo-controlled gate holds it steady.
2.  **Sensing:** While the object is held, the distance sensor detects its presence and activates the color sensor to take a clean reading.
3.  **Data Transmission:** Node A reads the color, distance, temperature, and humidity, and transmits this raw data packet to Node B via its RF module.
4.  **Release:** The initial servo gate lifts, releasing the object to travel along the moving conveyor belt.
5.  **Decision Making:** Node B receives the data packet. Based on the color value, it determines the correct sorting angle (e.g., red = 0°, green = 30°, blue = 60°).
6.  **Sorting:** As the object reaches the end of the line, Node B commands the second servo motor to move to the calculated angle. The servo's attached arm then diverts the object into its designated collection area.

For more detailed information, please see the project report: **[Εφαρμογές_Τηλεπικοινωνιακών_Διατάξεων_10622_10739_10718_10745.pdf](./Εφαρμογές_Τηλεπικοινωνιακών_Διατάξεων_10622_10739_10718_10745.pdf)**

---

## 🎥 Project Showcase

Watch the videos below to see the project in action and get a detailed look at the setup.

* **[Video 1: Live Demonstration](https://youtu.be/xZcWGIzit1Y?si=HnmxsBM_TOrXAp0Y)**: A complete run-through of the system sorting objects by color.
* **[Video 2: Sketch](https://www.youtube.com/shorts/ypAJ1u6CufI)**: A funny advertising youtube short.
