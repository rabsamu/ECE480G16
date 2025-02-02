// void DPASV(
//   float initialE, float finalE, float incramentE, float pulse_width, float pulse_period, float amplitude, float quiet_time, float sample_width,
//   float holding_time, float holding_voltage, float holding_time2, float holding_voltage2) 
//   {
//   float initial_potential = ((initialE / 2.5) + 1) * 8192;
//   float final_potential = ((finalE / 2.5) + 1) * 8192;
//   holding_voltage = ((holding_voltage / 2.5) + 1) * 8192;
//   holding_voltage2 = ((holding_voltage2 / 2.5) + 1) * 8192;
//   delay(quiet_time * 1000);
//   float incrament_potential = voltageToBytes(incramentE);
//   float raw_amplitude = voltageToBytes(amplitude);
//   setVoltage(int(round(holding_voltage)));
//   delay(holding_time*1000);
//   setVoltage(int(round(holding_voltage2)));
//   delay(holding_time2 * 1000);
//   Serial.println("hold");
//   delay(100);
//   setVoltage(int(round(initial_potential)));
//   adc.read_value();
//   int incraments = floor((final_potential - initial_potential) / incrament_potential);
//   float newE = initial_potential;
//   float base_voltage = initial_potential;
//   float i1;
//   float i2;
//   sample_width = sample_width;  // now in milliseconds
//   for (int i = 0; i < incraments; i++) {
//     newE = int(round(newE + raw_amplitude));
//     setVoltage(newE);
    
//     base_voltage = newE;
    
//     i1 = measure(pulse_width, sample_width);
//     // delay(pulse_width);
//     // i1 = adc.read_value();
    
//     newE = int(round(newE - (raw_amplitude - incrament_potential)));
    
//     // Serial.print(newE);
//     // Serial.print(",");
    
//     setVoltage(newE);
//     //measure with new voltage
//     // delay(pulse_period);
//     // i2 = adc.read_value();
//     i2 = measure(pulse_period, sample_width);
//     // Serial.print(base_voltage);
//     Serial.print(newE);
//     Serial.print(",");
//     Serial.print(i1);
//     Serial.print(',');
//     Serial.println(i2);
//   }
// }

void DPASV(
  float initialE, float finalE, float incramentE, float pulse_width, float pulse_period, float amplitude, float quiet_time, float sample_width,
  float holding_time, float holding_voltage, float holding_time2, float holding_voltage2) 
  {
  float initial_potential = ((initialE / 2.5) + 1) * 8192;
  float final_potential = ((finalE / 2.5) + 1) * 8192;
  holding_voltage = ((holding_voltage / 2.5) + 1) * 8192;
  holding_voltage2 = ((holding_voltage2 / 2.5) + 1) * 8192;
  delay(quiet_time * 1000);
  float holding_time1_ms = 1000 * holding_time;
  float holding_time2_ms = 1000 * holding_time2;
  float current = 0;
  Serial.println("Hold1");
  setVoltage(int(round(holding_voltage)));
  for (int i = 0; i < holding_time1_ms; i += 100)
  {
    delay(100);
    current = adc.read_value();
    current = adc.read_value();
    Serial.print(i);
    Serial.print(",");
    Serial.println(current);
  }
  delay(100);
  Serial.println("Hold2");
  setVoltage(int(round(holding_voltage2)));
  for (int i = 0; i < holding_time2_ms; i += 100)
  {
    delay(100);
    current = adc.read_value();
    Serial.print(i);
    Serial.print(",");
    Serial.println(current);
  }
  delay(100);

  float incrament_potential = voltageToBytes(incramentE);
  float raw_amplitude = voltageToBytes(amplitude);
  // setVoltage(int(round(holding_voltage)));
  // delay(holding_time*1000);
  // setVoltage(int(round(holding_voltage2)));
  // delay(holding_time2 * 1000);
  Serial.println("hold");
  delay(100);
  setVoltage(int(round(initial_potential)));
  adc.read_value();
  int incraments = floor((final_potential - initial_potential) / incrament_potential);
  float newE = initial_potential;
  float base_voltage = initial_potential;
  float i1;
  float i2;
  sample_width = sample_width;  // now in milliseconds
  for (int i = 0; i < incraments; i++) {
    newE = int(round(newE + raw_amplitude));
    setVoltage(newE);
    
    base_voltage = newE;
    
    i1 = measure(pulse_width, sample_width);
    // delay(pulse_width);
    // i1 = adc.read_value();
    
    newE = int(round(newE - (raw_amplitude - incrament_potential)));
    
    // Serial.print(newE);
    // Serial.print(",");
    
    setVoltage(newE);
    //measure with new voltage
    // delay(pulse_period);
    // i2 = adc.read_value();
    i2 = measure(pulse_period, sample_width);
    // Serial.print(base_voltage);
    Serial.print(newE);
    Serial.print(",");
    Serial.print(i1);
    Serial.print(',');
    Serial.println(i2);
  }
}
