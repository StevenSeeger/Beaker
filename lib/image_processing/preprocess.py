import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import interpolation as inter

def load_image(path):
    img = cv2.imread(path)
    return img

def black_white(img):
    img32 = np.float32(img)
    ret, imgf = cv2.threshold(img32, 155, 255,cv2.THRESH_BINARY,cv2.THRESH_OTSU) #imgf contains Binary image
    imgf = Image.fromarray(np.uint8(imgf))
    return imgf

def fix_skew(img):
    wd, ht = imgf.size
    pix = np.array(imgf.convert('1').getdata(), np.uint8)
    bin_img = 1 - (pix.reshape((ht, wd)) / 255.0)
    
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
    return img

def noise_reduction(img):
    # This is expensive; need to make sure this is needed
    img = cv2.fastNlMeansDenoisingColored(np.uint8(img), None, 10, 10, 7, 15) 
    return img

def thin_skeleton(img):
    kernel = np.ones((3,3),np.uint8)
    img = cv2.erode(img,kernel,iterations = 1)
    return img

def segemtation(img):
    #Vertical segmenation
    proj = np.sum(np.sum(erosion,2),1)
    blank = np.where(np.sum(result,1)-255 == 0)[0]
    img_text = []
    for i, val in enumerate(blank):
        if (i == blank.size-1):
            continue
        elif (val+1 != blank[i+1]):
            img_text.append([val,blank[i+1]])
        else:
            continue
    
    # split up picture by line
    img_list = []
    for vals in img_text:
        img_list.append(erosion[vals[0]:vals[1], 0:W])

    # get pixels of characters
    line_chars = []
    for line in img_list:
        # Creates projection of word in sense of where pixels are white vs black
        proj = np.sum(np.sum(line,2),0)
        blank = np.where(proj==0)[0]
        img_char = []
        # Seperates the characters based off of blank space
        for i, val in enumerate(blank):
            if (i == blank.size-1):
                continue
            elif (val+1 != blank[i+1]):
                img_char.append([val,blank[i+1]])
            else:
                continue
        line_chars.append(img_char)

    # Seperation by word & letter
    reciept_deconstructed = []
    for line in line_chars:
        line_words = []
        start_word = line[0][0]
        for i, val in enumerate(line):
            if (i == len(line)-1):
                line_words.append([start_word, val[1]])
                continue
            elif (line[i+1][0] - val[1] >= 60):
                line_words.append([start_word, val[1]])
                start_word = line[i+1][0]
            else:
                continue
        reciept_deconstructed.append([line, line_words])

    # Image of each letter by word
    line_word_letter = []
    for i, line in enumerate(reciept_deconstructed):
        letters = line[0]
        words = line[1]
        img_line = img_list[i]
        height = img_line.shape[0]
        line_words = []
        for word in words:
            for letter in letters:
                if (letter[0] < word[0]):
                    line_words.append(img_line[0:height,letter[0]:letter[1]])
                else:
                    break
        line_word_letter.append(line_words)
    return line_word_letter

# Visualize Horizontal Segmentation histogram
# im = np.sum(erosion,2)
# m = np.max(proj)
# w = 500
# result = np.zeros((proj.shape[0],500))
# for row in range(im.shape[0]):
#    cv2.line(result, (0,row), (int(proj[row]*w/m),row), (255,255,255), 1)

# For outputing a picture of horizontal seperations by colored lines
# H,W = erosion.shape[:2]
# erosion2 = erosion
# for pix in img_text:
#     cv2.line(erosion2, (0,pix[0]), (W, pix[0]), (255,0,0), 1)
#     cv2.line(erosion2, (0,pix[1]), (W, pix[1]), (0,255,0), 1)

# Output Vertical segmentation picture not working
# proj = np.sum(np.sum(img_list[4],2),0)
# m = np.max(proj)
# w = proj.shape[0]
# result = np.zeros((proj.shape[0],w))
# for row in range(im.shape[0]):
#    cv2.line(result, (0,row), (int(proj[row]*w/m),row), (255,255,255), 1)