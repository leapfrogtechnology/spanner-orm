from spannerorm import SpannerDb


class MigrationScript(object):
    @classmethod
    def up(cls):
        SpannerDb.execute_ddl_query('''
        CREATE TABLE organizations (
            id STRING(MAX) NOT NULL,
            address STRING(MAX),
            created_at TIMESTAMP,
            created_by STRING(MAX),
            is_deleted BOOL,
            logo STRING(MAX),
            name STRING(MAX),
            state STRING(MAX),
            sub_domain STRING(MAX),
            updated_at TIMESTAMP,
            updated_by STRING(MAX),
            zip_code STRING(20),
        ) PRIMARY KEY (id)
        ''')


    @classmethod
    def down(cls):
        SpannerDb.execute_ddl_query('''
                DROP TABLE organizations
                ''')
