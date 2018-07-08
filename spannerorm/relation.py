import copy
import helper
import base_model
from functools import wraps
from .criteria import Criteria


class Relation(object):
    def __init__(self, join_on, relation_name, refer_to, relation_type):
        self._join_on = join_on
        self._refer_to = refer_to
        self._with_relation = False
        self._relation_name = relation_name
        self._relation_type = relation_type

    @property
    def join_on(self):
        return self._join_on

    @property
    def relation_name(self):
        return self._relation_name

    @property
    def refer_to(self):
        return self._refer_to

    @property
    def relation_type(self):
        return self._relation_type

    @classmethod
    def get_refer_model(cls, model_obj, relation_name):
        relations = model_obj._meta().relations()
        if relation_name not in relations:
            raise TypeError('Invalid model relation set')

        return relations.get(relation_name)

    def fetch_data(self, model_obj, refer_model):
        """
        Fetch relation data

        :type model_obj: base_model.BaseModel
        :param model_obj: model object

        :rtype: base_model.BaseModel | list | None
        :return:
        """
        join_on = self.join_on
        refer_to = self.refer_to
        join_on_value = helper.Helper.get_model_props_value_by_key(model_obj, join_on)
        refer_model_prop = helper.Helper.get_model_prop_by_name(refer_model, refer_to)

        if self.relation_type == 'ManyToOne' or self.relation_type == 'OneToOne':
            criteria = Criteria()
            if join_on_value is not None:
                criteria.add_condition((refer_model_prop, '=', join_on_value))
                return refer_model.find(criteria)

            return None
        else:
            return []

    @classmethod
    def copy_instance(cls, relation):
        if relation.relation_type == 'ManyToOne':
            return ManyToOne(relation.join_on, relation.relation_name, relation.refer_to)
        elif relation.relation_type == 'OneToOne':
            return OneToOne(relation.join_on, relation.relation_name, relation.refer_to)
        elif relation.relation_type == 'ManyToOne':
            return ManyToOne(relation.join_on, relation.relation_name, relation.refer_to)
        else:
            return ManyToMany(relation.join_on, relation.relation_name, relation.refer_to)

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
            print('-------------------------- relational getter -----------------------')
            if model_obj._model_state().is_new:
                if relation.relation_type == 'ManyToOne' or relation.relation_type == 'OneToOne':
                    return None
                else:
                    return []

            if relation is not None and relation.data is None:
                refer_model = Relation.get_refer_model(model_obj, relation.relation_name)
                join_on = relation.join_on
                refer_to = relation.refer_to
                join_on_value = helper.Helper.get_model_props_value_by_key(model_obj, join_on)
                refer_model_prop = helper.Helper.get_model_prop_by_name(refer_model, refer_to)

                # if relation.relation_type == 'ManyToOne':
                #   return ManyToOne.fetch_data(refer_model, refer_model_prop=refer_model_prop,
                #                               refer_prop_value=join_on_value)
                # Todo fetch data & set relational data
                print(type(refer_model))
                print(join_on)
                print(refer_to)
                print(join_on_value)
                print('-------------------------- relational getter end > 1 -----------------------')
                return relation.data
            elif relation is not None and relation.data is not None:
                print('-------------------------- relational getter end > 2 -----------------------')
                return relation.data
            else:
                print('-------------------------- relational getter end > 3 -----------------------')
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
            print('-------------------------- relational setter -----------------------')
            model_attr = helper.Helper.model_relational_attr_by_prop_name(model_obj, func.__name__)
            attr = copy.deepcopy(model_attr)
            model_attr.data = value

            print('-------------------------- relational setter end  -----------------------')
            return func(model_obj, attr)

        return wrapper


class OneToMany(Relation):
    def __init__(self, join_on, relation_name, refer_to):
        self._data_list = None
        Relation.__init__(self, join_on=join_on, relation_name=relation_name, refer_to=refer_to,
                          relation_type='OneToMany')

    @property
    def data(self):
        return self._data_list

    @data.setter
    def data(self, data_list):
        self._data_list = data_list


class ManyToOne(Relation):
    def __init__(self, join_on, relation_name, refer_to):
        self._data = None
        Relation.__init__(self, join_on=join_on, relation_name=relation_name, refer_to=refer_to,
                          relation_type='ManyToOne')

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data


class OneToOne(Relation):
    def __init__(self, join_on, relation_name, refer_to):
        self._relation_type = 'OneToOne'
        self._data = None
        Relation.__init__(self, join_on=join_on, relation_name=relation_name, refer_to=refer_to,
                          relation_type='OneToOne')

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data


class ManyToMany(Relation):
    def __init__(self, join_on, relation_name, refer_to):
        self._relation_type = 'ManyToMany'
        self._data_list = None
        Relation.__init__(self, join_on=join_on, relation_name=relation_name, refer_to=refer_to,
                          relation_type='ManyToMany')

    @property
    def data(self):
        return self._data_list

    @data.setter
    def data(self, data_list):
        self._data_list = data_list
