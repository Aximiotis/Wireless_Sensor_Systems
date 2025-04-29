#include <DFRobot_DHT11.h>
#define DHT11PIN 13
DFRobot_DHT11 dht;
void  setup()
{
  Serial.begin(115200);
 
}
void loop()
{
  Serial.println();

  dht.read(DHT11PIN);

  Serial.print("Humidity (%): ");
  Serial.println(dht.humidity);

  Serial.print("Temperature  (C): ");
  Serial.println(dht.temperature);

  delay(2000);

}