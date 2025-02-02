
#ifndef ADG715_h
#define ADG715_h

#if (ARDUINO >= 100)
	#include "Arduino.h"
#else
	#include "WProgram.h"
#endif

#include "Wire.h"	

#define BASE_KEY (0x48)

//I2C result success/fail
#define I2C_RESULT_SUCCESS       (0)
#define I2C_RESULT_DATA_TOO_LONG (1)
#define I2C_RESULT_ADDR_NAK      (2)
#define I2C_RESULT_DATA_NAK      (3)
#define I2C_RESULT_OTHER_FAIL    (4)
class ADG715
{
	public:
		static bool reset();		
		byte read(byte channel); //read all channels and return as a byte
		void all(boolean input);
		void writeChannel(uint8_t channel, byte state); //change status of a specified channel (0-7)
	private:
		byte _value; //shared value for all functions
		byte CH(int channel);
};
#endif