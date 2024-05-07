import uasyncio
from machine import Pin, PWM
import utime

# Stores the name of this file
# Used in order to maintain the correct indentation of debugging messages in the console
FILE = __file__ + " : "

# 

# Constants representing the possible states of the 'lightArray' and 'lightCircuit' objects.
OFF = 0
ON = 1
TURNING_ON = 2
TURNING_OFF = 3
    
# Class used to control all light circuits simultaneously.
class lightArray:
    def __init__(self):
        self.state = OFF
        
    # Turns all light circuits on or off based on the value of 'self.state'.
    def toggle(self):
        if self.state == OFF:
            self.state = TURNING_ON
            
        elif self.state == TURNING_ON:
            self.state = ON
            
        elif self.state == ON:
            self.state = TURNING_OFF
            
        elif self.state == TURNING_OFF:
            self.state = OFF
            
# Class used to control individual light circuits separatelly
class lightCircuit:
    def __init__(self, pin_number, frequency, fps, brightness_percentage, startup_time_seconds, shutdown_time_seconds):
        
        self.pwm_object = PWM(Pin(pin_number), freq=frequency)
        self.pwm_object.duty(0)
        
        # The multiplication by 0.8325 is used to fine tune the number of frames to compensate for execution time
        self.startup_frames_count = startup_time_seconds * fps * 0.8325
        self.startup_brightness_step = 1023 / 100 * brightness_percentage / self.startup_frames_count
        
        # The multiplication by 0.8325 is used to fine tune the number of frames to compensate for execution time
        self.shutdown_frames_count = shutdown_time_seconds * fps * 0.8325
        self.shutdown_brightness_step = 1023 / 100 * brightness_percentage / self.shutdown_frames_count
        
        self.fps = fps
        self.brightness = brightness_percentage
        
        self.state = OFF
        
        self.interrupt = False
        self.interrupt_confirm = False
        
    def circuit_update(self, brightness_percentage, startup_time_seconds, shutdown_time_seconds):
        """Update the light circuit's properties.

        Parameters:
        - brightness_percentage (float): The new brightness percentage.
        - startup_time_seconds (float): The new startup time in seconds.
        - shutdown_time_seconds (float): The new shutdown time in seconds.
        """
        
        self.startup_frames_count = startup_time_seconds * self.fps
        self.startup_brightness_step = 1023 / 100 * brightness_percentage / self.startup_frames_count
        
        self.shutdown_frames_count = shutdown_time_seconds * self.fps
        self.shutdown_brightness_step = 1023 / 100 * brightness_percentage / self.shutdown_frames_count
        
        self.brightness = brighntess_percentage
        
    # Turns the circuit on or off based on the value of 'self.state'.
    async def circuit_toggle(self):
        
        # Prevents the function from executing if the state is already being changed
        # Present in case the function is toggled multiple times in short succession
        if self.interrupt:
            print("circuit toggle dropped")
            return
        
        print("in circuit toggle")
        
        if self.state == OFF:
            print(FILE + "Circuit 1 : Changed state to 'TURNING_ON'.\n")
            start_time = utime.ticks_ms()
            print("Start Time: ", start_time)
            self.state = TURNING_ON
            
            for frame in range(self.startup_frames_count):
                self.pwm_object.duty(int(frame * self.startup_brightness_step))
                await uasyncio.sleep(1 / self.fps)
                if self.interrupt:
                    self.interrupt_confirm = True;
                    print("interrupted")
                    break
                
            print(FILE + "Circuit 1 : Changed state to 'ON'.\n")
            end_time = utime.ticks_ms()
            elapsed_time = utime.ticks_diff(end_time, start_time)  # Calculates the difference in a wrap-around safe manner
            print("Elapsed Time:", elapsed_time, "milliseconds")
            self.state = ON
            #self.interrupt_confirm = False
            
        elif self.state == TURNING_ON:
            
            # Interrupt the starting up of the light
            print("setting interrupt to true")
            self.interrupt = True
            
            # Await propagation of interrupt
            print("self.interrupt_confirm: " + str(self.interrupt_confirm))
            while not self.interrupt_confirm:
                await uasyncio.sleep(0.01)
                
            # Reset interrupt and interrupt confirmation
            self.interrupt = False
            self.interrupt_confirm = False
            
            # Turn light on instantaneously
            self.pwm_object.duty(int(1023 / 100 * self.brightness))
            
        elif self.state == ON:
            print(FILE + "Circuit 1 : Changed state to 'TURNING_OFF'.\n")
            self.state = TURNING_OFF
            
            for frame in range(self.shutdown_frames_count):
                self.pwm_object.duty(int((self.shutdown_frames_count - frame) * self.shutdown_brightness_step))
                await uasyncio.sleep(1 / self.fps)
                if self.interrupt:
                    self.interrupt_confirm = True;
                    print("interrupted")
                    break
            
            print(FILE + "Circuit 1 : Changed state to 'OFF'.\n")
            self.state = OFF
            #self.interrupt_confirm = False
            self.pwm_object.duty(0)
            
        elif self.state == TURNING_OFF:
            
            # Interrupt the starting up of the light
            print("setting interrupt to true")
            self.interrupt = True
            
            # Await propagation of interrupt
            while not self.interrupt_confirm:
                await uasyncio.sleep(0.01)
                
            # Reset interrupt and interrupt confirmation
            self.interrupt = False
            self.interrupt_confirm = False
            
            # Turn light off instantaneously
            self.pwm_object.duty(0)
        