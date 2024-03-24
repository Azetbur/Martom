#####################################################################################################
import utime
import boot
import machine
import uasyncio
import ujson as json
from machine import Pin, SoftI2C, PWM
from rotary_irq_esp import RotaryIRQ
from i2c_lcd import I2cLcd
from lcd_api import LcdApi

# Global disable signal
disable_signal = uasyncio.Event()

last_pressed_time = 0

print("even new")


#####################################################################################################
###################################################
# I2C DISPLAY #####################################

# Pins
DISPLAY_SDA_PIN = 21
DISPLAY_SCL_PIN = 22

# I2C parameters
DISPLAY_ADDR    = 0x27
DISPLAY_ROWS    = 4
DISPLAY_COLUMNS = 20

# Object initialization
i2c = SoftI2C(scl=Pin(DISPLAY_SCL_PIN), sda=Pin(DISPLAY_SDA_PIN), freq=10000)

try:
    display = I2cLcd(i2c, DISPLAY_ADDR, DISPLAY_ROWS, DISPLAY_COLUMNS)
except Exception as e:
    
    # Log or print the exception if needed
    print("Failed to initialize the real display due to:", str(e))
    
    # Define a fake display class with the same methods as the real one but with dummy implementations
    class FakeDisplay:
        def __init__(self, *args, **kwargs):
            print("Fake display initialized with args:", args, "and kwargs:", kwargs)
        
        def clear(self):
            print("Fake display cleared")
        
        def print(self, string):
            print("Fake display print:", string)
            
        def move_to(self, x, y):
            # Assuming x and y are the coordinates to move the cursor to
            print(f"Fake display cursor moved to ({x}, {y})")
            
        def putstr(self, string):
            # Mimic displaying a string on the display
            print(f"Fake display putstr: {string}")
        
        # Add other necessary methods that your actual display uses
        
    # Initialize the fake display as the display object
    display = FakeDisplay(i2c, DISPLAY_ADDR, DISPLAY_ROWS, DISPLAY_COLUMNS)


###################################################
# ENCODER #########################################

# Pins
ENCODER_DT_PIN  = 34  
ENCODER_CLK_PIN = 35  
ENCODER_BTN_PIN = 13

# Object initialization
encoder = RotaryIRQ(pin_num_clk=ENCODER_CLK_PIN, 
                    pin_num_dt=ENCODER_DT_PIN, 
                    min_val=0, 
                    max_val=100, 
                    reverse=False, 
                    range_mode=RotaryIRQ.RANGE_BOUNDED,
                    half_step=True)

encoder_btn = Pin(ENCODER_BTN_PIN, Pin.IN, Pin.PULL_UP)


# ON BUTTON #######################################
###################################################

# Pins
ON_BTN1_PIN = 12
ON_BTN2_PIN = 14
ON_BTN3_PIN = 27

# Object initialization
# on_btn = Pin(ON_BTN_PIN, Pin.IN)
on_btn1 = Pin(ON_BTN1_PIN, Pin.IN, Pin.PULL_UP)
on_btn2 = Pin(ON_BTN2_PIN, Pin.IN, Pin.PULL_UP)
on_btn3 = Pin(ON_BTN3_PIN, Pin.IN, Pin.PULL_UP)


###################################################
# LEDs ############################################

# Pins
OUTPUT_PINS = [15, 2, 0, 4, 16, 17, 5, 18, 19, 23]

# PWM parameters
frequency = 22000

# Object inicialization
outputs = [PWM(Pin(pin), frequency) for pin in OUTPUT_PINS]
for output in outputs:
    output.duty(0)


###################################################
#####################################################################################################

# ... (previous code) ...

