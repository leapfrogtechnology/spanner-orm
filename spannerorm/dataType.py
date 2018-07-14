import copy
import spannerorm.helper
from functools import wraps
from google.cloud.spanner_v1.proto.type_pb2 import Type, INT64, FLOAT64, STRING, BOOL, BYTES, TIMESTAMP, DATE


class DataType:
    def __init__(self, db_column, null=True, default=None):
        self.value = None
        self.null = null
        self.db_column = db_column
        self.default = default

    @staticmethod
    def get(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            model_obj = args[0]
            data_field = function(*args, **kwargs)
            return data_field.value

        return wrapper

    @staticmethod
    def set(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            model_obj = args[0]
            value = args[1]

            model_attr = spannerorm.helper.Helper.model_attr_by_prop_name(model_obj, function.__name__)
            attr = copy.deepcopy(model_attr)
            attr.value = value

            if isinstance(attr, IntegerField) or isinstance(attr, FloatField):
                validation = spannerorm.helper.Helper.validate_number_field(attr.value, max_value=attr.max_value,
                                                                 min_value=attr.min_value, null=attr.null)
            elif isinstance(attr, StringField):
                validation = spannerorm.helper.Helper.validate_string_field(attr.value, max_length=attr.max_length,
                                                                 reg_exr=attr.reg_exr, null=attr.null)
            elif isinstance(attr, BoolField):
                validation = spannerorm.helper.Helper.validate_bool_field(attr.value, null=attr.null)
            elif isinstance(attr, TimeStampField):
                validation = spannerorm.helper.Helper.validate_timestamp_field(attr.value, null=attr.null)
            elif isinstance(attr, DateField):
                validation = spannerorm.helper.Helper.validate_date_field(attr.value, null=attr.null)
            elif isinstance(attr, EnumField):
                validation = spannerorm.helper.Helper.validate_enum_field(attr.value, enum_list=attr.enum_list, null=attr.null)
            else:
                validation = {
                    'is_valid': False,
                    'error_msg': 'Invalid DataField'
                }

            if validation.get('is_valid'):
                return function(model_obj, attr)
            else:
                error = {
                    function.__name__: validation
                }
                raise RuntimeError('Data validation error: {}'.format(error))

        return wrapper


class IntegerField(DataType):
    def __init__(self, db_column, max_value=None, min_value=None, null=True, default=None):
        self.data_type = Type(code=INT64)
        self.max_value = max_value
        self.min_value = min_value
        DataType.__init__(self, db_column=db_column, null=null, default=default)


class FloatField(DataType):
    def __init__(self, db_column, max_value=None, min_value=None, null=True, default=None, decimal_places=2):
        self.data_type = Type(code=FLOAT64)
        self.max_value = max_value
        self.min_value = min_value
        self.decimal_places = decimal_places
        DataType.__init__(self, db_column=db_column, null=null, default=default)


class StringField(DataType):
    def __init__(self, db_column, max_length=None, null=True, default=None, reg_exr=None):
        self.data_type = Type(code=STRING)
        self.max_length = max_length
        self.reg_exr = reg_exr
        DataType.__init__(self, db_column=db_column, null=null, default=default)


class BoolField(DataType):
    def __init__(self, db_column, null=True, default=None):
        self.data_type = Type(code=BOOL)
        DataType.__init__(self, db_column=db_column, null=null, default=default)


class BytesField(DataType):
    def __init__(self, db_column, null=True, default=None):
        self.data_type = Type(code=BYTES)
        DataType.__init__(self, db_column=db_column, null=null, default=default)


class TimeStampField(DataType):
    def __init__(self, db_column, null=True, default=None):
        self.data_type = Type(code=TIMESTAMP)
        DataType.__init__(self, db_column=db_column, null=null, default=default)


class DateField(DataType):
    def __init__(self, db_column, null=True, default=None):
        self.data_type = Type(code=DATE)
        DataType.__init__(self, db_column=db_column, null=null, default=default)


class EnumField(DataType):
    def __init__(self, db_column, enum_list, null=True, default=None):
        self.data_type = Type(code=STRING)
        self.enum_list = enum_list
        DataType.__init__(self, db_column=db_column, null=null, default=default)
