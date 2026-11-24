"""CPC colours and screen decoding.

HW   hardware colour number (Gate Array value & &1F) -> RGB
FW   firmware colour number 0-26 -> RGB
px0  one mode-0 byte -> its two pen numbers (the CPC interleaves the pixel bits)
screen / linear   render screen memory, or a linear block of mode-0 bytes, to a Pillow image
Screen address of line y, byte x (standard 80-byte layout): base + (y % 8) * &800 + (y // 8) * 80 + x
"""
from PIL import Image
HW = {0x00:(128,128,128),0x01:(128,128,128),0x02:(0,255,128),0x03:(255,255,128),0x04:(0,0,128),0x05:(255,0,128),
0x06:(0,128,128),0x07:(255,128,128),0x08:(255,0,128),0x09:(255,255,128),0x0A:(255,255,0),0x0B:(255,255,255),
0x0C:(255,0,0),0x0D:(255,0,255),0x0E:(255,128,0),0x0F:(255,128,255),0x10:(0,0,128),0x11:(0,255,128),
0x12:(0,255,0),0x13:(0,255,255),0x14:(0,0,0),0x15:(0,0,255),0x16:(0,128,0),0x17:(0,128,255),0x18:(128,0,128),
0x19:(128,255,128),0x1A:(128,255,0),0x1B:(128,255,255),0x1C:(128,0,0),0x1D:(128,0,255),0x1E:(128,128,0),0x1F:(128,128,255)}
FW = [(0, 0, 0), (0, 0, 128), (0, 0, 255), (128, 0, 0), (128, 0, 128), (128, 0, 255), (255, 0, 0), (255, 0, 128),
      (255, 0, 255), (0, 128, 0), (0, 128, 128), (0, 128, 255), (128, 128, 0), (128, 128, 128), (128, 128, 255),
      (255, 128, 0), (255, 128, 128), (255, 128, 255), (0, 255, 0), (0, 255, 128), (0, 255, 255), (128, 255, 0),
      (128, 255, 128), (128, 255, 255), (255, 255, 0), (255, 255, 128), (255, 255, 255)]
def px0(b):
    return (((b>>7)&1)|(((b>>3)&1)<<1)|(((b>>5)&1)<<2)|(((b>>1)&1)<<3),
            ((b>>6)&1)|(((b>>2)&1)<<1)|(((b>>4)&1)<<2)|(((b>>0)&1)<<3))
def screen(mem, pal, base=0xC000, wb=80, lines=200):
    img = Image.new('RGB', (wb*4, lines))
    for y in range(lines):
        for x in range(wb):
            b = mem[(base + (y%8)*0x800 + (y//8)*wb + x) & 0xFFFF]
            for k, p in enumerate(px0(b)):
                img.putpixel((x*4+k*2, y), pal[p]); img.putpixel((x*4+k*2+1, y), pal[p])
    return img
def linear(data, wb, pal, bg=None):
    h = (len(data)+wb-1)//wb
    img = Image.new('RGB', (wb*4, h), bg or (40,0,40))
    for i, b in enumerate(data):
        x, y = (i % wb)*4, i//wb
        for k, p in enumerate(px0(b)):
            img.putpixel((x+k*2, y), pal[p]); img.putpixel((x+k*2+1, y), pal[p])
    return img
