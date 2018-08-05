# Google Cloud Spanner-ORM:
Spanner ORM is a simple and small ORM. It easy to learn and intuitive to use.

[![PYPI][pypi-image]][pypi-url]
[![Version][version-image]][pypi-url]

[pypi-image]: https://img.shields.io/pypi/v/spannerorm.svg?style=flat-square
[pypi-url]: https://pypi.org/project/spannerorm/
[version-image]: https://img.shields.io/pypi/pyversions/spannerorm.svg?style=flat-square   
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
- python 2.7 - 3.6
- Connection pooling
- Support DB Transaction
- Support DB Migration

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
    * [count(criteria, transaction)](#countcriteria-transaction)
    * [find(criteria, transaction)](#findcriteria-transaction)
    * [find_by_pk(pk, criteria, transaction)](#find_by_pkpk-criteria-transaction)
    * [find_all(criteria, transaction)](#find_allcriteria-transaction)
        * [Criteria](#criteria)
            * [criteria.condition(conditions, operator)](#criteriaconditionconditions-operator)
            * [criteria.add_condition(condition, operator)](#criteriaadd_conditioncondition-operator)
                * [Criteria condition](#criteria-condition)
                * [Criteria Condition Operators](#criteria-condition-operators)
            * [criteria.limit](#criterialimit)
            * [criteria.offset](#criteriaoffset)
            * [criteria.set_order_by(order_by_props, order)](#criteriaset_order_byorder_by_props-order)
            * [criteria.oin_with(relation, join_type)](#criteriaoin_withrelation-join_type)
* [Block Records INSERT | UPDATE](#block-records-insert--update)
    * [insert_block(raw_data_list, transaction)](#insert_blockraw_data_list-transaction)
    * [update_block(cls, raw_data_list, transaction)](#update_blockcls-raw_data_list-transaction)
* [Save Record (ADD / UPDATE)](#save-record-add--update)
    * [save(model_obj, transaction)](#savemodel_obj-transaction)
    * [save_all(model_obj_list, transaction)](#save_allmodel_obj_list-transaction)
    * [update_by_pk(pk, data, transaction)](#update_by_pkpk-data-transaction)
* [Delete Records](#delete-records)
    * [delete_one(criteria, transaction)](#delete_onecriteria-transaction)
    * [delete_by_pk(pk, transaction)](#delete_by_pkpk-transaction)
* [Running with Transaction](#running-with-transaction)
* [Model object functions](#model-object-functions)
    * [set_props(raw_data)](#set_propsraw_data)
    * [equals(obj)](#equalsobj)
    * [is_new_record()](#is_new_record)
    * [get_pk_value()](#get_pk_value)
    * [get_errors()](#get_errors)
    * [validate()](#validate)
    * [validate_property(prop)](#validate_propertyprop)
* [Model class functions](#model-class-functions)
    * [get_meta_data()](#get_meta_data)
    * [primary_key_property()](#primary_key_property)
    * [has_property(property_name)](#has_propertyproperty_name)
* [SpannerDb](#spannerdb)
    * [SpannerDb.execute_query(query_string, params, transaction)](#spannerdbexecute_queryquery_string-params-transaction)
    * [SpannerDb.execute_ddl_query(ddl_query_string)](#spannerdbexecute_ddl_queryddl_query_string)
    * [SpannerDb.insert_data(table_name, columns, data)](#spannerdbinsert_datatable_name-columns-data)
    * [SpannerDb.update_data(table_name, columns, data)](#spannerdbupdate_datatable_name-columns-data)
    * [SpannerDb.save_data(table_name, columns, data)](#spannerdbsave_datatable_name-columns-data)
    * [SpannerDb.delete_data(table_name, id_list)](#spannerdbdelete_datatable_name-id_list)
* [Database Migration](#database-migration)
    * [setup Db Migration](#setup-db-migration)
    * [Db Migration commands](#db-migration-commands)
        
    
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

### count(criteria, transaction)
Count record filter by criteria
```markdown
- params:
    - criteria:
        - Filter criteria
        - Type: Criteria
        - Default Value: None
        - Optional
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
- return:
    - Count of record
    - Type: bool
```

eg: With out join
```python
criteria = Criteria()
criteria.condition([(User.role_id, '=', '1'), (User.organization_id, '=', '4707145032222247178')])
user = User.count(criteria)
```

### find(criteria, transaction)
Fetch single record data filter by criteria
```markdown
- params:
    - criteria:
        - Filter criteria
        - Type: Criteria
        - Default Value: None
        - Optional
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
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
### find_by_pk(pk, criteria, transaction)
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
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
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

### find_all(criteria, transaction)
Fetch records filter by criteria
```markdown
- params:
    - criteria:
        - Filter criteria
        - Type: Criteria
        - Default Value: None
        - Optional
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
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

#### Criteria
`Criteria` object represents a query filter criteria, such as conditions, ordering by, limit/offset. 

##### criteria.condition(conditions, operator)
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

##### criteria.add_condition(condition, operator)
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

###### Criteria condition
Criteria `condition` object provide filter cirteria.
```markdown
- Type: tuple(3)
- suntax: (model.property, [= | > | < | >= | <= | <> | IN | NOT IN], value)
          (condition, [AND | OR], condition)

```

###### Criteria Condition Operators
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
| IS       | Is null                                 | (User.name, 'IS', 'NULL')                                            |
| IS NOT   | Is not null                             | (User.name, 'IS NOT', 'NULL')                                        |


##### criteria.limit
Setter limit criteria
```markdown
- Type: int
```

##### criteria.offset
Setter offset criteria
```markdown
- Type: int
```

eg: `WHERE users.name LIKE '%lf%' LIMIT 5 OFFSET 10`
```python
criteria = Criteria()
criteria.add_condition((User.name, 'LIKE', '%lf%'))
criteria.limit = 5
criteria.offset = 10
```

##### criteria.set_order_by(order_by_props, order)
Set order by criteria
```markdown
- params:
    - order_by_props:
        - Order by property or list of order by properties
        - Type: property | list
        - Require
    - order:
        - Define order on asc or desc
        - Type: str
        - Default: ASC
        - Optional
        - Allow values: [ASC | DESC]
```

eg: `WHERE users.name LIKE '%lf%' ORDER BY users.name DESC`
```python
criteria = Criteria()
criteria.add_condition((User.name, 'LIKE', '%lf%'))
criteria.set_order_by(User.name, 'DESC')
```

eg: `ORDER BY users.name, user.email ASC`
```python
criteria = Criteria()
criteria.set_order_by([User.name, User.email])
```

##### criteria.oin_with(relation, join_type, join_condition)
- Add join with criteria. For joining should define relation in model
`````markdown
- params:
    - relation:
        - Model relation property
        - Type: property
        - Require
    - join_type:
        - Define join type
        - Type: str
        - Default value: 'LEFT'
        - Optional
        - Allow values: [LEFT, RIGHT, FULL]
    - join_condition:
        - Define join condition
        - Type: tuple
        - Optional
`````

eg: `LEFT JOIN users on roles.id=users.role_id WHERE roles.name='admin' AND users.email='mjsanish+admin@gmail.com'` 
```python
criteria = Criteria()
criteria.join_with(Role.users, join_condition=(User.is_deleted, '=', False))
criteria.add_condition((Role.name, '=', 'admin'))
criteria.add_condition((User.email, '=', 'mjsanish+admin@gmail.com'))
```

## Block Records INSERT | UPDATE
Model Block function allow insert/update lots of data quickly. 

### insert_block(raw_data_list, transaction)
Insert block of data
```markdown
- params:
    - raw_data_list:
        - List of data
        - Type: list of dict 
        - Require
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
```

eg:
```python
    data_list = [{
        'email': 'mjsanish+1@gmail.com',
        'name': 'sanish1',
        "is_deleted": False,
        'organization_id' : '4707145032222247178',
        'role_id': '1',
        'created_by': '-1202895510759970011',
    }, {
        'email': 'mjsanish+2@gmail.com',
        'name': 'sanish2',
        "is_deleted": False,
        'organization_id' : '4707145032222247178',
        'role_id': '1',
        'created_by': '-1202895510759970011',
    }]

    users = User.insert_block(data_list)
```


### update_block(cls, raw_data_list, transaction)
Update block of data
```markdown
- params:
    - raw_data_list:
        - List of data
        - Type: list of dict 
        - Require
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
```

eg:
```python
    data_list = [{
        'id': '271fc766-6de7-44c7-bd1c-b04954cd401f',
        'email': 'mjsanish+100@gmail.com',
        'name': 'sanish100'
    }, {
        'id': '20b2e97f-4c77-460b-9324-bb7530d6b8f7',
        'role_id': '2'
    }]

    users = User.update_block(data_list)
```


## Save Record (ADD / UPDATE)
Model function provide ability to save model object.

### save(model_obj, transaction)
Add/Update model data to database
```markdown
- params:
    - model_obj:
        - Model object
        - Type: Model
        - Require 
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
- return:
    - Saved or updated  model
    - Type: Model
```

eg:
```python
user = User()
user.name = 'some one'
user.email = 'someone@gmail.com'
user.organization_id = '4707145032222247178'
user.role_id = '1'

user = User.save(user)
```

### save_all(model_obj_list, transaction)
Add / Update list of model to database
```markdown
- params:
    - model_obj_list:
        - list of model objects
        - Type: list
        - Require
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
- return: 
    - list of model
```

eg:
```python
user = User.find_by_pk('d3fefb2a-ef30-4c39-a560-81b459f5024e')
user.name = 'some one'
user.email = 'someone@gmail.com'
user.organization_id = '4707145032222247178'
user.role_id = '1'

users = []
users.append(user)
user = User.save_all(users)
```

### update_by_pk(pk, data, transaction)
Update by primary key of model to database

```markdown
- params:
    - pk:
        - primary key value
        - Type: int | str (base on primary key type)
        - Require
    - data:
        - Data to update
        - Type: dict
        - Require
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
- return: 
    - model
```

## Delete Records
Model delete function allow delete records from database

### delete_one(criteria, transaction)
Delete single record that match with criteria

```markdown
- params:
    - criteria:
        - Filter criteria
        - Type: Criteria
        - Default Value: None
        - Optional
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
- return: True on success else throw exception
```

### delete_by_pk(pk, transaction)
Delete record by primary key
```markdown
- params:
    - pk:
        - Primary key value
        - Type: int | str (base on primary key type)
        - Require
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
- return: True on success else throw exception
```

### delete_all(criteria, transaction)
Delete all records that match with criteria
```markdown
- params:
    - criteria:
        - Filter criteria
        - Type: Criteria
        - Default Value: None
        - Optional
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
- return: True on success else throw exception
```

## Running with Transaction
Spanner-ORM provide @transactional decoration to support transaction
eg:
```python
@transactional
def with_transaction(transaction):
    """
    :type transaction: Transaction
    :param transaction: provide automatically by @transactional 
    """
    role = Role()
    role.name = 'guest'
    role.save(role, transaction)
    
    user = User()
    user.name = 'person 10'
    user.email = 'transaction@gmail.com'
    user.role_id = role.id

    user = User.save(user, transaction)
```

## Model object functions
Spanner-ORM provide some basic model instance functions
### set_props(raw_data):
Set model properties
```markdown
- params: 
    - raw_data
        - Model properties values in prop-value pairs
        - Type : dict
        - Required
```

eg:
```python
user = User()
user.set_props({
    'name' : 'Sanish',
    'address' : 'Nepal'
})

```

### equals(obj)
Compare two model object is equals or not
```markdown
- params: 
    obj:
        - Model object that need to compare
        - Type : Model
        - Required
- return: 
    - True if both are same Model instance with equals values else return return False
    - Type: bool
```

### is_new_record()
Check is new record model instance or existing record model instance
```markdown
- return:
    - Is new record or not
    - Type: bool
```

### get_pk_value()
```markdown
- return:
    - primary key value
    - Type: int | str base on primary key data type
```

### get_errors()
```markdown
- return:
    - Model instance validation errors
    - Type: dict
```
eg:
```python
    user = User()
    user.email = 'someone@gmail.com'
    user.role_id = '1'
    
    if not user.validate():
        errors = user.get_errors()
```
### validate()
```markdown
- return:
    - Check model instance data valid or not
    - Type: bool
```
eg:
```python
    user = User()
    user.email = 'someone@gmail.com'
    user.role_id = '1'
    
    if not user.validate():
        errors = user.get_errors()
```
### validate_property(prop)
```markdown
- return:
    - Check model instance property data is valid or not
    - Type: dict 
            {'is_valid':bool, 'error_msg':str}
```

## Model class functions
Spanner-ORM provide some basic Model class functions

### get_meta_data()
```markdown
- return:
    - Return model mata data information
    - Type: dict

```

### primary_key_property()
```markdown
- return:
    - Primary key name
    - Type: str
```
### has_property(property_name)
```markdown
- return:
    - Check model has property by name, if exist return True else False
    - Type: bool
```

## SpannerDb
`SpannerDb` class provide some direct methods to run native and direct db operations. 

### SpannerDb.execute_query(query_string, params, transaction)
Execute query string
```markdown
- params:
    - query_string:
        - Sql select query string
        - Type: str
        - Required
    - params:
        - Sql params
        - Type: dict
    - transaction
        - DB transaction
        - Type: Transaction
        - Default value: None
        - Optional
- return:
    - Result set
    - Type dict
```
eg:
```python
query_string = 'SELECT * FROM users WHERE name=@name'
results = SpannerDb.execute_query(query_string, {'name': 'sanish'})
```

### SpannerDb.execute_ddl_query(ddl_query_string)
Execute DDL query string
```markdown
- params:
    - query_string:
        - DDL query string
        - Type: str
        - Required
```

eg:
```python
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
```

### SpannerDb.insert_data(table_name, columns, data)
Insert given table data
```markdown
- params:
    - table_name:
        - Db table name
        - Type: str
        - Required
    - columns:
        - list of columns in which date inserting
        - Type: list
        - Required
        - eg. ['id', 'name']
    - data:
        - List of data
        - Type: list
        - Required
        - eg. [(value11, value12), (value21, value22)]
```
### SpannerDb.update_data(table_name, columns, data)
Update given table data
```markdown
- params:
    - table_name:
        - Db table name
        - Type: str
        - Required
    - columns:
        - list of columns in which date updating
        - Type: list
        - Required
        - eg. ['id', 'name']
    - data:
        - List of data
        - Type: list
        - Required
        - eg. [(value11, value12), (value21, value22)]
```

### SpannerDb.save_data(table_name, columns, data)
Save given table data
```markdown
- params:
    - table_name:
        - Db table name
        - Type: str
        - Required
    - columns:
        - list of columns in which date saving
        - Type: list
        - Required
        - eg. ['id', 'name']
    - data:
        - List of data
        - Type: list
        - Required
        - eg. [(value11, value12), (value21, value22)]
```

### SpannerDb.delete_data(table_name, id_list):
Delete given ids data row
```markdown
- params:
    - table_name:
        - Db table name
        - Type: str
        - Required
    - id_list:
        - id tuple list 
        - Type: type
        - eg. [('1',), ('2',)]
```

## Database Migration
`DbMigration` class responsible to run Db migration

### setup Db Migration
- create migration.py file
- Add following code
```python
from spannerorm import DbMigration


class Migration(DbMigration):
    instance_id = ''
    database_id = ''
    service_account_json = ''


if __name__ == '__main__':
    Migration.run()
```
- Config db connection
```markdown
    instance_id: Spanner database instance id
    database_id: Database name
    service_account_json: service account json location full path
```

### Db Migration commands:
Available Migration Commands:
```markdown
    help                                : list available migration commands
    create [migration_name]             : Create new migration file
    up                                  : Run all new migrations
    down                                : Revert back last migration
    down <int>                          : Revert back last given number of migrations
```
eg: python migration.py create user_table            
