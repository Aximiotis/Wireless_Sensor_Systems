int res=13;
const int currentPin = A0;
int sensitivity = 190;
int adcValue= 0;
int offsetVoltage = 2500;
double adcVoltage = 0;
double currentValue = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(res,OUTPUT);
  Serial.begin(9600);
  digitalWrite(res,HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:
  double current=0;
  currentValue=0;
  for(int i=0;i<10000;i++){
    adcValue = analogRead(currentPin);
    adcVoltage = (adcValue / 1024.0) * 5000;
    currentValue = currentValue + ((adcVoltage - offsetVoltage) / sensitivity); // mA
  }
  current=((currentValue)/10-10);
  Serial.println(current);
  delay(500);
}
