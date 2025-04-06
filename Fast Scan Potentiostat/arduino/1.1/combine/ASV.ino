
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

  setFilter(80);
  delay(10000);
  setFilter(0);

  openValve();
  setSolution(80);
  setBuffer(80);
  
  setVoltage(hold_voltage1);
  if (hold_time1 > 0) {
    Serial.println("Holding at pre-clean voltage");
    delay(hold_time1*1000);
  }
  
  setVoltage(hold_voltage2);
  if (hold_time2 > 0) {
    Serial.println("Holding at concentration voltage");
    delay(hold_time2 * 1000);
  }
  closeValve();
  delay(500);
  setSolution(0);
  setBuffer(0);

  setVoltage(low_voltage);
  float current_voltage = low_voltage;
  delay(100);
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
      while (micros() - start_time < time_per_step);
      current_voltage += voltage_increment;
  }

  openValve();
  setBuffer(80);
  delay(5000);
  setBuffer(0);
  delay(2000);
  closeValve();

}
