import six
import copy
import inspect
from .helper import Helper
from .criteria import Criteria
from .executor import Executor
from .relation import Relation
from .data_parser import DataParser
from .query_builder import QueryBuilder
from .spanner_exception import SpannerException
from google.cloud.spanner_v1.transaction import Transaction


class BaseModel(object):
    def __init__(self, *args, **kwargs):
        if self._meta().db_table is None:
            raise Exception("Error: {0} model's Meta.db_table is not set".format(self.__class__.__name__))

        if self._meta().primary_key is None:
            raise SpannerException("Error: {0} model's Meta.primary_key is not set".format(self.__class__.__name__))

        model_attrs = Helper.get_model_attrs(self.__class__)
        for attr_name in model_attrs:
            self.__setattr__(attr_name, copy.deepcopy(model_attrs.get(attr_name)))

        model_relation_attrs = Helper.get_model_relations_attrs(self.__class__)
        for attr_name in model_relation_attrs:
            self.__setattr__(attr_name, Relation.copy_instance(model_relation_attrs.get(attr_name)))

        self.__state__ = self.__class__.ModelState()

    def __str__(self):
        return Helper.get_model_props_key_value(self).__str__()

    def __dict__(self):
        model_props = {}
        relation_attrs = Helper.get_model_relations_attrs(self)
        for key, value in inspect.getmembers(self.__class__, Helper.is_property):
            attr_name = '_' + key
            if attr_name not in relation_attrs or key in self._model_state().with_relation:
                model_props[key] = self.__getattribute__(key)

        return model_props

    def _model_state(self):
        """
        Return model object states

        :rtype: BaseModel.State
        :return:
        """
        return self.__state__

    def equals(self, obj):
        """
        Compare two model object is equals or not

        :type obj: BaseModel
        :param obj: model object

        :rtype: bool
        :return: True if two model objects are equal
        """
        if isinstance(BaseModel, obj) is False:
            return False

        return Helper.get_model_props_key_value(self) == Helper.get_model_props_key_value(obj)

    def is_new_record(self):
        """
        Return is new record object or existing record object

        :rtype: bool
        :return: True if new record else False
        """
        return self.__state__.is_new

    def get_pk_value(self):
        """
        Return primary key value

        :rtype: object
        :return:
        """
        props = Helper.get_model_props_key_value(self)
        return props.get(self._meta().primary_key)

    def get_errors(self):
        """
        Return validation errors

        :rtype: dict
        :return:
        """
        self.validate()
        return self.__state__.errors

    def validate(self):
        """
        Validate model properties

        :rtype: bool
        :return: True if model properties are valid else False
        """
        is_valid = True
        for key, value in inspect.getmembers(self.__class__, Helper.is_property):
            prop_validation = self.validate_property(value)
            if prop_validation.get('is_valid') is False:
                is_valid = False
                errors = self._model_state().errors
                errors[key] = prop_validation.get('error_msg')

        return is_valid

    def validate_property(self, prop):
        """
        Validate model property

        :type prop: property
        :param prop: model property

        :rtype: dict
        :return: {'is_valid':bool, 'error_msg':str}
        """
        return Helper.validate_model_prop(self, prop)

    def set_props(self, raw_data):
        """
        Set model properties

        :type raw_data: dict
        :param raw_data: properties key-values

        :rtype: BaseModel
        :return:
        """
        for key in raw_data:
            if self.has_property(key):
                value = raw_data.get(key)
                if isinstance(value, six.string_types):
                    self.__setattr__(key, str(raw_data.get(key)))
                else:
                    self.__setattr__(key, raw_data.get(key))

        return self

    @classmethod
    def _meta(cls):
        return cls.__dict__.get('Meta')

    @classmethod
    def _fetch_query(cls, query_builder, transaction=None):
        """
        Fetch data from query string

        :type query_string: str
        :param query_string:

        :type query_builder: QueryBuilder
        :param query_builder:

        :type transaction: Transaction
        :param transaction:

        :rtype: list
        :return: model list of result set
        """
        ids = None
        if query_builder.with_multi_joins:
            key_results = Executor.execute_query(query_builder.get_primary_keys(), query_builder.params, query_builder.param_types,
                                         transaction=transaction)
            ids = [row[0] for row in key_results]

        query_string = query_builder.get_query(ids)
        results = Executor.execute_query(query_string, query_builder.params, query_builder.param_types,
                                         transaction=transaction)
        result_sets = DataParser.map_model(results, query_builder.select_cols, cls)
        cls._fetch_multi_join_query(query_builder, result_sets)

        return result_sets

    @classmethod
    def _fetch_multi_join_query(cls, query_builder, result_sets, transaction=None):
        """
        Fetch data of multi join relation (OneToMany, ManyToMany) query

        :type query_builder: QueryBuilder
        :param query_builder:

        :type transaction: Transaction
        :param transaction:

        :type result_sets: list
        :param result_sets: model list result set
        """
        for relation_name in query_builder.multi_joins:
            multi_join = query_builder.multi_joins.get(relation_name)
            relation_prop = multi_join.get('relation_prop')
            relation_attr = Helper.model_relational_attr_by_prop(cls, relation_prop)
            refer_to_model = multi_join.get('refer_to_model')

            join_on_values = []
            for row in result_sets:
                join_on_value = getattr(row, relation_attr.join_on)
                if join_on_value:
                    join_on_values.append(join_on_value)

            if len(join_on_values) == 0:
                return []

            query_string = query_builder.get_multi_join_query(relation_name, join_on_values)
            join_results = Executor.execute_query(query_string, query_builder.params, query_builder.param_types,
                                                  transaction=transaction)
            join_result_sets = DataParser.map_model(join_results, multi_join.get('select_cols'), refer_to_model)

            DataParser.map_multi_join_model(result_sets, join_result_sets, relation_name, relation_attr.join_on,
                                            relation_attr.refer_to)

    @classmethod
    def _fetch_primary_keys(cls, criteria, transaction=None):
        """
        Fetch primary keys by criteria

        :type criteria: Criteria
        :param criteria: select criteria

        :type transaction: Transaction
        :param transaction:

        :rtype: list
        :return:
        """
        query_builder = QueryBuilder(cls, criteria)
        query_string = query_builder.get_primary_keys()
        results = Executor.execute_query(query_string, query_builder.params, query_builder.param_types,
                                         transaction=transaction)
        parse_results = DataParser.parse_result_set(results, [cls._meta().primary_key])

        primary_keys = []
        for row in parse_results:
            primary_keys.append(row.get(cls._meta().primary_key))

        return primary_keys

    @classmethod
    def get_meta_data(cls):
        """
        Return model mata data

        :rtype: dict
        :return:
        """
        class_meta = cls._meta()
        meta_data = {
            'db_table': class_meta.db_table,
            'primary_key': class_meta.primary_key,
            'properties': Helper.get_model_props_details(cls),
            'relations': Helper.get_relation_props_details(cls)
        }

        return meta_data

    @classmethod
    def primary_key_property(cls):
        """
        Return primary key property

        :rtype: property
        :return:
        """
        model_props = Helper.get_model_props(cls)
        return model_props.get(cls._meta().primary_key)

    @classmethod
    def has_property(cls, property_name):
        """
        Check is model has property by name

        :type property_name: str
        :param property_name: Property name

        :rtype: bool
        :return: True if property exist else False
        """
        model_props = Helper.get_model_props(cls)
        return property_name in model_props

    @classmethod
    def count(cls, criteria=None, transaction=None):
        """
        return count

        :type criteria: Criteria
        :param criteria:

        :type transaction: Transaction
        :param transaction:

        :rtype: int
        :return: count rows
        """
        if criteria is None:
            criteria = Criteria()

        query_builder = QueryBuilder(cls, criteria)
        query_string = query_builder.get_count()
        result = Executor.execute_query(query_string, query_builder.params, query_builder.param_types,
                                        transaction=transaction)

        return result.one()[0]

    @classmethod
    def delete_one(cls, criteria=None, transaction=None):
        """
        Delete match first record that satisfied criteria

        :type criteria: Criteria
        :param criteria:

        :type transaction: Transaction
        :param transaction:

        :rtype: bool
        :return: true if success
        """
        if criteria is None:
            criteria = Criteria()

        criteria.limit = 1
        primary_keys = cls._fetch_primary_keys(criteria)

        pk_list = []
        if len(primary_keys) != 0:
            pk_list.append((primary_keys[0],))
            Executor.delete_data(cls._meta().db_table, pk_list, transaction=transaction)

        return True

    @classmethod
    def delete_by_pk(cls, pk, transaction=None):
        """
        Delete record by primary key

        :type pk: object
        :param pk: primary key

        :rtype: bool
        :return: true if success

        :type transaction: Transaction
        :param transaction:

        :raise: RuntimeError
        """
        criteria = Criteria()
        criteria.add_condition((cls.primary_key_property(), '=', pk))
        primary_keys = cls._fetch_primary_keys(criteria)

        pk_list = []
        if len(primary_keys) != 0:
            pk_list.append((primary_keys[0],))
            Executor.delete_data(cls._meta().db_table, pk_list, transaction=transaction)
            return True
        else:
            raise RuntimeError('Record not exist with primary key : {}'.format(pk))

    @classmethod
    def delete_all(cls, criteria=None, transaction=None):
        """
        Delete all record that satisfied criteria

        :type criteria: Criteria
        :param criteria:

        :type transaction: Transaction
        :param transaction:

        :rtype: bool
        :return: return True if success
        """
        if criteria is None:
            criteria = Criteria()

        criteria.limit = 2
        primary_keys = cls._fetch_primary_keys(criteria)

        pk_list = []
        if len(primary_keys) != 0:
            for pk in primary_keys:
                pk_list.append((pk,))
            Executor.delete_data(cls._meta().db_table, pk_list, transaction=transaction)

        return True

    @classmethod
    def find(cls, criteria=None, transaction=None):
        """
        Fetch single record data filter by criteria

        :type criteria: Criteria
        :param criteria:

        :type transaction: Transaction
        :param transaction:

        :rtype: BaseModel
        :return: If exist return Model else None
        """
        if criteria is None:
            criteria = Criteria()

        criteria.limit = 1
        query_builder = QueryBuilder(cls, criteria)
        results = cls._fetch_query(query_builder, transaction)

        if len(results) == 1:
            return results[0]
        else:
            return None

    @classmethod
    def find_by_pk(cls, pk, criteria=None, transaction=None):
        """
        Fetch record by primary key filter by criteria

        :type pk: object
        :param pk: primary key

        :type criteria: Criteria
        :param criteria:

        :type transaction: Transaction
        :param transaction:

        :rtype: BaseModel
        :return: If exist return Model else None
        """
        if criteria is None:
            criteria = Criteria()

        criteria.limit = 1
        criteria.add_condition((cls.primary_key_property(), '=', pk))

        query_builder = QueryBuilder(cls, criteria)
        results = cls._fetch_query(query_builder, transaction)

        if len(results) == 1:
            return results[0]
        else:
            return None

    @classmethod
    def find_all(cls, criteria=None, transaction=None):
        """
        Fetch records filter by criteria

        :type criteria: Criteria
        :param criteria: select criteria

        :type transaction: Transaction
        :param transaction:

        :rtype: list
        :return: list of records
        """
        if criteria is None:
            criteria = Criteria()

        query_builder = QueryBuilder(cls, criteria)
        return cls._fetch_query(query_builder, transaction)

    @classmethod
    def insert_block(cls, raw_data_list, transaction=None):
        """
        Insert data row

        :type raw_data_list: list eg: [{'name': 'sanish', 'email': 'mjsanish@gmail.com}]
        :param raw_data_list: insert data list

        :type transaction: Transaction
        :param transaction:

        :rtype: list
        :return: list of inserted model
        """
        parse_raw_data = DataParser.parse_raw_data(cls, raw_data_list, insert=True)
        Executor.insert_data(cls._meta().db_table, parse_raw_data.get('columns'), parse_raw_data.get('data_list'),
                             transaction=transaction)

        for model_object in parse_raw_data.get('model_list'):
            model_object._model_state().is_new = False

        return parse_raw_data.get('model_list')

    @classmethod
    def update_block(cls, raw_data_list, transaction=None):
        """
        Update records in block

        :type raw_data_list: list
        :param raw_data_list: list of data to update

        :type transaction: Transaction
        :param transaction:

        :rtype: list
        :return: list of updated model
        """
        parse_raw_data = DataParser.parse_raw_data(cls, raw_data_list, insert=False)
        Executor.update_data(cls._meta().db_table, parse_raw_data.get('columns'), parse_raw_data.get('data_list'),
                             transaction=transaction)
        return parse_raw_data.get('model_list')

    @classmethod
    def save(cls, model_obj, transaction=None):
        """
        Add/Update model data

        :type model_obj: BaseModel
        :param model_obj: model object

        :type transaction: Transaction
        :param transaction:

        :rtype: BaseModel
        :return: model object
        """
        prepare_data = DataParser.build_model_data(cls, [model_obj])
        Executor.save_data(cls._meta().db_table, prepare_data.get('columns'), prepare_data.get('data_list'),
                           transaction=transaction)

        model_object = prepare_data.get('model_list')[0]
        model_object._model_state().is_new = False
        return model_object

    @classmethod
    def save_all(cls, model_obj_list, transaction=None):
        """
        Add / update all model data

        :type model_obj_list: list
        :param model_obj_list: list of model objects

        :type transaction: Transaction
        :param transaction:

        :rtype: list
        :return: list of updated model objects
        """
        prepare_data = DataParser.build_model_data(cls, model_obj_list)
        Executor.save_data(cls._meta().db_table, prepare_data.get('columns'), prepare_data.get('data_list'),
                           transaction=transaction)

        for model_object in prepare_data.get('model_list'):
            model_object._model_state().is_new = False

        return prepare_data.get('model_list')

    @classmethod
    def update_by_pk(cls, pk, data, transaction=None):
        """
        Update model by primary key

        :type pk: object
        :param pk:

        :type data: dict
        :param data: data to update

        :type transaction: Transaction
        :param transaction:

        :rtype: BaseModel
        :return: updated model object
        """
        model_object = cls.find_by_pk(pk)
        if not model_object:
            raise AssertionError('Record not exist with primary key : {}'.format(pk))

        model_object.set_props(data)
        return cls.save(model_object, transaction=transaction)

    @classmethod
    def relations(cls):
        """
        Return model relations

        :rtype: dict
        :return:
        """
        meta_class = cls._meta()
        return meta_class.relations

    class ModelState(object):
        _is_new = True
        _errors = {}
        _with_relation = []

        @property
        def is_new(self):
            return self._is_new

        @is_new.setter
        def is_new(self, is_new):
            if isinstance(is_new, bool) is False:
                raise TypeError('Should be bool type')
            self._is_new = is_new

        @property
        def errors(self):
            return self._errors

        @errors.setter
        def errors(self, errors):
            self._errors = errors

        @property
        def with_relation(self):
            return self._with_relation

        def add_with_relation(self, relation):
            self._with_relation.append(relation)
