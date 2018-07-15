import sys

sys.path.insert(0, '..')

from spannerorm import DbMigration


class Migration(DbMigration):
    instance_id = 'develop'
    database_id = 'auth'
    service_account_json = '/home/leapfrog/personal-data/python-work/opensource/spanner-orm/service_account.json'


if __name__ == '__main__':
    Migration.run()
