from config import CustomObject


class ObjectDetectResult(CustomObject):
    def __init__(self, obj_path, obj, score, coordinates):
        super(ObjectDetectResult, self).__init__()
        self.obj_path = obj_path
        self.obj = obj
        self.score = score
        self.coordinates = coordinates