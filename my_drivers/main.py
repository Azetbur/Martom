import uasyncio
from machine import Pin
from light_driver import lightCircuit
import utime  # Import the utime module for handling time-related functions

# Global variable to track the last button press time
last_press_time = 0

# Debounce period in milliseconds
debounce_ms = 200

# Callback function to toggle the light circuit
async def toggle_light(circuit):
    await circuit.circuit_toggle()

# Interrupt service routine for the button press with debounce
def button_isr(pin, circuit):
    global last_press_time
    current_time = utime.ticks_ms()  # Use utime.ticks_ms() to get the current time
    
    # Check if current press is within the debounce period
    if utime.ticks_diff(current_time, last_press_time) > debounce_ms:  # Use utime.ticks_diff() for time difference
        print("Button pressed")
        uasyncio.create_task(toggle_light(circuit))
        last_press_time = current_time

def setup_button(circuit):
    # Configure the pin (e.g., GPIO 12) as input with pull-up
    button_pin = Pin(12, Pin.IN, Pin.PULL_UP)
    
    # Attach an interrupt to the pin on the falling edge (button press) and call button_isr with debounce
    button_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: button_isr(pin, circuit))

async def main():
    # Create a lightCircuit instance
    circuit = lightCircuit(pin_number=15, frequency=20000, fps=60, brightness_percentage=100, startup_time_seconds=12, shutdown_time_seconds=6)
    
    # Setup the button with the lightCircuit instance and debounce
    setup_button(circuit)
    
    # Keep the script running to listen for button presses
    while True:
        await uasyncio.sleep(1)

# Run the main coroutine
uasyncio.run(main())
