#define HWSERIAL Serial5
void ASV(float args[16]) {
  // Remove delays and prints for max speed
  float gain_val = args[1];
  float low_voltage = args[2];
  float high_voltage = args[3];
  int times_to_sample = (int) args[4];
  float hold_time1 = args[5];
  float hold_voltage1 = args[6];
  float hold_time2 = args[7];
  float hold_voltage2 = args[8];
  float sample_rate = args[9];
  
  float voltage_increment = 6.10389e-5;
  
  // Calculate the number of steps and time per step
  int total_steps = abs(high_voltage - low_voltage) / voltage_increment;
  unsigned long time_per_step = (unsigned long)(1000000.0 / (sample_rate * total_steps)); // Time per step in microseconds
  bool increment = true; // Flag to toggle between incrementing and decrementing

  openValve();
  setSolution(80);
  setBuffer(80);
  
  setVoltage(hold_voltage1);
  if (hold_time1 > 0) {
    if(waitSeconds(hold_time1)) return;
  }
  
  setVoltage(hold_voltage2);
  if (hold_time2 > 0) {
    if(waitSeconds(hold_time2)) return;
  }
  
  closeValve();
  if(waitSeconds(0.5)) return;
  setSolution(0);
  setBuffer(0);

  setVoltage(low_voltage);
  float current_voltage = low_voltage;
  if(waitSeconds(0.1)) return;
  while (current_voltage <= high_voltage) {
      unsigned long start_time = micros();
      setVoltage(current_voltage);
      int total = 0;

      for (int j = 0; j < times_to_sample; j++) {
          total += readCurrent(gain_val);
      }
      float avg_current = total / times_to_sample;
      
      Serial.print(current_voltage);
      Serial.print(',');
      Serial.println(avg_current);

      // Wait for the remaining time in the step
      while (micros() - start_time < time_per_step) if(HWSERIAL.available() > 0) return;
      current_voltage += voltage_increment;
  }
}
