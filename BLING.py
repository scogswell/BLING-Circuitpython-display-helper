# A Class helper for UnexpectedMaker BLING to make interacting with the
# 2D matrix display easier.
#
# Steven Cogswell February 2024
# https://github.com/scogswell
#
# Get your own BLING: https://unexpectedmaker.com/bling
# More BLING On github: https://github.com/UnexpectedMaker/bling

import neopixel
from adafruit_bitmap_font.bdf import BDF
from adafruit_bitmap_font.pcf import PCF
import adafruit_framebuf
import struct

class display(object):
    """A Class object to interface with the 40x8 led matrix on UM BLING"""

    def __init__(self, matrix: neopixel.NeoPixel, rotation=2):
        # print("I'm a new displsay")
        self._width, self._height = self.pixel_size()
        # self._height = 8
        self._num_pixels = self._width * self._height
        if rotation not in [0,1,2,3]:
            raise ValueError("Rotation must be one of 0,1,2,3")
        self._rotation = rotation
        self._matrix = matrix

    @staticmethod
    def pixel_size():
        """
        Static method that returns the pixel_width and pixel_height of the BLING display
        """
        return (40,8)

    @property
    def rotation(self):
        """Returns the current rotation of the BLING display (0,1,2,3)"""
        return self._rotation

    @rotation.setter
    def rotation(self,value):
        """Set the rotation of the BLING display (0,1,2,3)"""
        self._rotation = value

    @property
    def num_pixels(self):
        """Returns the total number of led pixels on UM BLING"""
        return self._num_pixels

    @property
    def width(self):
        """
        Returns the viewport width of led pixels on BLING, accounting
        for rotation mode
        """
        if self._rotation in [0,2]:
            return self._width
        else:
            return self._height

    @property
    def height(self):
        """
        Returns the viewport height of led pixels on BLING, accounting
        for rotation mode
        """
        if self._rotation in [0,2]:
            return self._height
        else:
            return self._width

    def xy_to_array(self,x,y):
        """
        Function that converts an x,y coordinate into a Neopixel array index.
        Accounts for rotation mode.  Top left is always x=0,y=0

        Will return None if pixel is outside BLING array area.
        You may have to test separately if (x,y) is in the bounds of the display
        depending on rotation. We don't do it here because an every-pixel
        operation really slows things down.
        """
        if self._rotation == 2:
            loc = (39-x) + (7-y)*40
        elif self._rotation == 0:
            loc = x+y*40
        elif self._rotation == 1:
            loc = (39-y) + x*40
        elif self._rotation == 3:
            loc = y+(7-x)*40
        if 0<= loc <= 319:
            return loc
        else:
            return None

    def show(self):
        """
        Write the led pixel values to BLING and update display.  Like Neopixel .show()
        """
        self._matrix.show()

    def clear(self):
        """
        Always clears all BLING led pixels to black and updates display
        """
        self._matrix.fill(0x000000)
        self.show()

    def fill(self,color):
        """
        Fill BLING led pixels with a single color.   Like Neopixel .fill()
        """
        self._matrix.fill(color)

    def setpixel(self,x,y,color):
        """
        Sets a single pixel at x,y to a color. Accounts for rotation mode.
        """
        index = self.xy_to_array(x,y)
        if index is not None:
            self._matrix[index]=color

    def text(self, text, font, x, y, color_foreground, color_background=None, show=False):
        """
        Draws text at x,y coordinate using specified font.

        :param text: text to display
        :param font: font can be a Adafruit_Bitmap_font (PCF or BDF)
                    object.  Or a string which indicates a ".bin" circuitpython/micropython format
                    (i.e. - "font5x8.bin")
        :param x,y: x,y coordinates to place top left of text box
        :param color_foreground: color of the text
        :param color_background: if a color, the background color behind the text.  If None, then no background is drawn,
                                good for compositing over other BLING pixels.
        :param show: if true, text is shown immediately on BLING display
        """
        view_width = self.width
        view_height = self.height
        if isinstance(font, (PCF,BDF)):
            # This is a font object from Adafruit_Bitmap_Font, probably
            _, height, _, dy = font.get_bounding_box()
            font.load_glyphs(text)
            for yg in range(height):
                y_matrix = yg+y
                x_matrix = x
                if ( 0 <= y_matrix < view_height):
                    for c in text:
                        glyph = font.get_glyph(ord(c))
                        if not glyph:
                            continue
                        p=0
                        glyph_y = yg + (glyph.height - (height + dy)) + glyph.dy
                        if 0 <= glyph_y < glyph.height:
                            for i in range(glyph.width):
                                value = glyph.bitmap[i, glyph_y]
                                pixel = color_background
                                if value > 0:
                                    pixel = color_foreground
                                if (0 <= x_matrix < view_width):
                                    index = self.xy_to_array(x_matrix,y_matrix)
                                    if index is not None and pixel is not None:
                                        self._matrix[index]=pixel
                                x_matrix += 1
                                p+=1
                        else:
                            # empty section for this glyph
                                pass
                        for i in range(glyph.shift_x-p):
                            if (0 <= x_matrix < view_width):
                                index = self.xy_to_array(x_matrix,y_matrix)
                                if index is not None and color_background is not None:
                                    self._matrix[index]=color_background
                            x_matrix += 1

        elif isinstance(font,str):
            # https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/adafruit_framebuf.py#L608
            # This is likely a circuitpython/micropython binary fixed size ".bin" font like font5x8.bin
            font_bin = adafruit_framebuf.BitmapFont(font)
            size=1
            font_gap = 1
            font_width = font_bin.font_width
            font_height = font_bin.font_height
            for chunk in text.split("\n"):
                for i, char in enumerate(chunk):
                    text_x = x + (i * (font_width + font_gap)) * size
                    if (
                        text_x + (font_width * size) > 0
                        and text_x < view_width
                        and y + (font_height * size) > 0
                        and y < view_height
                    ):
                        # Go through each column of the character + the gap between characters.
                        for char_x in range(font_width+font_gap):
                            if char_x < font_width:
                                # Grab the byte for the current column of font data.
                                font_bin._font.seek(2 + (ord(char) * font_width) + char_x)
                                try:
                                    line = struct.unpack("B", font_bin._font.read(1))[0]
                                except RuntimeError:
                                    continue  # maybe character isnt there? go to next
                            else:
                                line = 0  # the gap between characters
                            # Go through each row in the column byte.
                            for char_y in range(font_bin.font_height):
                                # Draw a pixel for each bit that's flipped on.
                                x_matrix = text_x + char_x * size
                                y_matrix = y + char_y * size
                                if (0 <= x_matrix < view_width and 0 <= y_matrix < view_height):
                                    index = self.xy_to_array(x_matrix, y_matrix)
                                    if (line >> char_y) & 0x1:
                                        if index is not None:
                                            self._matrix[index]=color_foreground
                                    else:
                                        if index is not None and color_background is not None:
                                            self._matrix[index]=color_background
                y += font_height * size

        if show:
            self._matrix.show()

    def bitmap(self,image, palette, x,y):
        """
        Display a displayio-compatible bitmap on BLING display.  Like what you get from Adafruit_Imageload

        :param image: displayio-compatible bitmap object
        :param palette: palette associated with image, if None, will convert from RGB565_Swapped colorspace
                        to RGB888 on BLING display (used by gifio)
        :param x,y: coordinates on BLING display to show the bitmap's top left corner, accounts for rotation
        """
        self.bitmap_tile(image, palette,x,y,0,0,image.width,image.height)

    def bitmap_tile(self,image,palette,x,y,xb,yb,w,h):
        """
        Display a portion of a displayio-compatible bitmap on BLING display.  Can be used like
        displayio TileGrid

        :param image: displayio-compatible bitmap object
        :param palette: palette associated with image, if None, will convert from RGB565_Swapped colorspace
                        to RGB888 on BLING display (used by gifio)
        :param x,y: coordinates on BLING display to show the bitmap's top left corner, accounts for rotation
        :param xb,yb: the top left coordinates of the portion of the bitmap to be displayed
        :param w,h: width and height of the portion of the bitmap to be displayed
        """
        width = self.width
        height = self.height
        for y1 in range(h):
            yn = y1+y
            if (0 <= yn < height):
                for x1 in range(w):
                    xn = x1+x
                    if (0 <= xn < width):
                        if palette is not None:
                            self._matrix[self.xy_to_array(xn,yn)]=palette[image[xb+x1,yb+y1]]
                        else:
                            # gifio uses RGB565_Swapped, convert to RGB888 more or less
                            swap = ((image[xb+x1,yb+y1] & 0x00FF) << 8) | ((image[xb+x1,yb+y1] & 0xFF00) >> 8)
                            r = (swap & 0xF800) >> 8
                            g = (swap & 0x07E0) >> 3
                            b = (swap & 0x001F) << 3
                            self._matrix[self.xy_to_array(xn,yn)]=(r,g,b)

    def line(self, x_0, y_0, x_1, y_1, color):
        # Cribbed mercilessly from https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/adafruit_framebuf.py#L433
        # pylint: disable=too-many-arguments
        """
        Draw a line from x_0,y_0 to x_1,y_1 in color.  Uses Bresenham's line algorithm
        Based on Adafruit_CircuitPython_framebuf
        """
        d_x = abs(x_1 - x_0)
        d_y = abs(y_1 - y_0)
        x, y = x_0, y_0
        s_x = -1 if x_0 > x_1 else 1
        s_y = -1 if y_0 > y_1 else 1
        if d_x > d_y:
            err = d_x / 2.0
            while x != x_1:
                self.setpixel(x, y, color)
                err -= d_y
                if err < 0:
                    y += s_y
                    err += d_x
                x += s_x
        else:
            err = d_y / 2.0
            while y != y_1:
                self.setpixel(x, y, color)
                err -= d_x
                if err < 0:
                    x += s_x
                    err += d_y
                y += s_y
        self.setpixel(x, y, color)

    def hline_aligned(self,x,y,w,color):
        """
        Draws a horizontal line that's aliged with the wide-axis of the BLING display.  Used by hline()
        in cases of rotation (0,2)
        """
        x0 = max(0, min(self.width-1,x))
        x1 = max(0, min(self.width-1,x+w-1))

        x0_index = self.xy_to_array(x0,y)
        x1_index = self.xy_to_array(x1,y)

        if (x0_index is not None and x1_index is not None):
            if (x1_index > x0_index):
                self._matrix[x0_index:x1_index+1] =  [color]*(x1_index-x0_index+1)
            else:
                self._matrix[x1_index:x0_index+1] =  [color]*(x0_index-x1_index+1)

    def vline_aligned(self,x,y,h,color):
        """
        Draws a vertical line that's aliged with the wide-axis of the BLING display.  Used by hline()
        in cases of rotation (1,3)

        """
        y0 = max(0, min(self.height-1,y))
        y1 = max(0, min(self.height-1,y+h-1))

        y0_index = self.xy_to_array(x,y0)
        y1_index = self.xy_to_array(x,y1)

        if (y0_index is not None and y1_index is not None):
            if (y1_index > y0_index):
                self._matrix[y0_index:y1_index+1] =  [color]*(y1_index-y0_index+1)
            else:
                self._matrix[y1_index:y0_index+1] =  [color]*(y0_index-y1_index+1)

    def hline(self,x,y,w,color):
        """
        Draws a horiztonal line, accounting for rotation.  Will use an optimized function if the line
        is along the wide-axis of BLING display
        """
        if w <= 0:
            return
        if self._rotation in [0,2]:
            self.hline_aligned(x,y,w,color)
        else:
            self.hline_direct(x,y,w,color)

    def vline(self,x,y,h,color):
        """
        Draws a vertical line, accounting for rotation.  Will use an optimized function if the line
        is along the wide-axis of BLING display
        """
        if h <= 0:
            return
        if self._rotation in [1,3]:
            self.vline_aligned(x,y,h,color)
        else:
            self.vline_direct(x,y,h,color)

    def hline_direct(self,x,y,w,color):
        """
        Draws a horiztonal line, no optimization case.  Use hline() instead if possible.
        """
        if 0<= y < self.height:
            for i in range(w):
                if (0 <= x+i < self.width):
                    self.setpixel(x+i,y,color)

    def vline_direct(self,x,y,h,color):
        """
        Draws a vertical line, no optimization case.  Use hline() instead if possible.
        """
        if 0 <= x < self.width:
            for i in range(h):
                if (0 <= y+i < self.height):
                    self.setpixel(x,y+i,color)


    def circle(self, center_x, center_y, radius, color):
        # mercilessly cribbed from https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/dd4c4e927819f51ff1b1aa45ff11750581628d79/adafruit_framebuf.py#L369
        """Draw a circle at the given midpoint location, radius and color.
        The ```circle``` method draws only a 1 pixel outline.
        Based on Adafruit_CircuitPython_framebuf
        """
        x = radius - 1
        y = 0
        d_x = 1
        d_y = 1
        err = d_x - (radius << 1)
        while x >= y:
            self.setpixel(center_x + x, center_y + y, color)
            self.setpixel(center_x + y, center_y + x, color)
            self.setpixel(center_x - y, center_y + x, color)
            self.setpixel(center_x - x, center_y + y, color)
            self.setpixel(center_x - x, center_y - y, color)
            self.setpixel(center_x - y, center_y - x, color)
            self.setpixel(center_x + y, center_y - x, color)
            self.setpixel(center_x + x, center_y - y, color)
            if err <= 0:
                y += 1
                err += d_y
                d_y += 2
            if err > 0:
                x -= 1
                d_x += 2
                err += d_x - (radius << 1)

    def fill_rect(self, x,y,w,h,color):
        """
        Draws a filled rectangle, accounting for rotation

        :param x,y: corner or rectangle
        :param w,h: width and height of rectangle
        """
        if w<=0 or h<=0:
            return
        if self._rotation in [0,2]:
            for y in range(y,y+h):
                self.hline(x,y,w,color)
        else:
            for x in range(x,x+w):
                self.vline(x,y,h,color)

    def rect(self,x,y,w,h,color,fill=False):
        """
        Draws a rectangle, accounting for rotation, with optional fill

        :param x,y: corner or rectangle
        :param w,h: width and height of rectangle
        :param fill: if True, rectangle will be filled, otherwise just the outline is drawn
        """
        if w<=0 or h<=0:
            return
        if fill:
            self.fill_rect(x,y,w,h,color)
        else:
            self.hline(x,y,w,color)
            self.hline(x,y+h-1,w,color)
            self.vline(x,y,h,color)
            self.vline(x+w-1,y,h,color)
