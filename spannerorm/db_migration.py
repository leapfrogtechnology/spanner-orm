import re
import os
import sys
import logging
from time import time
from uuid import uuid4
import spannerorm.sample_migration
from shutil import copyfile
from datetime import datetime
from .executor import Executor
from .connection import Connection


class DbMigration(object):
    instance_id = None
    database_id = None
    service_account_json = None
    path = os.getcwd() + '/migration'

    @classmethod
    def run(cls):
        logging.basicConfig(level=logging.INFO)
        if len(sys.argv) == 1:
            cls.help()
        else:
            command = sys.argv[1]
            params = sys.argv[2:]

            logging.info('Running migration.....')
            if command == 'up':
                cls.up()
            elif command == 'down':
                arg = params[0] if params else None
                cls.down(arg)
            elif command == 'create':
                cls.create(params[0])
            else:
                logging.error('Invalid command: \n Available commands: {help}'.format(help=cls.help()))

    @classmethod
    def up(cls):
        try:
            with cls.DbConnection(cls.instance_id, cls.database_id, cls.service_account_json):
                processor = cls.Processor(cls.path)
                processor.migrate_up()
        except Exception as error:
            logging.error('Fail to run migrations: \n {error}'.format(error=error))

    @classmethod
    def down(cls, *args):
        try:
            with cls.DbConnection(cls.instance_id, cls.database_id, cls.service_account_json):
                num = int(args[0]) if args[0] else 1
                if num < 1:
                    raise AssertionError('Syntax: down <int> '
                                         'Error Message: Second arg should be <int> greater or equal than 1')

                processor = cls.Processor(cls.path)
                processor.migration_down(num)
        except Exception as error:
            logging.error('Fail to revert migrations: \n {error}'.format(error=error))

    @classmethod
    def create(cls, *args):
        try:
            if not args[0]:
                raise RuntimeError('Syntax: create [name] \n Error Message: Missing migration name')

            processor = cls.Processor(cls.path)
            processor.create_migration_file(args[0])
        except Exception as error:
            logging.error('Fail to create migration: \n {error}'.format(error=error))

    @classmethod
    def help(cls):
        return '''
        Available Migration Commands:
            help                                : list available migration commands
            create [migration_name]             : Create new migration file
            up                                  : Run all new migrations
            down                                : Revert back last migration
            down <int>                          : Revert back last given number of migrations
        
        eg: python migration.py create user_table          
        '''

    class DbConnection():
        """
        Connection Context Manager
        """

        def __init__(self, instance_id, database_id, service_account_json):
            if instance_id is None or database_id is None or service_account_json is None:
                raise AssertionError('Please set instance_id, database_id, service_account_json')

            Connection.config(instance_id=instance_id,
                              database_id=database_id,
                              service_account_json=service_account_json,
                              pool_size=1,
                              time_out=5,
                              ping_interval=300)

        def __enter__(self):
            pass

        def __exit__(self, *args):
            pass

    class Processor(object):
        """
        Migration processor
        """

        def __init__(self, path):
            self.path = path
            sys.path.append(path)

        @property
        def sample_migration_file(self):
            return os.path.dirname(spannerorm.sample_migration.__file__) + '/sample_migration.py'

        def get_new_migration(self, name):
            file_name = '{prefix}_{name}.py'.format(prefix=int(time()), name=name)
            return '{path}/{file_name}'.format(path=self.path, file_name=file_name)

        def get_migration_files(self):
            migration_files = []
            dir_files = os.listdir(self.path)
            migration_file_pattern = re.compile("^[0-9]{10}_[a-zA-Z_]+\.py$")

            for migration_file in dir_files:
                if migration_file_pattern.match(migration_file):
                    migration_files.insert(0, migration_file)

            return migration_files

        def create_migration_table(self):
            ddl_query_string = '''
                                CREATE TABLE db_migration (
                                    id STRING(MAX) NOT NULL,
                                    execution_time INT64,
                                    migrated_at TIMESTAMP NOT NULL,
                                    name STRING(MAX) NOT NULL,
                                ) PRIMARY KEY (id)
                                '''

            Executor.execute_ddl_query(ddl_query_string)

        def is_migration_table_exist(self):
            check_query_string = '''
                                SELECT count(table_name) as count 
                                FROM information_schema.tables AS t 
                                WHERE t.table_schema = '' and t.table_name='db_migration'
                                '''

            result = Executor.execute_query(check_query_string)
            return result.one()[0] != 0

        def get_already_run_migrations(self, limit=None):
            query_string = '''
                                   SELECT name, id FROM db_migration ORDER BY name DESC
                                   '''
            if limit is not None:
                query_string += ' limit ' + str(limit)

            result = Executor.execute_query(query_string)

            already_run_migrations = []
            for row in result:
                name = str(row[0])
                migration_id = str(row[1])
                already_run_migrations.append({'name': name, 'id': migration_id})

            return already_run_migrations

        def get_already_run_migration_name(self):
            already_run_migration_names = []
            already_run_migrations = self.get_already_run_migrations()

            for row in already_run_migrations:
                already_run_migration_names.insert(0, row.get('name'))

            return already_run_migration_names

        def insert_run_migration(self, module_name, execution_time):
            ts = datetime.fromtimestamp(time())
            migrated_at = ts.isoformat() + 'Z'
            Executor.insert_data('db_migration',
                                 ['id', 'name', 'execution_time', 'migrated_at'],
                                 [(str(uuid4()), module_name, execution_time, migrated_at)])

        def delete_migraiton(self, id):
            Executor.delete_data('db_migration', [(id,)])

        def create_migration_file(self, name):
            new_migration = self.get_new_migration(name)
            if not os.path.exists(self.path):
                os.mkdir(self.path)

            copyfile(self.sample_migration_file, new_migration)
            logging.info('Migration file created: {migration_file}'.format(migration_file=new_migration))

        def migrate_up(self):
            if not self.is_migration_table_exist():
                self.create_migration_table()

            migration_files = self.get_migration_files()
            migration_files.sort()
            already_run_migration_names = self.get_already_run_migration_name()
            migration_run_count = 0
            for migration_file in migration_files:
                module_name = os.path.splitext(migration_file)[0]
                if module_name not in already_run_migration_names:
                    start_time = time()
                    logging.info('Running migration file: {migration_file}'.format(migration_file=migration_file))

                    migration = __import__(module_name).MigrationScript
                    migration.up()
                    migration_run_count += 1
                    self.insert_run_migration(module_name, int(time() - start_time))

            if migration_run_count == 0:
                logging.info('No migrations to run')
            else:
                logging.info('Total {count} Migration files run'.format(count=migration_run_count))

        def migration_down(self, num=1):
            if not self.is_migration_table_exist():
                self.create_migration_table()

            already_run_migrations = self.get_already_run_migrations(num)
            for row in already_run_migrations:
                module_name = row.get('name')
                migration_file = self.path + '/' + module_name + '.py'

                logging.info('Reverting migration: {migration_file}'.format(migration_file=migration_file))
                migration = __import__(module_name).MigrationScript
                migration.down()
                self.delete_migraiton(row.get('id'))

            if len(already_run_migrations) == 0:
                logging.info('No migrations to revert back')
