#include <SPI.h>
#include <AD4000.h>
#include <teensy_clock.h>

// Constant definitions
#define HWSERIAL Serial5
#define DAC_CS 10
#define ADC_CS 9
#define MUX1_LINE 8
// gain muxes
#define MUX2_LINEA 7 
#define MUX2_LINEB 6 
#define MUX2_LINEC 5


#define FILTER_PUMP 33
#define VALVE 34
#define SOLUTION_PUMP 15
#define BUFFER_PUMP 14

int OVERSAMPLING = 0;

// ADC instantiation
AD4000 adc(ADC_CS);
float args[16];

//      ***Variables***
typedef teensy_clock::time_point timePoint;
typedef std::chrono::duration<float, std::micro> micros_f;


void setup() {
  // Serial
  //  while (!Serial) {} //wait until the connection to the PC is established
  Serial.begin(9600);
  HWSERIAL.begin(9600);
  SPI.begin();
  delay(100);

  // Digital pins setup
  pinMode(ADC_CS, OUTPUT);
  pinMode(DAC_CS, OUTPUT);
  pinMode(MUX1_LINE, OUTPUT);
  pinMode(MUX2_LINEA, OUTPUT);
  pinMode(MUX2_LINEB, OUTPUT);
  pinMode(FILTER_PUMP, OUTPUT);
  pinMode(SOLUTION_PUMP, OUTPUT);
  pinMode(BUFFER_PUMP, OUTPUT);
  pinMode(VALVE, OUTPUT);
  delay(100);

  //for cv, gonna find out if it breaks others
  digitalWriteFast(MUX1_LINE, HIGH); // Selects signal from MUX (ADG419) to be response (we're measuring response signal)

  setVoltage(0); // Set voltage to 0 V (instead of starting on -2.5V on startup, which could affect first time measurement)

  // ADC Setup
  adc.set_settings(false, false, false, true); //Enable status bits, span compression, high Z mode, turbo mode
  delay(100);
  adc.read_register();
  Serial.println("ADC setup complete!");
  delay(100);
}

void loop() {
  bool got_message = false;
  bool exitCode = false;
  if (HWSERIAL.available() > 0) {
    delay(1000);

    getMessage();
    got_message = true;
  }
  if (got_message) {
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE1));
    digitalWriteFast(MUX1_LINE, HIGH); // Selects signal from MUX (ADG419) to be response (we're measuring response signal)
    delayMicroseconds(5);
    setGain(args[1]);
    delay(100);
    Serial.println((int)args[0]);
    
    switch((int)args[0]) {
      case 0:
        Serial.println("Yessir!!!");
        exitCode = true;
        break;
      case 1:
        ASV(args);
        break;
      case 2:
        DPASV(args);
        break;
      case 3:
        DPV(args);
        break;
      case 4:
        Serial.println("Got CV!");
        CV(args);
        break;
      case 5:
        runFilter(args);
        Serial.println("END");
        HWSERIAL.println("END");
        exitCode = true;
        break;
    }
    if(!exitCode) {
      
      // flush the system with buffer
      openValve();
      setBuffer(80);
      delay(5000);
      setBuffer(0);
      delay(2000);
      closeValve();
      Serial.println("END");
      HWSERIAL.println("END");
      SPI.endTransaction();
      
    }
    setVoltage(0);
    delay(100);
    
  }
} 
void getMessage() {
  Serial.println("Hello");
  char sz[200];
  char buf[sizeof(sz)];
  String serialResponse = HWSERIAL.readStringUntil('\n');
  Serial.println(serialResponse);
  serialResponse.toCharArray(buf, sizeof(buf));
  char *p = buf;
  char *str;
  int iterator_count = 0;
  while ((str = strtok_r(p, ",", &p)) != NULL) {
    args[iterator_count] = atof(str);
    iterator_count += 1;
  }
}

