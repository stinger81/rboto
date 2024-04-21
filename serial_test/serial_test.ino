#include <A4988.h>
#include <BasicStepperDriver.h>
#include <Adafruit_MotorShield.h>
#include <SparkFun_TB6612.h>

// #include <MotorDriver.h>


int right_track_speed;
int left_track_speed;
int _left_dir;
int _right_dir;

int cannon_move = 0;
int up_down_pos = 0;
int arm_val = 0;
int fire_val = 0;
String buf;
String temp;

// direction Correction factors
const int _dir_cor_right_arm = 1;
const int _dir_cor_left_arm = 1;
const int _dir_cor_cannon = 1;

// silinoid 

const int arm_pin = 8;
const int fire_pin = 9;

// DC MOTORS STEUP
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
Adafruit_DCMotor  *leftMotor = AFMS.getMotor(2);
Adafruit_DCMotor  *rightMotor = AFMS.getMotor(4);

// STEPPER MOTOR SETUP
const int left_arm_dir = 7;
const int left_arm_step = 6;
const int right_arm_dir = 4;
const int right_arm_step = 5;
const int cannon_dir = 2;
const int cannon_step = 3;

const int STEPS = 200;
const int MY_RPM = 200;
const int MY_MICROSTEP = 1;

A4988 leftArmStepper(STEPS, left_arm_dir, left_arm_step);
A4988 rightArmStepper(STEPS, right_arm_dir, right_arm_step);
A4988 cannonStepper(STEPS, cannon_dir, cannon_step);

// DATA INTERFACE

const int JOY_SIZE = 1000; // Must match the size in the python files (serial_interface.py)
// The above is there to get rid of decimals in the data transfer which makes coding this so much easier
// unless we want to go to true bytes which may be harder to manage for inexperienced programmers
//
// Packet types
// D (Rx) - General Data for control of the vehicle
// S (Rx) - Stop Frame Halt All Movement
// R (Rx) - incoming request for telemetry
// T (Tx) - Telemetry From Rboto

// data type note "" = String | '' = char

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  AFMS.begin();
  leftArmStepper.begin(MY_RPM, MY_MICROSTEP);
  rightArmStepper.begin(MY_RPM, MY_MICROSTEP);
  cannonStepper.begin(MY_RPM, MY_MICROSTEP);
  pinMode(arm_pin, OUTPUT);
  pinMode(fire_pin, OUTPUT);

}

void loop() {
  read_incoming();
  cannonStepper.move(cannon_move);
  drive();
  updown();
  arm();
  fire();

  // cannonStepper.move(100);

  // delay(1000);

  // cannonStepper.move(-100);
  // delay(1000);

  

  // cannonStepper.





}

void read_incoming(){
  // read incoming in the order they are recived
  if(Serial.available() > 0){
    buf = Serial.readStrincannontil('\n');
    if (buf[0] == 'D'){ // Check if incoming packet is data
      decode_data_packet();
      // send_state();
    }else if (buf[0] == 'S'){ // Check if incoming data is a stop/halt packet
      decode_stop_packet();
    }else if (buf[0] == 'R'){ // Check if incoming data is a request for telemetry
      send_state();
    }

  }
}

void drive(){
  // left_track_speed = -left_track_speed;
  // right_track_speed = -right_track_speed;
  if (right_track_speed > 0){
    _right_dir = FORWARD;
    rightMotor->setSpeed(right_track_speed);
  } else if (right_track_speed < 0){
    _right_dir = BACKWARD;
    rightMotor->setSpeed(-right_track_speed);
  } else {
    _right_dir = RELEASE;
  }

  if (left_track_speed > 0){
    _left_dir = FORWARD;
    leftMotor->setSpeed(left_track_speed);
  } else if (left_track_speed < 0){
    _left_dir = BACKWARD;
    leftMotor->setSpeed(-left_track_speed);
  } else {
    _left_dir = RELEASE;
  }

  rightMotor->run(_right_dir);
  leftMotor->run(_left_dir);
}

void updown(){
  leftArmStepper.move(-up_down_pos);
  rightArmStepper.move(up_down_pos);
}

void arm(){
  if (arm_val == 1){
    digitalWrite(arm_pin, HIGH);
  } else {
    digitalWrite(arm_pin, LOW);
  }
}

void fire(){
  if (fire_val == 1){
    digitalWrite(fire_pin, HIGH);
  } else {
    digitalWrite(fire_pin, LOW);   
  }
}


void decode_data_packet(){

  left_track_speed = buf.substring(2,6).toInt() - 255; // get substring between 2 and up to but not icnluding 6 
  right_track_speed = buf.substring(7,11).toInt() - 255;
  up_down_pos = buf.substring(12,16).toInt() - 255;
  cannon_move = buf.substring(17,21).toInt() - 255;
  arm_val = buf.substring(22, 26).toInt();
  fire_val = buf.substring(27,31).toInt();
  stepper_state = buf.substring(32,36).toInt();

}

void decode_stop_packet(){
  left_track_speed = 0; 
  right_track_speed = 0;
  
}

void send_state(){
  Serial.print("T,");
  Serial.print(left_track_speed);
  Serial.print(",");
  Serial.print(right_track_speed);
  Serial.print(",");
  Serial.print(up_down_pos);
  Serial.print(",");
  Serial.print(cannon_move);
  Serial.print(",");
  Serial.print(arm_val);
  Serial.print(",");
  Serial.print(fire_val);
  Serial.println();

}

