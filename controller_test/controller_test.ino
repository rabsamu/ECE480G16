#define HWSERIAL Serial1;

// Motor A connections
int enA = 9;
int in1 = 8;
int in2 = 7;
// Motor B connections
int enB = 3;
int in3 = 5;
int in4 = 4;


int state = 0;

void setup() {
  // Set all the motor control pins to outputs
  pinMode(enA, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  
  // Turn off motors - Initial state
  digitalWrite(enA, 0);
  digitalWrite(enB, 0);
  digitalWrite(in1, 1);
  digitalWrite(in2, 0);
  digitalWrite(in3, 0);
  digitalWrite(in4, 0);
}

void loop() {

  speedCycle();
  delay(2000);
//  switch(state) {
//    case 0:
//      if(HWSERIAL.Available()) {
//        speedControl(1, 80);
//        speedcontrol(2, 0);
//        case = 1;
//      }
//      break;
//    case 1:
//      if(HWSERIAL.Available()) {
//        speedControl(1, 0);
//        speedcontrol(2, 80);
//        case = 1;
//      }
//  }
//  delay(20);
}

void speedControl(int motor, int percent) {
  int scaledVal = percent / 100 * 255;
  if(motor == 1) {
    analogWrite(enA, scaledVal);
  } else {
    analogWrite(enB, scaledVal);
  }
}

void directionControl() {
  // Set motors to maximum speed
  // For PWM maximum possible values are 0 to 255
  analogWrite(enA, 255);
  analogWrite(enB, 255);

  // Turn on motor A & B
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  delay(2000);
  
  // Now change motor directions
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  delay(2000);
  
  // Turn off motors
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

// This function lets you control speed of the motors
void speedCycle() {
  
  // Accelerate from zero to maximum speed
  for (int i = 50; i < 100; i++) {
    speedControl(1, i);
    delay(50);
  }
  
  // Decelerate from maximum speed to zero
  for (int i = 100; i >= 50; --i) {
    speedControl(1, i);
    delay(50);
  }
}
