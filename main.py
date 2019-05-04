import os

import cv2
import numpy as np
import pytesseract
from PIL import Image
import platform

win = 'windows'
linux = 'linux'

plat = platform.system()

src_path_linux = '/home/semen/drive/workspace.python/hack'
src_path_win = 'D:\Labas\hack\crop'

cropped_suffix = '_cropped'
sharp_suffix = '_sharp'
thres_suffix = '_thres'

crop_dir_linux = '/home/semen/drive/workspace.python/hack/photos/crop/'
orig_dir_linux = '/home/semen/drive/workspace.python/hack/photos/orig/'
sharp_dir_linux = '/home/semen/drive/workspace.python/hack/photos/sharp/'
thres_dir_linux = '/home/semen/drive/workspace.python/hack/photos/thres/'

crop_dir_win = "D:\Labas\hack\crop"
orig_dir_win = 'D:\Labas\hack\orig'
sharp_dir_win = 'D:\Labas\hack\sharp'
thres_dir_win = 'D:\Labas\hack\\thres'

kernel_sharpening = np.array([[-1, -1, -1],
                              [-1, 9, -1],
                              [-1, -1, -1]])


def get_origin_dir():
    if plat == win:
        return orig_dir_win
    else:
        return orig_dir_linux


def get_crop_dir():
    if plat == win:
        return crop_dir_win
    else:
        return crop_dir_linux


def get_sharp_dir():
    if plat == win:
        return sharp_dir_win
    else:
        return sharp_dir_linux


def get_thres_dir():
    if plat == win:
        return thres_dir_win
    else:
        return thres_dir_linux


def append_suffix(path: str, suffix: str) -> str:
    base_name = os.path.basename(path)
    name, extension = os.path.splitext(base_name)
    return name + suffix + extension


def get_croped_path(file_name: str) -> str:
    return os.path.join(get_crop_dir(), append_suffix(file_name, cropped_suffix))


def get_origin_path(file_name: str) -> str:
    return os.path.join(get_origin_dir(), append_suffix(file_name, ''))


def get_sharped_path(file_name: str) -> str:
    return os.path.join(get_sharp_dir(), append_suffix(file_name, sharp_suffix))


def get_thres_path(file_name: str) -> str:
    return os.path.join(get_thres_dir(), append_suffix(file_name, thres_suffix))


def get_string(file_path):
    image = cv2.imread(file_path)

    # Convert to gray
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((1, 1), np.uint8)

    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)

    THRES_IMAGE_PATH = get_thres_path(file_path)

    cv2.imwrite(THRES_IMAGE_PATH, image)

    # pytesseract.pytesseract.tesseract_cmd = r'tesseract'

    result = pytesseract.image_to_string(Image.open(THRES_IMAGE_PATH), lang="ukr")

    return result


if __name__ == '__main__':
    image_name = '4.png'

    # print(get_origin_path(get_origin_path(image_name)))
    # print(get_sharped_path(get_origin_path(image_name)))
    # print(get_thres_path(get_origin_path(image_name)))
    # print(get_croped_path(get_origin_path(image_name)))

    origin_image = cv2.imread(get_origin_path(image_name))

    hls_image = cv2.cvtColor(origin_image, cv2.COLOR_BGR2HLS)

    sensitivity = 80

    lower_white = np.array([0, 255 - sensitivity, 0])
    upper_white = np.array([255, 255, 255])

    color_range_mask = cv2.inRange(hls_image, lower_white, upper_white)

    kernel = np.ones((4, 4), np.uint8)
    dilatied_image = cv2.dilate(color_range_mask, kernel, iterations=5)

    kernel = np.ones((4, 4), np.uint8)
    dilatied_image = cv2.erode(dilatied_image, kernel, iterations=4)

    contours, hierarchy = cv2.findContours(dilatied_image, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_CCOMP)
    max_found_area = 0
    object_found = False

    MIN_OBJECT_AREA = 100 * 100

    if len(hierarchy) > 0:
        numPbjects = len(hierarchy)

        if numPbjects > 1:
            print(numPbjects + "ERROR")
        else:
            index = 0
            # print(hierarchy)
            while index >= 0:
                moment = cv2.moments(contours[index])
                area = moment["m00"]
                if area > MIN_OBJECT_AREA and area > max_found_area:
                    x = moment["m10"] / area
                    y = moment["m01"] / area
                    object_found = True
                    max_found_area = area
                else:
                    object_found = False

                if object_found == True:
                    # print(x)
                    # print(y)
                    # print(contours[index])
                    break
                index = hierarchy[0][index][0]

    left_upper = contours[index]

    x_s = [elem[0][0] for elem in contours[index]]
    x_min = min(x_s)
    x_max = max(x_s)

    y_s = [elem[0][1] for elem in contours[index]]
    y_min = min(y_s)
    y_max = max(y_s)

    CROPPED_IMAGE_PATH = get_croped_path(image_name)
    SHARPED_IMAGE_PATH = get_sharped_path(image_name)

    cropped_image = origin_image[y_min:y_max, x_min:x_max]
    equalized_image = cv2.equalizeHist(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY))

    cv2.imwrite(CROPPED_IMAGE_PATH, cropped_image)

    sharpened = cv2.filter2D(cv2.imread(CROPPED_IMAGE_PATH), -1, kernel_sharpening)

    cv2.imwrite(SHARPED_IMAGE_PATH, sharpened)

    parsed_text = get_string(SHARPED_IMAGE_PATH)

    print(parsed_text)

    print("------ Done -------")

