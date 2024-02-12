# BLING Circuitpython Display Helper and Demo

This is a demo showing how to use `BLING.py` to make 
using fonts, images, shapes, and animated gifs easier 
on the UnexpectedMaker BLING board. 

`BLING.py` gives you 2D access to the BLING led pixel grid
and abstracts away the Neopixel data structure to write to it. 

To use, copy `BLING.py` to your device.  import `BLING.py` and set up a display object:

```py
import BLING

# Setup BLING neopixel
bling_pixel_width, bling_pixel_height = BLING.display.pixel_size()
bling_num_pixels = bling_pixel_width * bling_pixel_height
BLING_raw = neopixel.NeoPixel(board.MATRIX_DATA,bling_num_pixels,brightness=BLING_BRIGHTNESS,auto_write=False)

# BLING display object
the_bling = BLING.display(matrix=BLING_raw,rotation=2)
```

With `BLING.py` you get access to these functions: 

`.pixel_size()` (static method) always returns 40,8 - the dimensions of BLING's led grid `w,h = BLING.display.pixel_size()`

`.rotation` (property) get/set the rotation of the BLING display (0,1,2,3) `the_bling.rotation=2` or `r = the_bling.rotation`.  Normally you set this in the constructor but this lets you rotate the display after the fact. 

`.num_pixels` (property) get the total number of led pixels on BLING (40*8)  `num = the_bling.num_pixels`

`.width` and `.height` (property) width and height of the BLING viewport, accounting for rotation

`.xy_to_array(x,y)` returns the array index converting x,y coordinate into neopixel array index, accounting for rotation. You don't normally need to use this but it's used by almost all the `BLING.py` functions internally. 

`.show()` updates the physical BLING display with led values. Use at the end of your display chain to actually write values out to the display.  

`.clear()` write all black to the BLING display and updates automatically 

`.fill(color)` fill BLING with a solid color, as neopixel `.fill(color)` function.

`.setpixel(x,y,color)` set a single pixel on BLING to a color, accounting for rotation 

`.text(text, font, x, y, color_foreground, color_background=None, show=False)` Dispays `text` on BLING using `font` which can either be a adafruit_bitmap_font object (PCF or BDF) or a string filename pointing to a .bin style font (ie `font5x8.bin`).  if `color_background` is a color, blank areas around the text are filled with that color.  if `color_background` is None then background pixels will not be written to (preseving pixels for lazy compositing)

`.bitmap(image, palette, x,y)` and `.bitmap_tile(self,image,palette,x,y,xb,yb,w,h):`  Show an `adafruit_imageload` compatible displaio bitmap at coordinates x,y.  for `.bitmap_tile` you can choose a subarea of the bitmap `x,y,w,h` and use it like how `TileGrid` works in `displayio`.  You can use this in conjunction with `gifio` to show (small) animated gifs on BLING, see the demo for detail.  

These shape functions account for rotation: 
* `.line(x_0, y_0, x_1, y_1, color):` Draw a line
* `.hline(x,y,w,color)` draw a horizatonal line 
* `.vline(x,y,h,color)` draw a vertical line 
* `.circle(center_x, center_y, radius, color)` draw a circle
* `.fill_rect(x,y,w,h,color)` draw a filled rectange
* `.rect(x,y,w,h,color,fill)` draw a rectagle outline, with optional fill

Notes: 

* Most drawing functions can extend outside the BLING physical display and just won't show up.  
* When you supply a `color` it can be in whatever is accepted by Neopixels, like a tuple of RGB `(128,255,32)` or a hexadecimal number `0xFFA322`

You need these libraries in /lib to satisfy dependencies:
* `adafruit_bitmap_font`
* `adafruit_imageload`
* `adafruit_led_animation`
* `adafruit_framebuf`
* `adafruit_pixel_framebuf`

https://github.com/scogswell/BLING-Circuitpython-display-helper/assets/3185255/17b2b02e-987c-454f-a1f6-67775d70cc35
