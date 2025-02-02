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

## Python
Not too sure about the Python. From the look of it, there is the top layer primary file "GUI_v1.0.py", plus two referenced json files, and the .ui (xml format) file.
My guess is that the .spec file is automatically read by the ui library when reading to the .ui file of the same name? 
I think the .autosave is probably not supposed to be there?

Things get hazy in the /src/Slow Scan... folder, which has nearly identical files as the top level. Think we can probably disregard all that since we are working on single-channel and I assume they want fast if it's single channel anyway. The changes don't seem that substantial, though...
Shouldn't need a /dist folder?
The build folder has cython compiled files, shouldn't need to use that? Maybe the ui lib requires it though. Should be git ignored, though.

Miscellaneous note, looks like one of those "other imporvements" he reference might be breaking apart the 2500 line main file