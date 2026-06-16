#!/usr/bin/env python3
"""Generate OG image for CouponBot"""
import sys
sys.path = [p for p in sys.path if 'venv' not in p]
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r'C:\Users\86130\Vibe-Trading\coupon-bot\static\og-image.png'
SIZE = (1200, 630)

img = Image.new('RGB', SIZE, '#1d1d1f')
draw = ImageDraw.Draw(img)

# Gradient overlay
for y in range(SIZE[1]):
    r = int(29 + (0 - 29) * y / SIZE[1])
    g = int(29 + (0 - 29) * y / SIZE[1])
    b = int(31 + (0 - 31) * y / SIZE[1])
    draw.rectangle([(0, y), (SIZE[0], y)], fill=(r, g, b))

# Accent bar
for y in range(240, 260):
    r = int(0 + (255 - 0) * (y - 240) / 20)
    g = int(122 + (255 - 122) * (y - 240) / 20)
    b = int(255 + (255 - 255) * (y - 240) / 20)
    draw.rectangle([(120, y), (SIZE[0]-120, y)], fill=(r, g, b))

# Text "CouponBot"
try:
    font_big = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 80)
    font_small = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 36)
except:
    font_big = ImageFont.load_default()
    font_small = ImageFont.load_default()

draw.text((120, 160), "CouponBot", fill='white', font=font_big)
draw.text((120, 290), "Verified Coupons & Deals from Top DTC Brands", fill='#a1a1a6', font=font_small)
draw.text((120, 380), "simumu.pythonanywhere.com", fill='#007aff', font=font_small)

img.save(OUT, 'PNG')
print(f"OG image saved: {OUT} ({os.path.getsize(OUT)} bytes)")