void setVoltage(float voltage) {
  int dacValue = int(round((voltage / 2.5 + 1) * 8191.5));
  digitalWriteFast(DAC_CS, LOW);
  SPI.transfer16(dacValue);
  digitalWriteFast(DAC_CS, HIGH);
}

float readCurrent(float gain_val) {
  Serial.println(adc.read_value());
  return (float)(adc.read_value() - 22043) / 21270 * 5 / gain_val;
}

void setGain(int resistanceGain) 
{
  switch(resistanceGain) {
    case 1000:
      digitalWrite(MUX2_LINEA, LOW);
      digitalWrite(MUX2_LINEB, LOW);
      digitalWrite(MUX2_LINEC, LOW);
      break;

    case 10000:
      digitalWrite(MUX2_LINEA, HIGH);
      digitalWrite(MUX2_LINEB, LOW);
      digitalWrite(MUX2_LINEC, LOW);
      break;
      
    case 100000:
      digitalWrite(MUX2_LINEA, LOW);
      digitalWrite(MUX2_LINEB, HIGH);
      digitalWrite(MUX2_LINEC, LOW);
      break;
      
    case 1000000:
      digitalWrite(MUX2_LINEA, HIGH);
      digitalWrite(MUX2_LINEB, HIGH);
      digitalWrite(MUX2_LINEC, LOW);
      break;

    case 200000:
      digitalWrite(MUX2_LINEA, LOW);
      digitalWrite(MUX2_LINEB, LOW);
      digitalWrite(MUX2_LINEC, HIGH);
      break;

    case 100:
      digitalWrite(MUX2_LINEA, HIGH);
      digitalWrite(MUX2_LINEB, LOW);
      digitalWrite(MUX2_LINEC, HIGH);
      break;

    case 20000:
      digitalWrite(MUX2_LINEA, LOW);
      digitalWrite(MUX2_LINEB, HIGH);
      digitalWrite(MUX2_LINEC, HIGH);
      break;

    case 50000:
      digitalWrite(MUX2_LINEA, HIGH);
      digitalWrite(MUX2_LINEB, HIGH);
      digitalWrite(MUX2_LINEC, HIGH);
      break;

    default:
      digitalWrite(MUX2_LINEA, HIGH);
      digitalWrite(MUX2_LINEB, HIGH);
      digitalWrite(MUX2_LINEC, LOW);
      Serial.println("SENSITIVY NOT AVAILABLE, SET TO 1M");
      delay(1000);
      break;
  }
}


// custom wait function with interuption from bluetooth
bool waitSeconds(float seconds) {
  long timeMicros = (long)(seconds * 1000000);
  long startTime = micros();
  while (micros() - startTime < timeMicros) {
    if(HWSERIAL.available() > 0) return true;
  }
  return false;
}

float measureCurrent(float pulse, float sample_width, float gain_val) {
  float total = 0;
  float how_many = 0;
  timePoint timeold = teensy_clock::now();
  timePoint timenew = teensy_clock::now();
  int time_for_measurements = pulse * 1000000 - sample_width * 1000000;
  int intervals = time_for_measurements / OVERSAMPLING;
  int next_measurement_time = sample_width * 1000000;
  
  while (std::chrono::duration_cast<micros_f>(timenew - timeold).count() <= 1000000 * pulse) {
    timenew = teensy_clock::now();
    if(HWSERIAL.available() > 0) return 0xFFFFFFFF;
    if (std::chrono::duration_cast<micros_f>(timenew - timeold).count() >= sample_width * 1000000) {
      if (std::chrono::duration_cast<micros_f>(timenew - timeold).count() >= next_measurement_time) {
        if (how_many <= OVERSAMPLING) {
          total = total + readCurrent(gain_val);
          how_many++;
          next_measurement_time += intervals;
        }
      }
    }
  }
  return total / how_many;
}

void setFilter(float percent) {
  setMotor(FILTER_PUMP, percent);
}

void setSolution(float percent) {
  setMotor(SOLUTION_PUMP, percent);
}

void setBuffer(float percent) {
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
