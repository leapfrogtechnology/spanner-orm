#!flask/bin/python
from flask import Flask, jsonify
from time import time
from spannerorm import Connection, Criteria, ModelJSONEncoder
from datetime import date
import logging
from uuid import uuid4

from models import Temp, User

app = Flask(__name__)
app.json_encoder = ModelJSONEncoder

Connection.config('develop', 'auth', '/home/leapfrog/personal-data/python-work/opensource/spanner-orm/service_account.json')


@app.route('/')
def root():
    return 'test api'

@app.route('/get')
def get_records():
    start_time = time()

    criteria = Criteria()
    criteria.add_condition((Temp.name, 'LIKE', '%Sa%'))
    criteria.set_order_by(Temp.name, order='ASC')
    temp = Temp.find(criteria)
    print("--- %s Application Execution time ---" % (time() - start_time))

    return jsonify(temp)


@app.route('/getAll')
def get_all_records():
    start_time = time()

    criteria = Criteria()
    criteria.add_condition((Temp.is_active, '=', True))
    criteria.limit = 2
    criteria.set_order_by([Temp.name, Temp.address], order='DESC')
    # criteria.add_condition((Temp.join_date, '=', date(2018, 02, 20)))
    temps = Temp.find_all(criteria)
    print("--- %s Application Execution time ---" % (time() - start_time))

    return jsonify(temps)


@app.route('/delete')
def delete_record():
    start_time = time()
    criteria = Criteria()
    criteria.add_condition((Temp.name, 'LIKE', 'Pradeep%'))
    Temp.delete_all(criteria)
    print("--- %s Application Execution time ---" % (time() - start_time))

    return jsonify('success')


@app.route('/insert')
def insert_record():
    start_time = time()
    data_list = [{
        "id": str(uuid4()),
        "is_active": True,
        "join_date": date(2018,02,20),
        "name": "Dinesh Thapa",
        "points": 150,
    }, {
        "address": "kalanki, Kathmandu",
        "id": str(uuid4()),
        "join_date": date(2018,02,20),
        "name": "Rasna Shakya",
        "points": 200
    }]

    temps = Temp.insert_block(data_list)
    print("--- %s Application Execution time ---" % (time() - start_time))

    return jsonify(temps)

@app.route('/save')
def save_record():
    start_time = time()
    temp = Temp.find_by_pk('8921e454-7161-44af-9b8b-1b84f81a22bc')
    temp.name = 'Rammu Cha'
    temp.is_active = False
    print(temp)
    response = Temp.save(temp)
    print("--- %s Application Execution time ---" % (time() - start_time))

    return jsonify(response)

@app.route('/updateByPk')
def update__by_pk():
    start_time = time()
    data = {
        "is_active": True,
        "name": "Ram Maya Thapa",
        "points": 150,
    }

    response = Temp.update_by_pk('8921e454-7161-44af-9b8b-1b84f81a22bc', data)
    print("--- %s Application Execution time ---" % (time() - start_time))

    return jsonify(response)

@app.route('/test')
def test():
    user = User()
    user.role_id = '8921e454-7161-44af-9b8b-1b84f81a22bc'
    user.password = 12345
    print('======================')
    print(user.role_id)
    print(user.password)
    user.role = 'sanish'
    response = user.role
    print(response)
    #relations = User.relations()
    #for name in relations:
    #    relation = relations.get(name)
    #    print(relation.reference_model)
    return 'success'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.error('This message should go to the log file')
    app.run(host='0.0.0.0', port=8282, debug=True)
