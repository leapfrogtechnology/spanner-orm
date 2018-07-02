import re
import inspect
import base_model
from .dataType import *
from datetime import date
from .dataType import DataType


class Helper(object):
    @classmethod
    def is_property(cls, v):
        """
        Check is property

        :type: object
        :param v:

        :return:
        """
        return isinstance(v, property)

    @classmethod
    def is_attr(cls, v):
        """
        Check is model attr

        :type: object
        :param v:
        """
        return isinstance(v, StringField) | isinstance(v, IntegerField) | isinstance(v, BoolField) \
               | isinstance(v, IntegerField) | isinstance(v, FloatField) | isinstance(v, BytesField) \
               | isinstance(v, DateField) | isinstance(v, TimeStampField) | isinstance(v, EnumField)

    @classmethod
    def get_model_props(cls, model_cls):
        """
        Return model props

        :type model_cls: base_model.BaseModel
        :param model_cls: model

        :rtype: dict
        :return:
        """
        model_props = {}
        for key, value in inspect.getmembers(model_cls, Helper.is_property):
            model_props[key] = value

        return model_props

    @classmethod
    def get_model_attrs(cls, model_cls):
        """
        Return model attr

        :type model_cls: base_model.BaseModel
        :param model_cls: Model class

        :rtype: dict
        :return: model attributes in key value pairs
        """
        attrs = {}
        for key, value in inspect.getmembers(model_cls, Helper.is_attr):
            attrs[key] = value

        return attrs

    @classmethod
    def get_model_props_key_value(cls, model_obj):
        """
        Return model props key-value

        :type model_obj: base_model.BaseModel
        :param model_obj: model

        :rtype: dict
        :return:
        """
        model_props = {}
        for key, value in inspect.getmembers(model_obj.__class__, Helper.is_property):
            model_props[key] = model_obj.__getattribute__(key)

        return model_props

    @classmethod
    def model_attr_by_prop(cls, model_cls, prop):
        """
        Return model attribute by property

        :type model_cls: base_model.BaseModel
        :param model_cls: Model class

        :type prop: property
        :param prop: Model class property

        :rtype: DataType
        :return: Model attribute
        """
        if isinstance(prop, property) is False:
            raise TypeError('Invalid object property')

        model_attr_name = '_' + prop.fget.__name__
        model_attrs = Helper.get_model_attrs(model_cls)
        if model_attrs.has_key(model_attr_name) is False:
            raise TypeError('Criteria model property {} not exist'.format(model_attr_name))

        return model_attrs.get(model_attr_name)

    @classmethod
    def get_db_columns(cls, model_cls):
        model_attrs = Helper.get_model_attrs(model_cls)

        columns = []
        for attr_name in model_attrs:
            attr = model_attrs.get(attr_name)
            columns.append(attr.db_column)

        return columns

    @classmethod
    def validate_model_prop(cls, model_cls, prop):
        """
        Validate model attr

        :type model_cls: base_model.BaseModel
        :param model_cls: Model class

        :type prop: property
        :param prop:

        :rtype: dict
        :return: {'is_valid':bool, 'error_msg':str}
        """
        if isinstance(prop, property) is False:
            raise TypeError('Invalid object property')

        model_attr_name = '_' + prop.fget.__name__
        model_attrs = Helper.get_model_attrs(model_cls)

        if model_attrs.has_key(model_attr_name):
            attr = model_attrs.get(model_attr_name)
            if isinstance(attr, IntegerField) or isinstance(attr, FloatField):
                return Helper.validate_number_field(attr.value, max_value=attr.max_value, min_value=attr.min_value,
                                                    null=attr.null)
            elif isinstance(attr, StringField):
                return Helper.validate_string_field(attr.value, max_length=attr.max_length, reg_exr=attr.reg_exr,
                                                    null=attr.null)
            elif isinstance(attr, BoolField):
                return Helper.validate_bool_field(attr.value, null=attr.null)
            elif isinstance(attr, TimeStampField):
                return Helper.validate_timestamp_field(attr.value, null=attr.null)
            elif isinstance(attr, DateField):
                return Helper.validate_date_field(attr.value, null=attr.null)
            elif isinstance(attr, EnumField):
                return Helper.validate_enum_field(attr.value, enum_list=attr.enum_list, null=attr.null)

        return {
            'is_valid': True,
            'error_msg': None
        }

    @classmethod
    def validate_number_field(cls, value, max_value=None, min_value=None, null=True):
        """
        Validate number field value

        :type value: int | float
        :param value: integer value

        :type max_value: int
        :param max_value: max allow number value

        :type min_value: int
        :param min_value: min allow integer value

        :type null: bool
        :param null: is allow None value

        :rtype: dict
        :return: {'is_valid':bool, 'error_msg':str}
        """

        is_valid = True
        error_msg = None
        if null is False and value is None:
            is_valid = False
            error_msg = 'Property value should not be None'

        if value is not None:
            if isinstance(value, int) is False:
                is_valid = False
                error_msg = 'Data type should be <int>'

            if max_value is not None and value > max_value:
                is_valid = False
                error_msg = 'Max allow value: {}'.format(max_value)

            if min_value is not None and value < min_value:
                is_valid = False
                error_msg = 'Min allow value: {}'.format(min_value)

        return {
            'is_valid' : is_valid,
            'error_msg' : error_msg
        }

    @classmethod
    def validate_string_field(cls, value, max_length=None, reg_exr=None, null=True):
        """
        Validate string field value

        :type max_length: int
        :param max_length: max allow string lenght

        :type reg_exr: str
        :param reg_exr: regex pattern

        :type null: bool
        :param null: is allow None value

        :rtype: dict
        :return: {'is_valid':bool, 'error_msg':str}
        """
        is_valid = True
        error_msg = None
        if null is False and (value is None or value.strip() == ''):
            is_valid = False
            error_msg = 'Data should not be None or empty'

        if value is not None:
            if isinstance(value, str) is False:
                is_valid = False
                error_msg = 'Data type should be <str>'

            if max_length is not None and len(value) > max_length:
                is_valid = False
                error_msg = 'Max allow string length: {}'.format(max_length)

            if reg_exr is not None:
                pattern = re.compile(reg_exr)
                if pattern.match(value) is None:
                    is_valid = False
                    error_msg = 'String should match regex pattern: {}'.format(reg_exr)

        return {
            'is_valid': is_valid,
            'error_msg': error_msg
        }

    @classmethod
    def validate_bool_field(cls, value, null=True):
        """
        Validate bool field value

        :type value: bool
        :param value:

        :type null: bool
        :param null: is allow None value

        :rtype: dict
        :return: {'is_valid':bool, 'error_msg':str}
        """
        is_valid = True
        error_msg = None
        if null is False and value is None:
            is_valid = False
            error_msg = 'Data should not be None'

        if value is not None and isinstance(value, bool) is False:
            is_valid = False
            error_msg = 'Data type should be <bool>'

        return {
            'is_valid': is_valid,
            'error_msg': error_msg
        }

    @classmethod
    def validate_timestamp_field(cls, value, null=True):
        """
        Validate timestamp field value

        :type value: int | float
        :param value:

        :type null: bool
        :param null: is allow None value

        :rtype: dict
        :return: {'is_valid':bool, 'error_msg':str}
        """
        is_valid = True
        error_msg = None
        if null is False and value is None:
            is_valid = False
            error_msg = 'Data should not be None'

        if value is not None and isinstance(value, int) is False and isinstance(value, float) is False:
            is_valid = False
            error_msg = 'Data type should be <float> or <int> timestamp'

        return {
            'is_valid': is_valid,
            'error_msg': error_msg
        }

    @classmethod
    def validate_date_field(cls, value, null=True):
        """
        Validate enum field value

        :type value: date
        :param value:

        :type null: bool
        :param null: is allow None value

        :rtype: dict
        :return: {'is_valid':bool, 'error_msg':str}
        """
        is_valid = True
        error_msg = None
        if null is False and value is None:
            is_valid = False
            error_msg = 'Data should not be None'

        if value is not None and isinstance(value, date) is False:
            is_valid = False
            error_msg = 'Data type should be <datetime.date>'

        return {
            'is_valid': is_valid,
            'error_msg': error_msg
        }

    @classmethod
    def validate_enum_field(cls, value, enum_list, null=True):
        """
        Validate enum field value

        :type value: object
        :param value:

        :type enum_list: list
        :param enum_list: list of allow value

        :type null: bool
        :param null: is allow None value

        :rtype: dict
        :return: {'is_valid':bool, 'error_msg':str}
        """
        is_valid = True
        error_msg = None
        if null is False and value is None:
            is_valid = False
            error_msg = 'Data should not be None'

        if value is not None:
            if value in enum_list is False:
                is_valid = False
                error_msg = 'Data value should be from list: {}'.format(enum_list)

        return {
            'is_valid': is_valid,
            'error_msg': error_msg
        }

    @classmethod
    def get_model_props_details(cls, model_cls):
        """
        Return model props details

        :type model_cls: base_model.BaseModel
        :param model_cls:

        :rtype: dict
        :return:
        """
        model_props = Helper.get_model_props(model_cls)
        model_attrs = Helper.get_model_attrs(model_cls)

        props_details = {}
        for prop_name in model_props:
            model_attr_name = '_' + prop_name
            if model_attrs.has_key(model_attr_name):
                attr = model_attrs.get(model_attr_name)
                props_details.update({
                    prop_name: Helper.get_prop_details(attr)
                })

        return props_details

    @classmethod
    def get_prop_details(cls, attr):
        """
        Return model attr field details

        :type attr: DataType
        :param attr:

        :rtype: dict
        :return:
        """
        details = {
            'db_column': attr.db_column,
            'data_type': attr.data_type,
            'null': attr.null,
            'default_value': attr.default
        }

        if isinstance(attr, IntegerField):
            details.update({
                'max_value': attr.max_value,
                'min_value': attr.min_value
            })
        if isinstance(attr, FloatField):
            details.update({
                'max_value': attr.max_value,
                'min_value': attr.min_value,
                'decimal_places': attr.decimal_places
            })
        if isinstance(attr, StringField):
            details.update({
                'max_length': attr.max_length,
                'reg_exr': attr.reg_exr
            })
        if isinstance(attr, EnumField):
            details.update({
                'enum_list': attr.enum_list
            })

        return details

    @classmethod
    def init_model_with_default(cls, model_class):
        """
        Init model object with default values

        :type model_class: base_model.BaseModel
        :param model_class:

        :rtype: base_model.BaseModel
        :return: model object
        """
        model_object = model_class()
        model_attrs = Helper.get_model_attrs(model_object)
        for attr_name in model_attrs:
            attr = model_attrs.get(attr_name)
            if attr.default is not None:
                attr.value = attr.default

        return model_object
