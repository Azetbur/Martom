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
    def __init__(self, pin_number_array, frequency, fps, brightness_percentage, timer_active_bool, timer_time_minutes, startup_time_seconds,
                 shutdown_time_seconds, overlap_percentage):
        
        self.circuits = []
        
        # Creates a lightCircuit for each pin number in the pin_number_array
        for pin_number in pin_number_array:
            circuit = lightCircuit(pin_number, frequency, fps, brightness_percentage, startup_time_seconds, shutdown_time_seconds)
            self.circuits.append(circuit)
        
        self.timer_active_bool = timer_active_bool
        self.timer_time_minutes = timer_time_minutes
        self.startup_time_seconds = startup_time_seconds
        self.shutdown_time_seconds = shutdown_time_seconds
        self.overlap_percentage = overlap_percentage
        
        # Holds the asynchronous timer task
        self._timer_task = None
        
        self.state = OFF
        
        self.interrupt = False
        self.interrupt_confirm = False
        
        self._log("Light array initialized")
        
    def array_update(self, brightness_percentage, timer_active_bool, timer_time_minutes, startup_time_seconds, shutdown_time_seconds,
                     overlap_percentage):
        """Update all light circuits' properties in the array.

        Parameters:
        - brightness_percentage (float): The new brightness percentage.
        - startup_time_seconds (float): The new startup time in seconds.
        - shutdown_time_seconds (float): The new shutdown time in seconds.
        """
        
        self.timer_active_bool = timer_active_bool
        self.timer_time_minutes = timer_time_minutes
        self.startup_time_seconds = startup_time_seconds
        self.shutdown_time_seconds = shutdown_time_seconds
        self.overlap_percentage = overlap_percentage
        
        # Update each circuit in the array with the new parameters
        for circuit in self.circuits:
            circuit.circuit_update(brightness_percentage, startup_time_seconds, shutdown_time_seconds)
            
    def _log(self, message):
        print("\n" + __file__ + " : " + str(message))
            
    async def _interrupt_toggle(self):
        self.interrupt = True
            
        # Await propagation of interrupt
        while not self.interrupt_confirm:
            await uasyncio.sleep(0.01)
                
        # Reset interrupt and interrupt confirmation
        self.interrupt = False
        self.interrupt_confirm = False
        
    # Waits for the specified delay and then toggles the lightArray
    async def _timer_function(self, delay):
        await uasyncio.sleep(delay * 60)
        
        self._log("Timer countdown reached, turning off array")
        
        # In case the turning on period is longer than the timer time
        if self.state == TURNING_ON:
            await self.toggle()
            
        # Spacing the two toggles in case the first triggers 
        await uasyncio.sleep(1)
            
        await self.toggle()
        
    
    async def _delay_checking_interrupt(self, delay_time_seconds, bool_flag_to_break):
        start_time = utime.ticks_ms()  # Get the current time in milliseconds
        while utime.ticks_diff(utime.ticks_ms(), start_time) < delay_time_seconds * 1000:
            await uasyncio.sleep(0.1)
            if self.interrupt:
                self.interrupt_confirm = True;
                bool_flag_to_break[0] = True;
                return
        if self.interrupt:
                self.interrupt_confirm = True;
                bool_flag_to_break[0] = True;
        
    # Turns all light circuits on or off based on the value of 'self.state'.
    async def toggle(self):
        
        # Prevents the function from executing if the state is already being changed
        # Present in case the function is toggled multiple times in short succession
        if self.interrupt:
            self._log("Array toggle dropped")
            return
        
        if self.state == OFF:
            self.state = TURNING_ON
            
            # Begin countdown of the off-timer if it is active
            if self.timer_active_bool:
                self._timer_task = uasyncio.create_task(self._timer_function(self.timer_time_minutes))
            
            # Turn all circuits on with set overlap
            for idx, circuit in enumerate(self.circuits):
                if idx == 0:
                    uasyncio.create_task(circuit.nudge_on())
                    
                else:
                    break_flag = [False]
                    
                    await self._delay_checking_interrupt(self.startup_time_seconds * (1 - (self.overlap_percentage / 100.0)), break_flag)
                    
                    if break_flag[0]:
                        break
                    
                    if not idx == len(self.circuits) - 1:
                        uasyncio.create_task(circuit.nudge_on())
                    else:
                        uasyncio.create_task(circuit.nudge_on())
                        await self._delay_checking_interrupt(self.startup_time_seconds, break_flag)
                        self.state = ON
            
                
            
            
        elif self.state == TURNING_ON:  
            # Interrupt the turning on off the array
            await self._interrupt_toggle()
            # Turn all circuits on instantaneously
            await uasyncio.gather(*(circuit.jump_on() for circuit in self.circuits))
            
            self.state = ON
            
        elif self.state == ON:
            self.state = TURNING_OFF
            
            # Attempt cancelation of the the off-timer
            try:
                self._timer_task.cancel()
                await self._timer_task  # Awaiting the cancellation to handle it gracefully
            except (uasyncio.CancelledError, RuntimeError):
                pass  # Ignore the cancelled error
            
            # Turn all circuits off with set overlap
            for idx, circuit in enumerate(reversed(self.circuits)):
                if idx == 0:
                    uasyncio.create_task(circuit.nudge_off())

                else:
                    break_flag = [False]
                    
                    await self._delay_checking_interrupt(self.shutdown_time_seconds * (1 - (self.overlap_percentage / 100.0)), break_flag)
                    
                    if break_flag[0]:
                        break
                    
                    if not idx == len(self.circuits) - 1:
                        uasyncio.create_task(circuit.nudge_off())
                    else:
                        uasyncio.create_task(circuit.nudge_off())
                        await self._delay_checking_interrupt(self.shutdown_time_seconds, break_flag)
                        self.state = OFF
                        
        elif self.state == TURNING_OFF:
            # Interrupt the turning off of the array
            await self._interrupt_toggle()
            # Turn all circuits off instantaneously
            await uasyncio.gather(*(circuit.jump_off() for circuit in self.circuits))
                
            self.state = OFF
            
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
        
        self.brightness = brightness_percentage
        
    def _log(self, message):
        log_message = "\n{} : Circuit {:>2} : {}".format(__file__, self.pin_number, message)
        print(log_message)
        return

        
    # Turns the circuit on gradually, taking startup_time_seconds if beginning from the OFF state
    async def _turn_on(self):
        self._log("Changed state to 'TURNING_ON'.")
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
        self.state = ON
        
    # Turns the circuit off instantaneously
    async def _instant_off(self):
        self.pwm_object.duty(0)
        self.virtual_duty = 0
        self.state = OFF
        
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
