
void CV(float args[16]) {
  for(int i = 1; i < 9; i++) {
    Serial.print("value: ");
    Serial.println(args[i]);
  }
  float gain_val = args[1];
  float low_voltage = args[2]; // 0.5V
  float high_voltage = args[3]; // 0.5V
  float increment_voltage = args[4]; // 0.1V
  int times_to_sample = (int) args[5]; // 100
  float sample_rate = args[6]; // 
//  float scan_rate = args[7];
  int segments = args[8];
  
  // Calculate the number of steps and time per step
  int voltage_increment_code = 1; // Use 1 or 2 based on feasibility
  int total_steps = abs(high_voltage - low_voltage) / increment_voltage;
  unsigned long time_per_step = (unsigned long)(1000000.0 / (sample_rate * total_steps)); // Time per step in microseconds
  bool increment = true; // Flag to toggle between incrementing and decrementing
  
  setVoltage(low_voltage);
  float current_voltage = low_voltage;
  delay(100);
  
  // Old code that get's enough solution through the system for demonstration, should probably be way shorter
//  openValve();
//  setSolution(75);
//  setBuffer(75);
//  if (waitSeconds(60)) return;
//
//  closeValve();
//  setSolution(0);
//  setBuffer(0);
  
  unsigned long run_time = micros();
  for (int i = 0; i < segments; i++) {

      while ((increment && current_voltage <= high_voltage) || 
            (!increment && current_voltage >= low_voltage)) {
          
          unsigned long start_time = micros();
          setVoltage(current_voltage);
          float total = 0;
          

          for (int j = 0; j < times_to_sample; j++) {
              float reading = readCurrent(gain_val);
              if(reading == 0xFFFFFFFF) return;
              total += reading;
          }

          float avg_current = total / times_to_sample;
          HWSERIAL.print(current_voltage);
          HWSERIAL.print(',');
          HWSERIAL.print(avg_current, 12);
          HWSERIAL.print("\n");
          Serial.print(current_voltage);
          Serial.print(',');
          Serial.print(avg_current, 12);
          Serial.print("\n");

          // Change voltage code based on the increment flag
          if (increment) {
              current_voltage += increment_voltage;
          } else {
              current_voltage -= increment_voltage;
          }
          if(HWSERIAL.available() > 0) {
              Serial.println("aborted");
              return;
            }

          // Wait for the remaining time in the step
          if ((increment && current_voltage < high_voltage) || (!increment && current_voltage > low_voltage)) {
            while (micros() - start_time < time_per_step) {
              if(HWSERIAL.available() > 0) {
                Serial.println("aborted");
                return;
              }
            }
          }
      }

      // Toggle the increment flag and decrement segments_left after each segment
      increment = !increment;
      
  }
}
