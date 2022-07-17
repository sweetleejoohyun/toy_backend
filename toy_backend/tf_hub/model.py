from toy_backend import logger


class Model(object):
    def __init__(self):
        self.models = {}

    def register_model(self, model):
        self.models[model.__class__.__name__] = model
        logger.info(self.models)

    def is_exists_model(self, model_name):
        if model_name in self.models:
            return True
        else:
            return False

    def get_model(self, model_name):
        return self.models.get(model_name)

    def delete_model(self, model_name):
        self.models.pop(model_name)