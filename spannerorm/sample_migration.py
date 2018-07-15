from spannerorm import SpannerDb


class MigrationScript(object):
    @classmethod
    def up(cls):
        """Sample up migration code"""
        """
        SpannerDb.execute_ddl_query('''
        CREATE TABLE sample (
            id STRING(64) NOT NULL,
            address STRING(MAX),
            is_active BOOL NOT NULL,
            join_date DATE,
            modified_at TIMESTAMP,
            name STRING(100) NOT NULL,
            points INT64 NOT NULL,
        ) PRIMARY KEY (id)
        ''')

        SpannerDb.insert_data('sample',
                              ['id', 'address', 'is_active', 'name', 'points'],
                              [
                                  ('5ba641c0-1630-420a-bc77-79722bece827', 'address-1', True, 'name-1', 1000),
                                  ('a9f6ef63-882b-4d0c-a791-209506f936c0', 'address-1', True, 'name-1', 1000)
                              ])
        """

    @classmethod
    def down(cls):
        """Sample down migration code"""
        """
        SpannerDb.execute_ddl_query('''
                DROP TABLE sample
                ''')
        """
