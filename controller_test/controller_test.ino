#define HWSERIAL Serial1

// Motor A connections
int enA = 9;
int in1 = 8;
int in2 = 7;
// Motor B connections
int enB = 3;
int in3 = 5;
int in4 = 4;

int directionA = 0;
int directionB = 0;


void setup() {
  // Set all the motor control pins to outputs
  pinMode(enA, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  
  // Set motors to forwrd - Initial state
  digitalWrite(enA, 0);
  digitalWrite(enB, 0);
  digitalWrite(in1, 1);
  digitalWrite(in2, 0);
  digitalWrite(in3, 1);
  digitalWrite(in4, 0);
}

void loop() {
  if(HWSERIAL.available()) {
    char msg = HWSERIAL.read();
    switch(msg) {
      case '1':
        gotoState1();
        break;
      case '2':
        gotoState2();
        break;
      case '3':
        gotoState3();
        break;
      case '4':
        toggleDirection(1);
        toggleDirection(2);
        break;
    }
  }
  delay(10);
}

void gotoState1() {
  speedControl(1, 80);
  speedControl(2, 0);
}

void gotoState2() {
  speedControl(1, 0);
  speedControl(2, 80);
}

void gotoState3() {
  speedControl(1, 0);
  speedControl(2, 0);
}

void speedControl(int motor, int percent) {
  int scaledVal = percent / 100 * 255;
  if(motor == 1) {
    analogWrite(enA, scaledVal);
  } else {
    analogWrite(enB, scaledVal);
  }
}

void setDirection(int motor, int dir) {
  if (motor== 1) {
    directionA = dir;
    digitalWrite(in1, directionA);
    digitalWrite(in2, 1-directionA);
  } else {
    directionB = dir;
    digitalWrite(in3, directionB);
    digitalWrite(in4, 1-directionB);
  }
}

void toggleDirection(int motor) {
  if (motor == 1) {
    directionA = 1 - directionA;
    digitalWrite(in1, directionA);
    digitalWrite(in2, 1-directionA);
  } else {
    directionB = 1 - directionB;
    digitalWrite(in3, directionB);
    digitalWrite(in4, 1-directionB);
  }
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