class Controller:
    def __init__(self, modes, encoder, display):
        self.modes = modes
        self.encoder = encoder
        self.display = display
        self.current_mode_idx = 0
        self.edit_mode = False  # Track if editing mode is active
        encoder.set(range_mode=RotaryIRQ.RANGE_UNBOUNDED)
        self.prev_display_lines = [""] * len(modes)
        
        
    def save_modes(self, modes):
        try:
            # Ensure 'modes' is serializable; it should be a dict, list, etc.
            json_data = json.dumps(modes)
            with open("modes.json", "w") as file:
                file.write(json_data)
        except Exception as e:
            print("Error saving modes:", e)

    def load_modes(self):
        try:
            with open("modes.json", "r") as file:
                return json.loads(file.read())
        except Exception as e:
            print("Error loading modes:", e)
            return None


    def initialize_display(self):
        self.display.clear()
        max_colon_pos = max(len(mode['name']) for mode in self.modes) + 1

        for idx, mode in enumerate(self.modes):
            prefix = ">> " if idx == self.current_mode_idx else "   "
            line = f"{prefix}{mode['name']}:{' ' * (max_colon_pos - len(mode['name']))} {' ' * (3 - len(str(mode['value'])))}{mode['value']}"
            self.display.move_to(0, idx)
            self.display.putstr(line)
            self.prev_display_lines[idx] = line
            
        utime.sleep_ms(300)
    
    
    def refresh_display(self):
        print("REFRESH")
        
        if not self.edit_mode:
            # Update only the ">>" indicator when not in editing mode
            for idx in range(len(self.modes)):
                prefix = ">> " if idx == self.current_mode_idx else "   "
                if prefix != self.prev_display_lines[idx][:3]:
                    self.display.move_to(0, idx)
                    self.display.putstr(prefix)
                    self.prev_display_lines[idx] = prefix
        else:
            for idx, mode in enumerate(self.modes):
                max_colon_pos = max(len(mode['name']) for mode in self.modes) + 1
                prefix = ">> " if idx == self.current_mode_idx else "   "
                new_line = f"{prefix}{mode['name']}:{' ' * (max_colon_pos - len(mode['name']))} {' ' * (3 - len(str(mode['value'])))}{mode['value']}"
                prev_line = self.prev_display_lines[idx]

                # Find the first character position where the lines differ
                diff_pos = 15
                while diff_pos < len(new_line) and diff_pos < len(prev_line) and new_line[diff_pos] == prev_line[diff_pos]:
                    diff_pos += 1
                
                # Update only the differing section of the line
                if diff_pos < len(new_line):
                    updated_section = new_line[diff_pos:]
                    self.display.move_to(diff_pos, idx)

                    # Calculate how many characters from the previous line need to be cleared
                    clear_chars = len(prev_line) - diff_pos

                    # Clear characters from the previous line
                    self.display.putstr(" " * clear_chars)

                    # Update the differing section with the new value
                    self.display.move_to(diff_pos, idx)
                    self.display.putstr(updated_section)
                    self.prev_display_lines[idx] = new_line
        
            utime.sleep_ms(300)
            
    def next_mode(self):
        if not self.edit_mode:
            if self.encoder.value() > encoder_val_old:
                self.current_mode_idx = (self.current_mode_idx + 1) % len(self.modes)
            else:
                self.current_mode_idx = (self.current_mode_idx - 1) % len(self.modes)
            
        self.refresh_display()

    def toggle_edit_mode(self):
        print("toggle edit mode")
        if self.edit_mode:
            self.encoder.set(range_mode=RotaryIRQ.RANGE_UNBOUNDED)
            self.save_modes(self.modes)  # Save modes when exiting edit mode
        else:
            print("self.current_mode_idx: " + str(self.current_mode_idx))
            mode = self.modes[self.current_mode_idx]
            self.encoder.set(value=mode['value'], min_val=mode['min'], max_val=mode['max'], incr=mode['incr'], range_mode=RotaryIRQ.RANGE_BOUNDED)
            
        self.edit_mode = not self.edit_mode


    def encoder_turned(self):
        print("value changed")
        if self.edit_mode:
            print("encoder turned in edit mode")
            self.modes[self.current_mode_idx]['value'] = self.encoder.value()
            print("value: " + str(self.modes[self.current_mode_idx]['value']))
            self.refresh_display()
        else:
            self.next_mode()


