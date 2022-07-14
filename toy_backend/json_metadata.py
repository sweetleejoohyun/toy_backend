import os
import json

from toy_backend.common.util import create_dir


class DetectionJson(object):
    @staticmethod
    def save(out_path: str, metadata: dict):
        create_dir(os.path.dirname(out_path))
        with open(out_path, 'w') as json_file:
            json.dump(obj=metadata, fp=json_file, indent=2)

