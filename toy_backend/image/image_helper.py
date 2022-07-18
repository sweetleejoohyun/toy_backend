import os
import cv2

from toy_backend.common.util import is_file_exist


TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.5


def crop_image(np_image, result, base_dir, file_name='0'):
    coordinates, entity, score = tuple(result)
    ymin, xmin, ymax, xmax = tuple(coordinates)
    img_height, img_width, _ = np_image.shape
    cropped_image = np_image[int(ymin*img_height):int(ymax*img_height),
                    int(xmin*img_width):int(xmax*img_width)]

    result_saved_img_url = os.path.join(base_dir, file_name + '_' + entity+'_' + str(score) + '.jpg')
    cv2.imwrite(result_saved_img_url, cropped_image)
    new_coordinates = {'xmin': int(xmin*img_width),
                       'ymin': int(ymin*img_height),
                       'xmax': int(xmax*img_width),
                       'ymax': int(ymax*img_height)}
    return result_saved_img_url, new_coordinates


def bound_box_image(np_image, result):
    coordinates, entity, score = tuple(result)
    ymin, xmin, ymax, xmax = tuple(coordinates)
    img_height, img_width, _ = np_image.shape
    src = cv2.rectangle(np_image, (int(xmin*img_width), int(ymin*img_height)),
                        (int(xmax*img_width), int(ymax*img_height)), (255, 0, 0), 1)
    cv2.putText(src, entity, (int(xmin*img_width), int(ymin*img_height)), TEXT_FONT, FONT_SIZE, (255, 0, 0))
    return src


def to_ndarray(image_path: str):
    if not is_file_exist(image_path):
        return None

    np_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    return np_image
