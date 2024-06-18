import uasyncio
from machine import Pin, PWM
import utime

# Constants representing the possible states of the 'pwmArray' and 'pwmCircuit' objects.
OFF = 0
ON = 1
TURNING_ON = 2
TURNING_OFF = 3

class pwmArray:
    def __init__(self, pin_number_array, frequency, fps, brightness_percentage, startup_time_seconds, shutdown_time_seconds):
        """
        Initializes a new pwmArray object which controls a collection of pwmCircuit instances.

        Each pwmCircuit is associated with a pin from the pin_number_array and configured
        with the specified PWM settings and timing parameters.

        Parameters:
        - pin_number_array (list): A list of integers representing the GPIO pin numbers
          to which the PWM circuits are connected.
        - frequency (int): The frequency of the PWM signal in Hertz.
        - fps (int): Frames per second, used to calculate the update intervals for brightness adjustments.
        - brightness_percentage (float): Target brightness as a percentage, 0 to 100.
        - startup_time_seconds (float): The time in seconds over which the brightness should ramp up from 0 to the target brightness.
        - shutdown_time_seconds (float): The time in seconds over which the brightness should ramp down from the target brightness to 0.

        The constructor initializes each circuit with these parameters and sets up the initial state.
        """
        
        self.circuits = []
        
        # Creates a pwmCircuit for each pin number in the pin_number_array
        for pin_number in pin_number_array:
            circuit = pwmCircuit(pin_number, frequency, fps, brightness_percentage, startup_time_seconds, shutdown_time_seconds)
            self.circuits.append(circuit)
        
        # Defines the initial state of the array as OFF
        self.state = OFF
        
        # Flag to handle any interruptions in PWM signal transitions
        self.interrupt = False
        # Flag to confirm handling of interruptions
        self.interrupt_confirm = False
        
    def array_update(self, brightness_percentage, startup_time_seconds, shutdown_time_seconds):
        """
        Updates all light circuits' properties in the array.

        Parameters:
        - brightness_percentage (float): The new brightness percentage.
        - startup_time_seconds (float): The new startup time in seconds.
        - shutdown_time_seconds (float): The new shutdown time in seconds.
        """
        
        # Update each circuit in the array with the new parameters
        for circuit in self.circuits:
            circuit.circuit_update(brightness_percentage, startup_time_seconds, shutdown_time_seconds)
            
    async def _interrupt_toggle(self):
        """
        Asynchronously toggles an interrupt to handle the immediate stopping or modification of PWM operations.
    
        This method sets an interrupt flag to True, waits for the interrupt to be acknowledged, and then
        resets the interrupt flags. This is used to safely and quickly halt ongoing PWM operations
        across all circuits in response to state changes or external triggers.
        """

        self.interrupt = True
            
        # Await propagation of interrupt
        while not self.interrupt_confirm:
            await uasyncio.sleep(0.01)
                
        # Reset interrupt and interrupt confirmation
        self.interrupt = False
        self.interrupt_confirm = False
        
        
    # Turns all light circuits on or off based on the value of 'self.state'.
    async def toggle(self):
        """
        Asynchronously toggles the state of all circuits based on the current state of the array.

        State changes:
        - OFF to TURNING_ON: Gradually turns on all circuits.
        - TURNING_ON to ON: Interrupts the ongoing gradual turn-on process and turns all circuits on instantaneously.
        - ON to TURNING_OFF: Gradually turns off all circuits.
        - TURNING_OFF to OFF: Interrupts the ongoing gradual turn-off process and turns all circuits off instantaneously.
        """
        
        
        # Prevents the function from executing if the state is already being changed,
        # which could happen if the function is toggled multiple times in quick succession.
        if self.interrupt:
            return
        
        if self.state == OFF:
            self.state = TURNING_ON
            # Begins turning on all circuits gradually, one by one
            for circuit in self.circuits:
                await circuit.nudge_on()
                if self.interrupt:
                    self.interrupt_confirm = True;
                    break
                
            self.state = ON
            
        elif self.state == TURNING_ON:
            # Interrupts the ongoing turning-on of the array
            self._interrupt_toggle()
            # Turns all circuits on instantaneously
            await uasyncio.gather(*(circuit.jump_on() for circuit in self.circuits))
            
        elif self.state == ON:
            self.state = TURNING_OFF
            # Begins turning off all circuits gradually, one by one, in reverse order
            for circuit in reversed(self.circuits):
                await circuit.nudge_off()
                if self.interrupt:
                    self.interrupt_confirm = True;
                    break
                
            self.state = OFF
            
        elif self.state == TURNING_OFF:
            # Interrupts the ongoing turning-off of the array
            self._interrupt_toggle()
            # Turn all circuits off instantaneously
            for circuit in self.circuits:
                await circuit.jump_off()
            
class pwmCircuit:
    def __init__(self, pin_number, frequency, fps, brightness_percentage, startup_time_seconds, shutdown_time_seconds):
        """
        Initializes a new pwmCircuit object which controls a single PWM-driven light circuit.

        Parameters:
        - pin_number (int): The GPIO pin number to which the PWM signal is output.
        - frequency (int): The frequency of the PWM signal in Hertz.
        - fps (int): Frames per second, used to calculate the update intervals for brightness adjustments.
        - brightness_percentage (float): Target brightness as a percentage, 0 to 100.
        - startup_time_seconds (float): The time in seconds over which the brightness should ramp up from 0 to the target brightness.
        - shutdown_time_seconds (float): The time in seconds over which the brightness should ramp down from the target brightness to 0.

        Sets up the PWM on the specified pin with an initial duty cycle of 0 (off) and calculates the necessary steps for
        smooth brightness transitions based on provided parameters.
        """
        
        self.pwm_object = PWM(Pin(pin_number), freq=frequency)
        self.pwm_object.duty(0)
        
        # Storing pin number for console logging purposes
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
        
        print("circuit created")
        
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
        print(__file__ + " : Circuit " + str(self.pin_number) + " : " + str(message))
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
        #end_time = utime.ticks_ms()
        #elapsed_time = utime.ticks_diff(end_time, start_time)  # Calculates the difference in a wrap-around safe manner
        #print("Elapsed Time:", elapsed_time, "milliseconds")
        self.state = ON
        
    # Turns the circuit off gradually, taking shutdown_time_seconds if beginning from the ON state
    async def _turn_off(self):
        self._log("Changed state to 'TURNING_OFF'.")
        #start_time = utime.ticks_ms()
        self.state = TURNING_OFF
        
        #print("self.shutdown_brightness_step = " + str(self.shutdown_brightness_step))
            
        while not self.pwm_object.duty() <= 0:
            self.virtual_duty = max(self.virtual_duty - self.shutdown_brightness_step, 0)
            self.pwm_object.duty(int(self.virtual_duty))
            await uasyncio.sleep(1 / self.fps)
            if self.interrupt:
                self.interrupt_confirm = True;
                break
            
        self._log("Changed state to 'OFF'.")
        #end_time = utime.ticks_ms()
        #elapsed_time = utime.ticks_diff(end_time, start_time)  # Calculates the difference in a wrap-around safe manner
        #print("Elapsed Time:", elapsed_time, "milliseconds")
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
            print("circuit toggle dropped")
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
            
        