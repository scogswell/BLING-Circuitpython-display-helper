# A UnexpectedMaker BLING demo program in Circuitpython to demonstrate the BLING display
# convenience functions for shapes, fonts, images, and animated gifs.
#
# THIS DEMO HAS LOTS OF FLASHING LIGHTS.  If you are affected by such things use caution.
#
# Get your own BLING: https://unexpectedmaker.com/bling
# More BLING On github: https://github.com/UnexpectedMaker/bling
#
# Steven Cogswell February 2024

import board
import displayio
import digitalio
import neopixel
import time
from adafruit_bitmap_font import bitmap_font
import math
from adafruit_pixel_framebuf import PixelFramebuffer
import math
import adafruit_imageload
import gifio
import BLING
import random
import rainbowio

def bitmap_to_neopixel(b: displayio.Bitmap, n: neopixel):
    """ This function is only for the demo, to show speed comparison"""
    for y in range(b.height):
        for x in range(b.width):
            n[the_bling.xy_to_array(x,y)] = palette[b[x,y]]
    n.show()

def draw_text_on_bitmap(text, font, x, y, color_index, bitmap):
    """ This function is only for the demo, to show speed comparison"""
    # adapted from https://github.com/adafruit/Adafruit_CircuitPython_Bitmap_Font/blob/main/examples/bitmap_font_displayio_simpletest.py
    _, height, _, dy = font.get_bounding_box()
    font.load_glyphs(text)
    for yg in range(height):
        pixels = []
        y_matrix = yg+y
        x_matrix = x
        for c in text:
            glyph = font.get_glyph(ord(c))
            if not glyph:
                continue
            p=0
            glyph_y = yg + (glyph.height - (height + dy)) + glyph.dy
            if 0 <= glyph_y < glyph.height:
                for i in range(glyph.width):
                    value = glyph.bitmap[i, glyph_y]
                    pixel = 0
                    if value > 0:
                        pixel = color_index
                    pixels.append(pixel)
                    if (0 <= x_matrix < bling_pixel_width and 0 <= y_matrix < bling_pixel_height):
                        bitmap[x_matrix,y_matrix]=pixel
                    x_matrix += 1
                    p += 1
            else:
                # empty section for this glyph
                pass
            for i in range(glyph.shift_x-p):
                if (0 <= x_matrix < bling_pixel_width and 0 <= y_matrix < bling_pixel_height):
                    bitmap[x_matrix,y_matrix]=0
                x_matrix += 1

def gif_demo(rounds=4):
    """
    Demo of using gifio with BLING.py to play animated gifs
    """
    #
    #
    # Gifs processed with imagemagick:
    # convert $1 -coalesce -gamma 0.4 -resize 40x20^ -gravity center -extent 40x20 -dispose Background -alpha off  -interlace None -ordered-dither o4x4,32,64,32 -layers OptimizeFrame out.gif
    # get a black background probably.
    #
    # Displayio has access to the transparency data, but it appears the bitmap object itself does not.  So some
    # transparent background gifs may look weird if not processed to have actual black background pixels.
    GIFS="/gifs/"
    the_bling.fill((0,0,0))
    the_bling.show()
    choices = [
        "out.gif",
        "blinka-172x40.gif",
        "badger-172x40.gif",
        "LED-Glasses-172x40.gif",
        "led_matrices_ruby_walk.gif",
        ]
    for choice in choices:
        print("GIF",choice)
        odg = gifio.OnDiskGif(GIFS+choice)
        f=0
        p=0
        dir=1
        play_gif = True
        while(play_gif):
            start = time.monotonic()
            next_delay = odg.next_frame()
            the_bling.fill((0,0,0))
            the_bling.bitmap_tile(odg.bitmap,odg.palette,0,-p,0,0,40,22)
            the_bling.show()
            end = time.monotonic()
            overhead = end-start

            p += dir
            if p == 11 or p == 0:
                dir = -dir
            time.sleep(max(0, next_delay-overhead))
            f += 1
            if f > odg.frame_count * rounds:
                play_gif = False
                odg.deinit()

