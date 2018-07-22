#!flask/bin/python
import sys

sys.path.insert(0, '..')

import logging
from time import time
from datetime import date
from models import User, Role, Organization
from flask import Flask, jsonify, g, request
from google.cloud.spanner_v1.session import Session
from google.cloud.spanner_v1.transaction import Transaction
from spannerorm import Connection, Criteria, ModelJSONEncoder, SpannerDb, transactional
from google.cloud.spanner_v1.pool import SessionCheckout

app = Flask(__name__)
app.json_encoder = ModelJSONEncoder
logging.basicConfig(level=logging.DEBUG)

service_account_json = '/home/leapfrog/personal-data/python-work/opensource/spanner-orm/service_account.json'
Connection.config('develop', 'auth', service_account_json)


@app.before_request
def before_request():
    logging.debug('Request [{request_method}] : {request_url}'
                  .format(request_method=request.method, request_url=request.base_url))
    g.start_time = time()


@app.after_request
def after_request(response):
    execution_time = time() - g.start_time
    logging.debug('Request completion time: {execution_time}'.format(execution_time=execution_time))
    return response


@app.route('/')
def root():
    return 'example api'


@app.route('/user/meta')
def user_meta_data():
    return jsonify(User.get_meta_data())


@app.route('/user/one')
def one_user():
    criteria = Criteria()
    # criteria.condition([(User.role_id, '=', '1'), (User.organization_id, '=', '4707145032222247178')])
    # criteria.add_condition((User.is_deleted, '=', False))
    user = User.find(criteria)
    return jsonify(user)


@app.route('/user/by_pk')
def user_by_pk():
    criteria = Criteria()
    criteria.add_condition((User.is_deleted, '=', False))
    user = User.find_by_pk('-300113230644022007', criteria)
    return jsonify(user)


@app.route('/user/find_all')
def find_all_users():
    criteria = Criteria()
    criteria.join_with(User.role)
    criteria.condition([(User.email, 'LIKE', '%@lftechnology.com')])
    # criteria.add_condition((User.role_id, 'IN', ['1', '2']))
    # criteria.add_condition((User.organization_id, 'NOT IN', ['4707145032222247178']))
    criteria.set_order_by(User.email, 'ASC')
    criteria.limit = 2

    users = User.find_all(criteria)
    return jsonify(users)


@app.route('/user/find_all_with')
def find_all_user_with():
    criteria = Criteria()
    criteria.join_with(User.role)
    criteria.join_with(User.organization)
    criteria.condition([(User.email, 'LIKE', '%@lftechnology.com')])
    criteria.set_order_by(User.email, 'ASC')
    criteria.limit = 2

    users = User.find_all(criteria)
    for user in users:
        print(user.role)

    return jsonify(users)


@app.route('/role/users')
def role_one_to_many_users():
    criteria = Criteria()
    criteria.join_with(Role.users)
    criteria.add_condition((User.is_deleted, '=', False))
    criteria.add_condition((User.email, '=', 'mjsanish+admin@gmail.com'))
    criteria.set_order_by(User.email, order='DESC')
    role = Role.find(criteria)
    return jsonify(role)


@app.route('/user/insert_block')
def insert_block():
    data_list = [{
        'email': 'mjsanish+1@gmail.com',
        'name': 'sanish1',
        "is_deleted": False,
        'organization_id': '4707145032222247178',
        'role_id': '1',
        'created_by': '-1202895510759970011',
    }, {
        'email': 'mjsanish+2@gmail.com',
        'name': 'sanish2',
        "is_deleted": False,
        'organization_id': '4707145032222247178',
        'role_id': '1',
        'created_by': '-1202895510759970011',
    }]

    users = User.insert_block(data_list)
    return jsonify(users)


@app.route('/user/update_block')
def update_block():
    data_list = [{
        'id': '271fc766-6de7-44c7-bd1c-b04954cd401f',
        'email': 'mjsanish+100@gmail.com',
        'name': 'sanish100'
    }, {
        'id': '20b2e97f-4c77-460b-9324-bb7530d6b8f7',
        'role_id': '2'
    }]

    users = User.update_block(data_list)
    return jsonify(users)


@app.route('/user/save')
def save_user():
    user = User()
    user.name = 'some one'
    user.email = 'someone@gmail.com'
    user.organization_id = '4707145032222247178'
    user.role_id = '1'
    user.created_by = '-1202895510759970011'

    user = User.save(user)
    return jsonify(user)


@app.route('/user/update')
def update_user():
    user = User.find_by_pk('d3fefb2a-ef30-4c39-a560-81b459f5024e')
    user.name = 'some one'
    user.email = 'someone@gmail.com'
    user.organization_id = '4707145032222247178'
    user.role_id = '1'

    user = User.save(user)
    return jsonify(user)


@app.route('/count')
def count_role():
    criteria = Criteria()
    criteria.join_with(Role.users)
    count = Role.count(criteria)
    return str(count)


@app.route('/query')
def execute_query():
    query_string = 'SELECT users.created_by, users.email, users.role_id, users.acl, users.is_deleted, users.name, ' \
                   'users.created_at, users.updated_at, users.phone_number, users.updated_by, users.password, users.id, ' \
                   'users.photo_url, users.organization_id FROM users'

    criteria = Criteria()
    criteria.condition([(User.role_id, '=', '1'), (User.name, '=', 'sanish')])

    criteria = Criteria()
    criteria.add_condition((User.role_id, '=', '1'))
    criteria.add_condition((User.name, '=', 'sanish'))
    result = SpannerDb.execute_query(query_string)
    return jsonify(result)


@app.route('/transaction')
@transactional
def with_transaction(transaction):
    """
    :type transaction: Transaction
    :param transaction:
    :return:
    """
    print(transaction)
    user = User()
    user.name = 'person 10'
    user.email = 'transaction@gmail.com'
    user.organization_id = '4707145032222247178'
    user.role_id = '1'
    user.created_by = '-1202895510759970011'

    user = User.save(user, transaction)
    user.name = 'person 9.1'
    User.save(user, transaction)

    return jsonify(user)


@app.route('/create-table')
def create_table():
    query_string = '''
                    CREATE TABLE sample (
                        id STRING(64) NOT NULL,
                        address STRING(MAX),
                        is_active BOOL NOT NULL,
                        join_date DATE,
                        modified_at TIMESTAMP,
                        name STRING(100) NOT NULL,
                        points INT64 NOT NULL,
                    ) PRIMARY KEY (id)
                    '''
    SpannerDb.execute_ddl_query(query_string)
    return 'success'

@app.route('/drop')
def drop_table():
    query_string = '''
                    DROP TABLE temp
                    '''
    SpannerDb.execute_ddl_query(query_string)
    return 'success'

@app.route('/roles')
def roles():
    criteria = Criteria()
    #criteria.join_with((Role.users))

    criteria.limit = 2
    roles = Role.find_all(criteria)

    return jsonify(roles)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8282, debug=True)
