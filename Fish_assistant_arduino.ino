#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#include <OneWire.h>
#include <DallasTemperature.h>


#define ONE_WIRE_BUS 5 // pin D1 = GPIO 5 | For DS18B20 temperature sensor. 

#define PUMP_OUT_RELAY 4 // pin D2 = GPIO 4 | Part of pump system to regulate temperature. 

#define PUMP_IN_RELAY 12 //pin D6 = GPIO 12 | Part of pump system to regulate temperature. 

#define SOLENOID_RELAY 14 //pin D5 = GPIO 14 | To open and close a mechanism that feeds the fish w/ fish food. 

#define WATER_PUMP_RELAY 13 //pin D7 = GPIO 13 | Pump for adding new water to adjust both temperature & pH. 

#define FAN_PIN 16 //pin D0 = GPIO 16 | Fan for cooling internal water regulation system.

#define WIFI_NAME "Tangchartsiri"
#define WIFI_PASS "T75Vsr28"
#define MQTT_SERVER "maqiatto.com"
#define MQTT_PORT 1883
#define MQTT_USERNAME "gate.tang@gmail.com"
#define MQTT_PASSWORD "letmein" //Change to 
#define MQTT_NAME "Gate"
#define MQTT_TOPIC_LED "gate.tang@gmail.com/LED"
#define MQTT_TOPIC_FOOD "gate.tang@gmail.com/food"
#define MQTT_TOPIC_WATER "gate.tang@gmail.com/water"

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);


WiFiClient espClient;
PubSubClient mqtt(espClient);

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print ("Message arrived in topic:");
  Serial.println (topic);
  String msg = "";
  for(int i=0; i<length; i++){
    msg += (char) payload[i];
  }
  Serial.print("Message: ");
  Serial.println (msg);
  String myString = String(topic);
  if (myString == "gate.tang@gmail.com/food"){
    Serial.print ("Feeding:");
    Serial.println (msg); // For testing. 
    int sVal = msg.toInt();
    for (int t = 0; t<=sVal; t++){
      digitalWrite (SOLENOID_RELAY, LOW);
      delay (500); //Measure how much time is needed for the solenoid to drop 1 gram of food.
      digitalWrite (SOLENOID_RELAY, HIGH);
      delay(500);
    }
}
  if (myString == MQTT_TOPIC_WATER){
    if (msg == "ON"){
      Serial.print ("Changing Water ON");
      Serial.println (msg);
      digitalWrite(WATER_PUMP_RELAY, LOW);
    }
    if (msg == "OFF"){
      Serial.print ("Changing Water OFF");
      Serial.println (msg);
      digitalWrite (WATER_PUMP_RELAY, HIGH);
    }
  }
}
void setup() {
  // put your setup code here, to run once:
Serial.begin (115200); //Change to 9600bps if needed. (not sure)

sensors.begin();
pinMode(PUMP_OUT_RELAY, OUTPUT);
pinMode(PUMP_IN_RELAY, OUTPUT);

pinMode(SOLENOID_RELAY, OUTPUT);

digitalWrite(PUMP_OUT_RELAY, HIGH);
digitalWrite(PUMP_IN_RELAY, HIGH);

digitalWrite(SOLENOID_RELAY, HIGH);


WiFi.begin (WIFI_NAME, WIFI_PASS);
while (WiFi.status() !=WL_CONNECTED){
  delay (500);
  Serial.println (".");
}
Serial.println ("");
Serial.println ("WiFi connected");

mqtt.setServer (MQTT_SERVER, MQTT_PORT);
mqtt.setCallback(callback);
while (!mqtt.connected()){
  if (mqtt.connect (MQTT_NAME, MQTT_USERNAME, MQTT_PASSWORD)){
    mqtt.subscribe (MQTT_TOPIC_LED);
    mqtt.subscribe (MQTT_TOPIC_FOOD);
    Serial.println ("MQTT connected");
  } else {
    Serial.print ("Fail, rc ");
    Serial.print(mqtt.state());
    Serial.println (" try again in 5 seconds");
    delay(300000); //5 minutes (Change if needed if intervals are too short).
  }
}
pinMode(LED_BUILTIN, OUTPUT);
}

void temp() {
  sensors.requestTemperatures();
  float TEMP_VAL;
  TEMP_VAL = sensors.getTempCByIndex(0); //int or float not sure yet. 
  //Serial.println (TEMP_VAL);
  String object = String(TEMP_VAL);
  char post[object.length() + 1];
  for (int i = 0; i < object.length(); i++) {
    post[i] = object[i];
  }
  post[object.length()] = 0;
  mqtt.publish(MQTT_TOPIC_LED, post);
  Serial.println(post);

  float MAX_TEMP = 27.0;
  if (TEMP_VAL> MAX_TEMP){
    Serial.println("Pump Circulation ON");
    digitalWrite(PUMP_OUT_RELAY, LOW);
    digitalWrite (PUMP_IN_RELAY, LOW);
    delay (2000);
}
else {
    Serial.println("Pump Circulation OFF");
    digitalWrite(PUMP_OUT_RELAY, HIGH);
    digitalWrite (PUMP_IN_RELAY, HIGH);
    delay (2000);
}}


void loop() {
  // put your main code here, to run repeatedly:
mqtt.loop();
temp();
}
