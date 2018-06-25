from google.cloud import spanner
from .spanner_exception import SpannerExcption
from google.cloud.spanner_v1.database import Database


class Connection:
    _db_instance = None

    def __init__(self, instance_id, database_id):
        """
        :type database_id: str
        :param instance_id: Cloud Spanner instance ID.

        :type database_id: str
        :param database_id: Cloud Spanner database ID.
        """
        Connection._connect(instance_id, database_id)

    @staticmethod
    def config(instance_id, database_id):
        """
        Configure cloud spanner database connection

        :type database_id: str
        :param instance_id: Cloud Spanner instance ID.

        :type database_id: str
        :param database_id: Cloud Spanner database ID.
        """
        Connection._connect(instance_id, database_id)

    @staticmethod
    def _connect(instance_id, database_id):
        """
        Connect to the spanner database

        :type database_id: str
        :param instance_id: Cloud Spanner instance ID.

        :type database_id: str
        :param database_id: Cloud Spanner database ID.
        """
        try:
            spanner_client = spanner.Client()
            instance = spanner_client.instance(instance_id)
            Connection._db_instance = instance.database(database_id)
            with Connection._db_instance.snapshot() as snapshot:
                snapshot.execute_sql('SELECT * FROM information_schema.tables AS t WHERE t.table_schema = ''')
        except Exception:
            raise SpannerExcption('Fail to Connect Spanner Database')

    @staticmethod
    def get_instance():
        """
        Return spanner database instance

        :rtype: Database
        :return: a database owned by this instance.
        """
        if Connection._db_instance is None:
            raise SpannerExcption('Cloud Spanner database is not connected')

        return Connection._db_instance
