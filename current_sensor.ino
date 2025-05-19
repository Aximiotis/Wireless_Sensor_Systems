#include <Wire.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina219;
const int ledPin = 13;  // LED on pin 13 (with 470Ω resistor)

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  
  if (!ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1); // Stop if sensor not found
  }
  
  digitalWrite(ledPin, HIGH); // Turn on LED
  Serial.println("INA219 Current Sensor Test");
}

void loop() {
  float shuntVoltage_mV = ina219.getShuntVoltage_mV();
  float busVoltage_V = ina219.getBusVoltage_V();
  float current_mA = ina219.getCurrent_mA();
  float power_mW = ina219.getPower_mW();
  float loadVoltage_V = busVoltage_V + (shuntVoltage_mV / 1000);

  // Print measurements
  Serial.print("Load Voltage: "); Serial.print(loadVoltage_V); Serial.println(" V");
  Serial.print("Current: "); Serial.print(current_mA); Serial.println(" mA");
  Serial.print("Power: "); Serial.print(power_mW); Serial.println(" mW");
  Serial.println("-----------------------");
  
  delay(1000); // Update every second
}
