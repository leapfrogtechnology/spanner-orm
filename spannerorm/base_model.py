import inspect
from .helper import Helper
from .executor import Executor
from .criteria import Criteria
from .data_parser import DataParser
from .prepare_data import PrepareData
from .query_builder import QueryBuilder
from .spanner_exception import SpannerException


class BaseModel(object):
    def __init__(self, *args, **kwargs):
        if self._meta().db_table is None:
            raise Exception("Error: {0} model's Meta.db_table is not set".format(self.__class__.__name__))

        if self._meta().primary_key is None:
            raise SpannerException("Error: {0} model's Meta.primary_key is not set".format(self.__class__.__name__))

        for key in kwargs.iterkeys():
            self.__setattr__(key, kwargs.get(key))

        self.__state__ = self.__class__.State()

    def __str__(self):
        return Helper.get_model_props(self).__str__()

    def __dict__(self):
        return Helper.get_model_props(self)

    def equals(self, obj):
        if isinstance(BaseModel, obj) is False:
            return False

        return Helper.get_model_props(self) == Helper.get_model_props(obj)

    def _state(self):
        return self.__state__

    def is_new_record(self):
        return self.__state__.is_new

    def get_errors(self):
        return self.__state__.errors

    def before_save(self):
        """
        Overwrite method on implementation class that execute before save
        """
        return

    def before_update(self):
        """
        Overwrite method on implementation class that execute before update
        """
        return

    def after_save(self):
        """
        Overwrite method on implementation class that execute after save
        """
        return

    def after_update(self):
        """
        Overwrite method on implementation class that execute after update
        :return:
        """
        return

    def validate(self):
        """
        Validate model properties

        :rtype: bool
        :return: True if model properties are valid else False
        """
        for key, value in inspect.getmembers(self.__class__, Helper.is_property):
            if self.validate_property(value) is False:
                return False

        return True

    def validate_property(self, prop):
        """
        Validate model property

        :type prop: property
        :param prop: model property

        :rtype: bool
        :return:
        """
        return Helper.validate_model_prop(self, prop)

    @classmethod
    def _meta(cls):
        return cls.__dict__.get('Meta')

    @classmethod
    def _fetch_query(cls, query_string, query_builder):
        """
        Fetch data from query string

        :type query_string: str
        :param query_string:

        :type query_builder: QueryBuilder
        :param query_builder:

        :rtype: list
        :return:
        """
        results = Executor.execute_query(query_string, query_builder.params, query_builder.param_types)
        return DataParser.map_model(results, query_builder.select_cols, cls)

    @classmethod
    def count(cls, criteria=None):
        """
        return count

        :type criteria: Criteria
        :param criteria:

        :rtype: int
        :return: count rows
        """
        if criteria is None:
            criteria = Criteria()

        query_builder = QueryBuilder(cls, criteria)
        query_string = query_builder.get_count()
        result = Executor.execute_query(query_string, query_builder.params, query_builder.param_types)

        return result.one()[0]

    @classmethod
    def delete_one(cls, criteria):
        # Todo
        id_list = [('3')]
        Executor.delete_data(cls._meta().table_name, id_list)

    @classmethod
    def delete_by_pk(cls, pk):
        pass

    @classmethod
    def delete_all(cls, criteria=None):
        pass

    @classmethod
    def is_exist(cls, criteria):
        pass

    @classmethod
    def find(cls, criteria=None):
        """
        get single record data

        :type criteria: Criteria
        :param criteria:

        :rtype: BaseModel
        :return: If exist return Model & None
        """
        if criteria is None:
            criteria = Criteria()

        criteria.limit = 1
        query_builder = QueryBuilder(cls, criteria)
        query_string = query_builder.get_query()
        results = cls._fetch_query(query_string, query_builder)

        if len(results) == 1:
            return results[0]
        else:
            return None

    @classmethod
    def find_by_pk(cls, pk):
        pass

    @classmethod
    def find_all(cls, criteria=None):
        pass

    @classmethod
    def get_meta_data(cls):
        pass

    @classmethod
    def get_primary_key_value(cls):
        pass

    @classmethod
    def has_property(cls, property_name):
        pass

    @classmethod
    def insert(cls, columns, data):
        # Todo
        prepare_data = PrepareData(cls._meta().db_table)
        insert_data = prepare_data.get_data()
        columns = ('id', 'Active', 'Name', 'Subdomain')
        Executor.insert_data(cls._meta().db_table, columns, insert_data)

    @classmethod
    def primary_key(cls):
        pass

    @classmethod
    def relations(cls):
        pass

    @classmethod
    def validation_rules(cls):
        pass

    @classmethod
    def attr_validation_rules(cls):
        pass

    @classmethod
    def save(cls, model_obj):
        # Todo
        prepare_data = PrepareData(cls._meta().db_table)
        insert_data = prepare_data.get_data()
        columns = ('id', 'name', 'address', 'points', 'is_active', 'join_date', 'modified_at')
        Executor.save_data(cls._meta().db_table, columns, insert_data)

    @classmethod
    def save_all(cls, model_obj_list):
        pass

    @classmethod
    def table_name(cls):
        pass

    @classmethod
    def update(cls, columns, data):
        # Todo
        prepare_data = PrepareData(cls._meta().table_name)
        insert_data = prepare_data.get_data()
        columns = ('id', 'Active', 'Name', 'Subdomain')
        Executor.update_data(cls._meta().table_name, columns, insert_data)

    @classmethod
    def update_by_pk(cls, pk, data):
        pass

    @classmethod
    def update_all(cls, criteria, data):
        pass

    @classmethod
    def with_relation(cls):
        pass

    class State(object):
        _is_new = True
        _errors = {}

        @property
        def is_new(self):
            return self._is_new

        @is_new.setter
        def is_new(self, is_new):
            if isinstance(is_new, bool) is False:
                raise TypeError('Should be bool type')
            self._is_new = is_new

        @property
        def errors(self):
            return self._errors

        @errors.setter
        def errors(self, errors):
            self._errors = errors

