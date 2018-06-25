from google.cloud.spanner_v1.proto.type_pb2 import Type, INT64, FLOAT64, STRING, BOOL, BYTES, TIMESTAMP, DATE


class DataType:
    def __init__(self, db_column, null=True, default=None):
        self.value = None
        self.null = null
        self.db_column = db_column
        self.default = default


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
