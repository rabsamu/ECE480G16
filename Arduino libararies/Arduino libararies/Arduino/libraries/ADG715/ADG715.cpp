#include "ADG715.h"
//LOOK INTO ARDUINO bitWrite, bitRead, bitClear, bitSet

//return status as a byte of all channel (1-8)
byte ADG715::read(byte channel) //if channel exceeds 9, read all
{
	channel = 0x00;
	byte value = 255; //error possibly?
	Wire.requestFrom(BASE_KEY, 0x01); //request one byte from address
	while(Wire.available())
	{
		value = Wire.read(); //grab one byte
	}
	if(channel < 9) //1-8 
	{
		value = bitRead(value, channel);
	}
	return value; //return all	
};

void ADG715::all(boolean input) //255 for on, 0 for off
{
	byte output = 0x00;
	if(input)
		output = 0xFF;
	Wire.beginTransmission(BASE_KEY);
	Wire.write(output);
	Wire.endTransmission();		
};

//change status of a specified channel (1-8)
void ADG715::writeChannel(byte channel, byte state)
{
	byte value;
	value = read(9); //read all channels
	bitWrite(value, channel, state);
	Wire.beginTransmission(BASE_KEY);
	Wire.write(value);
	Wire.endTransmission();	
};

bool ADG715::reset() {
    Wire.beginTransmission(BASE_KEY);
    Wire.write(0x00); //clear out register
    // Wire.endTransmission();
	    // Check that transmission completed successfully
    if (byte res = Wire.endTransmission() != I2C_RESULT_SUCCESS) {
        return false;
    } else {
        return true;
    }
};