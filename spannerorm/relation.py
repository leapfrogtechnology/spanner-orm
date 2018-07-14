import copy
import spannerorm.helper
import spannerorm.base_model
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

        :type model_obj: spannerorm.base_model.BaseModel
        :param model_obj: model object

        :rtype: spannerorm.base_model.BaseModel | list | None
        :return:
        """
        join_on = self.join_on
        refer_to = self.refer_to
        join_on_value = spannerorm.helper.Helper.get_model_props_value_by_key(model_obj, join_on)
        refer_model_prop = spannerorm.helper.Helper.get_model_prop_by_name(refer_model, refer_to)

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
        """
        Copy relation instance

        :type relation: Relation
        :param relation: relation object

        :rtype: Relation
        :return:
        """
        if relation.relation_type == 'ManyToOne':
            return ManyToOne(relation.join_on, relation.relation_name, relation.refer_to)
        elif relation.relation_type == 'OneToOne':
            return OneToOne(relation.join_on, relation.relation_name, relation.refer_to)
        elif relation.relation_type == 'OneToMany':
            return OneToMany(relation.join_on, relation.relation_name, relation.refer_to)
        else:
            return ManyToMany(relation.join_on, relation.relation_name, relation.refer_to)

    @staticmethod
    def get(func):
        """
        Relation property get decorator

        :type func: function
        :param func:

        :rtype: list | spannerorm.base_model.BaseModel | None
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            model_obj = args[0]
            relation = func(*args, **kwargs)
            if model_obj._model_state().is_new:
                if relation.relation_type == 'ManyToOne' or relation.relation_type == 'OneToOne':
                    return None
                else:
                    return []

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

            model_attr = spannerorm.helper.Helper.model_relational_attr_by_prop_name(model_obj, func.__name__)
            attr = copy.deepcopy(model_attr)
            attr.data = value

            return func(model_obj, attr)

        return wrapper


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


class OneToMany(Relation):
    def __init__(self, join_on, relation_name, refer_to):
        self._data_list = []
        Relation.__init__(self, join_on=join_on, relation_name=relation_name, refer_to=refer_to,
                          relation_type='OneToMany')

    @property
    def data(self):
        return self._data_list

    @data.setter
    def data(self, data_list):
        self._data_list = data_list


class ManyToMany(Relation):
    def __init__(self, join_on, relation_name, refer_to):
        self._relation_type = 'ManyToMany'
        self._data_list = []
        Relation.__init__(self, join_on=join_on, relation_name=relation_name, refer_to=refer_to,
                          relation_type='ManyToMany')

    @property
    def data(self):
        return self._data_list

    @data.setter
    def data(self, data_list):
        self._data_list = data_list
