#!/usr/local/bin/python
## -*- coding: utf-8 -*-

import Image
import ImageFont
import ImageDraw
import string

#image will be 200x1600, line of 8 200x200 pics
#in 1x8 grid 

image_wdth = 800
image_hght = 600

#create new image 
#im = Image.new("RGB",(image_wdth,image_hght),(256,256,256))
im = Image.new("RGB",(image_wdth,image_hght),(0,0,0))

#specify font
font_size = 25
font = ImageFont.truetype("./fonts/DroidSerif-Bold.ttf", font_size)
#font = ImageFont.truetype("./fonts/GT2000K2.ttf", font_size)
fill = "white"

draw = ImageDraw.Draw(im)
draw.text((40,60), "\"GODOT Count Rates\" Error", font=font, fill=fill)
draw.text((40,140), "Possible reasons:", font=font, fill=fill)
draw.text((40,170), "1. The plot has not yet ben generated", font=font, fill=fill)
draw.text((40,200),"2. There are no GODOT data (yet) for this time", font=font, fill=fill)

#font = ImageFont.truetype("./fonts/GT2000K2.ttf", font_size)
#font = ImageFont.truetype("./fonts/mona.ttf", font_size)
font = ImageFont.truetype("./fonts/sazanami-mincho.ttf", font_size)
font_size=30
draw.text((40,290), u"\"GODOT Count Rates\" エラー", font=font, fill=fill)
draw.text((40,290+80), u"考えられる理由:", font=font, fill=fill)
draw.text((40,320+80), u"1. プロットはまだ生成されていない", font=font, fill=fill)
draw.text((40,350+80), u"2. 今回のデータは、（まだ）あります", font=font, fill=fill)

im.save("godot_error.png","PNG");
