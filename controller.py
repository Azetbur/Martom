JSON_FILENAME = "settings.json"

class Controller:

    def __init__(self, display):
        # Stores: BRIGHNTESS(%), TIMER(min), UPTIME(s), DOWNTIME(s), OVERLAP(S) 
        _settings_array = [85, 90, 9, 3, 0]
        
        no_lines = len(_settings_array)
        _active_line = 0
        _edit_mode = false
        _lcd = display
        
        # Try loading saved settings from json file
        try:
            
            # Check if the file exists
            if uos.stat(JSON_FILENAME):
                
                # Load the JSON string from the file
                with open(JSON_FILENAME, 'r') as file:
                    json_data = file.read()
                    
                # Convert the JSON string back to an array
                self._settings_array = ujson.loads(json_data)
            
        except OSError:
            # File does not exist
            print(f"File '{filename}' does not exist.")
        
        self._print_first_page()
        self.turned()

    # Pads numbers with spaces to be three characters long, returning them as strings
    def _pad(self, number):
        return f"{' ' * (3 - len(str(number)))}{number}"

    # Clears the lcd and prints the first page of settings
    def _print_first_page(self):
        lcd.clear()
        lcd.print("   BRIGHTNESS(%):" + self._pad(_settings_array[0]))
        lcd.print("   TIMER(min)   :" + self._pad(_settings_array[1]))
        lcd.print("   UPTIME(s)    :" + self._pad(_settings_array[2]))
        lcd.print("   DOWNTIME(s)  :" + self._pad(_settings_array[3]))
        
    # Clears the lcd and prints the second page of settings
    def _print_second_page(self):
        lcd.clear()
        lcd.print("   OVERLAP(%)   :" + self._pad(_settings_array[4]))

    def encoder_turned(self, encoder_value):
        
        # The encoder has been turned with no setting currently selected
        if not edit_mode:
            
            # On the lcd, handles scrolling from first to second page
            if active_line in range(0,3) and encoder not in range(0,3):
                self._print_first_page()
                
            # On the lcd, handles scrolling from second to first page
            if active line in range(4,7) and encoder not in range(4,7):
                self._print_second_page()
            
            # On the lcd, deletes the ">>" symbols from the previously active
            lcd.set_cursor(active_line, 0)
            lcd.print(">>")
            
            # On the lcd display, writes the ">>" symbols on the newly active line 
            lcd.set_cursor(encoder_value % (no_lines - 1), 0)
            lcd.print(">>")
            
            active_line = encoder_value
           
        # The encoder has been turned with a setting currently selected
        else:
            
            lcd.set_cursor(active_line, 17)
            lcd.print(self._pad(encoder_value))
            
            self._settings_array[_active_line] = encoder_value
            
    def encoder_pressed(self, lightArray):
        
        # The encoder has been pressed with no setting currently selected
        if edit_mode:
            
            # Update lightArray settings
            # TODO: Implement this
            
            # Save the new settings to a json file
            with open(JSON_FILENAME, 'w') as file:
                file.write(ujson.dumps(_settings_array))  
            
            
        edit_mode = not edit_mode
            
            
            
            
        