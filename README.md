Hello, World!

## Setting up Arduino libraries
For starters, follow the instructions at the link below to set up the Arduino IDE and Teensyduino extension
Make sure to align your Teensyduino version and your Arduino IDE version. I'm rocking with the 1.8.x IDE and have had problems with the v2 in the past
Here's where to get those install instructions: https://www.pjrc.com/teensy/td_download.html

Mohammad attatched his entire set of Arduino libraries in the zip so I pared down the folder to just the dependencies used in the current project. We'll definitely need to add more for Bluetooth
In the Arduino IDE, hit File > Preferences to check where your library file is gonna be.
For me it was just Documents/Arduino in the menu and I already had a "libraries" folder in there (not sure if it's there by default, make one if not)
Then just copy in the "teensy_clock" and "AD4000" folders into that libraries folder

## Building Teensy Code
Open the .ino files under the arduino folder of the Potentiostat code
Select Tools > Boards > Teensyduino > Teensy 4.1
Hit "Verify" and it should build just fine!!!

