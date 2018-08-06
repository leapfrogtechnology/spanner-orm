import time
import logging
from functools import wraps
from .connection import Connection
from .spanner_exception import SpannerException
from google.cloud.spanner_v1.pool import SessionCheckout
from google.api_core.exceptions import Aborted, GoogleAPICallError


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return execute_transaction(func, *args, **kwargs)

    return wrapper


def execute_transaction(func, *args, **kwargs):
    max_retry = 10
    while max_retry:
        max_retry -= 1
        db = Connection.get_instance()
        with SessionCheckout(db._pool) as session:
            transaction = session._transaction
            if transaction is None:
                transaction = session.transaction()
            if transaction._transaction_id is None:
                transaction.begin()
            try:
                response = func(transaction=transaction, *args, **kwargs)
                transaction.commit()
                return response
            except Aborted as error:
                transaction.rollback()
                session._transaction = None
                del transaction
                if max_retry:
                    logging.warn('Transaction Aborted; Will Retry in 1 sec...')
                    time.sleep(1)
                else:
                    logging.error(error)
                    raise SpannerException('Transaction Aborted')
            except GoogleAPICallError as error:
                del transaction
                logging.error(error)
                raise SpannerException('Spanner Db Api Call Error')
            except Exception as error:
                transaction.rollback()
                logging.error(error)
                raise error
