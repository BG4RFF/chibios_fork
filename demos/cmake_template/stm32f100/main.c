/*
 ChibiOS/RT - Copyright (C) 2006-2013 Giovanni Di Sirio

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

#include "ch.h"
#include "hal.h"
//#include "scheduler.hpp"
#include "scheduler.h"
systime_t sysTime;

/*
 * Application entry point.
 */


int main(void)
{
    halInit();
    chSysInit();


	while (TRUE)
	{        
        chThdSleepMilliseconds(5);
        sysTime = chVTGetSystemTime();
        shPlay();
	}

	return 1;
}



#ifdef __cplusplus

extern "C" void __cxa_pure_virtual(void)
{
    asm("bkpt");
    while(1);
}

#endif

