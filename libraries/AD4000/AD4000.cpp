#include "AD4000.h"
#include "Arduino.h"
#include "SPI.h"
#include <cmath>

/*
USER GUIDE to start reading in potentials with this library:
1) Instantiate an AD4000 object, e.g: "AD4000 adc(2, 10);" would instantiate an ADC object named 
   "adc" with 2 MHz clock with ChipSelect on pin 10 
2) Set desired settings on this object, e.g: "adc.set_settings(false, false, false, true);" which would only enable turbo mode.
   See set_settings function below or datasheet to see boolean and setting correspondence
3) You're ready to read ADC values! Just use: "adc.read_value()" to read your values! :) Values return ADC code, you need to transform
   this into a potential according to: pot = V_REF * ADC_CODE / (2^16 - 1)

Remember to set your ChipSelect pin/(s) to output mode!
// WRITTEN 12/15/2022 - Hevar Djeza M.
*/

/*
    UPDATE 5/1/2023: Method to beginTransaction and endTransaction after each data transfer obsolete. This had enough overhead that it was
    bottlenecking our speed that we could run at. Therefore, the lines that did this are commented out (which makes the setting of clckspeed in
    the AD4000:AD4000 function useless, but I will keep it there if this functionality wants to be implemented again in the future). Remember,
    the beginTransaction and endTransaction with the desired settings has to, in the current state of this library, be set in the main program
    using this library.
    One idea, if needed, is to imeplement a "Get ready/not ready" functions here that begins a transaction with settings you pass to it
    and that gets called by main program before/after a measurement is about to be done.
*/

// Initialize - Initialize device (clockspeed in MHz)
AD4000::AD4000(int CSPIN){
    //clckspeed = clockspeed * 1000000;
    CS_PIN = CSPIN;
    // SPI.begin();
}

// Set parameter settings (eg. turbo mode, high Z mode, span compression, status bits)
void AD4000::set_settings(boolean statusBits, boolean spanCompression, boolean highZmode, boolean turboMode){
    // boolean chosenSettings[4] = {statusBits, spanCompression, highZmode, turboMode}; 
    byte settingByte = 0b00000000;
    if(statusBits){
        settingByte += 1 << 4;
        sBits = true;
    }
    if(spanCompression){
        settingByte += 1 << 3;
    }
    if(highZmode){
        settingByte += 1 << 2;
    }
    if(turboMode){
        settingByte += 1 << 1;
    }
    write_register(settingByte);
}

// Write to register
void AD4000::write_register(byte setting){
    SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
    CSON();
    SPI.transfer(WREG);
    SPI.transfer(setting);
    CSOFF();
    SPI.endTransaction();
}

