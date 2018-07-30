from datetime import date
import six
from .helper import Helper
from .executor import Executor
from google.cloud.spanner_v1.transaction import Transaction
from google.cloud.spanner_v1.proto.type_pb2 import Type, INT64, FLOAT64, STRING, BOOL, DATE


class SpannerDb(object):
    @classmethod
    def execute_query(cls, query_string, params=None, transaction=None):
        """
        Execute query string

        :type query_string: str
        :param query_string:

        :type params: dict
        :param params:

        :type transaction: Transaction
        :param transaction:

        :rtype: list
        :return:
        """
        param_types = None
        if params is not None:
            param_types = {}

            for key in params:
                value = params.get(key)
                if isinstance(value, six.string_types):
                    param_types[key] = Type(code=STRING)
                elif isinstance(value, int):
                    param_types[key] = Type(code=INT64)
                elif isinstance(value, float):
                    param_types[key] = Type(code=FLOAT64)
                elif isinstance(value, bool):
                    param_types[key] = Type(code=BOOL)
                elif isinstance(value, date):
                    param_types[key] = Type(code=DATE)

        response = Executor.execute_query(query_string=query_string, params=params, param_types=param_types,
                                          transaction=transaction)
        return Helper.process_result_set(response)

    @classmethod
    def execute_ddl_query(cls, ddl_query_string):
        """
        Execute DDL query

        :type ddl_query_string: str
        :param ddl_query_string: DDL query string
        """
        Executor.execute_ddl_query(ddl_query_string)

    @classmethod
    def insert_data(cls, table_name, columns, data):
        """
        Insert given table data

        :type table_name: str
        :param table_name:

        :type columns: list
        :param columns: list of columns
            eg. ['id', 'name']

        :type data: list
        :param data: list of data
            eg. [(value11, value12), (value21, value22)]
        """
        Executor.insert_data(table_name, columns, data)

    @classmethod
    def update_data(cls, table_name, columns, data):
        """
        Update given table data rows

        :type table_name: str
        :param table_name: database table name

        :type columns: list
        :param columns: table columns
            eg. ['id', 'name']

        :type data: list
        :param data: row's data
            eg. [(value11, value12), (value21, value22)]
        """
        Executor.update_data(table_name, columns, data)

    @classmethod
    def save_data(cls, table_name, columns, data):
        """
        Add or update given table data rows

        :type table_name: str
        :param table_name: database table name

        :type columns: list
        :param columns: table columns
            eg. ['id', 'name']

        :type data: list
        :param data: row's data
            eg. [(value11, value12), (value21, value22)]
        """
        Executor.save_data(table_name, columns, data)

    @classmethod
    def delete_data(cls, table_name, id_list):
        """
        Delete given table data row

        :type table_name: str
        :param table_name: database table name

        :type id_list: list
        :param id_list: id tuple list
            eg. [('1'), ('2')]
        """
        Executor.delete_data(table_name, id_list)
