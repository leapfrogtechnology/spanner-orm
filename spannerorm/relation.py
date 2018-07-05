import copy
import helper
import inspect
import base_model
from functools import wraps


class Relation(object):
    def __init__(self, join_on, reference_module, refer_to):
        self._join_on = join_on
        self._reference_module = reference_module
        self._refer_model = Relation.get_refer_model_class(reference_module)
        self._refer_to = refer_to

    @property
    def join_on(self):
        return self._join_on

    @property
    def reference_module(self):
        return self._reference_module

    @property
    def refer_to(self):
        return self._refer_to

    @property
    def refer_model(self):
        return self._refer_model

    @classmethod
    def get_prop_value(cls, obj, prop_name):
        """
        Return object property value

        :type obj: object
        :param obj:

        :type prop_name: str
        :param prop_name: property name

        :rtype: object
        :return: value
        """
        return obj.__getattribute__(prop_name)

    @classmethod
    def get_refer_model_class(cls, reference_module):
        """
        Return refer model class by reference module

        :type reference_module: module
        :param reference_module: reference module

        :rtype: base_model.BaseModel
        :return:
        """
        module_name = reference_module.__name__
        for name, obj in inspect.getmembers(reference_module):
            if inspect.isclass(obj) and obj.__module__ == module_name:
                return obj

        return None

    @staticmethod
    def get(func):
        """
        Relation property get decorator

        :type func: function
        :param func:

        :rtype: list | base_model.BaseModel | None
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            model_obj = args[0]
            relation = func(*args, **kwargs)
            if relation.data is None:
                refer_model = relation.refer_model
                join_on = relation.join_on
                refer_to = relation.refer_to
                join_on_value = Relation.get_prop_value(model_obj, join_on)

                # Todo fetch data & set relational data

                return relation.data
            else:
                return relation.data

        return wrapper

    @staticmethod
    def set(func):
        """
        Relational property set decorator

        :type func: function
        :param func:

        :rtype: function
        :return: setter function
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            model_obj = args[0]
            value = args[1]

            model_attr = helper.Helper.model_relational_attr_by_prop_name(model_obj, func.__name__)
            attr = copy.deepcopy(model_attr)
            model_attr.data = value

            return func(model_obj, attr)

        return wrapper


class OneToMany(Relation):
    def __init__(self, join_on, reference_module, refer_to):
        self._relation_type = 'OneToMany'
        self._data_list = None
        Relation.__init__(self, join_on=join_on, reference_module=reference_module, refer_to=refer_to)

    @property
    def relation_type(self):
        return self._relation_type

    @property
    def data(self):
        return self._data_list

    @data.setter
    def data(self, data_list):
        self._data_list = data_list


class ManyToOne(Relation):
    def __init__(self, join_on, reference_module, refer_to):
        self._relation_type = 'ManyToOne'
        self._data = None
        Relation.__init__(self, join_on=join_on, reference_module=reference_module, refer_to=refer_to)

    @property
    def relation_type(self):
        return self._relation_type

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data


class ManyToMany(Relation):
    def __init__(self, join_on, reference_module, refer_to):
        self._relation_type = 'ManyToMany'
        self._data_list = None
        Relation.__init__(self, join_on=join_on, reference_module=reference_module, refer_to=refer_to)

    @property
    def relation_type(self):
        return self._relation_type

    @property
    def data(self):
        return self._data_list

    @data.setter
    def data(self, data_list):
        self._data_list = data_list
