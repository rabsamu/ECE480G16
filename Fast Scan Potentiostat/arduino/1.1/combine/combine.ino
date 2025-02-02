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

  // ASV
  if (got_message && arg_1 == 1) {
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE1));
    digitalWriteFast(MUX1_LINE, HIGH); // Selects signal from MUX (ADG419) to be response (we're measuring response signal)
    delayMicroseconds(5);
    // CV(cv_lower_voltage_limit, high_voltage, segments);
    setGain(10000);
    low_voltage = arg_2;
    high_voltage = arg_3;
    times_to_sample = arg_4;
    hold_time1 = arg_5;
    hold_voltage1 = arg_6;
    hold_time2 = arg_7;
    hold_voltage2 = arg_8;
    gain = arg_9;
    sample_rate = arg_10;
    setGain(gain);
    delay(100);

    ASV(low_voltage,high_voltage,times_to_sample,sample_rate,hold_time1,hold_voltage1,hold_time2,hold_voltage2);
    delay(100);
    Serial.println("Done!");
    SPI.endTransaction();
  }

  // DPASV
  if (got_message && arg_1 == 2) {
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE1));
    digitalWriteFast(MUX1_LINE, HIGH);
    delayMicroseconds(5);
    gain = arg_2;
    initial_potential = arg_3;
    final_potential = arg_4;
    increment_potential = arg_5;
    pulse_width = arg_6;
    pulse_period = arg_7;
    amplitude = arg_8;
    quiet_time = arg_9;
    sample_width = arg_10;
    hold_time1 = arg_11;
    hold_voltage1 = arg_12;
    hold_time2 = arg_13;
    hold_voltage2 = arg_14;
    OVERSAMPLING = arg_15;
    setGain(gain);
    delay(100);
    DPASV(initial_potential, final_potential, increment_potential, pulse_width, pulse_period, amplitude, quiet_time, sample_width,hold_time1,hold_voltage1,hold_time2,hold_voltage2);
    delay(100);
    Serial.println("Done!");
    SPI.endTransaction();
    setVoltage(8192);
  }

  // DPV
  if (got_message && arg_1 == 3) {
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE1));
    digitalWriteFast(MUX1_LINE, HIGH);
    delayMicroseconds(5);
    gain = arg_2;
    initial_potential = arg_3;
    final_potential = arg_4;
    increment_potential = arg_5;
    pulse_width = arg_6;
    pulse_period = arg_7;
    amplitude = arg_8;
    quiet_time = arg_9;
    sample_width = arg_10;
    OVERSAMPLING = arg_11;
    setGain(gain);
    delay(100);
    DPV(initial_potential, final_potential, increment_potential, pulse_width, pulse_period, amplitude, quiet_time, sample_width);
    delay(100);
    Serial.println("Done!");
    SPI.endTransaction();
    setVoltage(8192);
  }

  // FSCV
  if (got_message && arg_1 == 4) {
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE1));
    digitalWriteFast(MUX1_LINE, HIGH); // Selects signal from MUX (ADG419) to be response (we're measuring response signal)
    delayMicroseconds(5);
    // CV(cv_lower_voltage_limit, cv_upper_voltage_limit, cv_number_of_segments);
    setGain(10000);
    cv_lower_voltage_limit = arg_2;
    cv_upper_voltage_limit = arg_3;
    cv_number_of_segments = arg_4;
    cv_sensitivity = arg_5;
    cv_sampling_rate = arg_6;
    cv_scan_rate = arg_7;
    v_step = arg_8;
    setGain(cv_sensitivity);
    delay(100);
    CV(cv_lower_voltage_limit,cv_upper_voltage_limit,cv_sampling_rate,cv_number_of_segments,cv_scan_rate,v_step);
    delay(100);
    Serial.println("Done!");
    SPI.endTransaction();
  } 

} // figure out what the different argument_1 values should be for if statements

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
    switch (iterator_count) {
      case 1:
        arg_1 = atof(str);
        break;
      case 2:
        arg_2 = atof(str);
        break;
      case 3:
        arg_3 = atof(str);
        break;
      case 4:
        arg_4 = atof(str);
        break;
      case 5:
        arg_5 = atof(str);
        break;
      case 6:
        arg_6 = atof(str);
        break;
      case 7:
        arg_7 = atof(str);
        break;
      case 8:
        arg_8 = atof(str);
        break;
      case 9:
        arg_9 = atof(str);
        break;
      case 10:
        arg_10 = atof(str);
        break;
      case 11:
        arg_11 = atof(str);
        break;
      case 12:
        arg_12 = atof(str);
        break;
      case 13:
        arg_13 = atof(str);
        break;
      case 14:
        arg_14 = atof(str);
        break;
      case 15:
        arg_15 = atof(str);
        break;
    }
  }
}

double voltageToBytes(float voltage) {
  return map(voltage, 0, 5, 0, pow(2, 14) - 1);
}

void setVoltage(int DacValue) {
  digitalWriteFast(DAC_CS, LOW);
  SPI.transfer16(DacValue);
  digitalWriteFast(DAC_CS, HIGH);
}

double calculateVoltage(float voltage) {
  return map(voltage, -2.5, 2.5, 0, pow(2, 14) - 1);
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

float measure(float pulse, float sample_width) {
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
          total = total + adc.read_value();
          how_many++;
          next_measurement_time += intervals;
        }
      }
    }
  }
  return total / how_many;
}
