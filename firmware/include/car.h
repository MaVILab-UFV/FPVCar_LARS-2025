#ifndef CAR_H
#define CAR_H

#include "config.h"

#define MIN_TURN -100
#define DEF_TURN 0
#define MAX_TURN 100

#define MIN_SPEED -100
#define DEF_SPEED 0
#define MAX_SPEED 100

void carSetSpeed(int val);
int carGetSpeed();

void carSetTurn(int val);
int carGetTurn();

void carSetRunTime(int val);
int carGetRunTime();

void carSetParam(const char *param, int val);
int carGetParam(const char *param);

void carInit();
unsigned long carGetLastUpdateTime();
void carSetDefaults();
bool carIsUpdated();

#endif