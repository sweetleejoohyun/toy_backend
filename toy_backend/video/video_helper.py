import cv2

TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.5


def video_info(input_path):
    vid_cap = cv2.VideoCapture(input_path)
    if vid_cap.isOpened():
        return {'fps': vid_cap.get(cv2.CAP_PROP_FPS),
                'frame_width': int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'frame_height': int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'num_frames': int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))}