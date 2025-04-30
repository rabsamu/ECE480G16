#include <SD.h>


//#define HWSERIAL Serial1
#define FILTER_PUMP 33
#define VALVE 34
#define SOLUTION_PUMP 14
#define BUFFER_PUMP 15

int runNumber = 0;

void setup() {
  // Set all the motor control pins to outputs
  pinMode(FILTER_PUMP, OUTPUT);
  pinMode(SOLUTION_PUMP, OUTPUT);
  pinMode(BUFFER_PUMP, OUTPUT);
  pinMode(VALVE, OUTPUT);
//  if(!SD.begin()) {
//    Serial.println("really bad");
//  }
  delay(1000);
//  openFile();

  

}

void loop() {
//  Serial.println(runNumber);
  
//  setFilter(80);
//  delay(5000);
//  setFilter(0);
//
//  openValve();
  setSolution(75);
  setBuffer(75);
  delay(5000);
//
//  closeValve();
  setSolution(0);
  setBuffer(0);
//
  delay(5000);
  
//  if(Serial.available()) {
//    char msg = Serial.read();
//    switch(msg) {
//      case '1':
//        blinkLight();
////        gotoState1();
//        break;
//      case '2':
//        gotoState2();
//        break;
//      case '3':
//        gotoState3();
//        break;
//      case '4':
//        toggleDirection(1);
//        toggleDirection(2);
//        break;
//    }
//  }
  delay(10);
}

void openFile() {
  if(SD.exists("sysinfo.txt")) {
    Serial.println("old");
    File logFile = SD.open("sysinfo.txt", FILE_READ);
    String text = logFile.readStringUntil("\n");
    runNumber = text.toInt() + 1;
    Serial.println(runNumber);
    logFile.close();

    logFile = SD.open("sysinfo.txt", FILE_WRITE);
    logFile.println(runNumber);
    logFile.close();
    
  } else {
    Serial.println("new");
    runNumber = 0;
    File logFile = SD.open("sysinfo.txt", FILE_READ);
    if(logFile) {
      Serial.println("OKAY!!!");
    } else {
      Serial.println("Uh oh!");
    }
//    logFile.println(runNumber);
//    logFile.println("Waffle");
    logFile.close();
    
    logFile = SD.open("sysinfo.txt", FILE_READ);
    String text = logFile.readString();
//    runNumber = text.toInt() + 1;
    Serial.println(text);
    logFile.close();
    
  }
}

void gotoState1() {
  return;
}

void gotoState2() {
  return;
}

void gotoState3() {
  return;
}

void blinkLight() {
  digitalWrite(13, 1);
  delay(4000);
  digitalWrite(13, 0);
}

void setFilter(int percent) {
  setMotor(FILTER_PUMP, percent);
}

void setSolution(int percent) {
  setMotor(SOLUTION_PUMP, percent);
}

void setBuffer(int percent) {
  setMotor(BUFFER_PUMP, percent);
}

void setMotor(int pinNum, float percent) {
  int scaledVal = (int)(percent / 100 * 255);
  analogWrite(pinNum, scaledVal);
}

void openValve() {
  digitalWrite(VALVE, 1);
}

void closeValve() {
  digitalWrite(VALVE, 0);
}
