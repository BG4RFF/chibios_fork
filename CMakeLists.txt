macro(setByDefault VAR_NAME VAR_VALUE)
  if(NOT DEFINED ${VAR_NAME})
    set (${VAR_NAME} ${VAR_VALUE})
    message ("Default value set ${VAR_NAME}=${VAR_VALUE}")
  else()
    message ("User value set ${VAR_NAME}=${${VAR_NAME}}")
  endif()

endmacro()

message("")
message("-------------------Common-CMakeLists.txt---------------------")
message("")

#------------------------------------------------------------
#--------------default setup
#------------------------------------------------------------
setByDefault(OPTIMIZE_RTOS 0)
setByDefault(MAIN_STACK_SIZE 0x400)
setByDefault(PROCESS_STACK_SIZE 0x400)
setByDefault(USE_BOOTLOADER 0)
if (USE_BOOTLOADER EQUAL 1)
    setByDefault(BOOTLOADER_ITSELF 0)
    setbyDefault(USER_PROGRAM_START 0x08004000)
endif()
setByDefault(TOOLCHAIN "arm-none-eabi")
setByDefault(FLASH_BASE 0x08000000)
setByDefault(CHIP "STM32F407VG")
setByDefault (FLASH_SIZE "1M")
setByDefault (RAM_SIZE "128k")
setByDefault (GLOBAL_FLAGS "-O0  -ggdb ")
setByDefault (OPTIMIZED_FLAGS "-Os")
setByDefault (CPPFLAGS "-fno-rtti -fno-exceptions")
setByDefault (CFLAGS " ")
setByDefault (TARGET_NAME ${PROJECT_NAME})
setByDefault (HALCONF ${CMAKE_SOURCE_DIR}/halconf.h)
setByDefault (USE_COMMON_LIBRARY 0)
setByDefault (USE_PIRIS 0)
setByDefault (FPU_ENABLED FALSE)

set (ChibiOS_hal "${TARGET_NAME}_chibios_hal")
set (ChibiOS_rt "${TARGET_NAME}_chibios_rt")
set (ChibiOS_port "${TARGET_NAME}_chibios_port")
add_definitions(-DBECAUSE_OF_CODE_MODEL)

#------------------------------------------------------------
#--------------bootloader definitions
#------------------------------------------------------------
if (USE_BOOTLOADER EQUAL 1)
    message("Bootloader is planned")
    add_definitions(-DUSER_PROGRAM_START_ADDRESS=${USER_PROGRAM_START})
    add_definitions(-DBOOTLOADER_START_ADDRESS=0x08000000)

    if (BOOTLOADER_ITSELF EQUAL 0)
        set (FLASH_BASE ${USER_PROGRAM_START})
        add_definitions(-DBOOTLOADER_USER_PROGRAM)
        add_definitions(-DCORTEX_VTOR_INIT=${FLASH_BASE})
        message("program linked after bootlader offset ${FLASH_BASE}")
    else()
        add_definitions(-DBOOTLOADER_ITSELF)
    endif()
endif()

#------------------------------------------------------------
#--------------data preparation
#------------------------------------------------------------
#table of chips - ram size; flash size; hal driver versions; chip number; device

string (SUBSTRING ${CHIP} 6 1 CHAR)
if (${CHAR} MATCHES 1)
    set (DEVICE "STM32F1xx")
elseif(${CHAR} MATCHES 4)
    set (DEVICE "STM32F4xx")
elseif(${CHAR} MATCHES 0)
    set (DEVICE "STM32F0xx")
elseif(${CHAR} MATCHES 3)
    set (DEVICE "STM32F3xx")
else()
    message(FATAL_ERROR "Unsupported chip")
endif()


string (SUBSTRING ${CHIP} 9 1 CHAR)
#message (${CHAR})

#flash size
if (${CHAR} MATCHES "C" )
endif()

if (${DEVICE} MATCHES "STM32F1xx")
    set (ARCHITECTURE "v7m")
    set (CORE m3)
    set (GPIO 1)
    set (SPI 1)
    set (I2C 1)
    set (RTC 1)
    string (SUBSTRING ${CHIP} 6 3 CHAR)
    if (${CHAR} MATCHES 100)
        set (CHIP_NUMBER 100)
    elseif (${CHAR} MATCHES 103)
        set (CHIP_NUMBER 103)
    elseif (${CHAR} MATCHES 105 OR ${CHAR} MATCHES 107)
        set (CHIP_NUMBER 105_f107)
    endif()


