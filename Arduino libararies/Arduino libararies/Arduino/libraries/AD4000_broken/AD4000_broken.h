// AD4000.h
#ifndef AD4000_H
#define AD4000_H

#include <Arduino.h>
#include <SPI.h>

class AD4000 {
public:
    explicit AD4000(uint8_t cs_pin);
    void begin();
    uint16_t readData();
    void writeRegister(uint8_t reg, uint16_t value);
    void read_register();
    void startConversion();
    void waitForDataReady();

private:
    uint8_t _cs_pin;
    static const uint32_t SPI_CLOCK = 70000000; // 70 MHz, the max speed for AD4000 in turbo mode
    static const uint16_t READ_COMMAND = 0b11010000; // This combines WEN, R/W as read, and the address.
    static const uint16_t WRITE_COMMAND = 0b01010000; // This combines WEN, R/W, and the address.
    static const uint8_t DUMMY_BYTE = 0x00;
    
    // Timing constants
    static const unsigned int T_CONV = 1; // Conversion time in microseconds
    static const unsigned int T_QUIET1 = 1; // Delay after CNV goes high before the next command
    static const unsigned int T_QUIET2 = 1; // Delay after reading data before CNV goes high

    void sendCommand(uint16_t cmd);
    uint16_t transfer16(uint16_t data);
};

#endif // AD4000_H