# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This will show some Linux Statistics on the attached display. Be sure to adjust
to the display you have connected. Be sure to check the learn guides for more
usage information.

This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!
"""

import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735  # pylint: disable=unused-import

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# pylint: disable=line-too-long
# Create the display:
disp = st7735.ST7735R(spi, rotation=90, height=128, x_offset=2, y_offset=3,   # 1.44" ST7735R
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)
# pylint: enable=line-too-long

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# First define some constants to allow easy positioning of text.
padding = 5
x = 0

# Load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
font_middle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
font_data  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

bg_color = 0
index_color = '#F7E752'
middle_color = '#DD517F'
data_color = '#64CFF7'

prev_down = 0
prev_up = 0

while True:
    # Draw a black filled box to clear the image.
	draw.rectangle((0, 0, width, height), outline=0, fill=bg_color)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load

	cmd = "hostname -I | cut -d ' ' -f 1"
	ip = subprocess.check_output(cmd, shell=True).decode('utf-8')

	cmd = "netstat | grep ':2234' | wc -l"
	ssh = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd = "netstat | grep ':3344' | wc -l"
	vpn = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd = "netstat -n | grep ':445' | wc -l"
	smb = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd = "cat /proc/loadavg | awk 'NR==1{printf \"%d%%\", $1*100}'"
	cpu_load = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd = "cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"%.2f\u2103\", $1/1000'}"
	temp = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd = "free -m | awk 'NR==2{printf \"%.2f%%\",$3/$2}'"
	mem = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd = "ip -s link show dev wlan0 | awk 'NR==4{printf \"%.2f\",$1/1000000}'"
	buf = float(subprocess.check_output(cmd, shell=True).decode("utf-8"))
	down = '{:.1f}M'.format(buf - prev_down)
	prev_down = buf

	cmd = "ip -s link show dev wlan0 | awk 'NR==6{printf \"%.2f\",$1/1000000}'"
	buf = float(subprocess.check_output(cmd, shell=True).decode("utf-8"))
	up = '{:.1f}M'.format(buf - prev_up)
	prev_up = buf
	print(temp)

	cmd="df | grep root | awk '{printf \"%d%%\", $3/$2 * 100}'"
	strage_root = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd="df -h| grep sda1 | awk '{printf \"%s\", $3}'"
	strage_sda = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd="df -h| grep sdb1 | awk '{printf \"%s\", $3}'"
	strage_sdb = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # Write four lines of text.
	y = padding
	draw.text((x, y), 'IP', font=font_title, fill=index_color)
	y += 15
	draw.text((x, y), 'CLIENTS', font=font_title, fill=index_color)
	y += 15
	draw.text((x, y), 'ssh:', font=font_middle, fill=middle_color)
	draw.text((x+43, y), 'vpn:', font=font_middle, fill=middle_color)
	draw.text((x+86, y), 'smb:', font=font_middle, fill=middle_color)
	y += 15
	draw.text((x, y), 'CPU', font=font_title, fill=index_color)
	y += 15
	draw.text((x, y), 'NET', font=font_title, fill=index_color)
	draw.text((x+30, y), u'\u2B06', font=font_middle, fill=middle_color)
	draw.text((x+75, y), u'\u2B07', font=font_middle, fill=middle_color)
	y += 15
	draw.text((x, y), 'DISK', font=font_title, fill=index_color)
	draw.text((x+45, y), 'root', font=font_middle, fill=middle_color)
	y += 15
	draw.text((x, y), 'sda1', font=font_middle, fill=middle_color)
	draw.text((x+35, y), 'sdb1', font=font_middle, fill=middle_color)

	# data
	y = padding
	draw.text((x+20, y), ip, font=font_data, fill=data_color)
	y += 30
	draw.text((x+30, y), ssh, font=font_data, fill=data_color)
	draw.text((x+75, y), vpn, font=font_data, fill=data_color)
	draw.text((x+120, y), smb, font=font_data, fill=data_color)
	y += 15
	draw.text((x+35, y), cpu_load, font=font_data, fill=data_color)
	draw.text((x+70, y), temp, font=font_data, fill=data_color)
	y += 15
	draw.text((x+40, y), up, font=font_data, fill=data_color)
	draw.text((x+85, y), down, font=font_data, fill=data_color)
	y += 15
	draw.text((x+80, y), strage_root, font=font_data, fill=data_color)
	y += 30
	draw.text((x, y), strage_sda, font=font_data, fill=data_color)
	draw.text((x+35, y), strage_sdb, font=font_data, fill=data_color)
	

    # Display image.
	disp.image(image)
	time.sleep(2)

