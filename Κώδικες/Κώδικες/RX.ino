#include <Adafruit_INA219.h>
#include <RF22.h>
#include <RF22Router.h>
#include <Servo.h>
#include <Wire.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina219;

#define RED_LEDS A0 
#define GREEN_LEDS A1
#define BLUE_LEDS A2

#define MY_ADDRESS 5  // Διεύθυνση του δέκτη

RF22Router rf22(MY_ADDRESS);
Servo servo1;

// Κινητήρας A
const int enb1 = 4;   // PWM
const int inp1 = 8;
const int inp2 = 7;

// Κινητήρας B
const int enb2 = 4;   // PWM
const int inp3 = 8;
const int inp4 = 7;

// Ταχύτητες κινητήρων
const int motor_speed1 = 150;
const int motor_speed2 = 150;

int servopin = 6;

// Servo ελέγχου
unsigned long lastMoveTime = 0;
int servoIndex = 0;
int servoPhase = 0;  // 0: idle, 1: green-up, 2: green-down, 3: blue-up, 4: blue-down, 5: pause
String currentColor = "None";

// Χρονικές καθυστερήσεις (όπως τα delays)
const unsigned long servoDelayUp = 8;
const unsigned long servoDelayDown = 10;
const unsigned long pauseDelay = 4000; 

void setup() {
  Serial.begin(9600);

  if (!rf22.init()) {
    Serial.println("RF22 init failed");
  } else {
    if (!rf22.setFrequency(431.0)) {
      Serial.println("setFrequency Fail");
    }
    rf22.setTxPower(RF22_TXPOW_20DBM);
    rf22.setModemConfig(RF22::GFSK_Rb125Fd125);
    Serial.println("RF22 ready to receive...");
  }

  if (!ina219.begin()) {
    Serial.println("INA219 not found");
    while (1);
  }

  // LED RED
  pinMode(RED_LEDS, OUTPUT);
  pinMode(GREEN_LEDS, OUTPUT);
  pinMode(BLUE_LEDS, OUTPUT);

  pinMode(inp1, OUTPUT);
  pinMode(inp2, OUTPUT);
  pinMode(enb1, OUTPUT);

  pinMode(inp3, OUTPUT);
  pinMode(inp4, OUTPUT);
  pinMode(enb2, OUTPUT);


  digitalWrite(RED_LEDS, LOW);
  digitalWrite(GREEN_LEDS, LOW);
  digitalWrite(BLUE_LEDS, LOW);
  
  digitalWrite(inp1, HIGH);
  digitalWrite(inp2, LOW);

  digitalWrite(inp3, HIGH);
  digitalWrite(inp4, LOW);

  analogWrite(enb1, motor_speed1);
  analogWrite(enb2, motor_speed2);

  servo1.attach(servopin);
  servo1.write(0);
}

