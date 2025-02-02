#ifndef AD4000_h
#define AD4000_h

// AD4000 Register

// AD4000 Command
#define RREG 0b01010100
#define WREG 0b00010100

#include "Arduino.h"
#include "SPI.h"

class AD4000 {
 public:
  // Functions defined in cpp
  AD4000(int CSPIN);
  void set_settings(boolean statusBits, boolean spanCompression, boolean highZmode, boolean turboMode);
  void read_register();
  void write_register(byte setting);
  uint16_t read_value();
  void CSON();
  void CSOFF();

 private:
  // private variables/functions
  boolean sBits;
  int clckspeed;
  int CS_PIN;
};


#endif