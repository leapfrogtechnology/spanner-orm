import copy
import helper
import inspect
import base_model
from functools import wraps
from .criteria import Criteria


class Relation(object):
    def __init__(self, join_on, reference_module, refer_to):
        self._join_on = join_on
        self._reference_module = reference_module
        self._refer_model = Relation.get_refer_model_class(reference_module)
        self._refer_to = refer_to
        self._with_relation = False

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

    @classmethod
    def copy_instance(cls, relation):
        if relation.relation_type == 'ManyToOne':
            return ManyToOne(relation.join_on, relation.reference_module, relation.refer_to)

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
            if relation is not None and relation.data is None:
                refer_model = relation.refer_model
                join_on = relation.join_on
                refer_to = relation.refer_to
                join_on_value = helper.Helper.get_model_props_value_by_key(model_obj, join_on)
                refer_model_prop = helper.Helper.get_model_prop_by_name(refer_model, refer_to)

                # if relation.relation_type == 'ManyToOne':
                #   return ManyToOne.fetch_data(refer_model, refer_model_prop=refer_model_prop,
                #                               refer_prop_value=join_on_value)
                # Todo fetch data & set relational data

                return relation.data
            elif relation is not None and relation.data is not None:
                return relation.data
            else:
                return None

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

    @classmethod
    def fetch_data(cls, refer_model, refer_model_prop, refer_prop_value):
        """
        Fetch ManyToOne relation data

        :type refer_model: base_model.BaseModel
        :param refer_model: refer model class

        :type refer_model_prop: property
        :param refer_model_prop: refer model property

        :type refer_prop_value: object
        :param refer_prop_value: value of refer proper

        :rtype: base_model.BaseModel
        :return:
        """
        criteria = Criteria()
        if refer_prop_value != None:
            criteria.add_condition((refer_model_prop, '=', refer_prop_value))

            return refer_model.find(criteria)

        return None


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
