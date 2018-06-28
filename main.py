#!flask/bin/python
from flask import Flask, jsonify
from time import time
from spannerorm import Connection, Criteria, ModelJSONEncoder

from models import Temp

app = Flask(__name__)
app.json_encoder = ModelJSONEncoder

Connection.config('develop', 'auth')


@app.route('/get')
def get_records():
    start_time = time()

    criteria = Criteria()
    criteria.add_condition((Temp.name, 'LIKE', '%Sa%'))
    temp = Temp.find(criteria)
    print("--- %s Application Execution time ---" % (time() - start_time))

    return jsonify(temp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8282, debug=True)
