import os
import random


def create_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name, exist_ok=True)


def get_date_from_file_path(input_path):
    file_path = os.path.dirname(input_path)
    return os.path.basename(file_path)


def split_file_name(input_path):
    file_name = os.path.basename(input_path)
    return os.path.splitext(file_name)


def is_file_exist(file_dir):
    return os.path.isfile(file_dir)


def assign_file_name(original_path, extension):
    file_name = str(random.randint(0, 100000))
    if is_file_exist(os.path.join(original_path, file_name + extension)):
        _, file_name = assign_file_name(original_path, extension)
    return original_path, file_name


def round(num, digits=0):
    if digits:
        multiplier = 10 ** digits
        return int(num * multiplier + 0.5) / multiplier
    else:
        return int(num + 0.5)