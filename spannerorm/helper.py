import base_model
import inspect
from .dataType import *


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