def image_demo():
    """
    Demo of images loaded from storage in static and animated-TileGrid style
    """
    print("Sparkles from tile")
    image, palette = adafruit_imageload.load("bmps/wow.bmp")
    for q in range(5):
        for f in range(8):
            the_bling.fill((0,0,0))
            the_bling.bitmap_tile(image, palette,0,-f,20*f,0,40,32)
            the_bling.show()
            time.sleep(0.05)
    image.deinit()

    rounds=5
    print("Twitch logo")
    image, palette = adafruit_imageload.load("bmps/twitchlogo.bmp")
    t=time.monotonic()
    for i in range(rounds):
        for d in range(0,360,5):
            x=int(image.height*2/3*math.sin(d*math.pi/180))
            y=int(image.height*2/3*math.cos(d*math.pi/180))
            the_bling.fill((0,0,0))
            the_bling.bitmap(image,palette,x+10,y)
            the_bling.show()
    image.deinit()

    image, palette = adafruit_imageload.load("bmps/catjamtiles.bmp")
    print("catJAM from tiled bmp")
    for d in range(0,60,2):
        the_bling.fill((0,0,0))
        the_bling.bitmap_tile(image,palette,60-d,0,0,0,15,15)
        the_bling.show()
        time.sleep(0.01)
    for q in range(5):
        for f in range(13):
            the_bling.fill((0,0,0))
            the_bling.bitmap_tile(image, palette,0,0,16*f,0,16,8)
            the_bling.show()
            time.sleep(0.05)
    image.deinit()

    print("catJAM Mono from tiled bmp")
    image, palette = adafruit_imageload.load("bmps/Montage5b.bmp")
    t=time.monotonic()
    for f in range(255):
        the_bling.fill((0,0,0))
        the_bling.bitmap_tile(image, palette,0,-3,43*f,0,43,32)
        the_bling.show()
    print("catJAM Mono test {} seconds".format(time.monotonic()-t))
    image.deinit()

    print("catYAM Mono from tiled bmp")
    image, palette = adafruit_imageload.load("bmps/YAM.bmp")
    for f in range(211):
        the_bling.fill((0,0,0))
        the_bling.bitmap_tile(image, palette,0,-9,32*f,0,32,32)
        the_bling.show()
    image.deinit()

def fonts_demo(rounds=2):
    """
    Demo of various PCF and BDF fonts, and the famous font5x8.bin on BLING.
    """
    FONTS="/fonts/"
    many_fonts = ["LeagueSpartan-Bold-16.bdf", "lemon.bdf", "profont.pcf","4x6.pcf", "5x7.pcf", "5x8.pcf", "6x9.pcf", "6x10.pcf","6x13.pcf","9x15.pcf" ]
    r=5
    for font_file in many_fonts:
        print("Font file",font_file)
        font = bitmap_font.load_font(FONTS+font_file)
        _,height,_,y_offset = font.get_bounding_box()
        the_bling.fill((0,0,0))
        the_bling.text("Bling",font,x=0,y=0,color_foreground=FOREGROUND, color_background=BACKGROUND)
        the_bling.show()
        time.sleep(1)

        t=time.monotonic()
        for i in range(rounds):
            for d in range(0,360,5):
                x=int(height*2/3*math.sin(d*math.pi/180))
                y=int(height*2/3*math.cos(d*math.pi/180))
                the_bling.fill((0,0,0))
                the_bling.text("Bling",font,x=x,y=y,color_foreground=FOREGROUND, color_background=BACKGROUND)
                the_bling.show()
        print("Raw text circle",font_file,time.monotonic()-t)

    the_bling.fill((0,0,0))
    the_bling.text("Bling",FONTS+"font5x8.bin",x=0,y=0,color_foreground=FOREGROUND, color_background=BACKGROUND)
    the_bling.show()
    time.sleep(2)

    r=5
    height=8*2
    t=time.monotonic()
    for i in range(rounds):
        for d in range(0,360,5):
            x=int(height*2/3*math.sin(d*math.pi/180))
            y=int(height*2/3*math.cos(d*math.pi/180))
            the_bling.fill((0,0,0))
            the_bling.text("Bling",FONTS+"font5x8.bin",x=x,y=y,color_foreground=FOREGROUND, color_background=BACKGROUND)
            the_bling.show()
    print("font5x8.bin text circle:",time.monotonic()-t)

