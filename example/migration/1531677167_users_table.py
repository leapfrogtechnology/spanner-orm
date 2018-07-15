from spannerorm import SpannerDb


class MigrationScript(object):
    @classmethod
    def up(cls):
        """Sample up migration code"""
        SpannerDb.execute_ddl_query('''
        CREATE TABLE users (
            id STRING(MAX) NOT NULL,
            acl STRING(MAX),
            created_at TIMESTAMP,
            created_by STRING(MAX),
            email STRING(MAX),
            is_deleted BOOL,
            name STRING(MAX),
            organization_id STRING(MAX),
            password STRING(MAX),
            phone_number STRING(20),
            photo_url STRING(MAX),
            role_id STRING(MAX),
            updated_at TIMESTAMP,
            updated_by STRING(MAX),
        ) PRIMARY KEY (id)
        ''')

    @classmethod
    def down(cls):
        SpannerDb.execute_ddl_query('''
                DROP TABLE users
                ''')
