
void ASV(float low_voltage, float high_voltage, int times_to_sample, float sample_rate, int holding_time,  float holding_voltage, int holding_time2, float holding_voltage2) {
  // Remove delays and prints for max speed
  uint16_t low_voltage_code = (uint16_t)((low_voltage / 2.5 + 1) * 8191.5);
  uint16_t high_voltage_code = (uint16_t)((high_voltage / 2.5 + 1) * 8191.5);
  uint16_t voltage_increment_code = 1;
  uint16_t current_voltage_code = low_voltage_code;
  uint16_t current_raw_voltage = 0;
  holding_voltage = ((holding_voltage / 2.5) + 1) * 8192;
  holding_voltage2 = ((holding_voltage2 / 2.5) + 1) * 8192;
  // Calculate the number of steps and time per step
  uint16_t total_steps = abs(high_voltage_code - low_voltage_code) / voltage_increment_code;
  unsigned long time_per_step = (unsigned long)(1000000.0 / (sample_rate * total_steps)); // Time per step in microseconds
  bool increment = true; // Flag to toggle between incrementing and decrementing
  setVoltage(int(round(holding_voltage)));
  if (holding_time > 0) 
  {
    Serial.println("Holding at pre-clean voltage");
    delay(holding_time*1000);
  }
  setVoltage(int(round(holding_voltage2)));
  if (holding_time2 > 0) 
  {
    Serial.println("Holding at concentration voltage");
    delay(holding_time2 * 1000);
  }
  setVoltage(current_voltage_code);
  adc.read_value();
  delay(100);
    while (current_voltage_code <= high_voltage_code){
      //Serial.println("good");
        unsigned long start_time = micros();
        setVoltage(current_voltage_code);
        uint32_t total = 0;

        for (int j = 0; j < times_to_sample; j++) {
            total += adc.read_value();
        }

        uint16_t measured_value = total / times_to_sample;
        Serial.print(current_voltage_code);
        Serial.print(',');
        Serial.println(measured_value);

        current_voltage_code += voltage_increment_code;

        // Wait for the remaining time in the step
        while (micros() - start_time < time_per_step);
    }

} // *
