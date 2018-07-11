import sys
import logging
sys.path.insert(0,'..')

from spannerorm import Connection, Criteria
from models.user import User
from models.role import Role

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


print('------------------------ Find user with role (ManyToOne) ------------------------------------------------------')
criteria = Criteria()
criteria.join_with(User.role)
user = User.find()

print(user.role)
print(user)
print('------------------------ end ----------------------------------------------------------------------------------')

print('------------------------ Find role with users (OneToMany) -----------------------------------------------------')
criteria = Criteria()
criteria.join_with(Role.users)
criteria.add_condition((User.email, '=', 'mjsanish+admin@gmail.com'))
criteria.set_order_by(User.email, order='DESC')
role = Role.find(criteria)

print(role)
print('------------------------ end ----------------------------------------------------------------------------------')