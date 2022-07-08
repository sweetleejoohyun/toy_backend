import os
import cv2
import numpy as np
import random
import ffmpeg


def create_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name, exist_ok=True)


def is_file_exist(file_dir):
    return os.path.isfile(file_dir)


def assign_file_name(original_path, extension):
    file_name = str(random.randint(0, 3)) # 100000
    if is_file_exist(os.path.join(original_path, file_name + extension)):
        _, file_name = assign_file_name(original_path, extension)
    return original_path, file_name


def save_to_jpg(file, file_path, file_name):
    extension = '.jpg'
    np_img = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_UNCHANGED)
    file_full_path = os.path.join(file_path, file_name + extension)
    cv2.imwrite(file_full_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])


def save_to_mp4(file, file_path, file_name):
    change_video_codec(file, file_path, file_name)


def change_video_codec(file, file_path, file_name):
    extension = '.mp4'
    temp_path = os.path.join(file_path, file_name + extension)
    file.save(temp_path)
    probe = ffmpeg.probe(temp_path)
    if not probe['streams'][0]['codec_name'] == 'h264':
        ffmpeg.input(temp_path)\
            .output(os.path.join(file_path, 'temp.mp4'), vcodec='libx264')\
            .run(quiet=True)
        os.remove(temp_path)
        os.rename(os.path.join(file_path, 'temp.mp4'), temp_path)
