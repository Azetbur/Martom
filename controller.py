import uos
import ujson

from third_party_drivers.rotary_irq_esp import RotaryIRQ

JSON_FILENAME = "settings.json"

encoder_position_before_edit = None

class Controller:

    def __init__(self, brightness_percentage, timer_on_off_bool, timer_time_min, uptime_time_sec, downtime_time_sec, overlap_percentage,
                 display):
        
        # Stores: BRIGHNTESS(%), TIMER(on/off), TIMER(min), UPTIME(s), DOWNTIME(s), OVERLAP(S) 
        self.settings_array = [brightness_percentage, timer_on_off_bool, timer_time_min, uptime_time_sec, downtime_time_sec, overlap_percentage]
        
        self.no_lines = len(self.settings_array)
        self._active_line = 0
        self._edit_mode = False
        self._lcd = display
        
        # Try loading saved settings from json file
        try:
            
            # Check if the file exists
            if uos.stat(JSON_FILENAME):
                
                # Load the JSON string from the file
                with open(JSON_FILENAME, 'r') as file:
                    json_data = file.read()
                    
                # Convert the JSON string back to an array
                self.settings_array = ujson.loads(json_data)
            
        except OSError:
            # File does not exist
            print(f"File '{JSON_FILENAME}' does not exist.")

        self._print_first_page()
        self._lcd.cursor_set(0,0)
        self._lcd.print(">>")

    # Pads numbers with spaces to be three characters long, returning them as strings
    def _pad(self, number):
        return f"{' ' * (3 - len(str(number)))}{number}"
    
    def _bool_to_text(self, bool_value):
        return " ON" if bool_value else "OFF"

    # Clears the lcd and prints the first page of settings
    def _print_first_page(self):
        self._lcd.clear()
        self._lcd.print("   BRIGHTNESS(%):" + self._pad(self.settings_array[0]))
        self._lcd.cursor_set(1,0)
        self._lcd.print("   TIMER(on/off):" + self._bool_to_text(self.settings_array[1]))
        self._lcd.cursor_set(2,0)
        self._lcd.print("   TIMER(min)   :" + self._pad(self.settings_array[2]))
        self._lcd.cursor_set(3,0)
        self._lcd.print("   UPTIME(s)    :" + self._pad(self.settings_array[3]))
        
    # Clears the lcd and prints the second page of settings
    def _print_second_page(self):
        self._lcd.clear()
        self._lcd.print("   DOWNTIME(s)  :" + self._pad(self.settings_array[4]))
        self._lcd.cursor_set(1,0)
        self._lcd.print("   OVERLAP(%)   :" + self._pad(self.settings_array[5]))

    def encoder_turned(self, encoder_value):
        
        # The encoder has been turned with no setting currently selected
        if not self._edit_mode:
            
            # On the lcd, handles scrolling from first to second page
            if self._active_line in range(0,4) and encoder_value not in range(0,4):
                self._print_second_page()
                
            # On the lcd, handles scrolling from second to first page
            if self._active_line in range(4, self.no_lines) and encoder_value not in range(4, self.no_lines):
                self._print_first_page()
            
            # On the lcd, deletes the ">>" symbols from the previously active
            self._lcd.cursor_set(self._active_line % 4, 0)
            self._lcd.print("  ")
            
            # On the lcd display, writes the ">>" symbols on the newly active line 
            self._lcd.cursor_set(encoder_value % 4, 0)
            self._lcd.print(">>")
            
            self._active_line = encoder_value
           
        # The encoder has been turned with a setting currently selected
        else:
            
            self._lcd.cursor_set(self._active_line % 4, 17)
            
            # Line 1 contains on/off as supposed to numerical values and hence has to be treated differentlys
            if self._active_line == 1:
                self._lcd.print(self._bool_to_text(bool(encoder_value)))
                
                self.settings_array[self._active_line] = bool(encoder_value)
                
            else:
                self._lcd.print(self._pad(encoder_value))
            
                self.settings_array[self._active_line] = encoder_value
            
    def encoder_pressed(self, lightArray, encoder):
        global encoder_position_before_edit
        
        # The encoder has been pressed with a setting currently selected
        if self._edit_mode:
            
            # Update setting value in self.settings_array
            self.settings_array[encoder_position_before_edit] = encoder.value()
            
            # Update lightArray settings
            lightArray.array_update(brightness_percentage=self.settings_array[0],
                                    timer_active_bool=self.settings_array[1],
                                    timer_time_minutes=self.settings_array[2],
                                    startup_time_seconds=self.settings_array[3],
                                    shutdown_time_seconds=self.settings_array[4],
                                    overlap_percentage=self.settings_array[5])
            
            # Update encoder to scroll through setting
            encoder.set(value=encoder_position_before_edit, min_val=0, max_val=self.no_lines - 1, incr=1, range_mode=RotaryIRQ.RANGE_WRAP)
            
            # Save the new settings to a json file
            with open(JSON_FILENAME, 'w') as file:
                file.write(ujson.dumps(self.settings_array))
                
        else:
            
            encoder_position_before_edit = encoder.value()
            
            # Update encoder to behave according to setting being modifier
            if encoder.value() == 0:
                encoder.set(value=self.settings_array[0], min_val=5, max_val=100, incr=5, range_mode=RotaryIRQ.RANGE_BOUNDED)
            elif encoder.value() == 1:  
                encoder.set(value=int(self.settings_array[1]), min_val=0, max_val=1, incr=1, range_mode=RotaryIRQ.RANGE_WRAP)
            elif encoder.value() == 2:
                encoder.set(value=self.settings_array[2], min_val=10, max_val=720, incr=10, range_mode=RotaryIRQ.RANGE_BOUNDED)
            elif encoder.value() == 3:
                encoder.set(value=self.settings_array[3], min_val=1, max_val=60, incr=1, range_mode=RotaryIRQ.RANGE_BOUNDED)
            elif encoder.value() == 4:
                encoder.set(value=self.settings_array[4], min_val=0, max_val=60, incr=1, range_mode=RotaryIRQ.RANGE_BOUNDED)
            elif encoder.value() == 5:
                encoder.set(value=self.settings_array[5], min_val=0, max_val=100, incr=5, range_mode=RotaryIRQ.RANGE_BOUNDED)
                
               
        self._edit_mode = not self._edit_mode            
        