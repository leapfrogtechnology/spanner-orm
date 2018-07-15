import logging
import threading
from os import path
from google.cloud.spanner import Client
from .spanner_exception import SpannerException
from google.cloud.spanner_v1.database import Database
from google.cloud.spanner_v1.pool import PingingPool


class Connection:
    _db_instance = None

    def __init__(self, instance_id, database_id, service_account_json, pool_size=10, time_out=5, ping_interval=300):
        """
        :type database_id: str
        :param instance_id: Cloud Spanner instance ID.

        :type database_id: str
        :param database_id: Cloud Spanner database ID.
        """
        Connection._connect(instance_id, database_id, service_account_json, pool_size, time_out, ping_interval)

    @staticmethod
    def config(instance_id, database_id, service_account_json, pool_size=10, time_out=5, ping_interval=300):
        """
        Configure cloud spanner database connection

        :type database_id: str
        :param instance_id: Cloud Spanner instance ID.

        :type database_id: str
        :param database_id: Cloud Spanner database ID.
        """
        Connection._connect(instance_id, database_id, service_account_json, pool_size, time_out, ping_interval)

    @staticmethod
    def _connect(instance_id, database_id, service_account_json, pool_size, time_out, ping_interval):
        """
        Connect to the spanner database

        :type database_id: str
        :param instance_id: Cloud Spanner instance ID.

        :type database_id: str
        :param database_id: Cloud Spanner database ID.
        """
        try:
            if path.exists(service_account_json) is False:
                raise RuntimeError('Service account json file not exist')
            # Spanner DB Connection
            spanner_client = Client.from_service_account_json(service_account_json)
            instance = spanner_client.instance(instance_id)
            pool = PingingPool(size=pool_size, default_timeout=time_out, ping_interval=ping_interval)
            Connection._db_instance = instance.database(database_id, pool=pool)
            Connection.start_connection_thread(pool.ping)

            with Connection._db_instance.snapshot() as snapshot:
                snapshot.execute_sql("SELECT * FROM information_schema.tables AS t WHERE t.table_schema = ''")
                logging.debug('Cloud Spanner Db Connected \n Instance Id: %s \n Database Id: %s', instance_id,
                              database_id)
        except Exception:
            raise SpannerException('Fail to Connect Spanner Database')

    @staticmethod
    def get_instance():
        """
        Return spanner database instance

        :rtype: Database
        :return: a database owned by this instance.
        """
        if Connection._db_instance is None:
            raise SpannerException('Cloud Spanner database is not connected')

        return Connection._db_instance

    @classmethod
    def start_connection_thread(cls, ping):
        background = threading.Thread(target=ping, name='ping-pool')
        background.daemon = True
        background.start()