def fill_demo(rounds=20):
    """
    Demo of fill rates of BLING led display by various methods
    """
    t=time.monotonic()
    print("Color fill (Raw)")
    for i in range(rounds):
        BLING_raw.fill((0,0,0))
        BLING_raw.show()
        BLING_raw.fill((255,0,0))
        BLING_raw.show()
        BLING_raw.fill((0,255,0))
        BLING_raw.show()
        BLING_raw.fill((0,0,255))
        BLING_raw.show()
    print("Color fill (Raw) ({} rounds): {}".format(rounds,time.monotonic()-t))

    t=time.monotonic()
    print("Color fill (Class)")
    for i in range(rounds):
        the_bling.fill((0,0,0))
        the_bling.show()
        the_bling.fill((255,0,0))
        the_bling.show()
        the_bling.fill((0,255,0))
        the_bling.show()
        the_bling.fill((0,0,255))
        the_bling.show()
    print("Color fill (Class) ({} rounds): {}".format(rounds,time.monotonic()-t))

    print("Color Fill (bitmap intermediate)")
    t=time.monotonic()
    for i in range(rounds):
        bitmap.fill(0)
        bitmap_to_neopixel(bitmap,BLING_raw)
        bitmap.fill(1)
        bitmap_to_neopixel(bitmap,BLING_raw)
        bitmap.fill(2)
        bitmap_to_neopixel(bitmap,BLING_raw)
        bitmap.fill(3)
        bitmap_to_neopixel(bitmap,BLING_raw)
    print("Color Fill (bitmap intermediate) ({} rounds): {}".format(rounds,time.monotonic()-t))

    print("Color Fill (framebuf)")
    t=time.monotonic()
    for i in range(rounds):
        BLING_framebuf.fill(0x000000)
        BLING_framebuf.display()
        BLING_framebuf.fill(0xFF0000)
        BLING_framebuf.display()
        BLING_framebuf.fill(0x00FF00)
        BLING_framebuf.display()
        BLING_framebuf.fill(0x0000FF)
        BLING_framebuf.display()
    print("Color Fill (framebuf) ({} rounds): {}".format(rounds,time.monotonic()-t))

def font_speed_demo(rounds=100):
    """
    Font display speed testing by various methods
    """
    FONTS="/fonts/"
    the_bling.fill((0,0,0))
    the_bling.show()

    font = bitmap_font.load_font(FONTS+"5x8.pcf")
    t=time.monotonic()
    for i in range(rounds):
        the_bling.fill((0,0,0))
        the_bling.show()
        the_bling.text("Bling",font,x=0,y=0,color_foreground=FOREGROUND, color_background=BACKGROUND)
        the_bling.show()
    print("Bitmap font ({} rounds): {}".format(rounds,time.monotonic()-t))

    the_bling.fill((0,0,0))
    the_bling.show()

    t=time.monotonic()
    for i in range(rounds):
        the_bling.fill((0,0,0))
        the_bling.show()
        the_bling.text("Bling",FONTS+"font5x8.bin",x=0,y=0,color_foreground=FOREGROUND, color_background=BACKGROUND)
        the_bling.show()
    print("font5x8.bin ({} rounds): {}".format(rounds,time.monotonic()-t))

    t=time.monotonic()
    for i in range(100):
        bitmap.fill(0x000000)
        bitmap_to_neopixel(bitmap,BLING_raw)
        draw_text_on_bitmap("Bling",font,x=0,y=0,color_index=1,bitmap=bitmap)
        bitmap_to_neopixel(bitmap,BLING_raw)
    print("Using bitmap text:",time.monotonic()-t)

    the_bling.fill((0,0,0))
    the_bling.show()

    t=time.monotonic()
    for i in range(rounds):
        BLING_framebuf.fill(0x000000)
        BLING_framebuf.display()
        BLING_framebuf.text("Bling",font_name=FONTS+"font5x8.bin",x=0,y=0,color=0xFF0000)
        BLING_framebuf.display()
    print("framebuf font ({} rounds): {}".format(rounds,time.monotonic()-t))

    the_bling.fill((0,0,0))
    the_bling.show()


