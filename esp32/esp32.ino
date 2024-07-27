// Input Library
#include <WiFi.h>
#include <HTTPClient.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "slebew";
const char* password = "agusmaubaliksmt1";
const char* apiEndPoint = "https://ap-southeast-1.aws.data.mongodb-api.com/app/data-ldieife/endpoint/data/v1/action/insertOne";
const char* apiEndPoint2 = "https://ap-southeast-1.aws.data.mongodb-api.com/app/data-ldieife/endpoint/data/v1/action/findOne";
const char* apiKey = "Hq4MjYseMzjzfdfOmMTPrP2tOLOWsGrxUHeA2YdR3o4JEb0GasQUvb82zzzWOvST";
const String clusterName = "finalproject";
const String databaseName = "waterqualitysensor";
const String collectionName = "finalproject";
const String collectionName2 = "button";


// Sensor pin connections
// Analog input pin for TDS sensor
const int tdsPin = 32; 
// Analog input pin for Turbidity sensor
const int turbidityPin = 33; 
// Analog input pin for pH sensor
const int phPin = 34;
int samples = 10;
float adc_resolution = 1024.0;
// Analog input pin for Temperature sensor 
const int tempPin = 35;
OneWire oneWire(tempPin);
DallasTemperature sensors(&oneWire);


// Button pin connections
const int buttonPin1 = 4;
int mode1 = 0;
const int buttonPin2 = 5;
int mode2 = 0;


// Relay pin connections
const int phUp = 25;
const int phDown = 26;
const int pump = 27;


// LCD
LiquidCrystal_I2C lcd(0x27, 20, 4);