message ("Selected device: ${DEVICE} and chip number ${CHIP_NUMBER}")

elseif ( ${DEVICE} MATCHES "STM32F4xx" OR ${DEVICE} MATCHES "STM32F3xx")
    set (ARCHITECTURE "v7m")
    set (CORE m4)
    set (GPIO 2)
    set (SPI 1)
    set (I2C 1)
    set (RTC 2)
elseif (${DEVICE} MATCHES "STM32F0xx")
    set (ARCHITECTURE "v6m")
    set (CORE m0)
else()
    message(FATAL_ERROR "None valid chip selected")
endif()


message("selected core cortex-${CORE} and architecture arm-${ARCHITECTURE}")
set(CMAKE_BUILD_TYPE None)

#------------------------------------------------------------
#--------------dont change this!!!
#------------------------------------------------------------
set (CMAKE_C_COMPILER "${TOOLCHAIN}-gcc")
set (CMAKE_CXX_COMPILER "${TOOLCHAIN}-g++")
set (CMAKE_ASM_COMPILER "${TOOLCHAIN}-gcc")
set (CMAKE_LINKER "${TOOLCHAIN}-gcc")
set (OBJCOPY "${TOOLCHAIN}-objcopy")
set (OBJDUMP "${TOOLCHAIN}-objdump")
set (SIZE "${TOOLCHAIN}-size")

set (SUPER_FLAGS
-DCORTEX_USE_FPU=${FPU_ENABLED}
-DTHUMB_PRESENT
-DTHUMB_NO_INTERWORKING
-mcpu=cortex-${CORE}
-fomit-frame-pointer
-ffunction-sections
-fdata-sections
-fno-common
-Wall
-Wextra
-mthumb
-mno-thumb-interwork
-DTHUMB
${GLOBAL_FLAGS}
)

add_definitions(${SUPER_FLAGS})

message (${CFLAGS})
foreach(var ${CFLAGS})
    list (APPEND ${CMAKE_C_FLAGS} ${var})
endforeach()
list (APPEND ${CMAKE_C_FLAGS} -Wstrict-prototypes)

set (CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} ${CPPFLAGS})

#------------------------------------------------------------
#--------------parsing halconf
#------------------------------------------------------------

if (NOT EXISTS ${HALCONF})
    message(FATAL_ERROR "halconf.h doesn't exist")

else()
    file (READ  ${HALCONF} HALCONF)
    set (VAR_LIST ADC DAC PAL CAN EXT GPT I2C I2S ICU MAC SPI PWM RTC SDC SERIAL SERIAL_USB MMC_SPI UART USB)

#include set
    set (ADC_INCLUDE )
    set (DAC_INCLUDE        "DACv1")
    set (PAL_INCLUDE        "GPIOv${GPIO}")
    set (CAN_INCLUDE )
    set (EXT_INCLUDE )
    set (GPT_INCLUDE         "TIMv1")
    set (I2C_INCLUDE        "I2Cv${I2C}")
    set (I2S_INCLUDE        "SPIv${SPI}")
    set (ICU_INCLUDE         "TIMv1")
    set (MAC_INCLUDE )
    set (SPI_INCLUDE        "SPIv${SPI}")
    set (PWM_INCLUDE        "TIMv1")
    set (RTC_INCLUDE        "RTCv${RTC}")
    set (SDC_INCLUDE        "USBv1")
    set (SERIAL_INCLUDE     "USARTv1")
    set (SERIAL_USB_INCLUDE "USBv1")
    set (MMC_SPI_INCLUDE    "SPIv${SPI}")
    set (UART_INCLUDE       "USARTv1")
    set (USB_INCLUDE        "USBv1")

#high level drivers set
    set (ADC_HLD adc)
    set (DAC_HLD dac)
    set (PAL_HLD pal)
    set (CAN_HLD can)
    set (EXT_HLD ext)
    set (GPT_HLD gpt)
    set (I2C_HLD i2c)
    set (I2S_HLD i2s)
    set (ICU_HLD icu)
    set (MAC_HLD mac)
    set (SPI_HLD spi)
    set (PWM_HLD pwm)
    set (RTC_HLD rtc)
    set (SDC_HLD sdc)
    set (SERIAL_HLD serial)
    set (SERIAL_USB_HLD serial_usb)
    set (MMC_SPI_HLD mmc_spi hal_mmcsd)
    set (UART_HLD uart)
    set (USB_HLD usb)

