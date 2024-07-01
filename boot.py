import uasyncio
import utime
import gc
from machine import Pin
from light_driver import lightArray

# Global variable to track the last button press time
last_press_time = 0

# Debounce period for buttons in milliseconds
debounce_ms = 300

# Stores the last known value of the encoder
encoder_val_stored

# Garbage collection interval in seconds
garbage_s = 600

def _log(message):
    print("\n" + "boot.py         : " + str(message))
    return

# Asynchronous function to handle the button press
async def handle_button_press(circuit):
    await circuit.toggle()

# Interrupt service routine for button presses with debounce
def array_button_isr(pin, circuit):
    global last_press_time
    current_time = utime.ticks_ms()  # Use utime.ticks_ms() to get the current time

    # Check if current press is within the debounce period
    if utime.ticks_diff(current_time, last_press_time) > debounce_ms:  # Use utime.ticks_diff() for time difference
        last_press_time = current_time
        _log("Button press registered on " + str(pin))
        uasyncio.create_task(handle_button_press(circuit))

# Function to configure button pin and attach interrupt
def setup_button_pin(pin_number, circuit):
    button_pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
    button_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: array_button_isr(pin, circuit))

# Function to check whether the encoder was turned, returns bool
def check_encoder_turned(encoder):
    if encoder.value != encoder_val_stored
        encoder_val_stored = encoder.value
        return true
    else:
        return false
    
# Asynchronous function to periodically trigger garbage collection
async def garbage_collector():
    while True:
        gc.collect()
        _log("Garbage collection performed")
        await uasyncio.sleep(garbage_s)

async def main():
    _log("Initializing program")
    
    # Create a Display instance
    display = Display(21, 22, 10000, 0x27)
    _log("Display configured")
    
    # Create a Controller instance
    controller = Controller(display)
    _log("Controller configured")
    
    # Create a RotaryIRQ instance
    encoder = RotaryIRQ(pin_num_clk=35, 
                        pin_num_dt=34, 
                        min_val=0, 
                        max_val=controller.no_lines - 1,
                        reverse=False, 
                        range_mode=RotaryIRQ.RANGE_WRAP,
                        half_step=True)
    
    encoder_button_pin = Pin(13, Pin.IN, Pin.PULL_UP)
    encoder_btn.irq(trigger=Pin.IRQ_FALLING, handler=controller.encoder_pressed)
    _log("Encoder configured")
    
    # Create a lightCircuit instance
    array = lightArray(pin_number_array=[15, 2, 0, 4, 16, 17, 5, 18, 19, 23],
                       frequency=20000,
                       fps=60,
                       brightness_percentage=85,
                       startup_time_seconds=9,
                       shutdown_time_seconds=3)
    _log("Light control configured")

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
            controller.encoder_turned(encoder.value)
        

# Run the main coroutine
uasyncio.run(main())