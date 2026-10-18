#!/usr/bin/env python3
"""Build embedded Cyrillic bitmap font from DejaVu Sans (installed from distro)."""
from PIL import Image, ImageFont, ImageDraw
import sys
from pathlib import Path
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
chars = [chr(i) for i in range(32,127)] + [chr(i) for i in range(0x410,0x450)] + ['Ё','ё','№','—','•']
file=Path(sys.argv[1])
file.parent.mkdir(parents=True, exist_ok=True)
with file.open('w', encoding='utf-8') as o:
    o.write('typedef struct { unsigned int cp; unsigned short bits[18]; } glyph_t;\n')
    o.write('static const glyph_t font_glyphs[] = {\n')
    for ch in chars:
        img=Image.new('1',(12,18),0)
        ImageDraw.Draw(img).text((0,-1),ch,font=font,fill=1)
        rows=[]
        for y in range(18):
            bits=0
            for x in range(12):
                if img.getpixel((x,y)): bits |= 1 << (11-x)
            rows.append('0x%03X'%bits)
        o.write('{%s,{%s}},\n'%(ord(ch),','.join(rows)))
    o.write('};\n')
