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
    def __init__(self, pin_number_array, frequency, fps, brightness_percentage, startup_time_seconds, shutdown_time_seconds):
        
        self.circuits = []
        
        # Creates a lightCircuit for each pin number in the pin_number_array
        for pin_number in pin_number_array:
            circuit = lightCircuit(pin_number, frequency, fps, brightness_percentage, startup_time_seconds, shutdown_time_seconds)
            self.circuits.append(circuit)
        
        
        self.state = OFF
        
    def array_update(self, brightness_percentage, startup_time_seconds, shutdown_time_seconds):
        """Update all light circuits' properties in the array.

        Parameters:
        - brightness_percentage (float): The new brightness percentage.
        - startup_time_seconds (float): The new startup time in seconds.
        - shutdown_time_seconds (float): The new shutdown time in seconds.
        """
        
        # Update each circuit in the array with the new parameters
        for circuit in self.circuits:
            circuit.circuit_update(brightness_percentage, startup_time_seconds, shutdown_time_seconds)
        
        
    # Turns all light circuits on or off based on the value of 'self.state'.
    def array_toggle(self):
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
        
        # The virtual duty variable is used to have precision control over the length of each brightness step
        # This is desirable in order to achieve precise timing of the turn-on sequence, as it is in fact timed by the number of steps
        # The duty of pwm object has to be an integer, which results in less precise steps and less control, hence this variable is here
        self.virtual_duty = 0
        
        self.target_brightness = 1023 / 100 * brightness_percentage
        
        # The multiplication by 0.8325 is used to fine tune the number of frames to compensate for execution time
        self.startup_frames_count = startup_time_seconds * fps * 0.8325
        self.startup_brightness_step = self.target_brightness / self.startup_frames_count
        
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
        
    async def _turn_on(self):
        print(FILE + "Circuit 1 : Changed state to 'TURNING_ON'.\n")
        start_time = utime.ticks_ms()
        self.state = TURNING_ON
            
        while not self.pwm_object.duty() >= self.target_brightness:
            self.virtual_duty = min(self.virtual_duty + self.startup_brightness_step, 1023)
            self.pwm_object.duty(int(self.virtual_duty))
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
        
    async def _turn_off(self):
        print(FILE + "Circuit 1 : Changed state to 'TURNING_OFF'.\n")
        start_time = utime.ticks_ms()
        self.state = TURNING_OFF
        
        print("self.shutdown_brightness_step = " + str(self.shutdown_brightness_step))
            
        while not self.pwm_object.duty() <= 0:
            self.virtual_duty = max(self.virtual_duty - self.shutdown_brightness_step, 0)
            self.pwm_object.duty(int(self.virtual_duty))
            await uasyncio.sleep(1 / self.fps)
            if self.interrupt:
                self.interrupt_confirm = True;
                print("interrupted")
                break
            
        print(FILE + "Circuit 1 : Changed state to 'OFF'.\n")
        end_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(end_time, start_time)  # Calculates the difference in a wrap-around safe manner
        print("Elapsed Time:", elapsed_time, "milliseconds")
        self.state = OFF
        self.pwm_object.duty(0)
        
    async def _interrupt_turn_on_off(self):
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
        
    async def toggle_gradual(self):
        
        if self.state == OFF:
            # Begin turning on the circuit gradually
            await self._turn_on()
            
        elif self.state == TURNING_ON:
            # Interrupt the turning on of the circuit
            await self._interrupt_turn_on_off()
            # Begin turning off the circuit gradually
            await self._turn_off()
            
        elif self.state == ON:
            # Begin turning off the circuit gradually
            await self._turn_off()
            
        elif self.state == TURNING_OFF:
            # Interrupt the turning off of the circuit
            await self._interrupt_turn_on_off()
            # Begin turning on the circuit gradually
            await self._turn_on()
        
    # Turns the circuit on or off based on the value of 'self.state'.
    async def toggle_with_skip(self):
        
        # Prevents the function from executing if the state is already being changed
        # Present in case the function is toggled multiple times in short succession
        if self.interrupt:
            print("circuit toggle dropped")
            return
        
        print("in circuit toggle")
        
        if self.state == OFF:
            # Begin turning on the circuit gradually
            await self._turn_on()
            
        elif self.state == TURNING_ON:
            # Interrupt the turning on of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit on instantaneously
            self.pwm_object.duty(int(1023 / 100 * self.brightness))
            self.virtual_duty = int(1023 / 100 * self.brightness)
            
        elif self.state == ON:
            # Begin turning off the circuit gradually
            await self._turn_off()
            
        elif self.state == TURNING_OFF:
            # Interrupt the turning off of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit off instantaneously
            self.pwm_object.duty(0)
            self.virtual_duty = 0
        