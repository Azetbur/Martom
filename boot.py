# Set the correct pin numbers for each of the connected peripherals in this section ####################
DISPLAY_SDA_PIN_NO    = 21
DISPLAY_SCL_PIN_NO    = 22

ENCODER_DT_PIN_NO     = 34
ENCODER_CLK_PIN_NO    = 35

ENCODER_BUTTON_PIN_NO = 13

BUTTON_1_PIN_NO       =	12
BUTTON_2_PIN_NO       = 14
BUTTON_3_PIN_NO       = 27

# An array containing all the pins which belong to LED circuits.
# Correct formating example: [11, 12, 13]
PIN_NUMBER_ARRAY      = [15, 2, 0, 4, 16, 17, 5, 18, 19, 23]

# Set the default setting for the LED lightning in this section ########################################

# The brightness percentage value should be a multiple of 5
BRIGHTNESS_PERCENTAGE_DEFAULT = 90

TIMER_TIME_MIN_DEFAULT        = 60
UPTIME_TIME_SEC_DEFAULT       = 1
DOWNTIME_TIME_SEC_DEFAULT     = 2
OVERLAP_PERCENTAGE_DEFAULT    = 50

# Set this to True if you want the timer function to be active, False if not
TIMER_ON_OFF_BOOL_DEFAULT     = True

# End of section #######################################################################################

import uasyncio
import utime
import gc
import micropython
from machine import Pin

from controller import Controller
from my_drivers.light_driver import lightArray
from my_drivers.display_driver import Display
from third_party_drivers.rotary_irq_esp import RotaryIRQ

# Variable to track the last button press time
last_press_time = 0

# Debounce period for buttons in milliseconds
DEBOUNCE_MS = 300

# Stores the last known value of the encoder
encoder_val_stored = 0

# Garbage collection interval in seconds
GARBAGE_S = 600

def _log(message):
    print("\n" + "boot.py         : " + str(message))

# Asynchronous function to handle the button press
async def handle_button_press(array):
    print("right before toggle")
    await array.toggle()

# Interrupt service routine for button presses with debounce
def array_button_isr(pin, array):
    global last_press_time
    current_time = utime.ticks_ms()  # Use utime.ticks_ms() to get the current time

    # Check if current press is within the debounce period
    if utime.ticks_diff(current_time, last_press_time) > DEBOUNCE_MS:  # Use utime.ticks_diff() for time difference
        last_press_time = current_time
        _log("Button press registered on " + str(pin))
        uasyncio.create_task(handle_button_press(array))

# Function to configure button pin and attach interrupt
def setup_button_pin(pin_number, array):
    button_pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
    button_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: array_button_isr(pin, array))

# Function to check whether the encoder was turned, returns bool
def check_encoder_turned(encoder):
    global encoder_val_stored
    
    if encoder.value() != encoder_val_stored:
        encoder_val_stored = encoder.value()
        return True
    else:
        return False
    
# Asynchronous function to periodically trigger garbage collection
async def garbage_collector():
    while True:
        gc.collect()
        _log("Garbage collection performed")
        #_log("Free Memory: " + str(gc.mem_free()))
        #micropython.mem_info()
        await uasyncio.sleep(GARBAGE_S)

async def main():
    global encoder_val_stored
    
    _log("Initializing program")
    
    # Create a Display instance
    display = Display(sda_pin=DISPLAY_SDA_PIN_NO,
                      scl_pin=DISPLAY_SCL_PIN_NO,
                      freq=10000,
                      address=0x27)
    
    # Create a Controller instance
    controller = Controller(brightness_percentage=BRIGHTNESS_PERCENTAGE_DEFAULT,
                            timer_on_off_bool=TIMER_ON_OFF_BOOL_DEFAULT,
                            timer_time_min=TIMER_TIME_MIN_DEFAULT,
                            uptime_time_sec=UPTIME_TIME_SEC_DEFAULT,
                            downtime_time_sec=DOWNTIME_TIME_SEC_DEFAULT,
                            overlap_percentage=OVERLAP_PERCENTAGE_DEFAULT,
                            display=display)
    
    # Create a RotaryIRQ instance
    encoder = RotaryIRQ(pin_num_clk=ENCODER_CLK_PIN_NO, 
                        pin_num_dt=ENCODER_DT_PIN_NO, 
                        min_val=0, 
                        max_val=controller.no_lines - 1,
                        reverse=False, 
                        range_mode=RotaryIRQ.RANGE_WRAP,
                        half_step=True)
    encoder_val_stored = encoder.value()
    
    encoder_button_pin = Pin(ENCODER_BUTTON_PIN_NO, Pin.IN, Pin.PULL_UP)
    encoder_button_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: controller.encoder_pressed(array, encoder))
    _log("Encoder configured")
    
    # Create a lightArray instance
    array = lightArray(pin_number_array=[15, 2, 0, 4, 16, 17, 5, 18, 19, 23],
                       frequency=20000,
                       fps=40,
                       brightness_percentage=controller.settings_array[0],
                       timer_active_bool=controller.settings_array[1],
                       timer_time_minutes=controller.settings_array[2],
                       startup_time_seconds=controller.settings_array[3],
                       shutdown_time_seconds=controller.settings_array[4],
                       overlap_percentage=controller.settings_array[5])

    # Configure button pins and attach interrupts
    setup_button_pin(12, array)
    setup_button_pin(14, array)
    setup_button_pin(27, array)
    _log("Buttons configured")

    # Start the garbage collector coroutine
    uasyncio.create_task(garbage_collector())
    
    # Log initialization completion
    _log("Initialization complete, the program is now running")
    
    # Keep the script running to listen for button presses
    while True:
        await uasyncio.sleep(1)
        if check_encoder_turned(encoder):
            controller.encoder_turned(encoder.value())
            
        #display.check_connection(controller, encoder.value())


# Run the main coroutine
uasyncio.run(main())