// Read register
void AD4000::read_register(){
    SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
    CSON();
    SPI.transfer(RREG);
    byte returnValue = SPI.transfer(0b11111111);
    CSOFF();
    SPI.endTransaction();
    Serial.println("Current settings enabled:");
    for (int i=7; i>= 0; i--){
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

// OBS: This is the 3 wire turbo protocol. TODO: If turbo disabled, do other protocol (if needed)
uint16_t AD4000::read_value(){
    // SPI.beginTransaction(SPISettings(clckspeed, MSBFIRST, SPI_MODE1));
    CSON();
    SPI.transfer16(0xFFFF);
    CSOFF();
    CSON();
    uint16_t adcCode = SPI.transfer16(0xFFFF);
    CSOFF();
    // SPI.endTransaction();
    return adcCode;
}

// Chip select/unselect functions
void AD4000::CSON() {
    digitalWriteFast(CS_PIN, LOW);
}

void AD4000::CSOFF() {
    digitalWriteFast(CS_PIN, HIGH);
}

// #include "AD4000.h"
// #include "Arduino.h"
// #include "SPI.h"
// #include <cmath>

/*
USER GUIDE to start reading in potentials with this library:
1) Instantiate an AD4000 object, e.g: "AD4000 adc(2, 10);" would instantiate an ADC object named 
   "adc" with 2 MHz clock with ChipSelect on pin 10 
2) Set desired settings on this object, e.g: "adc.set_settings(false, false, false, true);" which would only enable turbo mode.
   See set_settings function below or datasheet to see boolean and setting correspondence
3) You're ready to read ADC values! Just use: "adc.read_value()" to read your values! :) Values return ADC code, you need to transform
   this into a potential according to: pot = V_REF * ADC_CODE / (2^16 - 1)

Remember to set your ChipSelect pin/(s) to output mode!
// WRITTEN 12/15/2022 - Hevar Djeza M.
*/

/*
    UPDATE 5/1/2023: Method to beginTransaction and endTransaction after each data transfer obsolete. This had enough overhead that it was
    bottlenecking our speed that we could run at. Therefore, the lines that did this are commented out (which makes the setting of clckspeed in
    the AD4000:AD4000 function useless, but I will keep it there if this functionality wants to be implemented again in the future). Remember,
    the beginTransaction and endTransaction with the desired settings has to, in the current state of this library, be set in the main program
    using this library.
    One idea, if needed, is to imeplement a "Get ready/not ready" functions here that begins a transaction with settings you pass to it
    and that gets called by main program before/after a measurement is about to be done.
 */

// Initialize - Initialize device (clockspeed in MHz)
// AD4000::AD4000(float clockspeed, int CSPIN){
//     clckspeed = clockspeed * 1000000;
//     CS_PIN = CSPIN;
//     SPI.begin();
// }

// // Set parameter settings (eg. turbo mode, high Z mode, span compression, status bits)
// void AD4000::set_settings(boolean statusBits, boolean spanCompression, boolean highZmode, boolean turboMode){
//     // boolean chosenSettings[4] = {statusBits, spanCompression, highZmode, turboMode}; 
//     byte settingByte = 0x0000;
//     if(statusBits){
//         settingByte += 1 << 4;
//         sBits = true;
//     }
//     if(spanCompression){
//         settingByte += 1 << 3;
//     }
//     if(highZmode){
//         settingByte += 1 << 2;
//     }
//     if(turboMode){
//         settingByte += 1 << 1;
//     }
//     write_register(settingByte);
// }

// // Write to register
// void AD4000::write_register(byte setting){
//     SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
//     CSON();
//     SPI.transfer(WREG);
//     SPI.transfer(setting);
//     CSOFF();
//     SPI.endTransaction();
// }

// // Read register
// void AD4000::read_register(){
//     SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
//     CSON();
//     SPI.transfer(RREG);
//     byte returnValue = SPI.transfer(0xFF);
//     CSOFF();
//     SPI.endTransaction();
//     Serial.println("Current settings enabled:");
//     for (int i=7; i>= 0; i--){
//         int currentBit = bitRead(returnValue, i);
//         if (i == 4 && currentBit == 1){
//             Serial.println("STATUS BITS");
//         }
//         if (i == 3 && currentBit == 1){
//             Serial.println("SPAN COMPRESSION");
//         }
//         if (i == 2 && currentBit == 1){
//             Serial.println("HIGH-Z");
//         }
//         if (i == 1 && currentBit == 1){
//             Serial.println("TURBO");
//         }      
//     }
// }

// // OBS: This is the 3 wire turbo protocol. TODO: If turbo disabled, do other protocol (if needed)
// uint16_t AD4000::read_value(){
//     uint16_t adcCode = 0;
    
//     // Assert CS to initiate communication
//     CSON();
    
//     // The delay for tEN (Enable Time) after asserting CS before starting the clock.
//     // Since tEN is very short, we may not need to explicitly account for it here due to the inherent delay of SPI.transfer() calls.
    
//     // Initiate the ADC conversion with a dummy write
//     SPI.transfer16(0xFFFF);
    
//     // De-assert CS to indicate end of conversion initiation
//     CSOFF();
    
//     // Delay for tQUIET1 or tQUIET2 as required here
//     // If using tQUIET1 (190 ms seems incorrect, probably should be 190 ns),
//     // you would use delayMicroseconds(1); // 1 microsecond is the smallest delay
//     delayNanoseconds(60); // Hypothetical function for tQUIET2, if timing resolution allows
    
//     // Re-assert CS to read the conversion result
//     CSON();
    
//     // Again, the delay for tEN after asserting CS before starting the clock.
    
//     // Read the conversion result
//     adcCode = SPI.transfer16(0xFFFF);
    
//     // De-assert CS after reading the value
//     CSOFF();
    
//     // The delay for tDIS (Disable Time) after de-asserting CS
//     delayNanoseconds(20); // Hypothetical function
    
//     return adcCode;
// }

// // Chip select/unselect functions
// void AD4000::CSON() {
//     digitalWriteFast(CS_PIN, LOW);
// }

// void AD4000::CSOFF() {
//     digitalWriteFast(CS_PIN, HIGH);
// }