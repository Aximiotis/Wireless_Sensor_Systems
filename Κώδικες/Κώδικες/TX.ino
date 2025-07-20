#include <RF22.h>
#include <RF22Router.h>
#include "DHT.h"
#include <Servo.h>
#include <Wire.h>

#define MY_ADDRESS 12
#define DESTINATION_ADDRESS 5
#define DHTPIN 7       // DATA pin is connected to digital pin 7
#define DHTTYPE DHT11  // DHT 11

DHT dht(DHTPIN, DHTTYPE);
RF22Router rf22(MY_ADDRESS);


// Distance Sensor (HC-SR04)
int sensorPin = A0;  // Trig & Echo στο ίδιο pin
int distance = 0;

// TCS3200 Color Sensor (χρησιμοποιούμε analog pins)
const int S2 = A3;
const int S3 = A1;
const int output = A2;  // OUT pin από TCS3200
// S0 → VCC
// S1 → GND (καρφωμένα με jumper)

// SERVO MOTOR
Servo barrierServo;
unsigned long actionStartTime = 0;
bool inAction = false;
int step = 0;


long randNumber;
boolean successful_packet = false;
int max_delay = 800;


void setup() {
  // Color Sensor
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(output, INPUT);

  Serial.begin(9600);
  if (!rf22.init())
    Serial.println("RF22 init failed");
  if (!rf22.setFrequency(431.0))
    Serial.println("setFrequency Fail");
  rf22.setTxPower(RF22_TXPOW_20DBM);
  rf22.setModemConfig(RF22::GFSK_Rb125Fd125);
  rf22.addRouteTo(DESTINATION_ADDRESS, DESTINATION_ADDRESS);

  // hum & temp sensor
  dht.begin();

  // servo motor
  barrierServo.attach(4);
  barrierServo.write(0);  // αρχικά κατεβασμένη
  
  randomSeed(micros());
}

void loop() {
  // Μέτρηση Απόστασης
  long duration;
  pinMode(sensorPin, OUTPUT);
  digitalWrite(sensorPin, LOW);
  delayMicroseconds(2);
  digitalWrite(sensorPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(sensorPin, LOW);

  pinMode(sensorPin, INPUT);
  delayMicroseconds(100);
  duration = pulseIn(sensorPin, HIGH, 30000);
  distance = (duration / 2) / 29.1;

  Serial.print("Measured Distance: ");
  Serial.println(distance);


  
  unsigned long now = millis();
  // SERVO MOTOR
  if (!inAction && distance > 5 && distance < 16) {
    inAction = true;
    actionStartTime = now;
    step = 0;
  }

  if (inAction) {
    if (step == 0 && now - actionStartTime >= 1000) {
      barrierServo.write(70);  // Σήκωσε την μπάρα
      actionStartTime = now;
      step = 1;
    }
    else if (step == 1 && now - actionStartTime >= 1000) {
      barrierServo.write(0);   // Κατέβασε την μπάρα
      inAction = false;
    }
  }

  

  // TEMP & HUM sensor
  float hmd = dht.readHumidity();
  float tmp = dht.readTemperature();
  // Check if reading failed
  if (isnan(hmd) || isnan(tmp)) {
    Serial.println(" Failed to read from DHT11 sensor!");
    return;
  }
  Serial.print("Temp: ");
  Serial.println(tmp);
  Serial.print("Hmd: ");
  Serial.println(hmd);



  // Δεδομένα για RF
  char data_read[RF22_ROUTER_MAX_MESSAGE_LEN];
  uint8_t data_send[RF22_ROUTER_MAX_MESSAGE_LEN];
  memset(data_read, '\0', RF22_ROUTER_MAX_MESSAGE_LEN);
  memset(data_send, '\0', RF22_ROUTER_MAX_MESSAGE_LEN);

  // DELAY DISTANCE-COLOUR
  delay(200);

  // Αν εντός αποδεκτής περιοχής, μετράμε και χρώμα
  int red = 255 - red_recognition();
  int green = 255 + 5 - green_recognition();
  int blue_raw = 255 +15 - blue_recognition();
  int blue = max(0, blue_raw - 15);  // μικρή διόρθωση

  Serial.print("Red = "); Serial.print(red);
  Serial.print(" Green = "); Serial.print(green);
  Serial.print(" Blue = "); Serial.println(blue);

  // Σύνθεση πακέτου με όλα τα δεδομένα
  // tmp * 10
  // hmd * 10 
  // they need to be divided by 10 at the receiver
  snprintf(data_read, sizeof(data_read), "D:%d R:%d G:%d B:%d Tmp:%d Hmd:%d", distance, red, green, blue, (int)(tmp * 10), (int)(hmd * 10));


  // Κωδικοποίηση σε RF πακέτο
  data_read[RF22_ROUTER_MAX_MESSAGE_LEN - 1] = '\0';
  memcpy(data_send, data_read, RF22_ROUTER_MAX_MESSAGE_LEN);

  // Αποστολή με retry
  successful_packet = false;
  while (!successful_packet) {
    if (rf22.sendtoWait(data_send, sizeof(data_send), DESTINATION_ADDRESS) != RF22_ROUTER_ERROR_NONE) {
      Serial.println("sendtoWait failed");
      randNumber = random(100, max_delay);
      Serial.print("Retrying after delay: ");
      Serial.println(randNumber);
      delay(randNumber);
    } else {
      successful_packet = true;
      Serial.print("Sent: ");
      Serial.println(data_read);
    }
  }

  delay(10);
}

// ---- Χρωματική μέτρηση ----

int red_recognition() {
  digitalWrite(S2, LOW);
  digitalWrite(S3, LOW);
  return pulseIn(output, LOW);
}

int green_recognition() {
  digitalWrite(S2, HIGH);
  digitalWrite(S3, HIGH);
  return pulseIn(output, LOW);
}

int blue_recognition() {
  digitalWrite(S2, LOW);
  digitalWrite(S3, HIGH);
  return pulseIn(output, LOW);
}