void loop() {
  // --- Έλεγχος για νέο μήνυμα ---
  uint8_t buf[RF22_ROUTER_MAX_MESSAGE_LEN];
  char incoming[RF22_ROUTER_MAX_MESSAGE_LEN];
  memset(buf, 0, RF22_ROUTER_MAX_MESSAGE_LEN);
  memset(incoming, 0, RF22_ROUTER_MAX_MESSAGE_LEN);
  uint8_t len = sizeof(buf);
  uint8_t from;

  float current_mA = ina219.getCurrent_mA();
  float voltage_V = ina219.getBusVoltage_V();
  float power_mW = ina219.getPower_mW();

  if (rf22.recvfromAck(buf, &len, &from)) {
    memcpy(incoming, buf, len);
    incoming[len] = '\0';

    int distance = 0, red = 0, green = 0, blue = 0;
    int hmd=0;
    int tmp=0;
    if (sscanf(incoming, "D:%d R:%d G:%d B:%d Tmp:%d Hmd:%d", &distance, &red, &green, &blue, &tmp, &hmd) == 6) {

      Serial.print(distance);
      Serial.print(" ");
      Serial.print(tmp);
      Serial.print(" ");
      Serial.print(hmd);
      Serial.print(" ");
      Serial.print(current_mA);
      Serial.print(" ");
      Serial.print(voltage_V);
      Serial.print(" ");
      Serial.print(power_mW);
      
      String color = "Unknown";

      if (green > red && green > blue) {
        color = "Green";
        if (distance > 5 && distance < 16 && servoPhase == 0) {
          
          digitalWrite(RED_LEDS, LOW);
          digitalWrite(GREEN_LEDS, HIGH);
          digitalWrite(BLUE_LEDS, LOW);
  
          currentColor = "Green";
          servoIndex = 0;
          servoPhase = 1;
          lastMoveTime = millis();
          Serial.print(" ");
          Serial.print(red);
          Serial.print(" ");
          Serial.print(green);
          Serial.print(" ");
          Serial.print(blue);
          //delay(100);
        }
      }
      else if (red > green && red > blue) {
        color = "Red";
        if (distance > 5 && distance < 16) {
          
          digitalWrite(RED_LEDS, HIGH);
          digitalWrite(GREEN_LEDS, LOW);
          digitalWrite(BLUE_LEDS, LOW);
          
          lastMoveTime = millis();
          Serial.print(" ");
          Serial.print(red);
          Serial.print(" ");
          Serial.print(green);
          Serial.print(" ");
          Serial.print(blue);
          delay(300);
        }
      }
      else if (blue > red && blue > green) {
        color = "Blue";
        if (distance > 5 && distance < 16 && servoPhase == 0) {
          
          digitalWrite(RED_LEDS, LOW);
          digitalWrite(GREEN_LEDS, LOW);
          digitalWrite(BLUE_LEDS, HIGH);

          currentColor = "Blue";
          servoIndex = 0;
          servoPhase = 3;
          lastMoveTime = millis();
          Serial.print(" ");
          Serial.print(red);
          Serial.print(" ");
          Serial.print(green);
          Serial.print(" ");
          Serial.print(blue);
          //delay(100);
        }
      }
      Serial.println("");
    } else {
      Serial.println("Invalid data format");
    }
  }

  // --- Έλεγχος servo με millis ---
  unsigned long now = millis();

  if (servoPhase == 1 && now - lastMoveTime >= servoDelayUp) {
    // Red-up
    servo1.write(servoIndex);
    servoIndex += 15;
    lastMoveTime = now;
    if (servoIndex > 130) {
      servoPhase = 5;
      lastMoveTime = now;
    }
  }
  else if (servoPhase == 3 && now - lastMoveTime >= servoDelayUp) {
    // Blue-up
    servo1.write(servoIndex);
    servoIndex += 30;
    lastMoveTime = now;
    if (servoIndex > 160) {
      servoPhase = 5;
      lastMoveTime = now;
    }
  }
  else if (servoPhase == 5 && now - lastMoveTime >= pauseDelay) {
    // Pause complete
    if (currentColor == "Green") {
      servoIndex = 130;
      servoPhase = 2; // green-down
    } else if (currentColor == "Blue") {
      servoIndex = 160;
      servoPhase = 4; // blue-down
    }
    lastMoveTime = now;
  }
  else if (servoPhase == 2 && now - lastMoveTime >= servoDelayDown) {
    // Red-down
    servo1.write(servoIndex);
    servoIndex -= 20;
    lastMoveTime = now;
    if (servoIndex <= 0) {
      servo1.write(0);
      servoPhase = 0;
    }
  }
  else if (servoPhase == 4 && now - lastMoveTime >= servoDelayDown) {
    // Blue-down
    servo1.write(servoIndex);
    servoIndex -= 20;
    lastMoveTime = now;
    if (servoIndex <= 0) {
      servo1.write(0);
      servoPhase = 0;
    }
  }
}
