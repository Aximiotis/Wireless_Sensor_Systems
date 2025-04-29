#include<Servo.h>
Servo servo1;
int servopin=9;
int i;
void setup() {
  // put your setup code here, to run once:
servo1.attach(servopin);
}

void loop() {
  // put your main code here, to run repeatedly:
for(i=0;i<=180;i=i+5){
    servo1.write(i);
    delay(50);

}
for(i=180;i>=0;i=i-5){
    servo1.write(i);
    delay(50);

}
}
