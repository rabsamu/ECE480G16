/*
Simple library for driving Analog Devices AD5683/R digital to analog converter.

 Name:		AD5683.h
 Created:	5/2/2018 4:16:22 PM
 Author:	Alek Krol adi@adigital.eu
 Editor:	http://www.visualmicro.com
*/

#ifndef _AD5683_h
#define _AD5683_h

#if defined(ARDUINO) && ARDUINO >= 100
#include "arduino.h"
#else
#include "WProgram.h"
#endif
#include <SPI.h>


/*
#define CMD_DO_NOTHING                  0b0000	
#define CMD_WRITE_TO_INPUT_REG          0b0001	
#define CMD_UPDATE_DAC_WITH_INPUT_REG   0b0010  //software LDAC
#define CMD_WRITE_AND_INPUT_REGISTER    0b0011
#define CMD_WRITE_CONTROL_REGISTER      0b0100
#define CMD_READBACK_INPUT_REGISTER     0b0101
*/

#define AD5683_FAILURE           		-1
#define CMD_DO_NOTHING           		0x0 // No operation.
#define CMD_WRITE_TO_INPUT_REG     		0x1 // Write Input Register.
#define CMD_UPDATE_DAC_WITH_INPUT_REG 	0x2 // Update DAC Register.
#define CMD_WRITE_AND_INPUT_REGISTER	0x3 // Write DAC and Input Register.
#define CMD_WRITE_CONTROL_REGISTER		0x4 // Write Control Register.
#define CMD_READBACK_INPUT_REGISTER     0x5 // Readback input register.

/*************************** Write Control Register Bits **********************/
#define AD5683_DCEN(x)     (((((x) & 0x1) << 0) << 10) & 0xFC00)
#define AD5683_CFG_GAIN(x) (((((x) & 0x1) << 1) << 10) & 0xFC00)
#define AD5683_REF_EN(x)   (((((x) & 0x1) << 2) << 10) & 0xFC00)
#define AD5683_OP_MOD(x)   (((((x) & 0x3) << 3) << 10) & 0xFC00)
#define AD5683_SW_RESET(x) (((((x) & 0x1) << 5) << 10) & 0xFC00)

/******************************************************************************/
/**************************** Variable Declarations ***************************/
/******************************************************************************/
struct ad5683_device {
	int slave_select_id;
	uint32_t dac_reg_value;
};

enum ad5683_state {
	AD5683_DC_DISABLE,
	AD5683_DC_ENABLE
};

enum ad5683_voltage_ref {
	AD5683_INT_REF_ON,
	AD5683_INT_REF_OFF
};

enum ad5683_amp_gain {
	AD5683_AMP_GAIN_1,
	AD5683_AMP_GAIN_2
};

enum ad5683_power_mode {
	AD5683_PWR_NORMAL,
	AD5683_PD_1K,
	AD5683_PD_100K,
	AD5683_PD_3STATE
};

enum ad5683_reset {
	AD5683_RESET_DISABLE,
	AD5683_RESET_ENABLE
};

// #define INTERNAL                            0
// #define EXTERNAL                            1

class AD5683 {
public:
    AD5683();
    AD5683(SPISettings spiConf, uint8_t CSpin);
    AD5683(SPISettings spiConf, uint8_t CSpin, uint8_t ResetPin);
    void SetVoltage(uint16_t vOut);
    //void SetReference(uint8_t source);
    void SoftReset();
    void SetGain(uint8_t gain_mode);
	void externalReference();
	void HardReset();
	    //void PowerDown(uint8_t operatingModeA, uint8_t operatingModeB); //0-normal, 1-1kOhm to ground, 2-100kOHm to ground, 3-three-state
private:
    SPISettings _spiConf;
    uint8_t		_CSpin;
    uint8_t		_ResetPin;
    bool        usesHardwareReset = false;
};

#endif

