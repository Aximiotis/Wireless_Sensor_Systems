#include<Wire.h>
const int voltage_regulator=A0;
int enb1=13;
int inp1=12;
int inp2=11;
void setup() {
  // put your setup code here, to run once:
  pinMode(inp1,OUTPUT);
  pinMode(inp2,OUTPUT);
  pinMode(enb1,OUTPUT);
  pinMode(voltage_regulator,INPUT);
  Serial.begin(115200);
  digitalWrite(inp1,HIGH);
  digitalWrite(inp2,LOW);
}

void loop() {
  // put your main code here, to run repeatedly:

  int read=analogRead(voltage_regulator);
  analogWrite(enb1,read/4);
  Serial.println(read);
}
