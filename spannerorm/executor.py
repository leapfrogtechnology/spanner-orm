import logging
from time import time
from .connection import Connection
from google.cloud.spanner import KeySet
from google.cloud.spanner_v1.transaction import Transaction
from google.cloud.spanner_v1.streamed import StreamedResultSet


class Executor:
    @classmethod
    def execute_query(cls, query_string, params=None, param_types=None, transaction=None):
        """
        Execute query string

        :type query_string: str
        :param query_string:
            eg. select id, name from users where name=@name

        :type transaction: Transaction
        :param transaction:

        :type params: dict
        :param params: query params
            eg. params={'name': value}

        :type param_types: dict
        :param param_types: query params types
            eg. param_types={'name': record_type}

        :rtype: StreamedResultSet
        :return: result set
        """
        start_time = time()
        if transaction is None:
            db_instance = Connection.get_instance()
            with db_instance.snapshot() as snapshot:
                response = snapshot.execute_sql(query_string, params, param_types)
                logging.debug('Query completion Time: %s', (time() - start_time))
                return response
        else:
            response = transaction.execute_sql(query_string, params, param_types)
            logging.debug('Query completion Time: %s', (time() - start_time))
            return response

    @classmethod
    def insert_data(cls, table_name, columns, values, transaction=None):
        """
        Insert new data rows

        :type table_name: str
        :param table_name: database table name

        :type columns: list
        :param columns: table columns
            eg. ['id', 'name']

        :type values: list
        :param values: row's data tuple list
            eg. [(value11, value12), (value21, value22)]

        :type transaction: Transaction
        :param transaction:
        """
        start_time = time()
        if transaction is None:
            db_instance = Connection.get_instance()
            with db_instance.batch() as batch:
                batch.insert(table=table_name, columns=columns, values=values)
        else:
            transaction.insert(table=table_name, columns=columns, values=values)

        logging.debug('Query completion Time: %s', (time() - start_time))

    @classmethod
    def update_data(cls, table_name, columns, values, transaction=None):
        """
        Update data rows

        :type table_name: str
        :param table_name: database table name

        :type columns: list
        :param columns: table columns
            eg. ['id', 'name']

        :type values: list
        :param values: row's data
            eg. [(value11, value12), (value21, value22)]

        :type transaction: Transaction
        :param transaction:
        :return:
        """
        start_time = time()
        if transaction is None:
            db_instance = Connection.get_instance()
            with db_instance.batch() as batch:
                batch.update(table=table_name, columns=columns, values=values)
        else:
            transaction.update(table=table_name, columns=columns, values=values)

        logging.debug('Query completion Time: %s', (time() - start_time))

    @classmethod
    def save_data(cls, table_name, columns, values, transaction=None):
        """
        Add or update data rows

        :type table_name: str
        :param table_name: database table name

        :type columns: list
        :param columns: table columns
            eg. ['id', 'name']

        :type values: list
        :param values: row's data
            eg. [(value11, value12), (value21, value22)]

        :type transaction: Transaction
        :param transaction:
        """
        start_time = time()
        if transaction is None:
            db_instance = Connection.get_instance()
            with db_instance.batch() as batch:
                batch.insert_or_update(table=table_name, columns=columns, values=values)
        else:
            transaction.insert_or_update(table=table_name, columns=columns, values=values)

        logging.debug('Query completion Time: %s', (time() - start_time))

    @classmethod
    def delete_data(cls, table_name, id_list, transaction=None):
        """
        Delete data row

        :type table_name: str
        :param table_name: database table name

        :type id_list: list
        :param id_list: id tuple list
            eg. [('1'), ('2')]

        :type transaction: Transaction
        :param transaction:
        """
        start_time = time()
        key_set = KeySet(keys=id_list, all_=False)
        if transaction is None:
            db_instance = Connection.get_instance()
            with db_instance.batch() as batch:
                batch.delete(table_name, key_set)
        else:
            transaction.delete(table_name, key_set)

        logging.debug('Query completion Time: %s', (time() - start_time))

    @classmethod
    def execute_ddl_query(cls, ddl_query_string):
        """
        Execute DDL query

        :type ddl_query_string: str
        :param ddl_query_string: DDL query string
        """
        start_time = time()
        db_instance = Connection.get_instance()
        operation = db_instance.update_ddl([ddl_query_string])

        operation.result()
        logging.debug('DDL Query execution completion Time: %s', (time() - start_time))
