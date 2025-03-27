#include <SPI.h>
#include <AD4000.h>
#include <teensy_clock.h>

// Constant definitions
#define DAC_CS 10
#define ADC_CS 9
#define MUX1_LINE 8
// gain muxes
#define MUX2_LINEA 7 
#define MUX2_LINEB 6 
#define MUX2_LINEC 5

int OVERSAMPLING = 0;

// ADC instantiation
AD4000 adc(ADC_CS);
float arg_1;
float arg_2;
float arg_3;
float arg_4;
float arg_5;
float arg_6;
float arg_7;
float arg_8;
float arg_9;
float arg_10;
float arg_11;
float arg_12;
float arg_13;
float arg_14;
float arg_15;
float args[16];

//      ***Variables***

//  old
int gain_value;
float v_step;
float low_voltage;
float high_voltage;
int segments;
int times_to_sample; // case 5
float sample_rate; // case 6
int technique; // case 1

//  dpasv/dpv
int gain; // case 2     (ohms) - Gain
float initial_potential;
float final_potential;
float increment_potential;
float pulse_width;   // (s) - Potential pulse width
float pulse_period;  // (s) - Potential pulse period or dropping time
float amplitude;     // (V)- Potential pulse amplitude
float quiet_time;    // (s) - Quiscent time before potential pulses begin
float sample_width;  // (s) - Data sampling width
float hold_time1; // (s)
float hold_voltage1; // (V)
float hold_time2; // (s)
float hold_voltage2; // (V)

//  cv
int cv_sensitivity;
int cv_sampling_rate;
float cv_scan_rate;
int cv_number_of_segments;
float cv_lower_voltage_limit; // case 3 - arg_1
float cv_upper_voltage_limit; // case 4

typedef teensy_clock::time_point timePoint;
typedef std::chrono::duration<float, std::micro> micros_f;


void setup() {
  // Serial
  //  while (!Serial) {} //wait until the connection to the PC is established
  Serial.begin(9600);
  SPI.begin();
  delay(100);

  // Digital pins setup
  pinMode(ADC_CS, OUTPUT);
  pinMode(DAC_CS, OUTPUT);
  pinMode(MUX1_LINE, OUTPUT);
  pinMode(MUX2_LINEA, OUTPUT);
  pinMode(MUX2_LINEB, OUTPUT);
  delay(100);

  //for cv, gonna find out if it breaks others
  digitalWriteFast(MUX1_LINE, HIGH); // Selects signal from MUX (ADG419) to be response (we're measuring response signal)

  setVoltage(8192); // Set voltage to 0 V (instead of starting on -2.5V on startup, which could affect first time measurement)

  // ADC Setup
  adc.set_settings(false, false, false, true); //Enable status bits, span compression, high Z mode, turbo mode
  delay(100);
  adc.read_register();
  Serial.println("ADC setup complete!");
  delay(100);
} //Good I think

void loop() {
  bool got_message = false;
  if (Serial.available() > 0) {
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
    
    switch((int)args[0]) {
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
        CV(args);
        break;
    }

    delay(100);
    Serial.println("Done!");
    SPI.endTransaction();
  }
} 
void getMessage() {
  char sz[200];
  char buf[sizeof(sz)];
  String serialResponse = Serial.readStringUntil('\r\n');
  serialResponse.toCharArray(buf, sizeof(buf));
  char *p = buf;
  char *str;
  int iterator_count = 0;
  while ((str = strtok_r(p, ", ", &p)) != NULL) {
    iterator_count += 1;
    args[iterator_count] = atof(str);
  }
}

int voltageToCode(float v) {
  return 0;
}

int voltageToBytes(float v) {
  return 0;
}

void setVoltage(float voltage) {
  int dacValue = int(round((voltage / 2.5 + 1) * 8191.5));
  digitalWriteFast(DAC_CS, LOW);
  SPI.transfer16(dacValue);
  digitalWriteFast(DAC_CS, HIGH);
}

float readCurrent(float gain_val) {
  return ((5 * (float)adc.read_value() / (1<<16-1)) - 2.5) * 2 / gain_val;
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

float codeToVoltage(int code) {
  return ((float)code / 8191.5 - 1) * 2.5;
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
