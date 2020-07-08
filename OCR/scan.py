import pytesseract
from pytesseract import Output
import image_manipulation as IM
import cv2
from PIL import Image
import pyocr
import pyocr.builders

# img = IM.scan('./test_pictures/test.png')

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

########################
# Straight pytesseract #
########################

text = pytesseract.image_to_string(Image.open('./test_pictures/walmart.jpg'))
text = text.split("\n")
for line in text:
    if "$" in line:
        print(line)
print(text)

########################

########################
# Straight other thing #
########################

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
txt = tool.image_to_string(
    Image.open('./test_pictures/walmart.jpg'),
    lang='eng',
    builder=pyocr.builders.TextBuilder()
)
print(txt)
for line in txt:
    if "$" in line:
        print(line)

########################


# text = pytesseract.image_to_string(Image.open('test.png').convert('L'))
# text = text.split("\n")
# for line in text:
#     if "$" in line:
#         print(line)


#################
# Another thing #
#################

## (1) read
img = cv2.imread('./test_pictures/test.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

## (2) threshold
th, threshed = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)

## (3) minAreaRect on the nozeros
pts = cv2.findNonZero(threshed)
ret = cv2.minAreaRect(pts)

(cx,cy), (w,h), ang = ret
if w>h:
    w,h = h,w
    ang += 90

## (4) Find rotated matrix, do rotation
M = cv2.getRotationMatrix2D((cx,cy), ang, 1.0)
rotated= cv2.warpAffine(threshed, M, (img.shape[1], img.shape[0]))
rotated_img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

## (5) find and draw the upper and lower boundary of each lines
hist = cv2.reduce(rotated,1, cv2.REDUCE_AVG).reshape(-1)

th = 2
H,W = img.shape[:2]
uppers = [y for y in range(H-1) if hist[y]<=th and hist[y+1]>th]
lowers = [y for y in range(H-1) if hist[y]>th and hist[y+1]<=th]

rotated = cv2.cvtColor(rotated, cv2.COLOR_GRAY2BGR)
for y in uppers:
    cv2.line(rotated, (0,y), (W, y), (255,0,0), 1)

for y in lowers:
    cv2.line(rotated, (0,y), (W, y), (0,255,0), 1)

cv2.imwrite("./test_pictures/result2.png", rotated)