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
    return os.path.join(original_path, file_name), file_name


def save_to_jpg(file, file_path):
    extension = '.jpg'
    np_img = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_UNCHANGED)
    file_full_path = file_path + extension
    cv2.imwrite(file_full_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])


def save_to_mp4(file, file_path, file_name):
    # np_img = np.frombuffer(file.read(), np.uint8)
    # img = cv2.imdecode(np_img, cv2.IMREAD_UNCHANGED)
    # extension = '.jpg'
    # file_full_path = file_path + extension
    # cv2.imwrite(file_full_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    change_video_codec(file, file_path)
    pass


def change_video_codec(file, temp_path):
    extension = '.mp4'
    file.save(temp_path + extension)
    if is_file_exist(temp_path + extension):
        print(temp_path + extension)
        probe = ffmpeg.probe(temp_path + extension)
        if not probe['streams'][0]['codec_name'] == 'h264':
            temp_filename = file.filename
            (
                ffmpeg.input(temp_path)
                      .output(os.path.join(temp_path, 'temp.mp4'), vcodec='libx264', acodec='aac')
                      .run(quiet=True)
            )
            print(f'temp_filename : {temp_filename}')
            print(f'temp_path : {temp_path}')
            os.remove(temp_path + extension)
            os.rename(os.path.join(temp_path, temp_filename), temp_path + extension)