#low level drivers
    set (ADC_LLD )
    set (DAC_LLD "DACv1/dac")
    set (PAL_LLD "GPIOv${GPIO}/pal")
    set (CAN_LLD "can")
    set (EXT_LLD "ext")
    set (GPT_LLD "TIMv1/gpt")
    set (I2C_LLD "I2Cv${I2C}/i2c")
    set (I2S_LLD )
    set (ICU_LLD "TIMv1/icu")
    set (MAC_LLD "mac")
    set (SPI_LLD "SPIv${SPI}/spi")
    set (PWM_LLD "TIMv1/pwm")
    set (RTC_LLD "RTCv${RTC}/rtc")
    set (SDC_LLD "sdc")
    set (SERIAL_LLD "USARTv1/serial")
    set (SERIAL_USB_LLD "USBv1/usb")
    set (MMC_SPI_LLD )
    set (UART_LLD "USARTv1/uart")
    set (USB_LLD "OTGv1/usb")

# family low level drivers
    set (ADC_LLD_FAMILY adc_lld)
    set (EXT_LLD_FAMILY ext_lld_isr)

    foreach(VAR ${VAR_LIST})
        set (regex "HAL_USE_${VAR}[\\t ]*(FALSE|TRUE)")
        string(REGEX MATCH ${regex} OUTPUT ${HALCONF}  )
		string (LENGTH "${OUTPUT}" sem)
		if (${sem} )
			string(REGEX REPLACE "HAL_USE_${VAR}[\\t ]*" "  " FILTER ${OUTPUT})
			if (${FILTER} MATCHES "TRUE")
				list (APPEND MODULES ${VAR})
				list (APPEND HLD_SOURCES ${${VAR}_HLD})
				list (APPEND INCLUDES ${${VAR}_INCLUDE})
				list (APPEND LLD_SOURCES ${${VAR}_LLD})
				list (APPEND LLD_FAMILY_SOURCES ${${VAR}_LLD_FAMILY})
				set (${VAR}_ENABLED 1)
			else()
				set (${VAR}_ENABLED 0)
			endif()
		endif()
    endforeach()
endif()

message("selected HAL modules to be compiled: ${MODULES}")

#------------------------------------------------------------
#--------------chibios includes
#------------------------------------------------------------
include_directories(
${CMAKE_CURRENT_SOURCE_DIR}
"${CHIBIOS_DIR}/os/hal/include"
"${CHIBIOS_DIR}/os/ext/CMSIS/include"
"${CHIBIOS_DIR}/os/ext/CMSIS/ST"
"${CHIBIOS_DIR}/os/rt/ports/ARMCMx"
"${CHIBIOS_DIR}/os/rt/ports/ARMCMx/cmsis_os"
"${CHIBIOS_DIR}/os/rt/ports/ARMCMx/compilers/GCC"
"${CHIBIOS_DIR}/os/rt/include"
"${CHIBIOS_DIR}/os/hal/osal/rt"
"${CHIBIOS_DIR}/os/hal/ports/common/ARMCMx"
"${CHIBIOS_DIR}/os/hal/ports/STM32/LLD"
"${CHIBIOS_DIR}/os/hal/ports/STM32/${DEVICE}"
"${CHIBIOS_DIR}/os/common/ports/ARMCMx/devices/${DEVICE}"
#"${CHIBIOS_DIR}/os/hal/ports/STM32/LLD/OTGv1"
"${CHIBIOS_DIR}/os/hal/ports/STM32/LLD/TIMv1"
)

foreach(I ${INCLUDES})
list (APPEND INCLUDES_FULL_PATH ${CHIBIOS_DIR}/os/hal/ports/STM32/LLD/${I})
endforeach()

INCLUDE_DIRECTORIES(${INCLUDES_FULL_PATH})


#------------------------------------------------------------
#--------------hal sources
#------------------------------------------------------------
set (HAL_FILES
"hal"
"hal_queues"
"st"
)

list (APPEND HAL_FILES ${HLD_SOURCES})