def shapes_demo():
    """
    Demo of primitive shapes on BLING
    """
    FONTS="/fonts/"
    font = bitmap_font.load_font(FONTS+"5x8.pcf")
    max_w,y0,x_off,y_off = font.get_bounding_box()
    message = "Bling!"
    max_w = max_w * len(message)

    the_bling.fill(0x000000)
    the_bling.line(0,0,39,7,(255,0,0))
    the_bling.show()
    time.sleep(0.5)

    the_bling.line(0,0,39,0,(0,255,0))
    the_bling.show()
    time.sleep(0.5)

    the_bling.line(39,0,39,7,(0,0,255))
    the_bling.show()
    time.sleep(0.5)

    the_bling.line(39,7,0,7,(255,0,255))
    the_bling.show()
    time.sleep(0.5)

    the_bling.line(0,7,0,0,(0,255,255))
    the_bling.show()
    time.sleep(0.5)

    the_bling.line(0,7,39,0,(255,255,255))
    the_bling.show()
    time.sleep(0.5)

    rounds=5
    for j in range(3):
        the_bling.clear()
        for i in range(rounds):
            x0=random.randint(0,39)
            y0=random.randint(0,7)
            x1=random.randint(0,39)
            y1=random.randint(0,7)
            colour = rainbowio.colorwheel(random.randint(0,255))
            the_bling.line(x0,y0,x1,y1,colour)
            the_bling.show()
            time.sleep(0.2)

    the_bling.clear()
    xt=-max_w
    j=0
    still_scrolling = True
    while (still_scrolling):
        x0=random.randint(0,the_bling.width-1)
        y0=random.randint(0,the_bling.height-1)
        for i in range(1,15):
            the_bling.fill(0x00000)
            the_bling.circle(x0,y0,i,rainbowio.colorwheel(i*35))
            if j > 3:
                the_bling.text(message,font,xt,0,color_foreground=(0,255,0),color_background=None)
                xt += 1
                if (xt > the_bling.width):
                    still_scrolling=False
            the_bling.show()
            time.sleep(0.01)
            j+=1
        the_bling.circle(x0,y0,i,(0,0,0))

    the_bling.clear()
    xt=-max_w
    j=0
    still_scrolling = True
    while (still_scrolling):
        x0=random.randint(0,the_bling.width-1)
        y0=random.randint(0,the_bling.height-1)
        for i in range(1,15):
            the_bling.fill(0x00000)
            the_bling.rect(int(x0-i/2),int(y0-i/2),i,i,rainbowio.colorwheel(j*35))
            if j > 3:
                the_bling.text(message,font,xt,0,color_foreground=(0,255,0),color_background=None)
                xt += 1
                if (xt > the_bling.width):
                    still_scrolling=False
            the_bling.show()
            j+=1
            time.sleep(0.01)

        the_bling.circle(x0,y0,i,(0,0,0))

    the_bling.clear()
    xt=-max_w
    j=0
    still_scrolling = True
    while (still_scrolling):
        x0=random.randint(0,the_bling.width-1)
        y0=random.randint(0,the_bling.height-1)
        for i in range(1,15):
            the_bling.fill(0x00000)
            the_bling.rect(int(x0-i/2),int(y0-i/2),i,i,rainbowio.colorwheel(j*35),fill=True)
            if j > 3:
                the_bling.text(message,font,xt,0,color_foreground=(0,255,0),color_background=None)
                xt += 1
                if (xt > the_bling.width):
                    still_scrolling=False
            the_bling.show()
            time.sleep(0.01)
            j+=1
        the_bling.circle(x0,y0,i,(0,0,0))


def timing_test():
    """
    Esoteric timing tests drawing lines in different rotation orientataions
    """
    for r in [0,1,2,3]:
        the_bling.rotation=r
        rounds=50
        print("Top Left is red.\nhorizontal lines, rotation",the_bling.rotation)
        points=[]
        for i in range(rounds):
            points.append( [random.randint(0,the_bling.width-1),random.randint(0,the_bling.height-1),random.randint(1,the_bling.width-1)] )

        the_bling.clear()
        t=time.monotonic()
        for i in range(len(points)):
            # print("x,y,w=",points[i][0],points[i][1],points[i][2])
            the_bling.fill(0x000000)
            the_bling.hline_direct(points[i][0],points[i][1],points[i][2], (0,255,0))
            the_bling.setpixel(0,0,(255,0,0))
            the_bling.show()
            # time.sleep(0.2)
            the_bling.hline(points[i][0],points[i][1],points[i][2], (0,0,255))
            the_bling.setpixel(0,0,(255,0,0))
            the_bling.show()
            # time.sleep(0.2)
        print("Hline with draw ({} rounds) {} seconds".format(len(points),time.monotonic()-t))

        the_bling.clear()
        t=time.monotonic()
        for i in range(len(points)):
            the_bling.hline_aligned(points[i][0],points[i][1],points[i][2], (0,255,0))
        print("Hline aligned ({} rounds) {} seconds".format(len(points),time.monotonic()-t))

        t=time.monotonic()
        for i in range(len(points)):
            the_bling.hline(points[i][0],points[i][1],points[i][2], (0,255,0))
        print("Hline ({} rounds) {} seconds".format(len(points),time.monotonic()-t))

        t=time.monotonic()
        for i in range(len(points)):
            the_bling.hline_direct(points[i][0],points[i][1],points[i][2], (0,255,0))
        print("Hline direct ({} rounds) {} seconds".format(len(points),time.monotonic()-t))

        print("vertical lines, rotation",the_bling.rotation)
        points=[]
        for i in range(rounds):
            points.append( [random.randint(0,the_bling.width-1),random.randint(0,the_bling.height-1),random.randint(1,the_bling.height-1)] )

        the_bling.clear()
        t=time.monotonic()
        for i in range(len(points)):
            the_bling.fill(0x000000)
            the_bling.vline_direct(points[i][0],points[i][1],points[i][2], (0,255,0))
            the_bling.setpixel(0,0,(255,0,0))
            the_bling.show()
            # time.sleep(1)
            the_bling.vline(points[i][0],points[i][1],points[i][2], (0,0,255))
            the_bling.setpixel(0,0,(255,0,0))
            the_bling.show()
            # time.sleep(1)
        print("Vline with draw ({} rounds) {} seconds".format(len(points),time.monotonic()-t))

        the_bling.clear()
        t=time.monotonic()
        for i in range(len(points)):
            the_bling.vline_aligned(points[i][0],points[i][1],points[i][2], (0,255,0))
        print("Vline aligned ({} rounds) {} seconds".format(len(points),time.monotonic()-t))

        t=time.monotonic()
        for i in range(len(points)):
            the_bling.vline(points[i][0],points[i][1],points[i][2], (0,255,0))
        print("Vline ({} rounds) {} seconds".format(len(points),time.monotonic()-t))

        t=time.monotonic()
        for i in range(len(points)):
            the_bling.vline_direct(points[i][0],points[i][1],points[i][2], (0,255,0))
        print("Vline direct ({} rounds) {} seconds".format(len(points),time.monotonic()-t))

    the_bling.rotation=2

