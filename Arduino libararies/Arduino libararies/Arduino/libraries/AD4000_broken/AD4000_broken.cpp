// AD4000.cpp
#include "AD4000.h"

AD4000::AD4000(uint8_t cs_pin) : _cs_pin(cs_pin) {}

void AD4000::begin() {
    pinMode(_cs_pin, OUTPUT);
    digitalWrite(_cs_pin, HIGH);
    SPI.begin();
}

uint16_t AD4000::readData() {
    delayMicroseconds(T_QUIET1); // Wait the required time after conversion, rounded up to the nearest microsecond
    digitalWrite(_cs_pin, LOW);
    SPI.beginTransaction(SPISettings(SPI_CLOCK, MSBFIRST, SPI_MODE1));
    uint16_t result = SPI.transfer16(READ_COMMAND);
    delayMicroseconds(T_QUIET2); // Ensure we respect the quiet time before bringing CS high, rounded up to the nearest microsecond
    digitalWrite(_cs_pin, HIGH);
    SPI.endTransaction();
    return result;
}

void AD4000::writeRegister(uint8_t reg, uint16_t value) {
    uint16_t cmd = WRITE_COMMAND | (reg << 1);
    sendCommand(cmd);
    transfer16(value);
}

void AD4000::read_register(){
    uint16_t returnValue = readData(); // Reads the conversion result and the status bits if enabled
    Serial.println("Current settings enabled:");
    for (int i = 7; i >= 0; i--){
        int currentBit = bitRead(returnValue, i);
        if (i == 4 && currentBit == 1){
            Serial.println("STATUS BITS");
        }
        if (i == 3 && currentBit == 1){
            Serial.println("SPAN COMPRESSION");
        }
        if (i == 2 && currentBit == 1){
            Serial.println("HIGH-Z");
        }
        if (i == 1 && currentBit == 1){
            Serial.println("TURBO");
        }      
    }
}
void AD4000::startConversion() {
    digitalWrite(_cs_pin, LOW); // CNV low
    delayMicroseconds(T_QUIET1); // Short delay
    digitalWrite(_cs_pin, HIGH); // CNV high signals the start of conversion
    delayMicroseconds(T_CONV); // Wait for conversion to complete
}

void AD4000::waitForDataReady() {
    // Poll the status bit or use a timing delay as per the datasheet specifications
    // This is a placeholder for the actual data ready checking mechanism
    delayMicroseconds(2); // Replace with actual timing requirement
}

void AD4000::sendCommand(uint16_t cmd) {
    digitalWrite(_cs_pin, LOW);
    SPI.beginTransaction(SPISettings(SPI_CLOCK, MSBFIRST, SPI_MODE0));
    SPI.transfer16(cmd);
    digitalWrite(_cs_pin, HIGH);
    SPI.endTransaction();
}

uint16_t AD4000::transfer16(uint16_t data) {
    digitalWrite(_cs_pin, LOW);
    SPI.beginTransaction(SPISettings(SPI_CLOCK, MSBFIRST, SPI_MODE0));
    uint16_t result = SPI.transfer16(data);
    digitalWrite(_cs_pin, HIGH);
    SPI.endTransaction();
    return result;
}