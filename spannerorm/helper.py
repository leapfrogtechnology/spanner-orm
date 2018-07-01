import re
import inspect
import base_model
from .dataType import *
from datetime import date


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
    def get_model_props(cls, model_obj):
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
    def validate_model_prop(cls, model_cls, prop):
        """
        Validate model attr

        :type model_cls: base_model.BaseModel
        :param model_cls: Model class

        :type prop: property
        :param prop:

        :rtype: bool
        :return:
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

        return True

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

        :rtype: bool
        :return: True if valid else False
        """
        if null is False and value is None:
            return False

        if value is not None:
            if isinstance(value, int) is False:
                return False

            if max_value is not None and value > max_value:
                return False

            if min_value is not None and value < min_value:
                return False

        return True

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

        :rtype: bool
        :return: True if valid else False
        """
        if null is False and (value is None or value.strip() == ''):
            return False

        if value is not None:
            if isinstance(value, str) is False:
                return False

            if max_length is not None and len(value) > max_length:
                return False
            if reg_exr is not None:
                pattern = re.compile(reg_exr)
                if pattern.match(value) is None:
                    return False

        return True

    @classmethod
    def validate_bool_field(cls, value, null=True):
        """
        Validate bool field value

        :type value: bool
        :param value:

        :type null: bool
        :param null: is allow None value

        :rtype: bool
        :return: True if valid else False
        """
        if null is False and value is None:
            return False

        if value is not None and isinstance(value, bool) is False:
            return False

        return True

    @classmethod
    def validate_timestamp_field(cls, value, null=True):
        """
        Validate timestamp field value

        :type value: int | float
        :param value:

        :type null: bool
        :param null: is allow None value

        :rtype: bool
        :return: True if valid else False
        """
        if null is False and value is None:
            return False

        if value is not None and isinstance(value, int) is False and isinstance(value, float) is False:
            return False

        return True

    @classmethod
    def validate_date_field(cls, value, null=True):
        """
        Validate enum field value

        :type value: date
        :param value:

        :type null: bool
        :param null: is allow None value

        :rtype: bool
        :return: True if valid else False
        """
        if null is False and value is None:
            return False

        if value is not None and isinstance(value, date) is False:
            return False

        return True

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

        :rtype: bool
        :return: True if valid else False
        """
        if null is False and value is None:
            return False

        if value is not None:
            if value in enum_list is False:
                return False

        return True
