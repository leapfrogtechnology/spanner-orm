import sys
import logging

sys.path.insert(0, '..')

from spannerorm import Connection, Criteria
from models.user import User

logging.basicConfig(level=logging.DEBUG)

instance_id = 'develop'
database_id = 'auth'
service_account_json = '/home/leapfrog/personal-data/python-work/opensource/spanner-orm/service_account.json'
pool_size = 10
time_out = 5
ping_interval = 300

Connection.config(instance_id=instance_id,
                  database_id=database_id,
                  service_account_json=service_account_json,
                  pool_size=pool_size,
                  time_out=time_out,
                  ping_interval=ping_interval)

print('------------------------ Find user with out criteria ----------------------------------------------------------')

user = User.find()
print(user)

print('------------------------ end ----------------------------------------------------------------------------------')

print('------------------------ Find user with role_id=1 & organization_id = 4707145032222247178 ---------------------')
criteria = Criteria()
criteria.condition([(User.role_id, '=', '1'), (User.organization_id, '=', '4707145032222247178')])
user = User.find(criteria)
print(user)
print('------------------------ end ----------------------------------------------------------------------------------')

print('------------------------ Find user by primary key -------------------------------------------------------------')
criteria = Criteria()
criteria.add_condition((User.is_deleted, '=', False))
user = User.find_by_pk('-300113230644022007', criteria)
print(user)
print('------------------------ end ----------------------------------------------------------------------------------')

print('------------------------ Find users filter by criteria --------------------------------------------------------')
criteria = Criteria()
criteria.condition([(User.email, 'LIKE', '%@lftechnology.com')])
criteria.add_condition((User.role_id, 'IN', ['1', '2']))
criteria.add_condition((User.organization_id, 'NOT IN', ['4707145032222247178']))
criteria.set_order_by(User.email, 'ASC')
criteria.limit = 2

users = User.find_all(criteria)
print(users)
print('------------------------ end ----------------------------------------------------------------------------------')
