#include "car.h"
#include <Arduino.h>
#include <ESP32Servo.h>

#define TURN "turn"
#define SPEED "speed"
#define RUNTIME "time"

#define SERVO_MIN_uS 500
#define SERVO_MAX_uS 2400
#define DEG_TO_uS(deg) (SERVO_MIN_uS + deg * (SERVO_MAX_uS - SERVO_MIN_uS) / 180)

/*
    Car State:
        turn: int [-100, 100]
        speed: int [-100, 100]
        runIme: int [0, 1000] 
*/
static volatile int turn;
static volatile int speed;
static volatile int runTime;
static volatile unsigned long lastUpdateTime = 0;

static TaskHandle_t updateServoTaskHandle;
static Servo servo;
static volatile int currentServoUS;
static volatile int expectedServoUS;

void updateServoTask(void *params) {
    static const int maxUs20ms = (DEG_TO_uS(configSERVO_DEG_PER_SEC) + 49) / 50;
    for(;;) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        while(currentServoUS < expectedServoUS) {
            int add = min(maxUs20ms, expectedServoUS - currentServoUS);
            currentServoUS += add;
            servo.write(currentServoUS);

#ifdef configDEBUG
            Serial.printf("Exp: %d\tCur: %d\n", expectedServoUS, currentServoUS);
#endif
            vTaskDelay(pdMS_TO_TICKS(20));
        }

        while(currentServoUS > expectedServoUS) {
            int add = min(maxUs20ms, currentServoUS - expectedServoUS);
            currentServoUS -= add;
            servo.write(currentServoUS);
#ifdef configDEBUG
            Serial.printf("Exp: %d\tCur: %d\n", expectedServoUS, currentServoUS);
#endif
            vTaskDelay(pdMS_TO_TICKS(20));
        }
    }
}

void carInit() {
    ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);

    /*
        Initialize servo task
            things shoud be in this order. First initialize the servo. Then the task.
            Finally set defaults.
    */
    servo.setPeriodHertz(50);
    servo.attach(configSERVO_PIN, SERVO_MIN_uS, SERVO_MAX_uS);
    currentServoUS = expectedServoUS = map(DEF_TURN, MIN_TURN, MAX_TURN, DEG_TO_uS(configSERVO_MIN_ANGLE), DEG_TO_uS(configSERVO_MAX_ANGLE));
#ifdef configDEBUG
    Serial.printf("Exp: %d\tCur: %d\n", expectedServoUS, currentServoUS);
#endif
    servo.writeMicroseconds(currentServoUS);
    xTaskCreate(updateServoTask, "update servo", 4096, NULL, 1, &updateServoTaskHandle);

    carSetDefaults();
    pinMode(configMOTOR1_PIN, OUTPUT);
    pinMode(configMOTOR2_PIN, OUTPUT);
}

void carSetSpeed(int val) {
    speed = constrain(val, MIN_SPEED, MAX_SPEED);
    int motorValue = map(speed, MIN_SPEED, MAX_SPEED, -configMOTOR_MAX_SPEED, configMOTOR_MAX_SPEED);
    if(motorValue >= 0) {
        analogWrite(configMOTOR1_PIN, motorValue);
        analogWrite(configMOTOR2_PIN, 0);
    } else {
        analogWrite(configMOTOR1_PIN, 0);
        analogWrite(configMOTOR2_PIN, -motorValue);
    }
    lastUpdateTime = millis();
#ifdef configDEBUG
    Serial.print("Set Speed to ");
    Serial.println(val);
#endif
}

int carGetSpeed() {
    return speed;
}

void carSetTurn(int val) {
    turn = constrain(val, MIN_TURN, MAX_TURN);
    expectedServoUS = map(turn, MIN_TURN, MAX_TURN, DEG_TO_uS(configSERVO_MIN_ANGLE), DEG_TO_uS(configSERVO_MAX_ANGLE));
    xTaskNotifyGive(updateServoTaskHandle);
    lastUpdateTime = millis();
#ifdef configDEBUG
    Serial.print("Set Turn to ");
    Serial.println(val);
#endif
}

int carGetTurn() {
    return turn;
}

void carSetRunTime(int val) {
    runTime = val;
#ifdef configDEBUG
    Serial.print("Set Time to ");
    Serial.println(val);
#endif
}

int carGetRunTime() {
    return runTime;
}

void carSetParam(const char *param, int val) {
    if(!strcmp(param, SPEED)) {
        carSetSpeed(val);
    } else if(!strcmp(param, TURN)) {
        carSetTurn(val);
    } else if(!strcmp(param, RUNTIME)) {
        carSetRunTime(val);
    } else {
#ifdef configDEBUG
        Serial.println("Invalid Param");
#endif
    }
}

int carGetParam(const char *param) {
    if(!strcmp(param, SPEED)) {
        return speed;
    } else if(!strcmp(param, TURN)) {
        return turn;
    } else if(!strcmp(param, RUNTIME)) {
        return runTime;
    } else {
#ifdef configDEBUG
        Serial.println("Invalid Param");
#endif
        return -1;
    }
    return -1;
}

unsigned long carGetLastUpdateTime() {
    return lastUpdateTime;
}

void carSetDefaults() {
    carSetSpeed(DEF_SPEED);
    carSetTurn(DEF_TURN);
    carSetRunTime(200);
}

bool carIsUpdated() {
    return millis() - lastUpdateTime < runTime;
}