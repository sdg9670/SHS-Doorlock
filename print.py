
import monitor
from time import *

lcdControl = monitor.lcd()
lcdControl.lcd_clear()

asd = 'asdafasdfafas'
lcdControl.lcd_display_string(asd, 1)
lcdControl.lcd_display_string("zxvzxvzxv", 2)
