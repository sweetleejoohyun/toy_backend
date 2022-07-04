class CustomObject(object):
    def __init__(self, attr_dict=None):
        if attr_dict:
            for k, v in attr_dict.items():
                if isinstance(v, dict):
                    v = CustomObject(v)
                setattr(self, k, v)

    def __repr__(self):
        return str(self.__dict__)