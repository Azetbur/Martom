import uasyncio
from machine import Pin
from light_driver import pwmArray
import utime  # Import the utime module for handling time-related functions

# Global variable to track the last button press time
last_press_time = 0

# Debounce period in milliseconds
debounce_ms = 200

# Callback function to toggle the light array
async def toggle_array(array):
    await array.toggle()
    
# Callback function to toggle one specific light circuit
async def toggle_circuit(circuit):
    await circuit.toggle_gradual()

# Interrupt service routine for the button press with debounce
def array_button_isr(pin, circuit):
    global last_press_time
    current_time = utime.ticks_ms()  # Use utime.ticks_ms() to get the current time
    
    # Check if current press is within the debounce period
    if utime.ticks_diff(current_time, last_press_time) > debounce_ms:  # Use utime.ticks_diff() for time difference
        print("Button pressed")
        uasyncio.create_task(toggle_array(circuit))
        last_press_time = current_time
        
def circuit_button_isr(pin, array):
    global last_press_time
    current_time = utime.ticks_ms()  # Use utime.ticks_ms() to get the current time
    
    # Check if current press is within the debounce period
    if utime.ticks_diff(current_time, last_press_time) > debounce_ms:  # Use utime.ticks_diff() for time difference
        print("Button pressed")
        uasyncio.create_task(toggle_circuit(array.circuits[2]))
        last_press_time = current_time

def setup_button(array):
    # Configure the pin (e.g., GPIO 12) as input with pull-up
    array_button_pin = Pin(12, Pin.IN, Pin.PULL_UP)
    circuit_button_pin = Pin(27, Pin.IN, Pin.PULL_UP)
    
    # Attach an interrupt to the pin on the falling edge (button press) and call button_isr with debounce
    array_button_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: array_button_isr(pin, array))
    circuit_button_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: circuit_button_isr(pin, array))

async def main():
    # Create a pwmCircuit instance
    array = pwmArray(pin_number_array=[15, 2, 0, 4, 16, 17, 5, 18, 19, 23], frequency=20000, fps=60, brightness_percentage=100, startup_time_seconds=2, shutdown_time_seconds=4)
    
    # Setup the button with the pwmCircuit instance and debounce
    setup_button(array)
    
    # Keep the script running to listen for button presses
    while True:
        await uasyncio.sleep(1)

# Run the main coroutine
uasyncio.run(main())
