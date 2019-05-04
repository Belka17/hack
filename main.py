import cv2
import numpy as np
import pytesseract
from PIL import Image

# Path of working folder on Disk
src_path = "D:/Labas/hack/"
imageName = "7cr.png"
def get_string(img_path):

    img = cv2.imread(img_path)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    cv2.imwrite(src_path + "thres.png", img)

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

    result = pytesseract.image_to_string(Image.open(src_path + "thres.png"),lang="ukr")

    return result

imgClean = cv2.imread(src_path + imageName)

img = cv2.cvtColor(imgClean,cv2.COLOR_BGR2HLS)
sensitivity = 80
lower_white = np.array([0,255-sensitivity,0])
upper_white = np.array([255,255,255])

mask = cv2.inRange(img, lower_white, upper_white)

kernel = np.ones((4,4),np.uint8)
dilation = cv2.dilate(mask,kernel,iterations = 5)

kernel = np.ones((4,4),np.uint8)
dilation = cv2.erode(dilation,kernel,iterations = 4)


contours, hierarchy = cv2.findContours(dilation,cv2.CHAIN_APPROX_SIMPLE,cv2.RETR_CCOMP)
refArea = 0
objectFound = False
MIN_OBJECT_AREA = 100*100

if len(hierarchy) > 0:
    numPbjects = len(hierarchy)
    if numPbjects > 1 :
        print(numPbjects + "ERROR")
    else :
        index = 0
        #print(hierarchy)
        while index >= 0:
            moment = cv2.moments(contours[index])
            area = moment["m00"]
            if area > MIN_OBJECT_AREA and area > refArea:
                x = moment["m10"] / area
                y = moment["m01"] / area
                objectFound = True
                refArea = area
            else:
                objectFound = False

            if objectFound == True:
                #print(x )
                #print(y)
                #print(contours[index])
                break

            index = hierarchy[0][index][0]
leftUpper = contours[index]
x_s = [elem[0][0] for elem in contours[index]]
x_min = min(x_s)
x_max = max(x_s)
y_s = [elem[0][1] for elem in contours[index]]
y_min = min(y_s)
y_max = max(y_s)

crop_img = imgClean[y_min:y_max, x_min:x_max]
equ = cv2.equalizeHist(cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY))
afterPreproccesing = "cropped.png"
cv2.imwrite(src_path + afterPreproccesing, crop_img)



kernel_sharpening = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])

sharpened = cv2.filter2D(cv2.imread(src_path + afterPreproccesing), -1, kernel_sharpening)
afterSharpening = "sharp.png"
cv2.imwrite(src_path + afterSharpening, sharpened)

print (get_string(src_path + afterSharpening))

print ("------ Done -------")
