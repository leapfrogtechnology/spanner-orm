from .model import Model
from datetime import date
from flask.json import JSONEncoder


class ModelJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, Model):
                return obj.__dict__()
            if isinstance(obj, date):
                return obj.strftime('%Y-%m-%d')
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)

        return JSONEncoder.default(self, obj)
