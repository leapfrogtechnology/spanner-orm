#!flask/bin/python
from flask import Flask, jsonify
from time import time
from spannerorm import Connection, Criteria, ModelJSONEncoder
from datetime import date
import logging

from models import Temp

app = Flask(__name__)
app.json_encoder = ModelJSONEncoder

Connection.config('develop', 'auth')


# criteria = Criteria()
# criteria.add_condition((Temp.name, '=', 'Sanish Maharjan'))
# count = Temp.count(criteria)
# print(count)
# print(type(count))

@app.route('/get')
def get_records():
    start_time = time()

    criteria = Criteria()
    criteria.add_condition((Temp.name, 'LIKE', '%Sa%'))
    temp = Temp.find(criteria)
    print("--- %s Application Execution time ---" % (time() - start_time))

    return jsonify(temp)


@app.route('/getAll')
def get_all_records():
    start_time = time()

    criteria = Criteria()
    criteria.add_condition((Temp.is_active, '=', True))
    criteria.limit = 2
    #criteria.add_condition((Temp.join_date, '=', date(2018, 02, 20)))
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.error('This message should go to the log file')
    app.run(host='0.0.0.0', port=8282, debug=True)