foreach (dir ${HAL_FILES})
set (f "${CHIBIOS_DIR}/os/hal/src/${dir}.c")
list (APPEND HAL_SRC ${f})
endforeach()

list (APPEND HAL_FILES
hal_channels
hal_ioblock
hal_streams
mii
)

foreach (dir ${HAL_FILES})
set (h "${CHIBIOS_DIR}/os/hal/include/${dir}.h")
list (APPEND HAL_HEADER ${h})
endforeach()

list (APPEND HAL_SRC "${CHIBIOS_DIR}/os/hal/osal/rt/osal.c")

#------------------------------------------------------------
#-------------- board
#------------------------------------------------------------
if (DEFINED BOARD)
        message("using board ${BOARD}")
        list (APPEND HAL_SRC "${CHIBIOS_DIR}/os/hal/boards/${BOARD}/board.c")
        list (APPEND HAL_HEADER "${CHIBIOS_DIR}/os/hal/boards/${BOARD}/board.h")
        include_directories( "${CHIBIOS_DIR}/os/hal/boards/${BOARD}")
else()
        message("using no board! you should use your own board init")
endif()

add_library(${ChibiOS_hal} OBJECT ${HAL_SRC} ${HAL_HEADER})
#------------------------------------------------------------
#-------------- rt sources
#------------------------------------------------------------

set (RT
"chcond"
"chdebug"
"chdynamic"
"chevents"
"chheap"
"chmboxes"
"chmemcore"
"chmempools"
"chmsg"
"chmtx"
"chqueues"
"chregistry"
"chsem"
"chschd"
"chstats"
"chsys"
"chthreads"
"chtm"
"chvt"
)

foreach (dir ${RT})
set (f "${CHIBIOS_DIR}/os/rt/src/${dir}.c")
list (APPEND RT_SRC ${f})
endforeach()

list (APPEND RT
ch
chbsem
chstreams
chsystypes
)

foreach (dir ${RT})
set (f "${CHIBIOS_DIR}/os/rt/include/${dir}.h")
list (APPEND RT_HEADER ${f})
endforeach()


add_library(${ChibiOS_rt} OBJECT ${RT_SRC} ${RT_HEADER})

#------------------------------------------------------------
#-------------- port sources
#------------------------------------------------------------
set (PORT_SRC
"${CHIBIOS_DIR}/os/common/ports/ARMCMx/compilers/GCC/crt1.c"
"${CHIBIOS_DIR}/os/common/ports/ARMCMx/compilers/GCC/crt0_${ARCHITECTURE}.s"
"${CHIBIOS_DIR}/os/common/ports/ARMCMx/compilers/GCC/vectors.c"
"${CHIBIOS_DIR}/os/hal/ports/common/ARMCMx/nvic.c"
 )

set_source_files_properties("${CHIBIOS_DIR}/os/common/ports/ARMCMx/compilers/GCC/crt0_${ARCHITECTURE}.s" PROPERTIES COMPILE_FLAGS "-x assembler-with-cpp")

set (PORT_HEADERS
${CHIBIOS_DIR}/os/rt/ports/ARMCMx/compilers/GCC/chtypes.h
${CHIBIOS_DIR}/os/rt/ports/ARMCMx/cmsis_os/cmsis_os.h
${CHIBIOS_DIR}/os/rt/ports/ARMCMx/chcore.h
${CHIBIOS_DIR}/os/rt/ports/ARMCMx/chcore_timer.h
${CHIBIOS_DIR}/os/rt/ports/ARMCMx/chcore_${ARCHITECTURE}.h
${CHIBIOS_DIR}/os/common/ports/ARMCMx/devices/${DEVICE}/cmparams.h
${CHIBIOS_DIR}/os/hal/ports/common/ARMCMx/nvic.h
)

#hal common
SET (LLD
"TIMv1/st"
)

list (APPEND LLD ${LLD_SOURCES})



foreach (dir ${LLD})
set (f "${CHIBIOS_DIR}/os/hal/ports/STM32/LLD/${dir}_lld.c")
list (APPEND PORT_SRC ${f})
endforeach()

foreach (dir ${LLD})
set (f "${CHIBIOS_DIR}/os/hal/ports/STM32/LLD/${dir}_lld.h")
list (APPEND PORT_HEADERS ${f})
endforeach()

set(LLD
OTGv1/stm32_otg
USBv1/stm32_usb
TIMv1/stm32_tim
)