def intro():
    """
    All good demos need an intro screen, right?
    """
    FONTS="/fonts/"
    font = FONTS+"font5x8.bin"
    message = "Bling Demo"
    max_w = 8 * len(message)
    for i in range(2*max_w):
        the_bling.fill(rainbowio.colorwheel(i*5))
        the_bling.text(message,font,max_w-i,0,color_foreground=(0,0,0))
        the_bling.show()

    # turn off individual pixels
    u=0
    for i in range(bling_num_pixels*2):
        x = random.randint(0,the_bling.width-1)
        y = random.randint(0,the_bling.height-1)
        the_bling.setpixel(x,y,0x00000)
        if u > 5:
            u=0
            the_bling.show()
        u+=1

#--------------------------------------------------------------------------------------
# Main Program Execution starts here
#

# BLING is very bright.   It also consumes a lot of current when very bright.
BLING_BRIGHTNESS = 0.08

# Enable power to BLING pixel display
bling_power = digitalio.DigitalInOut(board.MATRIX_POWER)
bling_power.switch_to_output()
bling_power.value=True

# Setup BLING neopixel and PixelFrameBuffer objects
bling_pixel_width, bling_pixel_height = BLING.display.pixel_size()
bling_num_pixels = bling_pixel_width * bling_pixel_height
BLING_raw = neopixel.NeoPixel(board.MATRIX_DATA,bling_num_pixels,brightness=BLING_BRIGHTNESS,auto_write=False)

# A bitmap for secondary drawing canvas for some demos
bitmap = displayio.Bitmap(bling_pixel_width, bling_pixel_height, 4)  # Create a bitmap object,width, height, bit depth

# A sample palette for things that need the palette in this demo, not needed normally
palette = displayio.Palette(4)
palette[0]=0x000000
palette[1]=0xFF0000
palette[2]=0x00FF00
palette[3]=0x0000FF

# Foreground/Background colors during font demos
FOREGROUND = (0,225,0)
BACKGROUND = (0,30,30)

# pixel framebuffers are created as RGB888.  This is only in the demo
# for comparison.  You don't need this normally.
BLING_framebuf = PixelFramebuffer(
    pixels=BLING_raw,
    width=bling_pixel_width,
    height=bling_pixel_height,
    alternating=False,
    rotation=2
)

# In the demo the BLING display object is named "the_bling" so you can see
# where the derived object is used more easily.
the_bling = BLING.display(matrix=BLING_raw,rotation=2)

while True:

    intro()

    shapes_demo()

    gif_demo()

    image_demo()

    fonts_demo()

    # fill_demo(), font_speed_demo(), and timing_test() show speed fill rates and may hurt
    # your head or cause epileptic seizures if you are sensitive to such things.
    #
    # fill_demo()
    # timing_test()
    # font_speed_demo()
