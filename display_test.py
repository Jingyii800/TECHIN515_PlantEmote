from PIL import Image, ImageDraw, ImageFont
import ST7789 as ST7789

# Create an ST7789 LCD display class.
disp = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # Depending on your display configuration
    dc=9,
    backlight=19,               # Change according to your wiring
    spi_speed_hz=80 * 1000 * 1000
)

# Initialize display.
disp.begin()

WIDTH = disp.width
HEIGHT = disp.height

# Create a new image with RGB (3 colors) and a size matching the display.
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))

# Create a drawing object that will draw over the image.
draw = ImageDraw.Draw(img)

# Draw some shapes into the image.
draw.rectangle((10, 10, WIDTH - 10, HEIGHT - 10), outline="cyan", fill=(0, 0, 0))
draw.text((10, 10), 'Hello World!', fill="white")

# Display the image on the screen.
disp.display(img)
