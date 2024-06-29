import uasyncio
from machine import Pin, PWM
import utime

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
        
        
        self.startup_time_seconds = startup_time_seconds
        self.shutdown_time_seconds = shutdown_time_seconds
        
        self.state = OFF
        
        self.interrupt = False
        self.interrupt_confirm = False
        
        self._log("Array created")
        
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
            
    def _log(self, message):
        print("\n" + __file__ + " : " + str(message))
        return
            
    async def _interrupt_toggle(self):
        self.interrupt = True
            
        # Await propagation of interrupt
        while not self.interrupt_confirm:
            await uasyncio.sleep(0.01)
                
        # Reset interrupt and interrupt confirmation
        self.interrupt = False
        self.interrupt_confirm = False
        
        
    # Turns all light circuits on or off based on the value of 'self.state'.
    def toggle(self):
        
        # Prevents the function from executing if the state is already being changed
        # Present in case the function is toggled multiple times in short succession
        if self.interrupt:
            self.log("Array toggle dropped")
            return
        
        if self.state == OFF:
            self.state = TURNING_ON
            # Turn all circuits on gradually, one by one
            for circuit in self.circuits:
                await circuit.nudge_on()
                #await uasyncio.sleep(self.startup_time_seconds)
                if self.interrupt:
                    self.interrupt_confirm = True;
                    break
                
            self.state = ON
            
        elif self.state == TURNING_ON:
            # Interrupt the turning on off the array
            self._interrupt_toggle()
            # Turn all circuits on instantaneously
            await uasyncio.gather(*(circuit.jump_on() for circuit in self.circuits))
            
        elif self.state == ON:
            self.state = TURNING_OFF
            # Turn all circuits off gradually, one by one
            for circuit in reversed(self.circuits):
                await circuit.nudge_off()
                if self.interrupt:
                    self.interrupt_confirm = True;
                    break
                
            self.state = OFF
            
        elif self.state == TURNING_OFF:
            # Interrupt the turning off of the array
            self._interrupt_toggle()
            # Turn all circuits off instantaneously
            for circuit in self.circuits:
                await circuit.jump_off()
            
# Class used to control individual light circuits separatelly
class lightCircuit:
    def __init__(self, pin_number, frequency, fps, brightness_percentage, startup_time_seconds, shutdown_time_seconds):
        
        self.pwm_object = PWM(Pin(pin_number), freq=frequency)
        self.pwm_object.duty(0)
        
        self.pin_number = pin_number
        
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
        
        self._log("Circuit created")
        
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
        
    def _log(self, message):
        log_message = "\n{} : Circuit {:>2} : {}".format(__file__, self.pin_number, message)
        print(log_message)
        return

        
    # Turns the circuit on gradually, taking startup_time_seconds if beginning from the OFF state
    async def _turn_on(self):
        self._log("Changed state to 'TURNING_ON'.")
        #start_time = utime.ticks_ms()
        self.state = TURNING_ON
            
        while not self.pwm_object.duty() >= self.target_brightness:
            self.virtual_duty = min(self.virtual_duty + self.startup_brightness_step, 1023)
            self.pwm_object.duty(int(self.virtual_duty))
            await uasyncio.sleep(1 / self.fps)
            if self.interrupt:
                self.interrupt_confirm = True;
                break
                
        self._log("Changed state to 'ON'.")
        self.state = ON
        
    # Turns the circuit off gradually, taking shutdown_time_seconds if beginning from the ON state
    async def _turn_off(self):
        self._log("Changed state to 'TURNING_OFF'.")
        self.state = TURNING_OFF
            
        while not self.pwm_object.duty() <= 0:
            self.virtual_duty = max(self.virtual_duty - self.shutdown_brightness_step, 0)
            self.pwm_object.duty(int(self.virtual_duty))
            await uasyncio.sleep(1 / self.fps)
            if self.interrupt:
                self.interrupt_confirm = True;
                break
            
        self._log("Changed state to 'OFF'.")
        self.state = OFF
        self.pwm_object.duty(0)
        
    # Turns the circuit on instantaneously
    async def _instant_on(self):
        self.pwm_object.duty(int(1023 / 100 * self.brightness))
        self.virtual_duty = int(1023 / 100 * self.brightness)
        
    # Turns the circuit off instantaneously
    async def _instant_off(self):
        self.pwm_object.duty(0)
        self.virtual_duty = 0
        
    # When called, interrupts the execution of the turn_on() or turn_off() functions
    async def _interrupt_turn_on_off(self):
        # Interrupt the starting up of the light
        self.interrupt = True
            
        # Await propagation of interrupt
        while not self.interrupt_confirm:
            await uasyncio.sleep(0.01)
                
        # Reset interrupt and interrupt confirmation
        self.interrupt = False
        self.interrupt_confirm = False
        
    async def toggle_gradual(self):
        
        # Prevents the function from executing if the state is already being changed
        # Present in case the function is toggled multiple times in short succession
        if self.interrupt:
            return
        
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
        
    # 
    async def toggle_with_skip(self):
        
        # Prevents the function from executing if the state is already being changed
        # Present in case the function is toggled multiple times in short succession
        if self.interrupt:
            self._log("Circuit toggle dropped")
            return
        
        if self.state == OFF:
            # Begin turning on the circuit gradually
            await self._turn_on()
            
        elif self.state == TURNING_ON:
            # Interrupt the turning on of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit on instantaneously
            await self._instant_on()
            
        elif self.state == ON:
            # Begin turning off the circuit gradually
            await self._turn_off()
            
        elif self.state == TURNING_OFF:
            # Interrupt the turning off of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit off instantaneously
            await self._instant_off()
            
    # Turns the circuit on instantaneously, no matter its state
    async def jump_on(self):
        if self.state == OFF:
            # Turn the circuit on instantaneously
            await self._instant_on()
            
        elif self.state == TURNING_ON:
            # Interrupt the turning on of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit on instantaneously
            await self._instant_on()
            
        elif self.state == ON:
            # Do nothing
            return
            
        elif self.state == TURNING_OFF:
            # Interrupt the turning off of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit on instantaneously
            await self._instant_on()
            
    # Turns the circuit off instantaneously, no matter its state
    async def jump_off(self):
        if self.state == OFF:
            # Do nothing
            return
            
        elif self.state == TURNING_ON:
            # Interrupt the turning on of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit off instantaneously
            await self._instant_off()
            
        elif self.state == ON:
            await self._instant_off()
            
        elif self.state == TURNING_OFF:
            # Interrupt the turning off of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit off instantaneously
            await self._instant_off()
            
    async def nudge_on(self):
        if self.state == OFF:
            # Begin turning on the circuit gradually
            await self._turn_on()
            
        elif self.state == TURNING_ON:
            # Do nothing
            return
        
        elif self.state == ON:
            # Do nothing
            return
        
        elif self.state == TURNING_OFF:
            # Interrupt the turning off of the circuit
            await self._interrupt_turn_on_off()
            # Turn the circuit on gradually
            await self._turn_on()
            
    async def nudge_off(self):
        if self.state == OFF:
            # Do nothing
            return
        
        if self.state == TURNING_ON:
            # Interrupt the turning on of the circuit
            await self._interrupt_turn_on_off()
            # Begin turning the circuit off gradually
            await self._turn_off()
            
        if self.state == ON:
            # Begin turning off the circuit gradually
            await self._turn_off()
            
        if self.state == TURNING_OFF:
            # Do nothing
            return
