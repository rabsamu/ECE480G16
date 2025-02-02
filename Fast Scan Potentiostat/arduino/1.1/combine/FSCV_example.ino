
void CV(float low_voltage, float high_voltage, int times_to_sample, int segments, float sample_rate, float v_step) 
{
  // Convert voltages to DAC codes
  uint16_t low_voltage_code = (uint16_t)((low_voltage / 2.5 + 1) * 8191.5);
  uint16_t high_voltage_code = (uint16_t)((high_voltage / 2.5 + 1) * 8191.5);
  uint16_t current_voltage_code = low_voltage_code;
  // Calculate the number of steps and time per step
  // v_step = (v_step > 0.05) ? 0.05 : v_step;
  // uint16_t voltage_increment_code = (uint16_t) map(v_step, 0, 5, 0, pow(2,14));
  uint16_t voltage_increment_code = 1; // Use 1 or 2 based on feasibility
  uint16_t total_steps = abs(high_voltage_code - low_voltage_code) / voltage_increment_code;
  unsigned long time_per_step = (unsigned long)(1000000.0 / (sample_rate * total_steps)); // Time per step in microseconds
  bool increment = true; // Flag to toggle between incrementing and decrementing
  setVoltage(current_voltage_code);
  adc.read_value();
  delay(100);
  unsigned long run_time = micros();
  for (int i = 0; i < segments; i++) {

      while ((increment && current_voltage_code <= high_voltage_code) || 
            (!increment && current_voltage_code >= low_voltage_code)) {
          
          unsigned long start_time = micros();
          setVoltage(current_voltage_code);
          // delayMicroseconds(5);
          uint32_t total = 0;

          for (int j = 0; j < times_to_sample; j++) {
              total += adc.read_value();
          }

          uint16_t measured_value = total / times_to_sample;
          Serial.print(current_voltage_code);
          Serial.print(',');
          Serial.print(measured_value);
          Serial.print(',');
          Serial.println(micros()-run_time);

          // Change voltage code based on the increment flag
          if (increment) {
              current_voltage_code += voltage_increment_code;
          } else {
              current_voltage_code -= voltage_increment_code;
          }

          // Wait for the remaining time in the step
          if ((increment && current_voltage_code < high_voltage_code) || 
            (!increment && current_voltage_code > low_voltage_code)){
          while (micros() - start_time < time_per_step);
            }
      }

      // Toggle the increment flag and decrement segments_left after each segment
      increment = !increment;
  }

}


