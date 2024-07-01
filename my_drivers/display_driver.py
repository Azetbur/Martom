from machine import I2C, Pin
import time

# LCD Commands
LCD_CLR = 0x01  # Clear display
LCD_HOME = 0x02  # Return home
LCD_ENTRY_MODE = 0x04  # Entry mode set
LCD_DISPLAY_CONTROL = 0x08  # Display on/off control
LCD_FUNCTION_SET = 0x20  # Function set
LCD_SET_DDRAM_ADDR = 0x80  # Set DDRAM address

# Flags for display entry mode
LCD_ENTRY_LEFT = 0x02
LCD_ENTRY_SHIFT_DECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAY_ON = 0x04
LCD_CURSOR_OFF = 0x00
LCD_BLINK_OFF = 0x00

# Flags for function set
LCD_4BIT_MODE = 0x00
LCD_2LINE = 0x08
LCD_5x8DOTS = 0x00

class Display:
    
    def __init__(self, sda_pin, scl_pin, freq, address):

        # Configure I2C
        i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)  # Adjust pins and frequency as needed
        
        self._ADDRESS = address
        
        # Initialize the lcd
        self._send_command(0x33)  # Initialize to 8-bit mode
        self._send_command(0x32)  # Switch to 4-bit mode
        self._send_command(LCD_FUNCTION_SET | LCD_4BIT_MODE | LCD_2LINE | LCD_5x8DOTS)
        self._send_command(LCD_DISPLAY_CONTROL | LCD_DISPLAY_ON | LCD_CURSOR_OFF | LCD_BLINK_OFF)
        self._send_command(LCD_CLR)  # Clear display
        self._send_command(LCD_ENTRY_MODE | LCD_ENTRY_LEFT | LCD_ENTRY_SHIFT_DECREMENT)
        time.sleep_ms(2)  # Wait for the command to be processed

    def _send_to_lcd(self, data, mode):
        high_nibble = mode | (data & 0xF0) | 0x08  # Send high nibble with backlight on
        low_nibble = mode | ((data << 4) & 0xF0) | 0x08  # Send low nibble with backlight on

        # Send high nibble
        i2c.writeto(self._ADDRESS, bytearray([high_nibble]))
        self._toggle_enable(high_nibble)

        # Send low nibble
         i2c.writeto(self._ADDRESS, bytearray([low_nibble]))
        self._toggle_enable(low_nibble)

    def _toggle_enable(self,data):
        time.sleep_us(500)
        i2c.writeto(self._ADDRESS, bytearray([data | 0x04]))  # Enable bit high
        time.sleep_us(500)
        i2c.writeto(self._ADDRESS, bytearray([data & ~0x04]))  # Enable bit low
        time.sleep_us(500)

    def _send_command(self, cmd):
        self._send_to_lcd(cmd, 0x00)

    def _send_data(self, data):
        self._send_to_lcd(data, 0x01)
        

    def clear(self):
        self._send_command(LCD_CLR)
        time.sleep_ms(2)  # Clear command needs a longer delay

    def cursor_set(row, col):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > 3:
            row = 3  # Limit to max row number
            self._send_command(LCD_SET_DDRAM_ADDR | (col + row_offsets[row]))

    def print(text):
        for char in text:
            self._send_data(ord(char))
