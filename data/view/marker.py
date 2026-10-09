from PIL import Image, ImageDraw, ImageFont
p = r'C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\data\view\test-marker.jpg'
im = Image.new('RGB', (600, 300), (255, 255, 255))
d = ImageDraw.Draw(im)
f = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 60)
d.text((30, 60), 'QX7 MARKER', font=f, fill=(200, 0, 0))
d.text((30, 160), 'see me?', font=f, fill=(0, 0, 200))
im.save(p, quality=95)
print(p)
