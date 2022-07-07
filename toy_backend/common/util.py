import os
import cv2
import numpy as np


def create_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name, exist_ok=True)


def is_file_exist(file_dir):
    return os.path.isfile(file_dir)


def to_jpg(file, file_path):
    np_img = np.frombuffer(file.read(), np.uint8)
    print(np_img)
    img = cv2.imdecode(np_img, cv2.IMREAD_UNCHANGED)
    print(np_img)

    extension = '.jpg'
    file_full_path = file_path + extension
    cv2.imwrite(file_full_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

