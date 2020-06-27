import pytesseract
from pytesseract import Output
import image_manipulation as IM
import cv2
from PIL import Image
import pyocr
import pyocr.builders

img = IM.scan('test.png')

# skip scan and look at monochrome
# img.convert('L')

# d = pytesseract.image_to_data(img, output_type=Output.DICT)
# n_boxes = len(d['level'])
# for i in range(n_boxes):
#     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])    
#     img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

# cv2.imshow('img', img)
# cv2.waitKey(0)

# Best to worst results

text = pytesseract.image_to_string(Image.open('test.png'))
text = text.split("\n")
for line in text:
    if "$" in line:
        print(line)

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
txt = tool.image_to_string(
    Image.open('test.png'),
    lang='eng',
    builder=pyocr.builders.TextBuilder()
)
for line in txt:
    if "$" in line:
        print(line)


# text = pytesseract.image_to_string(Image.open('test.png').convert('L'))
# text = text.split("\n")
# for line in text:
#     if "$" in line:
#         print(line)