foreach (dir ${LLD})
set (f "${CHIBIOS_DIR}/os/hal/ports/STM32/LLD/${dir}.h")
list (APPEND PORT_HEADERS ${f})
endforeach()



#family part
SET (LLD
"hal_lld"
"stm32_dma"
)


list (APPEND LLD ${LLD_FAMILY_SOURCES})


foreach (dir ${LLD})
set (f "${CHIBIOS_DIR}/os/hal/ports/STM32/${DEVICE}/${dir}.c")
list (APPEND PORT_SRC ${f})
endforeach()

list (APPEND LLD
stm32_isr
stm32_rcc
stm32_registry
)

if (${DEVICE} MATCHES "STM32F1xx")
list (APPEND LLD hal_lld_f${CHIP_NUMBER})
endif()

foreach (dir ${LLD})
set (f "${CHIBIOS_DIR}/os/hal/ports/STM32/${DEVICE}/${dir}.h")
list (APPEND PORT_SRC ${f})
endforeach()

set (vm "${CHIBIOS_DIR}/os/rt/ports/ARMCMx/compilers/GCC/chcoreasm_${ARCHITECTURE}.s")

#rt port
list (APPEND PORT_SRC
"${CHIBIOS_DIR}/os/rt/ports/ARMCMx/chcore.c"
"${CHIBIOS_DIR}/os/rt/ports/ARMCMx/cmsis_os/cmsis_os.c"
"${CHIBIOS_DIR}/os/rt/ports/ARMCMx/chcore_${ARCHITECTURE}.c"
${vm}
)

#set_property(SOURCE ${vm} PROPERTY LANGUAGE C)
set_source_files_properties(${vm} PROPERTIES COMPILE_FLAGS "-x assembler-with-cpp")

add_library(${ChibiOS_port} OBJECT ${PORT_SRC} ${PORT_HEADERS})

#------------------------------------------------------------
#-------------- linker setup
#------------------------------------------------------------

if (NOT DEFINED ${LINKER_SCRIPT})