# Modes
modes = [
    {'name': 'BRIGHTNESS ', 'value': 80, 'min': 5, 'max': 100, 'incr': 5},
    {'name': 'TIMER(min) ', 'value': 10, 'min': 10, 'max': 720, 'incr': 10},
    {'name': 'UPTIME(s)  ', 'value': 10, 'min': 1, 'max': 60, 'incr': 1},
    {'name': 'DOWNTIME(s)', 'value': 10, 'min': 0, 'max': 60, 'incr': 1}
]


# Callbacks
def encoder_pressed(pin):
    controller.toggle_edit_mode()
    
encoder_btn.irq(trigger=Pin.IRQ_FALLING, handler=encoder_pressed)

def on_btn_pressed(pin):
    
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    
    global disable
    global disable_signal
    
    # Debounce
    global last_pressed_time
    ms = utime.ticks_ms()
    if last_pressed_time + 500 >= ms:
        return
    last_pressed_time = ms
    
    print("got through debounce")
    
    if not disable:
        print("RUNNING LED SEQUENCE")
        disable_signal.clear()
        uasyncio.create_task(run_led_sequence(disable_signal))
    else:
        print("DISABLE SIGNAL SET")
        disable_signal.set()
    disable = not disable
    
    
on_btn1.irq(trigger=Pin.IRQ_FALLING, handler=on_btn_pressed)
on_btn2.irq(trigger=Pin.IRQ_FALLING, handler=on_btn_pressed)
on_btn3.irq(trigger=Pin.IRQ_FALLING, handler=on_btn_pressed)


# Instantiate controller
controller = Controller(modes, encoder, display)


# New asynchronous function to run the LED sequence
async def run_led_sequence(disable_signal):
    num_leds = len(outputs)
    tasks = []
    for i, output in enumerate(outputs):
        delay_before_start = controller.modes[2]['value'] * i / num_leds
        task = uasyncio.create_task(activate_output(output, delay_before_start, disable_signal))
        tasks.append(task)



# Async function to handle LED outputs
async def activate_output(output, delay_before_start, disable_signal):
    print("activating led " + str(output))
    BRIGHTNESS = controller.modes[0]['value']
    TIMER = controller.modes[1]['value']
    ONTIME = controller.modes[2]['value']
    DOWNTIME = controller.modes[3]['value']

    max_brightness = BRIGHTNESS * 10 + 23

    # Wait for the delay before starting the activation sequence
    await uasyncio.sleep(delay_before_start)

    # Gradually increase brightness over ONTIME
    steps = 25
    total_steps = ONTIME * steps
    for step in range(total_steps):
        if disable_signal.is_set():
            print("in break")
            break  # Skip to the off phase if disable signal is set
        brightness = (max_brightness * step) // total_steps
        output.duty(brightness)
        await uasyncio.sleep(1 / steps)

    if not disable_signal.is_set():
        # Keep the LEDs on, but check for disable signal periodically
        timer_seconds = TIMER * 60
        while timer_seconds > 0:
            if disable_signal.is_set():
                print("in break")
                break  # Skip to the off phase if disable signal is set
            
                #disable_signal.clear()
            await uasyncio.sleep(1)
            timer_seconds -= 1
            
    await uasyncio.sleep(delay_before_start)

    # Gradually decrease brightness over DOWNTIME
    total_steps = DOWNTIME * steps
    for step in range(total_steps, 0, -1):
        #if disable_signal.is_set():
            #break  # Turn off immediately if disable signal is set
        brightness = (max_brightness * step) // total_steps
        output.duty(brightness)
        await uasyncio.sleep(1 / steps)

    # Turn off the LED
    output.duty(0)


    
encoder_val_old = None

# Main Loop (Async)
async def main():
    
    loaded_modes = controller.load_modes()
    if loaded_modes:
        controller.modes = loaded_modes
        
    global disable
    disable = False
        
    global disable_signal
    disable_signal.clear()
        
    global encoder_val_old
    encoder_val_old = encoder.value()
    
    controller.initialize_display()
    
    while True:
        
        # Read and update values from the rotary encoder
        if encoder.value() != encoder_val_old:
            print("if condition in main")
            await uasyncio.sleep_ms(200)
            controller.encoder_turned()
            encoder_val_old = encoder.value()
        
        await uasyncio.sleep_ms(100)


# Start event loop and run entry point coroutine
uasyncio.run(main())