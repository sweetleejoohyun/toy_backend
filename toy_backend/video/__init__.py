import os
import ffmpeg


def save_to_mp4(file, file_path, file_name):
    return change_video_codec(file, file_path, file_name)


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
    return temp_path


def get_video_info(video_path):
    probe = ffmpeg.probe(video_path)
    w = probe['streams'][0]['width']
    h = probe['streams'][0]['height']
    return {'width': w, 'height': h}