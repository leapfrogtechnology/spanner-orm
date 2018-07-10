# Google Cloud Spanner-ORM:
Spanner ORM is a simple and small ORM. It easy to learn and intuitive to use.

```
product:
  name: Google Cloud Spanner ORM
  short_name: spannerorm
  url: https://github.com/leapfrogtechnology/spanner-orm.git
  description:
    spannerdb ORM is a highly scalable, efficient Google Cloud Spanner ORM.
```

## Features
- A small, simple ORM
- Support Cloud Spanner Database
- python 2.7+ (Not tested yet in python 3+)
- Connection pooling

## Table of contents
<!--ts-->
* [Installation](#installation)
* [Connection](#connection)
* [BaseModel and DataType](#basemodel-and-datatype)
    * [DataType](#datatype)
    * [DataType Field arguments](#datatype-field-arguments)
    * [Relation](#relation)
    * [Meta](#meta)
    * [Model Decorator](#model-decorator)
* [Query Records](#query-records)
    * [find(criteria)](#findcriteria)
    * [find_by_pk(pk, criteria)](#find_by_pkpk-criteria)
    * [find_all(criteria)](#find_allcriteria)
<!--te-->

## Installation
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

## Connection
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

## BaseModel and DataType
BaseModel classes, DataType instances, BaseModel instances, Relation instances all map to database concepts:

|        Class \ Instance            | Corresponds to…                             |
| ---------------------------------- | ------------------------------------------- |
| BaseModel                          | Database table                              |
| DataType instance                  | Column on a table                           |
| BaseModel instance                 | Row in a database table                     |
| Relation instance                  | Database relational                         |

### DataType
The `DataType` class is used to describe the mapping of Model attributes to database columns. Each field type has a 
corresponding SQL storage class (i.e. varchar, int), and conversion between DataType and underlying storage is handled 
transparently.

| DataType            | Corresponding Spanner Data Type |
| -----------         | ------------------------------- |
| StringField         | STRING                          |
| IntegerField        | INT64                           |
| FloatField          | FLOAT64                         |
| BoolField           | BOOL                            |
| BytesField          | BYTES                           |
| TimeStampField      | TIMESTAMP                       |
| DateField           | DATE                            |
| EnumField           | STRING                          |

### DataType Field arguments
- StringField arguments

| Arguments           | Require / Optional | Type         | Description                                                |
| ------------------- | ------------------ | ------------ | -----------------------------------------------------------|
| db_column           | Required           | str          | Corresponding db column                                    |
| null                | False              | bool         | is allow null value, Default True                          |
| default             | False              | str          | Default value                                              |
| max_length          | False              | int          | Max allow string length                                    |
| reg_exr             | False              | str          | Regex expression                                           |

eg: 
```python
from spannerorm import StringField

_email = StringField(db_column='email', null=False, reg_exr='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
```


- IntegerField arguments

| Arguments           | Require / Optional | Type         | Description                                                |
| ------------------- | ------------------ | ------------ | -----------------------------------------------------------|
| db_column           | Required           | str          | Corresponding db column                                    |
| null                | Optional           | bool         | is allow null value, Default True                          |
| default             | Optional           | int          | Default value                                              |
| min_value           | Optional           | int          | Max allow value                                            |
| max_value           | Optional           | int          | Min allow value                                            |

- FloatField arguments

| Arguments           | Require / Optional | Type         | Description                                                |
| ------------------- | ------------------ | ------------ | -----------------------------------------------------------|
| db_column           | Required           | str          | Corresponding db column                                    |
| null                | Optional           | bool         | is allow null value, Default True                          |
| default             | Optional           | float        | Default value                                              |
| min_value           | Optional           | float        | Max allow string length                                    |
| max_value           | Optional           | float        | Regex expression                                           |
| decimal_places      | Optional           | int          | Regex expression                                           |


- BoolField arguments

| Arguments           | Require / Optional | Type         | Description                                                |
| ------------------- | ------------------ | ------------ | -----------------------------------------------------------|
| db_column           | Required           | str          | Corresponding db column                                    |
| null                | Optional           | bool         | is allow null value, Default True                          |
| default             | Optional           | bool         | Default value                                              |

- BytesField arguments

| Arguments           | Require / Optional | Type         | Description                                                |
| ------------------- | ------------------ | ------------ | -----------------------------------------------------------|
| db_column           | Required           | str          | Corresponding db column                                    |
| null                | Optional           | bool         | is allow null value, Default True                          |
| default             | Optional           | str          | Default value                                              |

- TimeStampField arguments

| Arguments           | Require / Optional | Type         | Description                                                |
| ------------------- | ------------------ | ------------ | -----------------------------------------------------------|
| db_column           | Required           | str          | Corresponding db column                                    |
| null                | Optional           | bool         | is allow null value, Default True                          |
| default             | Optional           | float          | Default value                                            |

- DateField arguments

| Arguments           | Require / Optional | Type           | Description                                              |
| ------------------- | ------------------ | -------------- | -------------------------------------------------------- |
| db_column           | Required           | str            | Corresponding db column                                  |
| null                | Optional           | bool           | is allow null value, Default True                        |
| default             | Optional           | datetime.date  | Default value                                            |

- EnumField arguments

| Arguments           | Require / Optional | Type         | Description                                                |
| ------------------- | ------------------ | ------------ | -----------------------------------------------------------|
| db_column           | Required           | str          | Corresponding db column                                    |
| null                | Optional           | bool         | is allow null value, Default True                          |
| default             | Optional           | str          | Default value                                              |
| enum_list           | Require            | list         | Enum values                                                |

- Simple Example
```python
from time import time
from uuid import uuid4
from spannerorm import BaseModel, IntegerField, StringField, BoolField, TimeStampField, DateField


class Sample(BaseModel):
    # Db Fields
    _id = StringField(db_column='id', null=False)
    _name = StringField(db_column='name', null=False, reg_exr='^[A-Z][ a-z]+')
    _modified_at = TimeStampField(db_column='modified_at', null=True, default=time())
    

    @property
    @StringField.get
    def id(self):
        return self._id

    @id.setter
    @StringField.set
    def id(self, id):
        self._id = id

    @property
    @StringField.get
    def name(self):
        return self._name

    @name.setter
    @StringField.set
    def name(self, name):
        self._name = name

    @property
    @TimeStampField.get
    def modified_at(self):
        return self._modified_at

    @modified_at.setter
    @TimeStampField.set
    def modified_at(self, created):
        self._modified_at = created

    class Meta:
        db_table = 'sample'
        primary_key = 'id'

        @classmethod
        def generate_pk(cls):
            return uuid4()

```

### Relation
Relation class is a special field type that allows one model to reference another.

| RelationType        | Description                                                 |
| ------------------- | ----------------------------------------------------------- |
| OneToOne            | OneToOne relation with reference model                      |
| ManyToOne           | ManyToOne relation with reference model                     |
| OneToMany           | OneToMany relation with reference model                     |
| ManyToMany          | ManyToMany relation with reference model                    |

- RelationType arguments

| Arguments           | Require / Optional | Type         | Description                                                |
| ------------------- | ------------------ | ------------ | -----------------------------------------------------------|
| join_on             | Required           | str          | Corresponding db column                                    |
| relation_name       | Required              | bool         | is allow null value, Default True                       |
| refer_to            | Required              | str          | Default value                                           |


- Simple Example : 
    - User Model

    ```python
    import hashlib
    import role
    from time import time
    from uuid import uuid4
    from spannerorm import BaseModel, StringField, BoolField, TimeStampField, ManyToOne
    
    
    class User(BaseModel):
        # Db column Fields
        _id = StringField(db_column='id', null=False)
        _name = StringField(db_column='name', null=False)
        _role_id = StringField(db_column='role_id', null=False)
        _created_at = TimeStampField(db_column='created_at', null=False, default=time())
    
        # Relational Fields
        _role = ManyToOne(join_on='role_id', relation_name='role', refer_to='id')
    
        @property
        @StringField.get
        def id(self):
            return self._id
    
        @id.setter
        @StringField.set
        def id(self, id):
            self._id = id
    
        @property
        @StringField.get
        def name(self):
            return self._name
    
        @name.setter
        @StringField.set
        def name(self, name):
            self._name = name
    
        @property
        @StringField.get
        def role_id(self):
            return self._role_id
    
        @role_id.setter
        @StringField.set
        def role_id(self, role_id):
            self._role_id = role_id
    
        @property
        @TimeStampField.get
        def created_at(self):
            return self._created_at
    
        @created_at.setter
        @TimeStampField.set
        def created_at(self, created_at):
            self._created_at = created_at
    
        @property
        @ManyToOne.get
        def role(self):
            return self._role
    
        @role.setter
        @ManyToOne.set
        def role(self, data):
            self._role = data
    
        class Meta:
            db_table = 'users'
            primary_key = 'id'
    
            @classmethod
            def relations(cls):
                return {
                    'role': role.Role
                }
    
            @classmethod
            def generate_pk(cls):
                return uuid4()
    
    ```
    
**_Note_**: Model `Field` & `Relation Field` name should be `_[prop_name]` form & should have property with `getter` & `setter`

### Meta
Model-specific configuration is placed in a special class called `Meta`. Meta Class created inside model class.
```python
    # This Meta class placed inside mode class
    class Meta:
            db_table = 'users'
            primary_key = 'id'
    
            @classmethod
            def relations(cls):
                return {
                    'role': role.Role
                }
    
            @classmethod
            def generate_pk(cls):
                return uuid4()
```
- db_table: database table map to model
- primary_key: primary key of db table
- relations(cls): function return relations that reference to another model.
- generate_pk(cls): function that generate & return primary key value

### Model Decorator
- spannerorm decorators

| Decorator               |  Description                                                            |
| ----------------------- | ----------------------------------------------------------------------- |
| @StringField.get        | StringField getter, should use with `property` decorator                |
| @StringField.set        | StringField setter, should use with `setter`  decorator                 |
| @IntegerField.get       | IntegerField getter, should use with `property` decorator               |
| @IntegerField.set       | IntegerField setter, should use with `setter`  decorator                |
| @FloatField.get         | FloatField getter, should use with `property` decorator                 |
| @FloatField.set         | FloatField setter, should use with `setter`  decorator                  |
| @BoolField.get          | BoolField getter, should use with `property` decorator                  |
| @BoolField.set          | BoolField setter, should use with `setter`  decorator                   |
| @BytesField.get         | BytesField getter, should use with `property` decorator                 |
| @BytesField.set         | BytesField setter, should use with `setter`  decorator                  |
| @TimeStampField.get     | TimeStampField getter, should use with `property` decorator             |
| @TimeStampField.set     | TimeStampField setter, should use with `setter`  decorator              |
| @DateField.get          | DateField getter, should use with `property` decorator                  |
| @DateField.set          | DateField setter, should use with `setter`  decorator                   |
| @EnumField.get          | EnumField getter, should use with `property` decorator                  |
| @EnumField.set          | EnumField setter, should use with `setter`  decorator                   |
|                         |                                                                         |
| @OneToOne.get           | OneToOne relation getter, should use with `property` decorator          |
| @OneToOne.set           | OneToOne relation setter, should use with `setter`  decorator           |
| @OneToMany.get          | OneToMany relation getter, should use with `property` decorator         |
| @OneToMany.set          | OneToMany relation setter, should use with `setter`  decorator          |
| @ManyToOne.get          | ManyToOne relation getter, should use with `property` decorator         |
| @ManyToOne.set          | ManyToOne relation setter, should use with `setter`  decorator          |
| @ManyToMany.get         | ManyToMany relation getter, should use with `property` decorator        |
| @ManyToMany.set         | ManyToMany relation setter, should use with `setter`  decorator         |

## Query Records
Model query records public methods

#### find(criteria)
Fetch single record data filter by criteria
```markdown
- params:
    - criteria:
        - Filter criteria
        - Type: Criteria
        - Default Value: None
        - Optional
- return:
    - If exist return Model object else None
    - Type: Model object | None
```

eg: With out join
```python
criteria = Criteria()
criteria.condition([(User.role_id, '=', '1'), (User.organization_id, '=', '4707145032222247178')])
user = User.find(criteria)
```

eg: With join
```python
criteria = Criteria()
criteria.join_with(User.role)
user = User.find()
user_role = user.role
```
#### find_by_pk(pk, criteria)
Fetch record by primary key filter by criteria
```markdown
- params:
    - pk:
        - Primary Key value
        - Type: str | int (depending on primary key data type)
        - Required
    - criteria:
        - Filter criteria
        - Type: Criteria
        - Default Value: None
        - Optional
- return:
    - If exist return Model object else None
    - Type: Model object | None
```

eg:
```python
criteria = Criteria()
criteria.add_condition((User.is_deleted, '=', False))
user = User.find_by_pk('-300113230644022007', criteria)
```

#### find_all(criteria)
Fetch records filter by criteria
```markdown
- params:
    - criteria:
        - Filter criteria
        - Type: Criteria
        - Default Value: None
        - Optional
- return:
    - list of model
    -Type: list
```

eg: With out join
```python
criteria = Criteria()
criteria.condition([(User.email, 'LIKE', '%@lftechnology.com')])
criteria.add_condition((User.role_id, 'IN', ['1', '2']))
criteria.add_condition((User.organization_id, 'NOT IN', ['4707145032222247178']))
criteria.set_order_by(User.email, 'ASC')
criteria.limit = 2

users = User.find_all(criteria)
```

eg: With ManyToOne Join
```python
criteria = Criteria()
criteria.join_with(User.role)
criteria.join_with(User.organization)
criteria.condition([(User.email, 'LIKE', '%@lftechnology.com')])
criteria.set_order_by(User.email, 'ASC')
criteria.limit = 2

users = User.find_all(criteria)

for user in users:
    print(user.role)
```

eg: With OneToMany Join
```python
criteria = Criteria()
criteria.join_with(Role.users)
criteria.add_condition((User.email, '=', 'mjsanish+admin@gmail.com'))
criteria.set_order_by(User.email, order='DESC')
role = Role.find(criteria)
users = role.users

for user in users:
    print(user)
```

### Criteria
`Criteria` object represents a query filter criteria, such as conditions, ordering by, limit/offset. 

#### Criteria.condition(conditions, operator)
Set criteria condition that filter result set
```markdown
- params:
    - conditions:
        - List of conditions
        - Type: list
        - Required
    - operator:
        - Sql operator
        - Type: str
        - Default: AND
        - Allow values: [AND | OR]
        - Optional
```

eg: `WHERE users.email LIKe '%@lftechnology.com'`
```python
criteria = Criteria()
criteria.condition([(User.email, 'LIKE', '%@lftechnology.com')])
```

eg: `WHERE users.email LIKe '%@lftechnology.com' OR users.role_id IN ('1', '2')`
```python
criteria = Criteria()
criteria.condition([(User.email, 'LIKE', '%@lftechnology.com'), (User.role_id, 'IN', ['1', '2'])], 'OR')
```

eg: `WHERE user.name LIKE '%lf%' AND (users.active=true OR users.is_deleted=false)`
```python
criteria = Criteria()
criteria.condition([((User.name, 'LIKE', '%lf%'), 'AND', ((User.active, '=', True), 'OR', (User.is_deleted, '=', False)))])
```

eg: `WHERE (((users.name LIKE '%lf%') AND (users.active=true OR users.is_deleted=false)) OR (users.user_name='mjsanish' AND users.password='pass')) OR (users.role_id IN (1, 3))`
```python
criteria = Criteria()
criteria.condition([(((User.name, 'LIKE', '%lf%'), 'AND', ((User.active, '=', True), 'OR', (User.is_deleted, '=', False))), 'OR', ((User.user_name, '=', 'mjsanish'), 'AND', (User.password, '=', 'pass'))), (User.role_id, 'IN', [1, 3])], 'OR')

```

#### add_condition(condition, operator)
Add criteria condition that filter result set
```markdown
- params:
    - condition:
        - Filter condition
        - Type: tuple
        - Required
    - operator:
        - Condition operator
        - Type: str
        - Default: AND
        - Allow values: [AND | OR]
        - Optional
```

eg: `WHERE users.email LIKe '%@lftechnology.com'`
```python
criteria = Criteria()
criteria.add_condition([(User.email, 'LIKE', '%@lftechnology.com')])
```

eg: `WHERE users.email LIKe '%@lftechnology.com' OR users.role_id IN ('1', '2')`
```python
criteria = Criteria()
criteria.condition([(User.email, 'LIKE', '%@lftechnology.com')])
criteria.add_condition((User.role_id, 'IN', ['1', '2']), 'OR')
```

eg:
eg: `WHERE user.name LIKE '%lf%' AND (users.active=false OR users.is_deleted=true)`
```python
criteria = Criteria()
criteria.add_condition((User.name, 'LIKE', '%lf%'))
criteria.add_condition(((User.active, '=', False), 'OR', (User.is_deleted, '=', True)))
```

#### Criteria Condition Operators

| Operator  | Description                            |  Example                                                             |
| --------- | ---------------------------------------| -------------------------------------------------------------------- |
| =        | Equal                                   | (User.name, '=', 'sanish')                                           |
| >        | Greater Than                            | (User.points, '>', 100)                                              |
| <        | Less Than                               | (User.points, '<', 2000)                                             |
| >=       | Greater Than Or Equal                   | (User.points, '>=', 100)                                             |
| <=       | Less Than Or Equal                      | (User.points, '<=', 1000)                                            |
| <>       | Not Equal                               | (User.name, '<>', 'sanish')                                          |
| LIKE     | Search for a pattern                    | (User.name, 'LIKE', '%sa%')                                          |
| IN       | Search for `In` Multiple values         | (User.role_id, 'IN', ['1', '2'])                                     |
| NOT IN   | Search for `Not In` Multiple values     | (Task.status, 'NOT IN', ['pending', 'under review'])                 |
| AND      | Join two condition with `AND` operator  | ((User.name, 'LIKE', '%sa%') , 'AND', (User.is_deleted, '=', False)) |
| OR       | Join two condition with `OR` operator   | ((User.name, 'LIKE', '%sa%') , 'OR', (User.is_deleted, '=', False))  |




