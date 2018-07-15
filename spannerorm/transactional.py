from functools import wraps
from .connection import Connection
from .spanner_exception import SpannerException
from google.cloud.spanner_v1.pool import SessionCheckout
from google.api_core.exceptions import Aborted, GoogleAPICallError


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
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
        except Aborted as exc:
            del transaction
            raise SpannerException('Transaction Aborted')
        except GoogleAPICallError:
            del transaction
            raise SpannerException('Spanner Db Api Call Error')
        except Exception:
            transaction.rollback()
            raise

    return wrapper
