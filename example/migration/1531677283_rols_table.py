from time import time
from datetime import datetime
from spannerorm import SpannerDb


class MigrationScript(object):
    @classmethod
    def up(cls):
        SpannerDb.execute_ddl_query('''
            CREATE TABLE roles (
                id STRING(MAX) NOT NULL,
                created_at TIMESTAMP,
                created_by STRING(MAX),
                is_deleted BOOL,
                name STRING(50),
                updated_at TIMESTAMP,
                updated_by STRING(MAX),
            ) PRIMARY KEY (id)
        ''')

        ts = datetime.fromtimestamp(time())
        created_at = ts.isoformat() + 'Z'
        SpannerDb.insert_data('roles',
                              ['id', 'name', 'is_deleted', 'created_at'],
                              [
                                  ('5ba641c0-1630-420a-bc77-79722bece827', 'Admin', False, created_at),
                                  ('a9f6ef63-882b-4d0c-a791-209506f936c0', 'User', False, created_at)
                              ])

    @classmethod
    def down(cls):
        SpannerDb.execute_ddl_query('''
                DROP TABLE roles
                ''')
