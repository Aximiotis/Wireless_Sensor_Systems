#include<Wire.h>
const int flame=8;
const int led=9;
void setup() {
  // put your setup code here, to run once:
  pinMode(flame,INPUT);
  pinMode(led,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int detect=digitalRead(flame);
  Serial.println(detect);
  if (detect==1){
      digitalWrite(led,HIGH);
  }
  else if (detect==0){
      digitalWrite(led,LOW);
  }
}
