from PIL import Image
from PIL import ImageChops

_img_cur = Image.open('./config/img_cur.png')
_img_last = Image.open('./config/img_cur.png')
diff = ImageChops.difference(_img_cur, _img_last)
if diff.getbbox() is None:
	print('same')
else:
    print('diff')