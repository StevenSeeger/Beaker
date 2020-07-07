import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import interpolation as inter

                                            # PREPROCESSING #

###################
# Black and White #
###################

img = cv2.imread('./test_pictures/walmart.jpg')
img32 = np.float32(img)
ret, imgf = cv2.threshold(img32, 155, 255,cv2.THRESH_BINARY,cv2.THRESH_OTSU) #imgf contains Binary image
imgf = Image.fromarray(np.uint8(imgf))

################
# Correct Skew #
################

wd, ht = imgf.size
pix = np.array(imgf.convert('1').getdata(), np.uint8)
bin_img = 1 - (pix.reshape((ht, wd)) / 255.0)
plt.imshow(bin_img, cmap='gray')

def find_score(arr, angle):
    data = inter.rotate(arr, angle, reshape=False, order=0)
    hist = np.sum(data, axis=1)
    score = np.sum((hist[1:] - hist[:-1]) ** 2)
    return hist, score

delta = .25
limit = 5 # As limit increases, so does the computation
angles = np.arange(-limit, limit+delta, delta)
scores = []
for angle in angles:
    hist, score = find_score(bin_img, angle)
    scores.append(score)

best_score = max(scores)
best_angle = angles[scores.index(best_score)]

data = inter.rotate(bin_img, best_angle, reshape=False, order=0)
img = Image.fromarray((255 * data).astype("uint8")).convert("RGB")

###################
# Noise Reduction #
###################

# This is expensive; need to make sure this is needed

dst = cv2.fastNlMeansDenoisingColored(np.uint8(img), None, 10, 10, 7, 15) 
dst = Image.fromarray(dst)
plt.imshow(dst)

################################
# Thinning and Skeletonization #
################################

kernel = np.ones((3,3),np.uint8)
erosion = cv2.erode(np.uint8(dst),kernel,iterations = 1)

                                        # SEGMENTATION #

###########################
# Horizontal Segmentation #
###########################

im = np.sum(erosion,2)

proj = np.sum(np.sum(erosion,2),1)
# Create output image same height as text, 500 px wide
m = np.max(proj)
w = 500
result = np.zeros((proj.shape[0],500))

for row in range(im.shape[0]):
   cv2.line(result, (0,row), (int(proj[row]*w/m),row), (255,255,255), 1)

blank = np.where(np.sum(result,1)-255 == 0)[0]
upper = []
lower = []
for i, val in enumerate(blank):
    if (i == blank.size-1):
        continue
    elif (val+1 != blank[i+1]):
        upper.append(val)
        lower.append(blank[i+1])
    else:
        continue

H,W = erosion.shape[:2]
erosion2 = erosion
for y in upper:
    cv2.line(erosion2, (0,y), (W, y), (255,0,0), 1)
for y in lower:
    cv2.line(erosion2, (0,y), (W, y), (0,255,0), 1)