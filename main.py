import os

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance
import platform

import parsing

win = 'windows'
linux = 'linux'

plat = platform.system()

src_path_linux = '/home/semen/drive/workspace.python/hack'
src_path_win = 'D:\Labas\hack\crop'

cropped_suffix = '_cropped'
sharp_suffix = '_sharp'
thres_suffix = '_thres'
contrast_suffix = '_contrast'

crop_dir_linux = '/home/semen/drive/workspace.python/hack/photos/crop/'
orig_dir_linux = '/home/semen/drive/workspace.python/hack/photos/orig/'
sharp_dir_linux = '/home/semen/drive/workspace.python/hack/photos/sharp/'
thres_dir_linux = '/home/semen/drive/workspace.python/hack/photos/thres/'
contrast_dir_linux = '/home/semen/drive/workspace.python/hack/photos/contrast/'

crop_dir_win = "D:\Labas\hack\photos\crop"
orig_dir_win = 'D:\Labas\hack\photos\orig'
sharp_dir_win = 'D:\Labas\hack\photos\sharp'
thres_dir_win = 'D:\Labas\hack\photos\\thres'
contrast_dir_win = 'D:\Labas\hack\photos\contrast'


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


def get_contrast_dir():
    if plat == win:
        return contrast_dir_win
    else:
        return contrast_dir_linux


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


def get_contrast_path(file_name: str) -> str:
    return os.path.join(get_contrast_dir(), append_suffix(file_name, contrast_suffix))


def recognize_text(file_path):
    image = cv2.imread(file_path)

    greyed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    transform = np.ones((1, 1), np.uint8)

    greyed_image = cv2.dilate(greyed_image, transform, iterations=1)
    greyed_image = cv2.erode(greyed_image, transform, iterations=1)

    THRES_IMAGE_PATH = get_thres_path(file_path)

    cv2.imwrite(THRES_IMAGE_PATH, greyed_image)

    result = pytesseract.image_to_string(Image.open(THRES_IMAGE_PATH), lang="ukr")
    return result


def margin_face(location, image_array):
    top, right, bottom, left = location

    MARGIN = 0.25

    face_height = bottom - top
    face_width = right - left
    top = top - face_height * MARGIN if top - face_height * MARGIN > 0 else 0
    bottom = bottom + face_height * MARGIN if bottom + face_height * MARGIN < image_array.shape[0] \
        else image_array.shape[0] - 1
    left = left - face_width * MARGIN if left - face_width * MARGIN > 0 else 0
    right = right + face_width * MARGIN if right + face_width * MARGIN < image_array.shape[1] \
        else image_array.shape[1] - 1
    top, right, bottom, left = list(map(int, (top, right, bottom, left)))
    return top, right, bottom, left


image_name = 'cool.jpg'
CROPPED_IMAGE_PATH = get_croped_path(image_name)
SHARPED_IMAGE_PATH = get_sharped_path(image_name)
CONTRAST_IMAGE_PATH = get_contrast_path(image_name)


def image_process():
    origin_image = cv2.imread(get_origin_path(image_name))
    current_image = origin_image
    iteration = 3
    for i in range(0, iteration):

        if i != 0:

            cv2.imwrite("iteration" + str(i) + ".png", current_image)
            lightImg = Image.open("iteration" + str(i) + ".png")
            enhancer = ImageEnhance.Contrast(lightImg)
            enhanced_im = enhancer.enhance(1.5)
            enhanced_im.save("iteration" + str(i) + ".png")

            hls_image = cv2.cvtColor(cv2.imread("iteration" + str(i) + ".png"), cv2.COLOR_BGR2HLS)

        else:
            hls_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2HLS)

        sensitivity = 80

        lower_white = np.array([0, 255 - sensitivity, 0])
        upper_white = np.array([255, 255, 255])

        color_range_mask = cv2.inRange(hls_image, lower_white, upper_white)
        cv2.imwrite("mask" + str(i) + ".png", color_range_mask)

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

        location = [y_min, x_max, y_max, x_min]
        top, right, bottom, left = margin_face(location, origin_image)

        if i != iteration - 1:
            current_image = current_image[top:bottom, left:right]
            cv2.imwrite(CROPPED_IMAGE_PATH, current_image)
        else:
            cropped_image = current_image[y_min:y_max, x_min:x_max]
            cv2.imwrite(CROPPED_IMAGE_PATH, cropped_image)

    image = Image.open(CROPPED_IMAGE_PATH)
    enhancer = ImageEnhance.Contrast(image)
    enhanced_im = enhancer.enhance(1.2)
    enhanced_im.save(CONTRAST_IMAGE_PATH)

    image = Image.open(CONTRAST_IMAGE_PATH)
    enhancer = ImageEnhance.Sharpness(image)
    enhanced_im = enhancer.enhance(4.0)
    enhanced_im.save(SHARPED_IMAGE_PATH)

    # image = Image.open(SHARPED_IMAGE_PATH)
    # enhancer = ImageEnhance.Brightness(image)
    # enhanced_im = enhancer.enhance(1.03)
    # enhanced_im.save(SHARPED_IMAGE_PATH)

    return recognize_text(SHARPED_IMAGE_PATH)


if __name__ == '__main__':
    # print(plat)
    # print(get_origin_path(get_origin_path(image_name)))
    # print(get_sharped_path(get_origin_path(image_name)))
    # print(get_thres_path(get_origin_path(image_name)))
    # print(get_croped_path(get_origin_path(image_name)))

    parsed_text = image_process()

    data = parsing.parse(parsed_text)
    print(data)
