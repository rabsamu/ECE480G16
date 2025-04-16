void DPV(float args[16]) {
  float gain_val = args[1];
  float low_voltage = args[2];
  float high_voltage = args[3];
  float increment_voltage = args[4];
  float pulse_width = args[5];
  float pulse_period = args[6];
  float pulse_voltage = args[7];
  float sample_width = args[8];
  float hold_time1 = args[9];
  float hold_voltage1 = args[10];
  float hold_time2 = args[11];
  float hold_voltage2 = args[12];
  int oversampling = (int) args[13];
    
  int num_increments = floor((high_voltage - low_voltage) / increment_voltage);

  float current = 0;
  
  setVoltage(hold_voltage1);
  if (hold_time1 > 0) {
    if(waitSeconds(hold_time1)) return;
  }
  
  setVoltage(hold_voltage2);
  if (hold_time2 > 0) {
    if(waitSeconds(hold_time2)) return;
  }
  
  delay(100);
  setVoltage(low_voltage);
  float current_voltage = low_voltage;
  float i1;
  float i2;
  for (int i = 0; i < num_increments; i++) {
    current_voltage = current_voltage + pulse_voltage;
    setVoltage(current_voltage);
    
    i1 = measureCurrent(pulse_width, sample_width, gain_val);
    
    current_voltage = current_voltage - pulse_voltage + increment_voltage;
    setVoltage(current_voltage);
    //measure with new voltage
    i2 = measureCurrent(pulse_period, sample_width, gain_val);
    
    Serial.print(current_voltage);
    Serial.print(",");
    Serial.print(i1);
    Serial.print(',');
    Serial.println(i2);
  }
}
