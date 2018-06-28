import inspect
from .helper import Helper
from .executor import Executor
from .criteria import Criteria
from .data_parser import DataParser
from .prepare_data import PrepareData
from .query_builder import QueryBuilder
from .spanner_exception import SpannerException


class Model(object):
    def __init__(self, *args, **kwargs):
        if self._meta().db_table is None:
            raise Exception("Error: {0} model's Meta.db_table is not set".format(self.__class__.__name__))

        if self._meta().primary_key is None:
            raise SpannerException("Error: {0} model's Meta.primary_key is not set".format(self.__class__.__name__))

        for key in kwargs.iterkeys():
            self.__setattr__(key, kwargs.get(key))

    def __str__(self):
        object_str = {}
        for key, value in inspect.getmembers(self.__class__, Helper.is_property):
            object_str[key] = self.__getattribute__(key)

        return object_str.__str__()

    def __dict__(self):
        model_data = {}
        for key, value in inspect.getmembers(self.__class__, Helper.is_property):
            model_data[key] = self.__getattribute__(key)

        return model_data

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
    def find(cls, criteria=None):
        """
        get single record data

        :type criteria: Criteria
        :param criteria:

        :rtype: Model
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

    # Todo
    def insert(self):
        prepare_data = PrepareData(self._meta().db_table)
        insert_data = prepare_data.get_data()
        columns = ('id', 'Active', 'Name', 'Subdomain')
        Executor.insert_data(self._meta().db_table, columns, insert_data)

    # Todo
    @classmethod
    def save(cls):
        prepare_data = PrepareData(cls._meta().db_table)
        insert_data = prepare_data.get_data()
        columns = ('id', 'name', 'address', 'points', 'is_active', 'join_date', 'modified_at')
        Executor.save_data(cls._meta().db_table, columns, insert_data)

    # Todo
    def update(self):
        prepare_data = PrepareData(self._meta().table_name)
        insert_data = prepare_data.get_data()
        columns = ('id', 'Active', 'Name', 'Subdomain')
        Executor.update_data(self._meta().table_name, columns, insert_data)

    # Todo
    def delete(self):
        id_list = [('3')]
        Executor.delete_data(self._meta().table_name, id_list)