set (TMP_LINKER
"
MEMORY
{
    flash : org = ${FLASH_BASE}, len = ${FLASH_SIZE}
    ram0  : org = 0x20000000, len = ${RAM_SIZE}    /* SRAM1 + SRAM2 */
    ram1  : org = 0x20000000, len = 0    /* SRAM1 */
    ram2  : org = 0x2001C000, len = 0     /* SRAM2 */
    ram3  : org = 0x00000000, len = 0
    ram4  : org = 0x10000000, len = 0     /* CCM SRAM */
    ram5  : org = 0x40024000, len = 0      /* BCKP SRAM */
    ram6  : org = 0x00000000, len = 0
    ram7  : org = 0x00000000, len = 0

}
/* RAM region to be used for Main stack. This stack accommodates the processing
   of all exceptions and interrupts*/
REGION_ALIAS(\"MAIN_STACK_RAM\", ram0);

/* RAM region to be used for the process stack. This is the stack used by
   the main() function.*/
REGION_ALIAS(\"PROCESS_STACK_RAM\", ram0);

/* RAM region to be used for data segment.*/
REGION_ALIAS(\"DATA_RAM\", ram0);

/* RAM region to be used for BSS segment.*/
REGION_ALIAS(\"BSS_RAM\", ram0);

INCLUDE rules.ld

"
)

set (LINKER_SCRIPT "${CMAKE_BINARY_DIR}/linker.ld")
file (WRITE ${LINKER_SCRIPT} ${TMP_LINKER})

message ("No user linker script defined, using default ram-size:${RAM_SIZE} and flash-size:${FLASH_SIZE}")
endif()

set (muj_list
"-mcpu=cortex-${CORE} -flto -O0 -ggdb -fomit-frame-pointer -falign-functions=16 \
-ffunction-sections -fdata-sections -fno-common -nostartfiles  \
-Wl,--cref,--no-warn-mismatch,-Map=${CMAKE_BINARY_DIR}/${TARGET_NAME}.map,\
--library-path=${CHIBIOS_DIR}/os/common/ports/ARMCMx/compilers/GCC,\
--script=${LINKER_SCRIPT},\
--gc-sections,--defsym=__process_stack_size__=${PROCESS_STACK_SIZE},--defsym=__main_stack_size__=${MAIN_STACK_SIZE} \
-mno-thumb-interwork -mthumb "
)

set (CMAKE_EXE_LINKER_FLAGS ${muj_list})
set (CMAKE_CXX_LINK_EXECUTABLE "<CMAKE_LINKER> <FLAGS> <CMAKE_CXX_LINK_FLAGS> <LINK_FLAGS> <OBJECTS> -o <TARGET> <LINK_LIBRARIES>")
#set (CMAKE_CXX_LINK_EXECUTABLE)

#------------------------------------------------------------
#-------------- rest
#------------------------------------------------------------
if(NOT EXISTS ${CHIBIOS_DIR})
        message(FATAL_ERROR "ChibiOS directory doesn't exists")
endif()

if (${OPTIMIZE_RTOS} EQUAL 1)
    message("ChibiOS code will be optimized")
    #set_source_files_properties(${PORT_SRC} COMPILE_FLAGS ${OPTIMIZED_FLAGS})
    set_source_files_properties(${HAL_SRC} COMPILE_FLAGS ${OPTIMIZED_FLAGS})
    set_source_files_properties(${RT_SRC} COMPILE_FLAGS ${OPTIMIZED_FLAGS})
endif()


set(USER_CODE "${TARGET_NAME}_user_code")

add_executable(${TARGET_NAME}
$<TARGET_OBJECTS:${ChibiOS_hal}>
$<TARGET_OBJECTS:${ChibiOS_rt}>
$<TARGET_OBJECTS:${ChibiOS_port}>
$<TARGET_OBJECTS:${USER_CODE}>
)

add_library(${USER_CODE} OBJECT ${USER_SOURCES} ${OPTIMIZED_SOURCES} ${EXTRA_HEADERS})

#optimized sources
set_source_files_properties(${OPTIMIZED_SOURCES} COMPILE_FLAGS ${OPTIMIZED_FLAGS})

enable_language(ASM)
target_include_directories(${USER_CODE} PUBLIC ${INCLUDE_DIRS} )

if (USE_PIRIS EQUAL 1)
add_subdirectory(${CHIBIOS_DIR}/piris/framework ${CMAKE_CURRENT_BINARY_DIR}/chibios_piris)
target_link_libraries(${TARGET_NAME} piris)
endif()

if (USE_COMMON_LIBRARY EQUAL 1)
add_subdirectory(${CHIBIOS_DIR}/library ${CMAKE_CURRENT_BINARY_DIR}/chibios_library)
target_link_libraries(${TARGET_NAME} library)
endif()

set (CMAKE_EXECUTABLE_SUFFIX .elf)

#------------------------------------------------------------
#-------------- custom commands
#------------------------------------------------------------
# generate HEX
set (OUT ${CMAKE_BINARY_DIR}/${TARGET_NAME})
add_custom_command(
OUTPUT ${OUT}.hex COMMAND ${OBJCOPY} -O ihex ${OUT}.elf ${OUT}.hex
DEPENDS ${TARGET_NAME} COMMENT "Creating HEX > ${OUT}.hex"
)

# generate BIN
add_custom_command(
OUTPUT ${OUT}.bin COMMAND ${OBJCOPY} -O binary ${OUT}.elf ${OUT}.bin
DEPENDS ${TARGET_NAME} COMMENT "Creating BIN > ${OUT}.bin"
)

#dump
add_custom_command(
OUTPUT ${OUT}.dmp COMMAND ${OBJDUMP} -x --syms ${OUT}.elf ${OUT}.dmp
DEPENDS ${TARGET_NAME} COMMENT "Creating DMP > ${OUT}.dmp"
)

# show size
add_custom_command(
OUTPUT ${OUT}.size
COMMAND python2 ${CHIBIOS_DIR}/sizer.py ${OUT}.elf
DEPENDS ${TARGET_NAME} COMMENT "${OUT}.bin"
)

add_custom_target("${TARGET_NAME}_hex" ALL DEPENDS ${OUT}.hex )
add_custom_target("${TARGET_NAME}_bin" ALL DEPENDS ${OUT}.bin )
#add_custom_target(dmp ALL DEPENDS ${OUT}.dmp )
add_custom_target("${TARGET_NAME}_size" ALL DEPENDS ${OUT}.size )

message(" ")
message("------------End-of-Common-CMakeLists.txt---------------------")
message(" ")
