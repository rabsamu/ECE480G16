/*
Name:		AD5683.cpp
Created:	5/2/2018 9:45:56 AM
Author:	adi
Editor:	http://www.visualmicro.com
*/

#include "AD5683.h"

AD5683::AD5683() {}

AD5683::AD5683(SPISettings spiConf, uint8_t CSpin) {
    _spiConf = spiConf;
    _CSpin = CSpin;
    pinMode(_CSpin, OUTPUT);
    SPI.begin();
}

AD5683::AD5683(SPISettings spiConf, uint8_t CSpin, uint8_t ResetPin)
    :AD5683(spiConf, CSpin) {
    usesHardwareReset = true;
    _ResetPin = ResetPin;
    pinMode(_ResetPin, OUTPUT);
}


void AD5683::SetVoltage(uint16_t vOut) {
	SPI.beginTransaction(_spiConf);
    digitalWrite(_CSpin, LOW);
  	uint8_t buf[3];
		buf[2] = ((vOut << 4) & 0xF0);
		buf[1] = (vOut >> 4);
		buf[0] = (vOut >> 12) | (CMD_WRITE_AND_INPUT_REGISTER << 4);
	SPI.transfer(buf,3);
	delayMicroseconds(1);
	digitalWrite(_CSpin, HIGH);
    SPI.endTransaction();
	//Serial.println("Set voltage here");
}

/*
void AD5683::SetReference(uint8_t source) {
    SPI.beginTransaction(_spiConf);
    digitalWrite(_CSpin, LOW);
    SPI.transfer(CMD_REFERENCE_SOURCE << 4);
    SPI.transfer(0);
    SPI.transfer(source);
    digitalWrite(_CSpin, HIGH);
    SPI.endTransaction();
}
*/

void AD5683::SoftReset() {
    SPI.beginTransaction(_spiConf);
    digitalWrite(_CSpin, LOW);
	uint8_t buf[3];
		buf[2] = ((AD5683_SW_RESET(AD5683_RESET_ENABLE) << 4) & 0xF0);
		buf[1] = (AD5683_SW_RESET(AD5683_RESET_ENABLE) >> 4);
		buf[0] = (AD5683_SW_RESET(AD5683_RESET_ENABLE) >> 12) | (CMD_WRITE_CONTROL_REGISTER << 4);
	SPI.transfer(buf,3);
	delayMicroseconds(1);
    digitalWrite(_CSpin, HIGH);
    SPI.endTransaction();
	//Serial.println("Soft Reset here");
}

void AD5683::SetGain(uint8_t gain_mode) {
    SPI.beginTransaction(_spiConf);
    digitalWrite(_CSpin, LOW);
    if(gain_mode=1){
	uint8_t buf[3];
		buf[2] = ((AD5683_CFG_GAIN(AD5683_AMP_GAIN_2) << 4) & 0xF0);
		buf[1] = (AD5683_CFG_GAIN(AD5683_AMP_GAIN_2) >> 4);
		buf[0] = (AD5683_CFG_GAIN(AD5683_AMP_GAIN_2) >> 12) | (CMD_WRITE_CONTROL_REGISTER << 4);
	SPI.transfer(buf,3);
	delayMicroseconds(1);
	}else{
	uint8_t buf[3];
		buf[2] = ((AD5683_CFG_GAIN(AD5683_AMP_GAIN_1) << 4) & 0xF0);
		buf[1] = (AD5683_CFG_GAIN(AD5683_AMP_GAIN_1) >> 4);
		buf[0] = (AD5683_CFG_GAIN(AD5683_AMP_GAIN_1) >> 12) | (CMD_WRITE_CONTROL_REGISTER << 4);
	SPI.transfer(buf,3);
	delayMicroseconds(1);
	}
    digitalWrite(_CSpin, HIGH);
    SPI.endTransaction();
	//Serial.println("gain here");
}

void AD5683::externalReference() {
    SPI.beginTransaction(_spiConf);
    digitalWrite(_CSpin, LOW);
	uint8_t buf[3];
		buf[2] = ((AD5683_REF_EN(AD5683_INT_REF_OFF) << 4) & 0xF0);
		buf[1] = (AD5683_REF_EN(AD5683_INT_REF_OFF) >> 4);
		buf[0] = (AD5683_REF_EN(AD5683_INT_REF_OFF) >> 12) | (CMD_WRITE_CONTROL_REGISTER << 4);
	SPI.transfer(buf,3);
	delayMicroseconds(1);
    digitalWrite(_CSpin, HIGH);
    SPI.endTransaction();
	//Serial.println("Soft Reset here");
}


void AD5683::HardReset() {
    if (usesHardwareReset) {
        digitalWrite(_ResetPin, LOW);
        delayMicroseconds(1);   //minimum reset pulse width time is 30ns
        digitalWrite(_ResetPin, HIGH);
    }
}