void setup() {
  Serial.begin(115200);
  lcd.init();
  lcd.backlight();
  sensors.begin();

  // Initialize WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status()!= WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
    lcd.setCursor(0, 1);
    lcd.println("     Connecting");
    lcd.setCursor(0, 2);
    lcd.println("     to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println("Initializing sensors...");

  // Initialize sensors
  pinMode(tdsPin, INPUT);
  pinMode(turbidityPin, INPUT);
  pinMode(phPin, INPUT);
  pinMode(tempPin, INPUT);

  // Initialize button
  pinMode(buttonPin1, INPUT_PULLUP);
  pinMode(buttonPin2, INPUT_PULLUP);
}


// pH Reading
float ph (float voltage) {
    return 7 + ((2.5 - voltage) / 0.18);
}


void loop() {
  // Read TDS sensor value
  int tdsValue = analogRead(tdsPin);
  float tdsVoltage = tdsValue * (3.3 / 4095.0);
  float tdsPPM = tdsVoltage * 1000.0; // Convert voltage to PPM (parts per million)

  // Read Turbidity sensor value
  int turbidityValue = analogRead(turbidityPin);
  float turbidityVoltage = turbidityValue * (3.3 / 4095.0);
  float turbidityNTU = turbidityVoltage * 100.0; // Convert voltage to NTU (Nephelometric Turbidity Units)

  // Read pH sensor value
  int measurings=0;

    for (int i = 0; i < samples; i++)
    {
        measurings += analogRead(phPin);
        delay(10);

    }

    float voltage = 5 / adc_resolution * measurings/samples;

  // Read Temperature sensor value
  sensors.requestTemperatures();
  float tempValue = sensors.getTempCByIndex(0);
  

  //Switch screen LCD
  int buttonState1 = digitalRead(buttonPin1);

  if (buttonState1 == LOW) {
      mode1 = (mode1 + 1) % 5;
      delay(100);
  }

  //Update Display
  switch (mode1) {
    case 0:
      updateLCD1();
      break;
    case 1:
      updateLCD2();
      break;
    case 2:
      updateLCD3();
      break;
    case 3:
      updateLCD4();
      break;
    case 4:
      updateLCD5();
      break;
    default:
      mode1 = 0;
  }


  //Button filtrasi
  int buttonState2 = digitalRead(buttonPin2);

  if (buttonState2 == LOW) {
      mode2 = (mode2 + 1) % 2;
      delay(100);
  }

  //Update Display
  switch (mode2) {
    case 0:
      // Checking for web button
      HTTPClient http2
      String url2 = apiEndPoint2;
      http2.begin(url2);
      http2.addHeader("Content-Type", "application/json");
      http2.addHeader("Access-Control-Request-Headers", "*");
      http2.addHeader("api-key", apiKey);

      String jsonData2 = "{"
                      "\"dataSource\": \"" + clusterName + "\","
                      "\"database\": \"" + databaseName + "\","
                      "\"collection\": \"" + collectionName2 + "\","
                    "}";
  
      int httpResponseCode2 = http.POST(jsonData2);

      if (httpResponseCode2 > 0) {
      Serial.println("Data get successfully!");

      String response = http.getString();
      DynamicJsonDocument doc(1024);
      deserializeJson(doc, response);
      const char* filtration = doc["document"]["filtration"];

      if (strcmp(filtration, "on") == 0) {
          digitalWrite(pump, HIGH);
          digitalWrite(phUp, (ph(voltage) < 6) ? LOW : HIGH);
          digitalWrite(phDown, (ph(voltage) > 8) ? LOW : HIGH);
        } else {
          digitalWrite(pump, LOW);
        }
      } else {
        Serial.println("Error getting data:");
        Serial.println(http.errorToString(httpResponseCode));
      }

      http2.end()

      break;
    case 1:
      digitalWrite(pump, HIGH);
      digitalWrite(phUp, (ph(voltage) < 6) ? LOW : HIGH);
      digitalWrite(phDown, (ph(voltage) > 8) ? LOW : HIGH);
      break;
    default:
      mode2 = 0;
  }


  // Sreial Screen
  Serial.print("TDS value: ");
  Serial.print(tdsPPM);
  Serial.println(" PPM");

  Serial.print("Turbidity value: ");
  Serial.print(turbidityNTU);
  Serial.println(" NTU");

  Serial.print("pH value: ");
  Serial.print(ph(voltage));
  Serial.println(" pH");

  Serial.print("Temperature value: ");
  Serial.print(tempValue);
  Serial.println(" Celsius");

  // Send sensor data to API endpoint
  HTTPClient http;
  String url = apiEndPoint;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Access-Control-Request-Headers", "*");
  http.addHeader("api-key", apiKey);

  String jsonData = "{"
                      "\"dataSource\": \"" + clusterName + "\","
                      "\"database\": \"" + databaseName + "\","
                      "\"collection\": \"" + collectionName + "\","
                      "\"document\": {"
                        "\"tds\": " + String(tdsPPM) + ", "
                        "\"turbidity\": " + String(turbidityNTU) + ", "
                        "\"ph\": " + String(ph(voltage)) + ", "
                        "\"temperature\": " + String(tempValue) + 
                      "}"
                    "}";

  int httpResponseCode = http.POST(jsonData);

  if (httpResponseCode > 0) {
    Serial.println("Data sent successfully!");
  } else {
    Serial.println("Error sending data:");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();
  
  delay(1000); // Send data every 10 seconds
}

// LCD Screen
void updateLCD1() {
  // Display Introduction
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print("   WELCOME TO");
  lcd.setCursor(0, 2);
  lcd.print("       SIWAQU");
  delay(500);
}

void updateLCD2() {
  // Display TDS
  int tdsValue = analogRead(tdsPin);
  float tdsVoltage = tdsValue * (3.3 / 4095.0);
  float tdsPPM = tdsVoltage * 1000.0; // Convert voltage to PPM (parts per million)

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("TOTAL DISOLVED SOLID");
  lcd.setCursor(0, 1);
  lcd.print("Value: ");
  lcd.print(tdsPPM);
  lcd.print(" PPM");
  lcd.setCursor(0, 2);
  lcd.print("Ideal TDS:");
  lcd.setCursor(0, 3);
  lcd.print("< 500 PPM");
  delay(500);
}

void updateLCD3() {
  // Display Turbidity
  int turbidityValue = analogRead(turbidityPin);
  float turbidityVoltage = turbidityValue * (3.3 / 4095.0);
  float turbidityNTU = turbidityVoltage * 100.0; // Convert voltage to NTU (Nephelometric Turbidity Units)
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("     TURBIDITY");
  lcd.setCursor(0, 1);
  lcd.print("Value: ");
  lcd.print(turbidityNTU);
  lcd.print(" NTU");
  lcd.setCursor(0, 2);
  lcd.print("Ideal Turbidity:");
  lcd.setCursor(0, 3);
  lcd.print("< 5 NTU");
  delay(500);
}

void updateLCD4() {
  // Display pH
  int measurings=0;

    for (int i = 0; i < samples; i++)
    {
        measurings += analogRead(phPin);
        delay(10);

    }

    float voltage = 5 / adc_resolution * measurings/samples;
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("POTENTIAL OF HYDROGEN");
  lcd.setCursor(0, 1);
  lcd.print("Value: ");
  lcd.print(ph(voltage));
  lcd.print(" pH");
  lcd.setCursor(0, 2);
  lcd.print("Ideal pH: 6,5-8,5 pH");
  if (phUp ==  HIGH){
    lcd.setCursor(0, 3);
    lcd.print("Pump pH Up: ON");
  }
  else if (phDown ==  HIGH){
    lcd.setCursor(0, 3);
    lcd.print("Pump pH Down: ON");
  }
  else {
    lcd.setCursor(0, 3);
    lcd.print("Pump pH: OFF");
  }
  
  delay(500);
}

void updateLCD5() {
  // Display Temperature
  int tempValue = tempPin;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("    TEMPERATURE");
  lcd.setCursor(0, 1);
  lcd.print("Value: ");
  lcd.print(tempValue);
  lcd.print("*C");
  lcd.setCursor(0, 2);
  lcd.print("Ideal Temperature:");
  lcd.setCursor(0, 3);
  lcd.print("20*C - 25*C");
  delay(500);
}