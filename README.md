## Google Cloud Spanner-ORM:
Spanner ORM is a simple and small ORM. It easy to learn and intuitive to use.

```
product:
  name: Google Cloud Spanner ORM
  short_name: spannerorm
  url: https://github.com/leapfrogtechnology/spanner-orm.git
  description:
    spannerdb ORM is a highly scalable, efficient Google Cloud Spanner ORM.
```

### Features
- A small, simple ORM
- Support Cloud Spanner Database
- python 2.7+ (Not tested yet in python 3+)
- Connection pooling

Table of contents
=================

<!--ts-->
   * [Installation](#Installation)
   * [Connection](#Connection)
<!--te-->

Installation
------------
- Install pip (If not install in your system)
```bash
sudo apt-get install python-pip
```
- Install client library
```bash
    pip install --upgrade google-cloud-spanner
```
- Installing with Git
```bash
    git clone https://github.com/leapfrogtechnology/spanner-orm.git
    cd spanner-orm
    python setup.py install
```
- Download `Service account json`
    - Go to the `GCP Console` > `Service accounts`
    - Download key from service account list by clicking at `action`  > `create key`

Connection
----------
The spannerorm Connection object represents a connection to a database. The Connection class is instantiated with all 
the information needed to open a connection to a database, and then can be used.

```python
from spannerorm import Connection

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
```

|        Parameter            | DataType    | Required / Optional |           Description                              |
| --------------------------- | ----------- | ------------------- | -------------------------------------------------- |
| instance_id                 | String      | Required            | Cloud Spanner Instance Id                          |
| database_id                 | String      | Required            | Cloud Spanner Database                             |
| service_account_json        | String      | Required            | Service account json's file full path              |
| pool_size                   | Integer     | Optional            | Max number of database pool connection             |
| time_out                    | Integer     | Optional            | In seconds, to wait for a returned session         |
| ping_interval               | Integer     | Optional            | Interval at which to ping sessions                 |

