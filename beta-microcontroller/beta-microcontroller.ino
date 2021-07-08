#include <Wire.h>
#include <DS18B20.h>

DS18B20 ds(2);

#define COMMAND_SOIL_LED_OFF     0x00
#define COMMAND_SOIL_LED_ON      0x01
#define COMMAND_SOIL_GET_VALUE        0x05
#define COMMAND_SOIL_NOTHING_NEW   0x99

const byte defaultSoilAddress = 0x28;     //Default Sensor Address

void setup() {
  // put your setup code here, to run once:
  initSerial(9600);

  Wire.begin();
  testForSoilSensorConnectivity();

}

void loop() {
  // put your main code here, to run repeatedly:
  ledOff();
  getSoilSensorValue();
  ledOn();
  Serial.print(":");
  Serial.print("TF:");
  Serial.print(ds.getTempF());
  Serial.println("");
  delay(10000);
}

// initSerial - initialization method for the serial interface
void initSerial(int baud){
  Serial.begin(baud);
  Serial.println();
  Serial.println("Garden Base Station Beta Initialization...");
}

// getSoilSensorValue tries to read soil sensor data through the connected
// mux.
// LED is off, and a -1 if an error occurred.
void getSoilSensorValue() {
  ledOn();
  Wire.beginTransmission(defaultSoilAddress);
  Wire.write(COMMAND_SOIL_GET_VALUE); // command for status
  Wire.endTransmission();    // stop transmitting //this looks like it was essential.

  Wire.requestFrom(defaultSoilAddress, 2);    // request 1 bytes from slave device qwiicAddress

  while (Wire.available()) { // slave may send less than requested
    uint16_t localADC;
    uint8_t ADC_VALUE_L = Wire.read(); 
    uint8_t ADC_VALUE_H = Wire.read();
    localADC = ADC_VALUE_H;
    localADC <<= 8;
    localADC |= ADC_VALUE_L;
    Serial.print("SM:");
    Serial.print(localADC,DEC);

  }
  uint16_t x=Wire.read(); 
  ledOff();
}

// testForSoilSensorConnectivity() checks for an ACK from an Sensor. If no ACK
// program freezes and notifies user.
void testForSoilSensorConnectivity() {
  Wire.beginTransmission(defaultSoilAddress);
  //check here for an ACK from the slave, if no ACK don't allow change?
  if (Wire.endTransmission() != 0) {
    Serial.println("Check connections. No slave attached.");
  }
}

void ledOn() {
  Wire.beginTransmission(defaultSoilAddress);
  Wire.write(COMMAND_SOIL_LED_ON);
  Wire.endTransmission();
}

void ledOff() {
  Wire.beginTransmission(defaultSoilAddress);
  Wire.write(COMMAND_SOIL_LED_OFF);
  Wire.endTransmission();
}
