from datetime import date
from .executor import Executor
from .helper import Helper
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
            params = {}
            param_types = {}

            for key in params:
                value = param_types.get(key)
                if isinstance(value, str):
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
