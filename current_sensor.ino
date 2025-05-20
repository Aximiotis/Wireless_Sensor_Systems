#include <Wire.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina219;

void setup() {
  Serial.begin(9600);
  while (!Serial) delay(1);  // Wait for serial monitor

  if (!ina219.begin()) {
    Serial.println("INA219 not found");
    while (1);
  }
}

void loop() {
  float current_mA = ina219.getCurrent_mA();
  float voltage_V = ina219.getBusVoltage_V();
  float power_mW = ina219.getPower_mW();

  Serial.print(current_mA);
  Serial.print(",");
  Serial.print(voltage_V);
  Serial.print(",");
  Serial.println(power_mW);

  delay(1000);
}
