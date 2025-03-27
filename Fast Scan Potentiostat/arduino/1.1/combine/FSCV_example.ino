
void CV(float args[16]) {
  float gain_val = args[1];
  float low_voltage = args[2];
  float high_voltage = args[3];
  float increment_voltage = args[4];
  int times_to_sample = (int) args[5];
  float sample_rate = args[6];
  float scan_rate = args[7];
  int segments = args[8];
  
  // Calculate the number of steps and time per step
  int voltage_increment_code = 1; // Use 1 or 2 based on feasibility
  int total_steps = abs(high_voltage - low_voltage) / increment_voltage;
  unsigned long time_per_step = (unsigned long)(1000000.0 / (sample_rate * total_steps)); // Time per step in microseconds
  bool increment = true; // Flag to toggle between incrementing and decrementing
  
  setVoltage(low_voltage);
  float current_voltage = low_voltage;
  delay(100);
  unsigned long run_time = micros();
  for (int i = 0; i < segments; i++) {

      while ((increment && current_voltage <= high_voltage) || 
            (!increment && current_voltage >= low_voltage)) {
          
          unsigned long start_time = micros();
          setVoltage(current_voltage);
          uint32_t total = 0;

          for (int j = 0; j < times_to_sample; j++) {
              total += readCurrent(gain_val);
          }

          uint16_t avg_current = total / times_to_sample;
          Serial.print(current_voltage);
          Serial.print(',');
          Serial.print(avg_current);
          Serial.print(',');
          Serial.println(micros()-run_time);

          // Change voltage code based on the increment flag
          if (increment) {
              current_voltage += increment_voltage;
          } else {
              current_voltage -= increment_voltage;
          }

          // Wait for the remaining time in the step
          if ((increment && current_voltage < high_voltage) || (!increment && current_voltage > low_voltage)) {
            while (micros() - start_time < time_per_step);
          }
      }

      // Toggle the increment flag and decrement segments_left after each segment
      increment = !increment;
  }

}
