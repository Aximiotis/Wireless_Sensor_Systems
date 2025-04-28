#include <Wire.h>

const int S3=4;
const int S2=5;
const int S1=12;
const int S0=13;

int output=8;
int red_recognition(int a,int b);
int green_recognition(int a,int b);
int bleu_recognition(int a,int b);

int red_recognition(int a,int b){
  digitalWrite(a,LOW);
  digitalWrite(b,LOW);
  
  // Reading the output frequency
  int redFrequency = pulseIn(output, LOW);
  return redFrequency;
}

int green_recognition(int a,int b){
  digitalWrite(a,HIGH);
  digitalWrite(b,HIGH);
  
  // Reading the output frequency
  int greenFrequency = pulseIn(output, LOW);
  
  return greenFrequency;
}

int bleu_recognition(int a,int b){
  digitalWrite(a,LOW);
  digitalWrite(b,HIGH);
  
  // Reading the output frequency
  int bleuFrequency = pulseIn(output, LOW);

  return bleuFrequency;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(S0,OUTPUT);
  pinMode(S1,OUTPUT);
  pinMode(S2,OUTPUT);
  pinMode(S3,OUTPUT);
  pinMode(output,INPUT);

  digitalWrite(S0,HIGH);
  digitalWrite(S1,LOW);
}

void loop() {
  // put your main code here, to run repeatedly:

  int red_g=0;
  int bleu_g=0;
  int green_g=0;

  red_g=red_recognition(S2,S3);
  green_g=green_recognition(S2,S3);
  bleu_g=bleu_recognition(S2,S3);
  Serial.print(255-red_g);
  Serial.print(" ");
  Serial.print(260-green_g);
  Serial.print(" ");
  Serial.println(255-bleu_g);
  delay(1000);
}